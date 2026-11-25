"""
tree-sitter → IR lowering for Java, C, C++, C# and Rust
=========================================================
Lowers every function / method / constructor into an ``IRFunction`` made of
basic blocks of three-address instructions — the same IR the Python front end
produces — so ``analysis.cfg_builder``, ``analysis.dfa_engine`` and
``analysis.pattern_detector`` run on it unchanged.

What is modelled
----------------
* statements: declarations, assignments (plain, compound, field / index / deref
  stores), expression statements, ``if``/``else``, ``while``, ``do``, ``for``,
  for-each / range-for / Rust ``for``/``loop``/``while``, ``switch``/``match``,
  ``try``/``catch``/``finally``, ``return``, ``throw``, ``break``, ``continue``,
  blocks, Rust ``unsafe`` blocks, C# ``using``/``lock``, Java ``synchronized``;
* expressions: literals (string values kept), names, field access, indexing,
  calls (receiver, method, argument operands, a dotted callee chain and the
  receiver's declared type when it is known), object creation (C# object
  initialisers become named arguments), binary / unary operators, casts,
  conditional expressions, string interpolation, Rust macros (``format!`` …),
  lambdas / closures (their bodies are lowered in place).

Anything else is lowered conservatively: its sub-expressions are lowered and
combined with a ``BUILD`` so data still flows through it, and the construct is
listed in ``IRFunction.unsupported``.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from ..ir.ir_nodes import CallInfo, IRBlock, IRFunction, IRInstruction, IRModule, IROpcode

GRAMMARS = {
    "java": "tree_sitter_java", "c": "tree_sitter_c", "cpp": "tree_sitter_cpp",
    "csharp": "tree_sitter_c_sharp", "rust": "tree_sitter_rust",
}
_PARSERS: Dict[str, object] = {}


def parser_for(lang: str):
    if lang not in _PARSERS:
        import importlib

        import tree_sitter
        grammar = importlib.import_module(GRAMMARS[lang])
        _PARSERS[lang] = tree_sitter.Parser(tree_sitter.Language(grammar.language()))
    return _PARSERS[lang]


FUNCTION_TYPES = {
    "java": {"method_declaration", "constructor_declaration", "compact_constructor_declaration"},
    "c": {"function_definition"},
    "cpp": {"function_definition"},
    "csharp": {"method_declaration", "constructor_declaration", "local_function_statement",
               "operator_declaration", "destructor_declaration"},
    "rust": {"function_item"},
}
CLASS_TYPES = {"class_declaration", "interface_declaration", "enum_declaration", "record_declaration",
               "struct_declaration", "class_specifier", "struct_specifier", "impl_item", "trait_item"}
BLOCK_TYPES = {"block", "compound_statement", "declaration_list", "statement_list", "field_declaration_list",
               "switch_block", "constructor_body", "unsafe_block", "else_clause", "finally_clause"}
LOOP_TYPES = {"while_statement", "do_statement", "for_statement", "enhanced_for_statement", "foreach_statement",
              "for_range_loop", "for_expression", "while_expression", "loop_expression", "for_each_statement"}
STRING_TYPES = {"string_literal", "raw_string_literal", "verbatim_string_literal", "character_literal",
                "char_literal", "text_block", "concatenated_string", "string"}
LITERAL_TYPES = STRING_TYPES | {"integer_literal", "decimal_integer_literal", "hex_integer_literal",
                                "number_literal", "float_literal", "real_literal", "decimal_floating_point_literal",
                                "true", "false", "boolean_literal", "null_literal", "null", "nullptr",
                                "boolean", "unit_expression"}
NAME_TYPES = {"identifier", "field_identifier", "type_identifier", "this", "self", "this_expression",
              "base_expression", "super", "shorthand_field_identifier", "namespace_identifier"}
CALL_TYPES = {"method_invocation", "call_expression", "invocation_expression"}
NEW_TYPES = {"object_creation_expression", "new_expression", "implicit_object_creation_expression",
             "struct_expression"}
FIELD_TYPES = {"field_access", "member_access_expression", "field_expression", "scoped_identifier",
               "qualified_identifier", "member_binding_expression", "conditional_access_expression"}
INDEX_TYPES = {"array_access", "element_access_expression", "subscript_expression", "index_expression"}
LAMBDA_TYPES = {"lambda_expression", "closure_expression", "anonymous_method_expression"}
COMPARE_OPS = {"==", "!=", "<", ">", "<=", ">=", "&&", "||", "instanceof", "is"}


def text(node, src: bytes) -> str:
    return src[node.start_byte:node.end_byte].decode("utf-8", errors="replace") if node is not None else ""


def fld(node, *names):
    for n in names:
        c = node.child_by_field_name(n)
        if c is not None:
            return c
    return None


def named(node) -> List:
    return [c for c in node.children if c.is_named and c.type not in ("comment", "line_comment", "block_comment")]


_WRAPPERS = {"Data", "Arc", "Rc", "Box", "Mutex", "RwLock", "RefCell", "Cell", "Option", "Pin", "Lazy",
             "Optional", "shared_ptr", "unique_ptr", "weak_ptr", "Lazy", "Task", "ValueTask"}


def base_type(type_text: str) -> str:
    """``final List<String>`` → ``List``; ``std::string&`` → ``string``; ``web::Data<Connection>`` → ``Connection``."""
    m = re.match(r"^\s*(?:&\s*(?:mut\s+)?)?([\w:.]+)\s*<(.*)>\s*$", type_text or "")
    if m and re.split(r"[:.]+", m.group(1))[-1] in _WRAPPERS:
        return base_type(m.group(2))
    t = re.sub(r"<.*>", "", type_text or "")
    t = re.sub(r"\[.*?\]|[&*]|\b(const|final|mut|ref|out|in|static|unsigned|signed|struct|class|dyn|impl)\b", " ", t)
    parts = [p for p in re.split(r"[\s:.]+", t) if p]
    return parts[-1] if parts else ""


def string_value(node, src: bytes) -> str:
    """Literal text without quotes / prefixes (escapes left as written)."""
    raw = text(node, src)
    m = re.match(r'^(?:[A-Za-z@$]*)?(r#*)?("""|"|\'|`)', raw)
    if node.type == "concatenated_string":
        return "".join(string_value(c, src) for c in named(node) if c.type in STRING_TYPES)
    if m:
        q = m.group(2)
        body = raw[m.end():]
        end = body.rfind(q)
        return body[:end] if end >= 0 else body
    return raw


