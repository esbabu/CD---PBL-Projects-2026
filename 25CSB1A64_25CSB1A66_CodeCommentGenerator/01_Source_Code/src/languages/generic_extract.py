"""
Comment features for C#, Rust and COBOL
========================================
Builds the same ``ForeignAnalysis`` the Java / C / C++ extractor produces
(``ModuleFeatures``, ``ContextGraph``, placement facts) from the multi-language
IR in ``src/multilang`` — parameters, return types, loops, branches, calls,
thrown exceptions / panics and cyclomatic complexity are read from the lowered
functions and their syntax trees.

COBOL: each paragraph of the PROCEDURE DIVISION is documented as a routine and
the program as a whole gets a header comment.
"""
from __future__ import annotations

import re
from typing import Dict, List, Optional

from ..ast_extractor import ClassFeature, FunctionFeature, ModuleFeatures, ParamFeature
from ..context_analyzer import ContextGraph, FunctionContext, VariableInfo, _complexity_label
from ..ir.ir_nodes import IROpcode
from .treesitter_extract import DeclFacts, ForeignAnalysis

_CLASS_NODES = {
    "csharp": {"class_declaration": "class", "struct_declaration": "struct", "interface_declaration": "interface",
               "enum_declaration": "enum", "record_declaration": "record"},
    "rust": {"struct_item": "struct", "enum_item": "enum", "trait_item": "interface", "union_item": "union"},
}


def _indent(lines: List[str], line: int) -> str:
    s = lines[line - 1] if 0 < line <= len(lines) else ""
    return s[: len(s) - len(s.lstrip())]


def _doc_above(lines: List[str], line: int, lang: str) -> bool:
    """A doc comment (/// or /** for C#, /// or //! for Rust) directly above ``line`` (attributes skipped)."""
    i = line - 2
    while i >= 0 and lines[i].strip().startswith(("[", "#[")):
        i -= 1
    if i < 0:
        return False
    s = lines[i].strip()
    return s.startswith("///") or s.startswith("/**") or (lang == "rust" and s.startswith("//!"))


def _decl_start(node, lines: List[str]) -> int:
    """First line of a declaration including attributes written on the lines above it."""
    start = node.start_point[0] + 1
    prev = node.prev_named_sibling
    while prev is not None and prev.type in ("attribute_item", "attribute_list") and prev.end_point[0] + 1 >= start - 1:
        start = prev.start_point[0] + 1
        prev = prev.prev_named_sibling
    return start


