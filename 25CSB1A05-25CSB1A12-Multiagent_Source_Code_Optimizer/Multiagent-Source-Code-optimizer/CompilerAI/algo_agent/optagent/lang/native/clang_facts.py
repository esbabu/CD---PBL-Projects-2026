"""C11 and C++17 static fact extraction via clang AST JSON with tree-sitter fallback."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from ...schemas import (
    Effect,
    EffectKind,
    FunctionFacts,
    ModuleFacts,
    ParamInfo,
    Pattern,
)
from ..treesitter.parse import find_functions, node_text, parse_source, walk


def _extract_clang_ast_json(source: str, language: str, flags: list[str] | None = None) -> dict[str, Any] | None:
    """Invoke `clang -Xclang -ast-dump=json -fsyntax-only` when clang is available."""
    compiler = "clang++" if language == "cpp" else "clang"
    if not shutil.which(compiler):
        return None
    suffix = ".cpp" if language == "cpp" else ".c"
    std_flag = "-std=c++17" if language == "cpp" else "-std=c11"
    with tempfile.NamedTemporaryFile("w", suffix=suffix, delete=False, encoding="utf-8") as tf:
        tf.write(source)
        tmp_path = tf.name
    try:
        cmd = [compiler, std_flag, "-Xclang", "-ast-dump=json", "-fsyntax-only"] + (flags or []) + [tmp_path]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if proc.returncode == 0 and proc.stdout.strip().startswith("{"):
            return json.loads(proc.stdout)
    except Exception:
        return None
    finally:
        Path(tmp_path).unlink(missing_ok=True)
    return None


def _split_c_params(param_list_text: str) -> list[ParamInfo]:
    """Parse C/C++ parameter list text `(const int* nums, int n, int target, int* out)`."""
    inner = param_list_text.strip()
    if inner.startswith("(") and inner.endswith(")"):
        inner = inner[1:-1].strip()
    if not inner or inner == "void":
        return []

    # Split on top-level commas (respecting template angle brackets `<>`)
    parts, cur, depth = [], [], 0
    for ch in inner:
        if ch in "<([":
            depth += 1
        elif ch in ">)]":
            depth = max(0, depth - 1)
        if ch == "," and depth == 0:
            parts.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    if cur:
        parts.append("".join(cur).strip())

    params: list[ParamInfo] = []
    for idx, raw in enumerate(parts):
        if not raw or raw == "...":
            continue
        default = None
        if "=" in raw:
            raw, default = raw.split("=", 1)
            raw, default = raw.strip(), default.strip()
        # Handle array suffix e.g. `int arr[]` or `int arr[10]`
        m_arr = re.match(r"^(.+?)\b([A-Za-z_]\w*)\s*(\[\s*\d*\s*\])$", raw)
        if m_arr:
            ptype = (m_arr.group(1).strip() + m_arr.group(3)).strip()
            pname = m_arr.group(2)
            params.append(ParamInfo(name=pname, annotation=ptype, default=default))
            continue
        # Standard `type [*|&] name`
        m = re.match(r"^(.+?)([*&]*)\s*([A-Za-z_]\w*)$", raw)
        if m:
            ptype = (m.group(1).strip() + (" " + m.group(2) if m.group(2) else "")).strip()
            ptype = re.sub(r"\s+([*&]+)", r"\1", ptype)
            pname = m.group(3)
            params.append(ParamInfo(name=pname, annotation=ptype, default=default))
        else:
            params.append(ParamInfo(name=f"arg{idx}", annotation=raw, default=default))
    return params


def _extract_return_type(fn_node, decl_node, src_bytes: bytes) -> str:
    """Extract the return type text preceding the function declarator."""
    parts = []
    for ch in fn_node.children:
        if ch == decl_node or ch.type == "compound_statement":
            break
        txt = node_text(ch, src_bytes).strip()
        if txt in ("static", "inline", "extern", "virtual", "constexpr"):
            continue
        if txt:
            parts.append(txt)
    # Handle pointer/reference return types attached to declarator (`int* foo(...)`)
    d = decl_node
    while d is not None and d.type in ("pointer_declarator", "reference_declarator"):
        if d.type == "pointer_declarator":
            parts.append("*")
        elif d.type == "reference_declarator":
            parts.append("&")
        d = d.child_by_field_name("declarator")
    res = " ".join(parts).strip()
    res = re.sub(r"\s+([*&])", r"\1", res)
    return res or "int"


def analyze_native_source(source: str, language: str, hints: dict[str, Any] | None = None) -> ModuleFacts:
    """Analyze C11 or C++17 source into ModuleFacts (clang AST JSON if available + tree-sitter)."""
    hints = hints or {}
    lang_key = "cpp" if language in ("cpp", "c++", "cxx") else "c"
    tree, src_bytes = parse_source(source, lang_key)
    if tree.root_node.has_error:
        raise SyntaxError(f"{lang_key.upper()} source contains syntax errors")

    # Optional clang AST metadata enrichment (no-op if clang not installed)
    clang_ast = _extract_clang_ast_json(source, lang_key)

    spans = find_functions(tree, src_bytes, lang_key)
    functions: dict[str, FunctionFacts] = {}
    imports: dict[str, str] = {}
    module_vars: list[str] = []
    mutable_vars: list[str] = []

    for ch in tree.root_node.children:
        if ch.type == "preproc_include":
            txt = node_text(ch, src_bytes)
            m = re.search(r'[<"]([^>"]+)[>"]', txt)
            if m:
                imports[m.group(1)] = m.group(1)
        elif ch.type == "declaration":
            txt = node_text(ch, src_bytes)
            if "(" not in txt:  # file-scope variable, not forward prototype
                m = re.search(r"\b([A-Za-z_]\w*)\s*(?:=|;|\[)", txt)
                if m:
                    vname = m.group(1)
                    module_vars.append(vname)
                    if not txt.lstrip().startswith("const "):
                        mutable_vars.append(vname)

    for fn_name, span in spans.items():
        node = span.node
        decl = node.child_by_field_name("declarator")
        ret_type = _extract_return_type(node, decl, src_bytes) if decl is not None else "int"

        # Find parameter_list inside declarator
        param_list_text = "()"
        if decl is not None:
            for sub in walk(decl):
                if sub.type == "parameter_list":
                    param_list_text = node_text(sub, src_bytes)
                    break
        params = _split_c_params(param_list_text)
        param_names = {p.name for p in params}

        # Check template wrapper
        template_params: list[str] = []
        if node.parent is not None and node.parent.type == "template_declaration":
            tp = node.parent.child_by_field_name("parameters")
            if tp is not None:
                template_params = re.findall(r"(?:typename|class)\s+([A-Za-z_]\w*)", node_text(tp, src_bytes))

        mutated: set[str] = set()
        effects: list[Effect] = []
        raises: set[str] = set()
        implicit_raises: set[str] = set()
        sort_uses: list[Pattern] = []
        cost_patterns: list[Pattern] = []
        callees: set[str] = set()
        float_reasons: list[str] = []
        is_recursive = False
        branching_self = 0
        loop_count = 0
        max_loop_depth = 0
        uses_threads = False
        uses_malloc = False

        # Non-const pointer/reference parameters may be mutated
        for p in params:
            ann = (p.annotation or "").strip()
            if ("*" in ann or ("&" in ann and not ann.endswith("&&"))) and not ann.startswith("const "):
                if not ann.startswith("const"):
                    mutated.add(p.name)
            if any(ft in ann for ft in ("float", "double")):
                if "float_param" not in float_reasons:
                    float_reasons.append("float_param")
        if any(ft in ret_type for ft in ("float", "double")):
            if "float_return" not in float_reasons:
                float_reasons.append("float_return")

        body = span.body_node or node

        def _visit(n, depth: int):
            nonlocal loop_count, max_loop_depth, is_recursive, branching_self, uses_threads, uses_malloc
            ntype = n.type
            line = n.start_point[0] + 1
            in_loop = depth > 0
            new_depth = depth

            if ntype in ("for_statement", "for_range_loop", "while_statement", "do_statement"):
                loop_count += 1
                new_depth = depth + 1
                if new_depth > max_loop_depth:
                    max_loop_depth = new_depth
                if new_depth >= 2:
                    cost_patterns.append(Pattern(
                        kind="nested_loop", line=line, in_loop=True,
                        detail=f"loop header at depth {new_depth}",
                    ))
                # Check strlen/strcmp in loop condition
                cond = n.child_by_field_name("condition")
                if cond is not None:
                    ct = node_text(cond, src_bytes)
                    if "strlen(" in ct:
                        cost_patterns.append(Pattern(
                            kind="strlen_in_loop", line=line, in_loop=True,
                            detail="strlen() called in loop condition (O(n^2))",
                        ))

            elif ntype == "throw_statement":
                txt = node_text(n, src_bytes)
                m = re.search(r"throw\s+([A-Za-z_][\w:]*)", txt)
                raises.add(m.group(1) if m else "std::exception")

            elif ntype == "assignment_expression":
                left = n.child_by_field_name("left")
                if left is not None:
                    lt = node_text(left, src_bytes)
                    for pn in param_names:
                        if lt.startswith(f"{pn}[") or lt == f"*{pn}":
                            mutated.add(pn)
                            effects.append(Effect(kind=EffectKind.ARG_MUTATION, line=line, detail=f"{lt} = ..."))

            elif ntype == "call_expression":
                fn_node = n.child_by_field_name("function")
                if fn_node is not None:
                    ft = node_text(fn_node, src_bytes)
                    callees.add(ft)
                    if ft == fn_name:
                        is_recursive = True
                        branching_self += 1
                    if ft in ("printf", "puts", "putchar", "fprintf"):
                        effects.append(Effect(kind=EffectKind.PRINT, line=line, detail=ft))
                    if ft in ("rand", "random"):
                        effects.append(Effect(kind=EffectKind.RANDOM, line=line, detail=ft))
                    if ft in ("time", "clock", "gettimeofday"):
                        effects.append(Effect(kind=EffectKind.TIME, line=line, detail=ft))
                    if ft in ("malloc", "calloc", "realloc", "free"):
                        uses_malloc = True
                    if ft in ("pthread_create", "std::thread"):
                        uses_threads = True
                        effects.append(Effect(kind=EffectKind.CONCURRENCY, line=line, detail=ft))
                    if ft in ("qsort", "std::sort", "sort"):
                        sort_uses.append(Pattern(kind="unstable_sort", line=line, in_loop=in_loop, detail=ft))
                    if ft in ("std::stable_sort", "stable_sort"):
                        sort_uses.append(Pattern(kind="stable_sort", line=line, in_loop=in_loop, detail=ft))
                    if in_loop and ft in ("strlen", "strcmp", "std::find", "find", "std::count", "count"):
                        cost_patterns.append(Pattern(
                            kind="linear_membership" if "find" in ft or "count" in ft else "linear_scan",
                            line=line, in_loop=True, detail=f"{ft}() inside loop",
                        ))
                    # C++ member calls: .push_back(), .at(), .insert(), .erase()
                    if fn_node.type == "field_expression":
                        arg = fn_node.child_by_field_name("argument")
                        fld = fn_node.child_by_field_name("field")
                        aname = node_text(arg, src_bytes) if arg is not None else ""
                        fname = node_text(fld, src_bytes) if fld is not None else ""
                        if fname in ("push_back", "emplace_back", "pop_back", "insert", "erase", "clear", "resize", "sort") and aname in param_names:
                            mutated.add(aname)
                            effects.append(Effect(kind=EffectKind.ARG_MUTATION, line=line, detail=f"{aname}.{fname}()"))
                        if fname == "at":
                            implicit_raises.add("std::out_of_range")
                        if in_loop and fname in ("insert", "erase"):
                            cost_patterns.append(Pattern(
                                kind="vector_mid_mutation", line=line, in_loop=True,
                                detail=f".{fname}() inside loop",
                            ))

            for ch in n.children:
                _visit(ch, new_depth)

        _visit(body, 0)

        # Also detect `std::cout << ...`
        if "std::cout" in node_text(body, src_bytes):
            effects.append(Effect(kind=EffectKind.PRINT, line=span.start_line, detail="std::cout"))
        if "std::thread" in source or "pthread" in source:
            uses_threads = True

        functions[fn_name] = FunctionFacts(
            name=fn_name,
            lineno=span.start_line,
            end_lineno=span.end_line,
            params=params,
            returns_annotation=ret_type,
            is_recursive=is_recursive,
            branching_self_calls=branching_self,
            callees_external=sorted(callees),
            effects=effects,
            transitive_effect_kinds=sorted({e.kind for e in effects}, key=lambda k: k.value),
            mutated_params=sorted(mutated),
            raises=sorted(raises),
            implicit_raises=sorted(implicit_raises),
            loop_count=loop_count,
            max_loop_depth=max_loop_depth,
            float_reasons=float_reasons,
            sort_uses=sort_uses,
            cost_patterns=cost_patterns,
            extra={
                "language": lang_key,
                "template_params": template_params,
                "uses_threads": uses_threads,
                "uses_malloc": uses_malloc,
                "clang_ast_used": clang_ast is not None,
            },
        )

    fn_names = set(functions.keys())
    for fn in functions.values():
        fn.callees_local = [c for c in fn.callees_external if c in fn_names and c != fn.name]
        fn.callees_external = [c for c in fn.callees_external if c not in fn_names]

    called = {c for f in functions.values() for c in f.callees_local}
    roots = [n for n in functions if n not in called and n != "main"] or [n for n in functions if n != "main"] or list(functions.keys())

    return ModuleFacts(
        functions=functions,
        imports=imports,
        module_vars=module_vars,
        mutable_module_vars=mutable_vars,
        module_side_effects=[],
        root_functions=roots,
    )