@dataclass
class FunctionInfo:
    """Lowered function plus the facts rules need about its declaration."""
    fn: IRFunction
    node: object
    param_types: Dict[str, str] = field(default_factory=dict)
    var_types: Dict[str, str] = field(default_factory=dict)
    annotations: List[str] = field(default_factory=list)   # decorators / attributes as written
    modifiers: str = ""
    class_annotations: List[str] = field(default_factory=list)
    name_line: int = 0                                     # line of the function's name (after annotations)


@dataclass
class LoweredModule:
    language: str
    source: str
    ir: IRModule
    functions: Dict[str, FunctionInfo]
    tree: object = None
    syntax_error: Optional[str] = None


class _FnLowerer:
    def __init__(self, lang: str, src: bytes, info: FunctionInfo):
        self.lang, self.src, self.info, self.fn = lang, src, info, info.fn
        self.cur: Optional[IRBlock] = None
        self._uid = self._temp = 0
        self._counts: Dict[str, int] = {}
        self.loops: List[Tuple[str, str]] = []    # (continue target, break target)
        self.line = info.fn.source_lineno
        self.guards: List[str] = []

    # ── block plumbing (mirrors ir.lowering) ────────────────────────────
    def count(self, k: str) -> int:
        self._counts[k] = self._counts.get(k, 0) + 1
        return self._counts[k]

    def uid(self) -> int:
        self._uid += 1
        return self._uid

    def temp(self) -> str:
        t = f"t{self._temp}"
        self._temp += 1
        return t

    def new_block(self, label: str, **meta) -> IRBlock:
        b = IRBlock(label=label, meta={k: str(v) for k, v in meta.items()})
        b.instructions.append(IRInstruction(IROpcode.LABEL, lineno=self.line, meta={"name": label}, uid=self.uid()))
        self.fn.blocks.append(b)
        return b

    def link(self, a: Optional[IRBlock], label: str) -> None:
        if a is None:
            return
        if label not in a.successors:
            a.successors.append(label)
        b = self.fn.get_block(label)
        if b is not None and a.label not in b.predecessors:
            b.predecessors.append(a.label)

    def ensure(self) -> IRBlock:
        if self.cur is None:
            self.cur = self.new_block(f"dead_{self.count('dead')}", kind="unreachable")
        return self.cur

    def emit(self, op: IROpcode, result=None, operands=None, node=None, call=None, **meta) -> IRInstruction:
        line = (node.start_point[0] + 1) if node is not None else self.line
        ins = IRInstruction(op=op, result=result, operands=list(operands or []), lineno=line,
                            meta={k: str(v) for k, v in meta.items()},
                            col=node.start_point[1] if node is not None else 0,
                            end_lineno=(node.end_point[0] + 1) if node is not None else line,
                            call=call, guards=list(self.guards), uid=self.uid())
        self.ensure().instructions.append(ins)
        if result and not re.fullmatch(r"t\d+", result):
            self.fn.locals.add(result)
        return ins

    def jump(self, label: str) -> None:
        if self.cur is not None:
            self.emit(IROpcode.JUMP, operands=[label])
            self.link(self.cur, label)
            self.cur = None

    def start(self, label: str, **meta) -> IRBlock:
        prev = self.cur
        b = self.new_block(label, **meta)
        if prev is not None:
            prev.instructions.append(IRInstruction(IROpcode.JUMP, operands=[label], lineno=self.line, uid=self.uid()))
            self.link(prev, label)
        self.cur = b
        return b

    # ── entry ───────────────────────────────────────────────────────────
    def run(self, body) -> None:
        self.cur = self.new_block("entry", kind="entry")
        for p in self.fn.params:
            self.emit(IROpcode.ASSIGN, result=p, operands=[f"param:{p}"], kind="param")
        if body is not None:
            if body.type in BLOCK_TYPES or body.type == "block":
                self.stmts(body)
            else:                      # expression body (C# =>, Rust closure-like)
                v = self.expr(body)
                self.emit(IROpcode.RETURN, operands=[v], node=body)
                self.link(self.cur, "exit")
                self.cur = None
        exit_b = IRBlock(label="exit", meta={"kind": "exit"})
        exit_b.instructions.append(IRInstruction(IROpcode.LABEL, lineno=self.fn.end_lineno, meta={"name": "exit"},
                                                 uid=self.uid()))
        self.fn.blocks.append(exit_b)
        if self.cur is not None:
            self.cur.instructions.append(IRInstruction(IROpcode.JUMP, operands=["exit"], lineno=self.fn.end_lineno,
                                                       uid=self.uid()))
            self.link(self.cur, "exit")
        for b in self.fn.blocks:                       # successors recorded before "exit" existed
            if "exit" in b.successors and b.label not in exit_b.predecessors:
                exit_b.predecessors.append(b.label)

    # ── statements ──────────────────────────────────────────────────────
    def stmts(self, node) -> None:
        for c in named(node):
            self.stmt(c)

    def stmt(self, n) -> None:
        t = n.type
        self.line = n.start_point[0] + 1
        if t in BLOCK_TYPES or t == "expression_statement" and not named(n):
            if t == "unsafe_block":
                self.emit(IROpcode.NOP, node=n, kind="unsafe_begin")
            for c in named(n):
                self.stmt(c)
            return
        if t == "expression_statement":
            for c in named(n):
                self.stmt(c) if c.type in _STMT_LIKE else self.expr(c)
            return
        if t in ("local_variable_declaration", "declaration", "local_declaration_statement", "variable_declaration",
                 "let_declaration", "field_declaration"):
            self.declaration(n)
            return
        if t in ("if_statement", "if_expression"):
            self.if_stmt(n)
            return
        if t in LOOP_TYPES:
            self.loop(n)
            return
        if t in ("return_statement", "return_expression", "yield_statement"):
            vals = named(n)
            v = self.expr(vals[0]) if vals else None
            self.emit(IROpcode.RETURN, operands=[v] if v else [], node=n)
            self.link(self.cur, "exit")
            self.cur = None
            return
        if t in ("throw_statement", "throw_expression"):
            for c in named(n):
                self.expr(c)
            self.emit(IROpcode.RETURN, operands=[], node=n, kind="raise")
            self.link(self.cur, "exit")
            self.cur = None
            return
        if t in ("break_statement", "break_expression") and self.loops:
            self.jump(self.loops[-1][1])
            return
        if t in ("continue_statement", "continue_expression") and self.loops:
            self.jump(self.loops[-1][0])
            return
        if t in ("switch_statement", "switch_expression", "match_expression"):
            self.switch(n)
            return
        if t == "try_statement" or t == "try_with_resources_statement":
            self.try_stmt(n)
            return
        if t in ("using_statement", "lock_statement", "synchronized_statement", "labeled_statement",
                 "checked_statement", "fixed_statement", "unsafe_statement"):
            for c in named(n):
                (self.stmt if c.type in BLOCK_TYPES or c.type in _STMT_LIKE else self.expr)(c)
            return
        if t in FUNCTION_TYPES.get(self.lang, set()) or t in CLASS_TYPES or t in (
                "preproc_include", "preproc_def", "using_directive", "use_declaration", "import_declaration",
                "empty_statement", "comment", "line_comment", "block_comment", "attribute_item", "goto_statement"):
            return
        self.expr(n)

    def declaration(self, n) -> None:
        tnode = fld(n, "type")
        decl_type = base_type(text(tnode, self.src)) if tnode is not None else ""
        if n.type == "local_declaration_statement":
            for c in named(n):
                if c.type == "variable_declaration":
                    self.declaration(c)
            return
        if n.type == "let_declaration":
            pat, val = fld(n, "pattern"), fld(n, "value")
            ty = fld(n, "type")
            names = [text(x, self.src) for x in _walk_names(pat)] if pat is not None else []
            v = self.expr(val) if val is not None else None
            for nm in names:
                if ty is not None:
                    self.info.var_types[nm] = base_type(text(ty, self.src))
                elif val is not None:
                    self._infer_type(nm, val)
                if v is not None:
                    self.emit(IROpcode.ASSIGN, result=nm, operands=[v], node=n, kind="decl")
            return
        for d in named(n):
            if d is tnode or d.type in ("modifiers", "attribute_list", "storage_class_specifier", "type_qualifier",
                                        "primitive_type", "type_identifier", "generic_type", "implicit_type",
                                        "predefined_type", "sized_type_specifier", "qualified_identifier",
                                        "scoped_type_identifier", "array_type", "nullable_type", "template_type"):
                continue
            if d.type == "function_declarator" and self.lang == "cpp" and decl_type:
                # "most vexing parse": T x(a, b); inside a body is an object construction, not a prototype
                inner = fld(d, "declarator")
                plist = fld(d, "parameters")
                args = []
                for p in named(plist) if plist is not None else []:
                    t_node = fld(p, "type")
                    if p.type == "parameter_declaration" and fld(p, "declarator") is None and t_node is not None:
                        args.append(text(t_node, self.src))
                if inner is not None and inner.type == "identifier":
                    nm = text(inner, self.src)
                    info = CallInfo(callee=f"new {decl_type}", raw_callee=text(tnode, self.src), args=args)
                    r = self.temp()
                    self.emit(IROpcode.CALL, result=r, operands=args, node=d, call=info, chain=f"new {decl_type}",
                              new="1")
                    self.emit(IROpcode.ASSIGN, result=nm, operands=[r], node=d, kind="decl")
                    self.info.var_types[nm] = decl_type
                continue
            name_node, val = self._declarator(d)
            if name_node is None:
                continue
            nm = text(name_node, self.src)
            if decl_type and decl_type not in ("var", "auto", "let"):
                self.info.var_types[nm] = decl_type
            if d.type in ("array_declarator",) or (d.type == "init_declarator" and
                                                    fld(d, "declarator") is not None and
                                                    fld(d, "declarator").type == "array_declarator"):
                self.info.var_types.setdefault(nm + "#array", "1")
            if val is not None and val.type in ("argument_list", "initializer_list") and decl_type and \
                    self.lang == "cpp":
                # std::ifstream in(path);  →  a constructor call
                pos, kw, nodes = self.args(val)
                info = CallInfo(callee=f"new {decl_type}", raw_callee=text(tnode, self.src), args=pos)
                for k, a in enumerate(nodes):
                    if a.type in STRING_TYPES:
                        info.const_kwargs[f"#{k}"] = string_value(a, self.src)
                r = self.temp()
                self.emit(IROpcode.CALL, result=r, operands=pos, node=d, call=info, chain=f"new {decl_type}", new="1")
                self.emit(IROpcode.ASSIGN, result=nm, operands=[r], node=d, kind="decl")
            elif val is not None:
                if not decl_type or decl_type in ("var", "auto"):
                    self._infer_type(nm, val)
                v = self.expr(val)
                self.emit(IROpcode.ASSIGN, result=nm, operands=[v], node=d, kind="decl")
            else:
                self.emit(IROpcode.ASSIGN, result=nm, operands=[], node=d, kind="decl_uninit")

    def _declarator(self, d):
        """(name node, initial value node) of one declarator."""
        if d.type in ("variable_declarator", "init_declarator"):
            name_node = fld(d, "name", "declarator")
            val = fld(d, "value")
            if val is None and d.type == "variable_declarator":
                rest = [c for c in named(d) if c is not name_node and c.type != "bracketed_argument_list"]
                val = rest[-1] if rest else None
                if name_node is None:
                    ids = [c for c in named(d) if c.type == "identifier"]
                    name_node = ids[0] if ids else None
                    rest = [c for c in named(d) if c is not name_node]
                    val = rest[-1] if rest else None
            while name_node is not None and name_node.type in ("pointer_declarator", "array_declarator",
                                                                "reference_declarator", "init_declarator"):
                name_node = fld(name_node, "declarator") or (named(name_node)[0] if named(name_node) else None)
            if val is not None and val.type == "equals_value_clause":
                val = named(val)[0] if named(val) else None
            return name_node, val
        if d.type in ("identifier", "field_identifier"):
            return d, None
        if d.type in ("pointer_declarator", "array_declarator", "reference_declarator"):
            inner = fld(d, "declarator")
            return (self._declarator(inner)[0] if inner is not None else None), None
        return None, None

    def _infer_type(self, name: str, val) -> None:
        if val.type in NEW_TYPES:
            ty = fld(val, "type", "name")
            if ty is not None:
                self.info.var_types[name] = base_type(text(ty, self.src))
        elif val.type in CALL_TYPES:
            chain = self.chain(fld(val, "function") or val)
            parts = chain.split(".")
            if len(parts) >= 2 and parts[-1] in ("new", "create", "builder", "Create", "getInstance", "newInstance"):
                self.info.var_types[name] = parts[-2]

    def if_stmt(self, n) -> None:
        k = self.count("branch")
        cond = fld(n, "condition")
        c = self.expr(cond) if cond is not None else self.const("", n)
        cond_text = re.sub(r"\s+", " ", text(cond, self.src))[:120]
        tl, fl, jl = f"branch_{k}_true", f"branch_{k}_false", f"branch_{k}_join"
        head = self.ensure()
        self.emit(IROpcode.BRANCH, operands=[c, tl, fl], node=cond or n, kind="if", src=cond_text)
        self.cur = None
        self.new_block(tl, kind="if_true")
        self.link(head, tl)
        self.cur = self.fn.get_block(tl)
        self.guards.append(f"if {cond_text}")
        cons = fld(n, "consequence")
        if cons is not None:
            self.stmt(cons)
        self.guards.pop()
        t_end = self.cur
        self.cur = None
        self.new_block(fl, kind="if_false")
        self.link(head, fl)
        self.cur = self.fn.get_block(fl)
        alt = fld(n, "alternative")
        if alt is not None:
            self.guards.append(f"not ({cond_text})")
            self.stmt(alt)
            self.guards.pop()
        f_end = self.cur
        self.cur = None
        jb = self.new_block(jl, kind="join")
        for e in (t_end, f_end):
            if e is not None:
                e.instructions.append(IRInstruction(IROpcode.JUMP, operands=[jl], lineno=self.line, uid=self.uid()))
                self.link(e, jl)
        self.cur = jb if (t_end is not None or f_end is not None) else None
        if self.cur is None:
            jb.meta["kind"] = "unreachable"

    def loop(self, n) -> None:
        k = self.count("loop")
        head, body_l, exit_l = f"loop_{k}_header", f"loop_{k}_body", f"loop_{k}_exit"
        init = fld(n, "initializer", "init")
        if init is not None:
            self.stmt(init) if init.type in _STMT_LIKE else self.expr(init)
        iterable = fld(n, "value", "right")
        it = self.expr(iterable) if iterable is not None and n.type != "for_statement" else None
        self.start(head, kind="loop_header")
        cond = fld(n, "condition")
        c = self.expr(cond) if cond is not None else self.const("", n)
        self.emit(IROpcode.BRANCH, operands=[c, body_l, exit_l], node=cond or n, kind="loop")
        hb = self.cur
        self.cur = None
        self.new_block(body_l, kind="loop_body")
        self.link(hb, body_l)
        self.cur = self.fn.get_block(body_l)
        target = fld(n, "pattern", "name", "left", "declarator")
        if it is not None and target is not None:
            for nm in _walk_names(target):
                self.emit(IROpcode.SUBSCR, result=text(nm, self.src), operands=[it], node=target, index="iter")
        self.loops.append((head, exit_l))
        body = fld(n, "body")
        if body is not None:
            self.stmt(body)
        upd = fld(n, "update")
        if upd is not None and self.cur is not None:
            self.expr(upd)
        self.loops.pop()
        if self.cur is not None:
            self.cur.instructions.append(IRInstruction(IROpcode.JUMP, operands=[head], lineno=self.line, uid=self.uid()))
            self.link(self.cur, head)
        self.cur = None
        eb = self.new_block(exit_l, kind="loop_exit")
        self.link(hb, exit_l)
        self.cur = eb

    def switch(self, n) -> None:
        k = self.count("switch")
        subj = fld(n, "condition", "value")
        s = self.expr(subj) if subj is not None else self.const("", n)
        body = fld(n, "body")
        arms = []
        if body is not None:
            for c in named(body):
                if c.type in ("switch_block_statement_group", "switch_section", "case_statement", "match_arm",
                              "switch_rule", "switch_expression_arm"):
                    arms.append(c)
        head = self.ensure()
        jl = f"switch_{k}_join"
        self.emit(IROpcode.BRANCH, operands=[s] + [f"switch_{k}_case_{i}" for i in range(len(arms))] + [jl],
                  node=n, kind="switch")
        ends = []
        self.cur = None
        for i, arm in enumerate(arms):
            lbl = f"switch_{k}_case_{i}"
            self.new_block(lbl, kind="case")
            self.link(head, lbl)
            self.cur = self.fn.get_block(lbl)
            self.loops.append((self.loops[-1][0] if self.loops else jl, jl))
            for c in named(arm):
                if c.type in ("switch_label", "case_switch_label", "default_switch_label", "match_pattern",
                              "constant_pattern", "default", "case"):
                    continue
                self.stmt(c) if c.type in BLOCK_TYPES or c.type in _STMT_LIKE else self.expr(c)
            self.loops.pop()
            ends.append(self.cur)
            self.cur = None
        jb = self.new_block(jl, kind="join")
        self.link(head, jl)
        for e in ends:
            if e is not None:
                e.instructions.append(IRInstruction(IROpcode.JUMP, operands=[jl], lineno=self.line, uid=self.uid()))
                self.link(e, jl)
        self.cur = jb

    def try_stmt(self, n) -> None:
        k = self.count("try")
        head = self.ensure()
        res = fld(n, "resources")
        if res is not None:
            for c in named(res):
                self.declaration(c) if c.type in ("resource",) else self.expr(c)
        body = fld(n, "body")
        bl, jl = f"try_{k}_body", f"try_{k}_join"
        self.emit(IROpcode.JUMP, operands=[bl], node=n, kind="try")
        self.cur = None
        self.new_block(bl, kind="try_body")
        self.link(head, bl)
        self.cur = self.fn.get_block(bl)
        if body is not None:
            self.stmt(body)
        ends = [self.cur]
        catches = [c for c in named(n) if c.type == "catch_clause"]
        for i, c in enumerate(catches):
            lbl = f"try_{k}_catch_{i}"
            self.cur = None
            self.new_block(lbl, kind="except")
            self.link(head, lbl)
            self.link(self.fn.get_block(bl), lbl)
            self.cur = self.fn.get_block(lbl)
            cb = fld(c, "body") or (named(c)[-1] if named(c) else None)
            if cb is not None:
                self.stmt(cb)
            ends.append(self.cur)
        self.cur = None
        jb = self.new_block(jl, kind="join")
        for e in ends:
            if e is not None:
                e.instructions.append(IRInstruction(IROpcode.JUMP, operands=[jl], lineno=self.line, uid=self.uid()))
                self.link(e, jl)
        self.cur = jb
        fin = next((c for c in named(n) if c.type == "finally_clause"), None)
        if fin is not None:
            self.stmt(fin)

    # ── expressions ─────────────────────────────────────────────────────
    def const(self, value: str, node, kind: str = "const") -> str:
        t = self.temp()
        self.emit(IROpcode.ASSIGN, result=t, operands=[], node=node, kind=kind, const=value)
        return t

    def chain(self, node) -> str:
        """Dotted name of a callee / attribute expression with call arguments dropped."""
        if node is None:
            return ""
        t = node.type
        if t in NAME_TYPES or t in ("primitive_type", "predefined_type", "generic_name"):
            return text(node, self.src).split("<")[0]
        if t in ("field_access", "member_access_expression", "field_expression"):
            obj = fld(node, "object", "expression", "argument", "value")
            nm = fld(node, "field", "name")
            return f"{self.chain(obj)}.{text(nm, self.src).split('<')[0]}"
        if t in ("scoped_identifier", "qualified_identifier", "scoped_type_identifier"):
            return text(node, self.src).replace("::", ".").split("<")[0].replace("..", ".")
        if t == "method_invocation":
            obj, nm = fld(node, "object"), fld(node, "name")
            return f"{self.chain(obj)}.{text(nm, self.src)}" if obj is not None else text(nm, self.src)
        if t in ("call_expression", "invocation_expression"):
            return self.chain(fld(node, "function"))
        if t in NEW_TYPES:
            return "new " + base_type(text(fld(node, "type", "name"), self.src))
        if t in ("generic_function", "template_function"):
            return self.chain(fld(node, "function", "name"))
        if t in ("parenthesized_expression", "reference_expression", "try_expression", "await_expression"):
            inner = named(node)
            return self.chain(inner[-1]) if inner else "?"
        return "?"

    def expr(self, n) -> str:
        if n is None:
            return self.const("", None)
        t = n.type
        if t in STRING_TYPES:
            return self.const(string_value(n, self.src), n, kind="string")
        if t in LITERAL_TYPES:
            return self.const(text(n, self.src), n)
        if t in NAME_TYPES:
            name = text(n, self.src)
            if self.lang == "rust" and name == "self":
                return "self"
            return name
        if t in ("parenthesized_expression", "argument", "expression_statement", "await_expression",
                 "try_expression", "checked_expression", "parenthesized_declarator", "condition_clause",
                 "equals_value_clause", "arrow_expression_clause", "non_null_assertion_expression",
                 "postfix_unary_expression") and named(n):
            inner = [c for c in named(n) if c.type not in ("name_colon", "refkind")]
            return self.expr(inner[-1]) if inner else self.const("", n)
        if t in CALL_TYPES:
            return self.call(n)
        if t == "macro_invocation":
            return self.macro(n)
        if t in NEW_TYPES:
            return self.new_obj(n)
        if t in ("assignment_expression", "compound_assignment_expr", "augmented_assignment_expression",
                 "assignment"):
            return self.assign(n)
        if t in ("binary_expression",):
            left, right = fld(n, "left"), fld(n, "right")
            op_node = fld(n, "operator")
            op = text(op_node, self.src) if op_node is not None else (
                text(n.children[1], self.src) if len(n.children) > 2 else "")
            if op == ">>" and left is not None and re.search(r"(^|::|\.)cin$|(^|::)wcin$|stringstream|ifstream|>>",
                                                              text(left, self.src)) and right is not None \
                    and right.type in NAME_TYPES:
                # std::cin >> x  (x receives input; the stream expression may itself be a chain of >>)
                self.expr(left)
                info = CallInfo(callee="std.cin>>", raw_callee="std::cin >>", args=[])
                r = self.temp()
                self.emit(IROpcode.CALL, result=r, operands=[], node=n, call=info, chain="std.cin>>")
                self.emit(IROpcode.ASSIGN, result=text(right, self.src), operands=[r], node=n, kind="decl")
                return r
            a, b = self.expr(left), self.expr(right)
            r = self.temp()
            if op in COMPARE_OPS:
                self.emit(IROpcode.BINOP, result=r, operands=[a, b], node=n, operator=op, kind="compare",
                          taint_ops="0")
            else:
                self.emit(IROpcode.BINOP, result=r, operands=[a, b], node=n, operator=op)
                if op == "<<" and left is not None and left.type in NAME_TYPES:     # C++ stream insertion
                    self.emit(IROpcode.ASSIGN, result=text(left, self.src), operands=[r], node=n, kind="stream")
            return r
        if t in ("unary_expression", "prefix_unary_expression", "pointer_expression", "reference_expression",
                 "update_expression", "prefix_expression", "postfix_expression", "dereference_expression"):
            inner = fld(n, "argument", "operand", "value") or (named(n)[-1] if named(n) else None)
            op = text(n.children[0], self.src) if n.children else ""
            if op in ("&", "&mut", "ref", "out") and inner is not None and inner.type in NAME_TYPES:
                return text(inner, self.src)          # address-of keeps the variable's identity
            if t == "reference_expression" and inner is not None and inner.type in NAME_TYPES:
                return text(inner, self.src)
            v = self.expr(inner)
            r = self.temp()
            meta = {"operator": op}
            if op == "!":
                meta["taint_ops"] = "0"
            if op == "*" or t in ("pointer_expression",) and op == "*":
                meta["deref"] = "1"
            self.emit(IROpcode.UNOP, result=r, operands=[v], node=n, **meta)
            return r
        if t in FIELD_TYPES and t not in ("scoped_identifier", "qualified_identifier"):
            obj = fld(n, "object", "expression", "argument", "value")
            nm = fld(n, "field", "name")
            if obj is None:
                kids = named(n)
                obj = kids[0] if kids else None
            b = self.expr(obj)
            r = self.temp()
            self.emit(IROpcode.ATTR, result=r, operands=[b], node=n, attr=text(nm, self.src), chain=self.chain(n),
                      base_name=text(obj, self.src) if obj is not None and obj.type in NAME_TYPES else "")
            return r
        if t in ("scoped_identifier", "qualified_identifier"):
            r = self.temp()
            self.emit(IROpcode.ATTR, result=r, operands=[], node=n, chain=self.chain(n), attr=self.chain(n).split(".")[-1])
            return r
        if t in INDEX_TYPES:
            kids = named(n)
            base = fld(n, "array", "expression", "argument") or (kids[0] if kids else None)
            idx = fld(n, "index", "subscript", "indices") or (kids[1] if len(kids) > 1 else None)
            if idx is not None and idx.type in ("subscript_argument_list", "bracketed_argument_list") and named(idx):
                idx = named(idx)[0]
                if idx.type == "argument" and named(idx):
                    idx = named(idx)[-1]
            b = self.expr(base)
            i = self.expr(idx) if idx is not None else self.const("", n)
            r = self.temp()
            self.emit(IROpcode.SUBSCR, result=r, operands=[b, i], node=n,
                      base_name=text(base, self.src) if base is not None and base.type in NAME_TYPES else "",
                      chain=self.chain(base) if base is not None else "")
            return r
        if t in ("cast_expression", "type_cast_expression", "as_expression"):
            v = self.expr(fld(n, "value") or (named(n)[-1] if named(n) else None) if t != "as_expression"
                          else named(n)[0])
            r = self.temp()
            ty = fld(n, "type")
            self.emit(IROpcode.UNOP, result=r, operands=[v], node=n, operator="cast",
                      cast_to=base_type(text(ty, self.src)) if ty is not None else "")
            return r
        if t in ("ternary_expression", "conditional_expression"):
            c = self.expr(fld(n, "condition"))
            a = self.expr(fld(n, "consequence"))
            b = self.expr(fld(n, "alternative"))
            r = self.temp()
            self.emit(IROpcode.BUILD, result=r, operands=[a, b, c], node=n, kind="ifexp", taint_ops="2")
            return r
        if t in ("interpolated_string_expression", "template_string", "format_string"):
            parts = []
            for c in named(n):
                if c.type == "interpolation":
                    inner = [x for x in named(c) if x.type not in ("interpolation_brace", "interpolation_format_clause",
                                                                    "interpolation_alignment_clause")]
                    parts.extend(self.expr(x) for x in inner[:1])
                elif c.type in ("string_content", "string_literal_content", "string_fragment"):
                    parts.append(self.const(text(c, self.src), c, kind="string"))
            r = self.temp()
            self.emit(IROpcode.BUILD, result=r, operands=parts, node=n, kind="fstring")
            return r
        if t in LAMBDA_TYPES:
            body = fld(n, "body")
            if body is not None:
                saved = self.cur
                if body.type in BLOCK_TYPES:
                    self.stmt(body)
                else:
                    self.expr(body)
                if self.cur is None:
                    self.cur = saved
            r = self.temp()
            self.emit(IROpcode.BUILD, result=r, operands=[], node=n, kind="lambda")
            return r
        if t in ("if_expression",):
            self.if_stmt(n)
            return self.const("", n)
        if t in ("match_expression", "switch_expression"):
            self.switch(n)
            return self.const("", n)
        if t in ("block", "unsafe_block") or t in LOOP_TYPES:
            self.stmt(n)
            return self.const("", n)
        if t in ("sizeof_expression", "alignof_expression", "typeof_expression", "nameof_expression",
                 "default_expression", "instanceof_expression", "is_expression", "is_pattern_expression"):
            for c in named(n):
                if c.type not in ("type_identifier", "primitive_type", "predefined_type"):
                    self.expr(c)
            return self.const(text(n, self.src), n, kind="sizeof")
        if t in ("delete_expression",):
            kids = named(n)
            v = self.expr(kids[-1]) if kids else self.const("", n)
            info = CallInfo(callee="delete[]" if "[" in text(n, self.src).split(kids[-1].type)[0] else "delete",
                            raw_callee="delete", args=[v])
            r = self.temp()
            self.emit(IROpcode.CALL, result=r, operands=[v], node=n, call=info, chain=info.callee)
            return r
        # conservative default: lower children, combine
        kids = named(n)
        if not kids:
            return self.const(text(n, self.src), n)
        if t not in _QUIET:
            tag = f"{t} (lowered conservatively)"
            if tag not in self.fn.unsupported:
                self.fn.unsupported.append(tag)
        ops = [self.expr(c) for c in kids]
        r = self.temp()
        self.emit(IROpcode.BUILD, result=r, operands=ops, node=n, kind=t)
        return r

    def args(self, arglist) -> Tuple[List[str], Dict[str, str], List]:
        """Positional operands, named operands and the argument nodes of an argument list."""
        pos, kw, nodes = [], {}, []
        if arglist is None:
            return pos, kw, nodes
        for a in named(arglist):
            if a.type in ("comment", "line_comment", "block_comment"):
                continue
            if a.type == "argument":
                nc = next((c for c in named(a) if c.type == "name_colon"), None)
                inner = [c for c in named(a) if c.type not in ("name_colon", "refkind")]
                v = self.expr(inner[-1]) if inner else self.const("", a)
                if nc is not None:
                    kw[text(nc, self.src).rstrip(":").strip()] = v
                else:
                    pos.append(v)
                    nodes.append(inner[-1] if inner else a)
            else:
                pos.append(self.expr(a))
                nodes.append(a)
        return pos, kw, nodes

    def call(self, n) -> str:
        if n.type == "method_invocation":
            obj, name_node = fld(n, "object"), fld(n, "name")
            arglist = fld(n, "arguments")
            method = text(name_node, self.src)
            recv_node = obj
        else:
            fn = fld(n, "function")
            arglist = fld(n, "arguments")
            recv_node, method = None, None
            if fn is not None and fn.type in ("field_expression", "member_access_expression", "field_access"):
                recv_node = fld(fn, "object", "expression", "argument", "value")
                method = text(fld(fn, "field", "name"), self.src).split("<")[0]
            elif fn is not None and fn.type in ("generic_function", "template_function"):
                inner = fld(fn, "function", "name")
                if inner is not None and inner.type in ("field_expression", "member_access_expression"):
                    recv_node = fld(inner, "argument", "value", "expression")
                    method = text(fld(inner, "field", "name"), self.src)
        recv = self.expr(recv_node) if recv_node is not None else None
        pos, kw, nodes = self.args(arglist)
        chain = self.chain(n)
        rtype = ""
        if recv_node is not None and recv_node.type in NAME_TYPES:
            nm = text(recv_node, self.src)
            rtype = self.info.var_types.get(nm) or self.info.param_types.get(nm, "")
        elif recv_node is not None and recv_node.type in NEW_TYPES:
            rtype = base_type(text(fld(recv_node, "type", "name"), self.src))
        callee = f"{rtype}.{method}" if rtype and method else chain
        info = CallInfo(callee=callee, raw_callee=text(fld(n, "function") or n, self.src)[:120],
                        method=method, receiver=recv, args=pos, keywords=kw)
        for k, a in enumerate(nodes):
            if a.type in STRING_TYPES:
                info.const_kwargs[f"#{k}"] = string_value(a, self.src)
            elif a.type in LITERAL_TYPES:
                info.const_kwargs[f"#{k}"] = text(a, self.src)
        r = self.temp()
        ins = self.emit(IROpcode.CALL, result=r, operands=([recv] if recv else []) + pos, node=n, call=info,
                        chain=chain, rtype=rtype,
                        receiver_name=text(recv_node, self.src) if recv_node is not None and recv_node.type in NAME_TYPES else "")
        if method and recv_node is not None:
            # a chained call is reported on the line of its method name, not the start of the chain
            name_line = self._method_line(n, method)
            if name_line:
                ins.lineno = name_line
        return r

    def _method_line(self, n, method: str) -> int:
        fn = fld(n, "function", "name")
        if fn is not None and fn.type in ("field_expression", "member_access_expression"):
            nm = fld(fn, "field", "name")
            return nm.start_point[0] + 1 if nm is not None else 0
        if n.type == "method_invocation":
            nm = fld(n, "name")
            return nm.start_point[0] + 1 if nm is not None else 0
        return 0

    def macro(self, n) -> str:
        name = text(fld(n, "macro") or named(n)[0], self.src).replace("::", ".")
        tree = next((c for c in named(n) if c.type == "token_tree"), None)
        ops = []
        consts = {}
        parsed = self._macro_args(tree) if tree is not None and self.lang == "rust" else None
        if parsed is not None:
            ops, consts = parsed
            tree = None
        if tree is not None:
            for i, c in enumerate(named(tree)):
                if c.type in STRING_TYPES:
                    consts[f"#{len(ops)}"] = string_value(c, self.src)
                    ops.append(self.const(string_value(c, self.src), c, kind="string"))
                elif c.type in NAME_TYPES:
                    ops.append(text(c, self.src))
                elif c.type not in ("token_tree",):
                    ops.append(self.expr(c))
                else:
                    ops.extend(text(x, self.src) for x in _walk_names(c))
        info = CallInfo(callee=name + "!", raw_callee=name + "!", args=ops, const_kwargs=consts)
        r = self.temp()
        self.emit(IROpcode.CALL, result=r, operands=ops, node=n, call=info, chain=name + "!", macro="1")
        return r

    def _macro_args(self, tree):
        """Parse a macro's token tree as call arguments and lower them as real expressions."""
        inner = text(tree, self.src)
        if not (inner.startswith("(") or inner.startswith("[")):
            return None
        row = tree.start_point[0]
        sub = ("\n" * row) + "fn __m(){__f(" + inner[1:-1] + ");}"
        subtree = parser_for("rust").parse(sub.encode("utf-8"))
        if subtree.root_node.has_error:
            return None
        call = next((x for x in _iter(subtree.root_node) if x.type == "call_expression"
                     and text(fld(x, "function"), sub.encode("utf-8")) == "__f"), None)
        if call is None:
            return None
        saved = self.src
        self.src = sub.encode("utf-8")
        try:
            ops, consts = [], {}
            for k, a in enumerate(named(fld(call, "arguments"))):
                if a.type in STRING_TYPES:
                    consts[f"#{k}"] = string_value(a, self.src)
                ops.append(self.expr(a))
            return ops, consts
        finally:
            self.src = saved

    def new_obj(self, n) -> str:
        ty = fld(n, "type", "name")
        tname = base_type(text(ty, self.src)) if ty is not None else "?"
        pos, kw, nodes = self.args(fld(n, "arguments"))
        init = fld(n, "initializer", "body")
        if init is not None:
            for a in named(init):
                if a.type in ("assignment_expression", "field_initializer", "shorthand_field_initializer"):
                    left = fld(a, "left", "field", "name") or (named(a)[0] if named(a) else None)
                    right = fld(a, "right", "value") or (named(a)[-1] if named(a) else None)
                    if left is not None:
                        kw[text(left, self.src)] = self.expr(right) if right is not None and right is not left \
                            else text(left, self.src)
                else:
                    pos.append(self.expr(a))
        info = CallInfo(callee=f"new {tname}", raw_callee=f"new {tname}", args=pos, keywords=kw)
        for k, a in enumerate(nodes):
            if a.type in STRING_TYPES:
                info.const_kwargs[f"#{k}"] = string_value(a, self.src)
            elif a.type in LITERAL_TYPES:
                info.const_kwargs[f"#{k}"] = text(a, self.src)
        for kname, v in list(kw.items()):
            info.const_kwargs.setdefault(kname, "")
        r = self.temp()
        self.emit(IROpcode.CALL, result=r, operands=pos + list(kw.values()), node=n, call=info,
                  chain=f"new {tname}", new="1")
        return r

    def assign(self, n) -> str:
        left, right = fld(n, "left"), fld(n, "right")
        if left is None or right is None:
            kids = named(n)
            left, right = (kids[0], kids[-1]) if len(kids) >= 2 else (None, kids[0] if kids else None)
        op_node = fld(n, "operator")
        op = text(op_node, self.src) if op_node is not None else ""
        if not op:
            between = text(n, self.src)[len(text(left, self.src)):].lstrip()
            op = between[:3].split(" ")[0] if left is not None else "="
        v = self.expr(right)
        if left is None:
            return v
        compound = n.type in ("compound_assignment_expr", "augmented_assignment_expression") or (
            op.endswith("=") and op not in ("=", "==", "!=", "<=", ">="))
        if left.type in NAME_TYPES:
            name = text(left, self.src)
            if compound:
                r = self.temp()
                self.emit(IROpcode.BINOP, result=r, operands=[name, v], node=n, operator=op.rstrip("="))
                v = r
            self.emit(IROpcode.ASSIGN, result=name, operands=[v], node=n)
            return name
        # store into a field / element / dereferenced pointer: the object becomes tainted
        root = left
        while root is not None and root.type not in NAME_TYPES and named(root):
            root = fld(root, "object", "expression", "argument", "array", "value") or named(root)[0]
        base = text(root, self.src) if root is not None and root.type in NAME_TYPES else ""
        kind = "attr" if left.type in FIELD_TYPES else "subscr" if left.type in INDEX_TYPES else "deref"
        idx = None
        if left.type in INDEX_TYPES:
            kids = named(left)
            idx_node = fld(left, "index", "subscript", "indices") or (kids[1] if len(kids) > 1 else None)
            idx = self.expr(idx_node) if idx_node is not None else None
        b = self.expr(left) if kind == "deref" else (base or self.expr(left))
        ops = [v, b] + ([idx] if idx else [])
        self.emit(IROpcode.STORE, operands=ops, node=n, kind=kind, base_name=base,
                  attr=text(fld(left, "field", "name"), self.src) if left.type in FIELD_TYPES else "",
                  target=text(left, self.src)[:80])
        return v