def analyze_generic(source: str, language: str, filepath: str = "") -> ForeignAnalysis:
    if language == "cobol":
        return _analyze_cobol(source, filepath)
    from ..multilang.lower import fld, lower_source, named, text
    mod = lower_source(source, language, filepath)
    src = source.encode("utf-8")
    lines = source.splitlines()
    mf = ModuleFeatures(filepath=filepath, total_lines=len(lines))
    facts: Dict[str, DeclFacts] = {}
    cg = ContextGraph(module_name=filepath, module_function_names={i.fn.name for i in mod.functions.values()})
    warnings = [f"The parser recovered from a {mod.syntax_error}; comments may be incomplete there."] \
        if mod.syntax_error else []

    for qual, info in mod.functions.items():
        fn, node = info.fn, info.node
        nid = f"func_{qual}_{fn.source_lineno}"
        params = [ParamFeature(p, info.param_types.get(p + "#raw") or None) for p in fn.params if p != "self"]
        ret_node = fld(node, "returns", "type", "return_type")
        ret = text(ret_node, src).strip() if ret_node is not None else None
        kind = "constructor" if node.type == "constructor_declaration" else (
            "destructor" if node.type == "destructor_declaration" else ("method" if fn.is_method else "function"))
        loops = sum(1 for b in fn.blocks if b.meta.get("kind") == "loop_header")
        conds = sum(1 for b in fn.blocks if b.meta.get("kind") == "if_true")
        decisions = sum(1 for i in fn.all_instructions() if i.op == IROpcode.BRANCH and i.meta.get("kind") in ("if", "loop"))
        decisions += sum(max(0, len(i.operands) - 2) for i in fn.all_instructions()
                         if i.op == IROpcode.BRANCH and i.meta.get("kind") == "switch")
        decisions += sum(1 for i in fn.all_instructions() if i.op == IROpcode.BINOP and i.meta.get("operator") in ("&&", "||"))
        calls = [i.meta.get("chain") or i.call.callee for i in fn.all_instructions()
                 if i.op == IROpcode.CALL and i.call and not i.call.callee.startswith("new ")]
        throws: List[str] = []
        for n in _walk(node):
            if n.type in ("throw_statement", "throw_expression"):
                m = re.search(r"new\s+([\w.]+)", text(n, src))
                if m and m.group(1) not in throws:
                    throws.append(m.group(1))
            elif n.type == "macro_invocation" and text(n, src).split("!")[0].strip() in ("panic", "unreachable",
                                                                                         "unimplemented", "todo"):
                if "panic" not in throws:
                    throws.append("panic")
        if language == "rust" and ret and ret.startswith("Result<"):
            throws.append("Err")
        start = _decl_start(node, lines)
        ff = FunctionFeature(node_id=nid, name=fn.name, lineno=fn.source_lineno, col_offset=node.start_point[1],
                             params=params, return_annotation=ret, decorators=list(info.annotations),
                             has_docstring=_doc_above(lines, start, language),
                             body_lines=fn.end_lineno - fn.source_lineno + 1, calls_made=calls[:40], loops=loops,
                             conditionals=conds, is_method=fn.is_method, parent_class=fn.class_name,
                             is_async="async" in info.modifiers or text(node, src).lstrip().startswith(("async ", "pub async ")))
        mf.functions.append(ff)
        facts[nid] = DeclFacts(kind=kind, insert_line=start, indent=_indent(lines, start), end_line=fn.end_lineno,
                               throws=throws, returns_value=bool(ret and ret not in ("void", "()")))
        cc = decisions + 1
        names = cg.module_function_names
        variables = [VariableInfo(name=v, inferred_type=info.var_types.get(v)) for v in sorted(fn.locals)
                     if v not in fn.params and "#" not in v][:20]
        cg.function_contexts.append(FunctionContext(
            node_id=nid, name=fn.name, cyclomatic_complexity=cc, variables=variables,
            calls_internal=[c for c in calls if c.split(".")[-1] in names and c.split(".")[-1] != fn.name],
            calls_external=[c for c in calls if c.split(".")[-1] not in names],
            complexity_label=_complexity_label(cc)))
        cg.call_graph[fn.name] = calls

    kinds = _CLASS_NODES.get(language, {})
    for n in _walk(mod.tree.root_node):
        if n.type not in kinds:
            continue
        name_node = fld(n, "name")
        name = text(name_node, src) if name_node is not None else "?"
        start = _decl_start(n, lines)
        nid = f"class_{name}_{start}"
        bases = []
        bl = fld(n, "bases") or next((c for c in named(n) if c.type in ("base_list", "trait_bounds")), None)
        if bl is not None:
            bases = [text(c, src) for c in named(bl)][:5]
        methods = [i.fn.name for i in mod.functions.values() if i.fn.class_name == name]
        fields = []
        body = fld(n, "body")
        for c in named(body) if body is not None else []:
            if c.type in ("field_declaration", "property_declaration", "enum_member_declaration", "enum_variant"):
                nn = fld(c, "name") or next((x for x in _walk(c) if x.type in ("identifier", "field_identifier")), None)
                if nn is not None:
                    fields.append(text(nn, src))
        mf.classes.append(ClassFeature(node_id=nid, name=name, lineno=start, col_offset=n.start_point[1], bases=bases,
                                       methods=methods, class_variables=fields[:12],
                                       has_docstring=_doc_above(lines, start, language)))
        facts[nid] = DeclFacts(kind=kinds[n.type], insert_line=start, indent=_indent(lines, start),
                               end_line=n.end_point[0] + 1, class_kind=kinds[n.type])
    mf.functions.sort(key=lambda f: f.lineno)
    mf.classes.sort(key=lambda c: c.lineno)
    return ForeignAnalysis(language, mf, cg, facts, warnings)