_STMT_LIKE = {"if_statement", "if_expression", "return_statement", "return_expression", "block", "compound_statement",
              "local_variable_declaration", "declaration", "local_declaration_statement", "let_declaration",
              "unsafe_block", "throw_statement", "try_statement", "switch_statement", "match_expression",
              "expression_statement", "break_statement", "continue_statement", "break_expression",
              "continue_expression", "yield_statement"} | LOOP_TYPES
_QUIET = {"argument_list", "arguments", "array_initializer", "initializer_list", "array_expression",
          "tuple_expression", "array_creation_expression", "implicit_array_creation_expression",
          "initializer_expression", "collection_expression", "token_tree", "range_expression", "string_interpolation",
          "compound_literal_expression", "array_creation", "comma_expression", "list_expression",
          "anonymous_object_creation_expression", "tuple", "char_literal", "element_binding_expression",
          "with_expression", "lambda_parameters", "method_reference", "class_literal", "type_arguments",
          "field_initializer_list", "base_field_initializer", "struct_expression", "generic_function",
          "template_function", "array_type", "type_identifier", "primitive_type", "predefined_type",
          "escape_sequence", "string_content", "string_fragment", "interpolated_verbatim_string_expression",
          "local_function_statement", "declaration_expression", "ref_expression", "throw_expression",
          "range_pattern", "tuple_pattern", "unit_expression", "label", "lifetime", "generic_type",
          "scoped_type_identifier", "qualified_name", "member_access_expression", "parenthesized_expression",
          "type_descriptor", "struct_specifier", "subscript_argument_list", "bracketed_argument_list"}


def _walk_names(node) -> List:
    out = []
    if node is None:
        return out
    stack = [node]
    while stack:
        n = stack.pop()
        if n.type in ("identifier", "shorthand_field_identifier"):
            out.append(n)
            continue
        if n.type in ("type_identifier", "primitive_type", "string_literal"):
            continue
        stack.extend(reversed(named(n)))
    return out


# ---------------------------------------------------------------------------
# Module: find functions, read signatures, lower bodies
# ---------------------------------------------------------------------------

def _func_name_params(lang: str, node, src: bytes) -> Tuple[str, List[Tuple[str, str, str]], object]:
    """(name, [(param, type, declaration text)], body node) of a function node."""
    params: List[Tuple[str, str, str]] = []
    if lang in ("c", "cpp"):
        decl = fld(node, "declarator")
        while decl is not None and decl.type != "function_declarator":
            decl = fld(decl, "declarator") or (named(decl)[0] if named(decl) else None)
        name = text(fld(decl, "declarator"), src) if decl is not None else "?"
        plist = fld(decl, "parameters") if decl is not None else None
        for p in named(plist) if plist is not None else []:
            if p.type not in ("parameter_declaration", "optional_parameter_declaration"):
                continue
            ty = text(fld(p, "type"), src)
            d = fld(p, "declarator")
            stars = ""
            while d is not None and d.type in ("pointer_declarator", "array_declarator", "reference_declarator",
                                               "abstract_pointer_declarator"):
                stars += "*" if d.type != "reference_declarator" else "&"
                d = fld(d, "declarator") or (named(d)[0] if named(d) else None)
            if d is not None and d.type == "identifier":
                params.append((text(d, src), ty + stars, text(p, src)))
        return name.split("::")[-1], params, fld(node, "body")
    name_node = fld(node, "name")
    name = text(name_node, src) if name_node is not None else "?"
    plist = fld(node, "parameters")
    for p in named(plist) if plist is not None else []:
        if p.type in ("formal_parameter", "parameter", "spread_parameter", "receiver_parameter"):
            pn = fld(p, "name", "pattern")
            ty = fld(p, "type")
            if pn is None:
                ids = [c for c in named(p) if c.type in ("identifier",)]
                pn = ids[-1] if ids else None
            if pn is not None:
                for nm in _walk_names(pn) or [pn]:
                    params.append((text(nm, src), text(ty, src) if ty is not None else "", text(p, src)))
        elif p.type == "self_parameter":
            params.append(("self", "Self", "self"))
    body = fld(node, "body")
    return name, params, body