def _walk(node):
    stack = [node]
    while stack:
        n = stack.pop()
        yield n
        stack.extend(reversed(n.children))


def _analyze_cobol(source: str, filepath: str) -> ForeignAnalysis:
    from ..multilang.cobol import lower_cobol, tokenize
    mod = lower_cobol(source, filepath)
    p = mod.cobol
    lines = source.splitlines()
    mf = ModuleFeatures(filepath=filepath, total_lines=len(lines))
    facts: Dict[str, DeclFacts] = {}
    cg = ContextGraph(module_name=filepath)
    fn = mod.ir.functions[0]
    # paragraphs: blocks named "para_N" carry the paragraph name; find their source lines
    para_lines: Dict[str, int] = {}
    toks = tokenize(source)
    for k, t in enumerate(toks[p.proc_start:], p.proc_start):
        if k + 1 < len(toks) and toks[k + 1].text == "." and t.col <= 11 and t.up not in ("GOBACK", "EXIT", "END-IF") \
                and (k == p.proc_start or toks[k - 1].text == "."):
            para_lines.setdefault(t.up, t.line)
    blocks = [b for b in fn.blocks if b.meta.get("kind") == "paragraph" and b.meta.get("name") != "<start>"]
    names = {b.meta["name"] for b in blocks}
    cg.module_function_names = names
    for b in blocks:
        name = b.meta["name"]
        line = para_lines.get(name.replace(" SECTION", ""), 0)
        if not line:
            continue
        nid = f"para_{name}_{line}"
        body = [i for i in b.instructions]
        calls = [i.call.raw_callee for i in body if i.op == IROpcode.CALL and i.call]
        uses = sorted({i.result for i in body if i.op == IROpcode.ASSIGN and i.result and
                       not re.fullmatch(r"t\d+", i.result)})
        has_doc = line >= 2 and lines[line - 2].strip().startswith(("*>", "*")) or (
            line >= 2 and len(lines[line - 2]) > 6 and lines[line - 2][6:7] == "*")
        ff = FunctionFeature(node_id=nid, name=name, lineno=line, col_offset=7, has_docstring=has_doc,
                             calls_made=calls[:20], body_lines=1)
        mf.functions.append(ff)
        facts[nid] = DeclFacts(kind="paragraph", insert_line=line, indent=_indent(lines, line), end_line=line)
        cg.function_contexts.append(FunctionContext(node_id=nid, name=name, cyclomatic_complexity=1,
                                                    variables=[VariableInfo(name=u) for u in uses[:12]],
                                                    calls_external=calls[:12], complexity_label="simple"))
    # the program header
    pid_line = next((t.line for t in toks if t.up == "PROGRAM-ID"), 1)
    nid = f"program_{p.program}_{pid_line}"
    mf.classes.append(ClassFeature(node_id=nid, name=p.program, lineno=pid_line, col_offset=7,
                                   methods=[b.meta["name"] for b in blocks],
                                   class_variables=[i.name for i in p.items.values() if i.level in (1, 77)][:12],
                                   has_docstring=f"*> Program {p.program}" in source))
    facts[nid] = DeclFacts(kind="program", insert_line=next((t.line for t in toks if t.up == "IDENTIFICATION"), 1),
                           indent=_indent(lines, pid_line), end_line=len(lines), class_kind="program")
    mf.functions.sort(key=lambda f: f.lineno)
    for a, b in zip(mf.functions, mf.functions[1:] + [None]):     # a paragraph runs to the next one
        end = (b.lineno - 1) if b is not None else len(lines)
        a.body_lines = max(1, end - a.lineno)
        facts[a.node_id].end_line = end
    return ForeignAnalysis("cobol", mf, cg, facts, [])