def _annotations(node, src: bytes) -> Tuple[List[str], str]:
    """Annotations / attributes / Rust #[...] attributes and modifiers of a declaration."""
    ann, mods = [], ""
    for c in node.children:
        if c.type in ("modifiers",):
            mods = text(c, src)
            ann += [text(x, src) for x in named(c) if x.type in ("annotation", "marker_annotation")]
        elif c.type in ("attribute_list",):
            ann.append(text(c, src))
        elif c.type in ("modifier", "visibility_modifier"):
            mods += " " + text(c, src)
    prev = node.prev_named_sibling
    while prev is not None and prev.type in ("attribute_item", "attribute_list"):
        ann.append(text(prev, src))
        prev = prev.prev_named_sibling
    return ann, mods.strip()


def lower_source(source: str, lang: str, filepath: str = "") -> LoweredModule:
    src = source.encode("utf-8")
    tree = parser_for(lang).parse(src)
    root = tree.root_node
    err = None
    if root.has_error:
        bad = next((n for n in _iter(root) if n.type == "ERROR" or n.is_missing), None)
        err = (f"syntax error near line {bad.start_point[0] + 1}" if bad is not None else "syntax error")
    module = IRModule(source_file=filepath)
    functions: Dict[str, FunctionInfo] = {}
    seen: Dict[str, int] = {}

    def visit(node, cls: Optional[str], cls_ann: List[str]):
        for c in named(node):
            t = c.type
            if t in FUNCTION_TYPES[lang]:
                name, params, body = _func_name_params(lang, c, src)
                qual = f"{cls}.{name}" if cls else name
                if qual in seen:
                    seen[qual] += 1
                    qual = f"{qual}#{seen[qual]}"
                else:
                    seen[qual] = 1
                fn = IRFunction(name=name, params=[p for p, _, _ in params], is_method=cls is not None,
                                source_lineno=c.start_point[0] + 1, end_lineno=c.end_point[0] + 1,
                                qualname=qual, class_name=cls, source_file=filepath)
                ann, mods = _annotations(c, src)
                info = FunctionInfo(fn=fn, node=c, param_types={p: base_type(ty) for p, ty, _ in params},
                                    annotations=ann, modifiers=mods, class_annotations=cls_ann)
                info.param_types.update({p + "#raw": ty for p, ty, _ in params})
                info.param_types.update({p + "#decl": decl for p, _, decl in params})
                fn.decorators = ann
                nn = fld(c, "name", "declarator")
                info.name_line = (nn.start_point[0] + 1) if nn is not None else fn.source_lineno
                _FnLowerer(lang, src, info).run(body)
                module.functions.append(fn)
                functions[qual] = info
                if body is not None:          # nested local functions (C#) / closures declared as items
                    visit(body, cls, cls_ann)
            elif t in CLASS_TYPES:
                nm = fld(c, "name", "type")
                cname = base_type(text(nm, src)) if nm is not None else (cls or "?")
                ann, _ = _annotations(c, src)
                module.classes.append(cname)
                visit(fld(c, "body") or c, cname, ann)
            elif t in ("namespace_declaration", "namespace_definition", "file_scoped_namespace_declaration",
                       "declaration_list", "mod_item", "program", "translation_unit", "compilation_unit",
                       "source_file", "linkage_specification", "template_declaration", "class_body",
                       "interface_body", "enum_body", "field_declaration_list", "preproc_ifdef", "preproc_if",
                       "preproc_else", "access_specifier"):
                visit(fld(c, "body") or c, cls, cls_ann)
    visit(root, None, [])
    return LoweredModule(lang, source, module, functions, tree, err)


def _iter(node):
    stack = [node]
    while stack:
        n = stack.pop()
        yield n
        stack.extend(n.children)
