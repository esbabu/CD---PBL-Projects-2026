"""JavaScript LanguageAdapter implementation (Node 22 + Babel / tree-sitter)."""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import yaml

from ...analysis.static_facts import AmbiguousEntry
from ...oracle.schema_infer import ParamSchema, VS as ValSchema
from ...oracle.schemas import CaseResult
from ...proposers.schemas import Candidate
from ...runtime.sandbox import PKG_ROOT, SandboxProfile
from ...schemas import (
    Aspect,
    Effect,
    EffectKind,
    FunctionFacts,
    Level,
    ModuleFacts,
    ParamInfo,
    Pattern,
    Source,
)
from ..base import (
    BenchProfile,
    BuildResult,
    Capabilities,
    ContractRule,
    MutationOps,
    PromptPack,
    RulePack,
    Rung,
)
from ..treesitter.editor import SourceEditor
from ..treesitter.mutate import TreeSitterMutator
from ..treesitter.parse import executable_statement_lines, find_functions, node_text, parse_source, walk
from .prompts import JS_PROMPT_PACK

JS_DIR = Path(__file__).resolve().parent
JS_HARNESS = PKG_ROOT / "optagent" / "runtime" / "js" / "batch_harness.mjs"
JS_FACTS_SCRIPT = JS_DIR / "facts.mjs"

MUTATING_ARRAY_METHODS = {
    "push", "pop", "shift", "unshift", "splice", "sort", "reverse", "fill", "copyWithin",
}

_JSDOC_PARAM_RE = re.compile(r"@param\s+\{([^}]+)\}\s+(\w+)")
_JSDOC_RET_RE = re.compile(r"@returns?\s+\{([^}]+)\}")


def _extract_jsdoc(source: str, start_line: int) -> tuple[str | None, dict[str, str], str | None]:
    """Extract JSDoc comment immediately preceding `start_line` (1-based)."""
    lines = source.splitlines()
    idx = start_line - 2
    while idx >= 0 and not lines[idx].strip():
        idx -= 1
    if idx < 0 or not lines[idx].strip().endswith("*/"):
        return None, {}, None
    end = idx
    while idx >= 0 and "/**" not in lines[idx]:
        idx -= 1
    if idx < 0:
        return None, {}, None
    block = "\n".join(lines[idx:end + 1])
    param_types = {m.group(2): m.group(1).strip() for m in _JSDOC_PARAM_RE.finditer(block)}
    ret_m = _JSDOC_RET_RE.search(block)
    ret_type = ret_m.group(1).strip() if ret_m else None
    return block, param_types, ret_type


def _analyze_js_treesitter(source: str) -> ModuleFacts:
    """Tree-sitter based JS static fact analyzer (works with zero Node/Babel requirement)."""
    tree, src_bytes = parse_source(source, "javascript")
    if tree.root_node.has_error:
        raise SyntaxError("JavaScript source contains syntax errors")

    spans = find_functions(tree, src_bytes, "javascript")
    functions: dict[str, FunctionFacts] = {}
    module_vars: list[str] = []
    mutable_vars: list[str] = []
    imports: dict[str, str] = {}

    for ch in tree.root_node.children:
        if ch.type == "import_statement":
            txt = node_text(ch, src_bytes)
            m = re.search(r"from\s+['\"]([^'\"]+)['\"]", txt)
            if m:
                imports[m.group(1)] = m.group(1)
        elif ch.type in ("lexical_declaration", "variable_declaration"):
            txt = node_text(ch, src_bytes)
            is_const = txt.lstrip().startswith("const ")
            for sub in ch.children:
                if sub.type == "variable_declarator":
                    nm = sub.child_by_field_name("name")
                    val = sub.child_by_field_name("value")
                    if nm is not None and (val is None or val.type not in ("arrow_function", "function_expression", "function")):
                        vname = node_text(nm, src_bytes)
                        module_vars.append(vname)
                        if not is_const:
                            mutable_vars.append(vname)

    for fn_name, span in spans.items():
        node = span.node
        jsdoc, jsdoc_params, jsdoc_ret = _extract_jsdoc(source, span.start_line)

        # Parameters
        params: list[ParamInfo] = []
        params_node = node.child_by_field_name("parameters")
        if params_node is not None:
            for ch in params_node.children:
                if ch.type == "identifier":
                    pname = node_text(ch, src_bytes)
                    params.append(ParamInfo(name=pname, annotation=jsdoc_params.get(pname)))
                elif ch.type == "assignment_pattern":
                    left = ch.child_by_field_name("left")
                    right = ch.child_by_field_name("right")
                    if left is not None:
                        pname = node_text(left, src_bytes)
                        params.append(ParamInfo(
                            name=pname,
                            annotation=jsdoc_params.get(pname),
                            default=node_text(right, src_bytes) if right else None,
                        ))
                elif ch.type == "rest_pattern":
                    for sub in ch.children:
                        if sub.type == "identifier":
                            pname = node_text(sub, src_bytes)
                            params.append(ParamInfo(name=pname, annotation=jsdoc_params.get(pname), kind="vararg"))
        else:
            # Single-param arrow function `x => ...`
            pnode = node.child_by_field_name("parameter")
            if pnode is not None:
                pname = node_text(pnode, src_bytes)
                params.append(ParamInfo(name=pname, annotation=jsdoc_params.get(pname)))

        param_names = {p.name for p in params}
        is_async = node_text(node, src_bytes).lstrip().startswith("async ")
        is_gen = node.type in ("generator_function_declaration", "generator_function")

        mutated: set[str] = set()
        effects: list[Effect] = []
        raises: set[str] = set()
        sort_uses: list[Pattern] = []
        cost_patterns: list[Pattern] = []
        callees: set[str] = set()
        may_alias = False
        is_recursive = False
        branching_self = 0
        loop_count = 0
        max_loop_depth = 0
        float_reasons: list[str] = []

        body = span.body_node or node

        def _visit(n, depth: int):
            nonlocal loop_count, max_loop_depth, is_recursive, branching_self, may_alias
            ntype = n.type
            line = n.start_point[0] + 1
            in_loop = depth > 0
            new_depth = depth

            if ntype in ("for_statement", "for_in_statement", "while_statement", "do_statement"):
                loop_count += 1
                new_depth = depth + 1
                if new_depth > max_loop_depth:
                    max_loop_depth = new_depth
                if new_depth >= 2:
                    cost_patterns.append(Pattern(
                        kind="nested_loop", line=line, in_loop=True,
                        detail=f"loop header at depth {new_depth}",
                    ))

            elif ntype == "throw_statement":
                txt = node_text(n, src_bytes)
                m = re.search(r"new\s+([A-Za-z_]\w*)", txt)
                raises.add(m.group(1) if m else "Error")

            elif ntype == "return_statement":
                for ch in n.children:
                    if ch.type == "identifier" and node_text(ch, src_bytes) in param_names:
                        may_alias = True

            elif ntype == "assignment_expression":
                left = n.child_by_field_name("left")
                if left is not None and left.type in ("subscript_expression", "member_expression"):
                    obj = left.child_by_field_name("object")
                    if obj is not None and node_text(obj, src_bytes) in param_names:
                        oname = node_text(obj, src_bytes)
                        mutated.add(oname)
                        effects.append(Effect(kind=EffectKind.ARG_MUTATION, line=line, detail=f"{oname}[...] = ..."))
                # Spread accumulation in loop: acc = [...acc, x]
                right = n.child_by_field_name("right")
                if in_loop and right is not None and right.type == "array" and "..." in node_text(right, src_bytes):
                    cost_patterns.append(Pattern(
                        kind="spread_in_reduce", line=line, in_loop=True,
                        detail="array spread accumulation inside loop",
                    ))

            elif ntype == "augmented_assignment_expression":
                txt = node_text(n, src_bytes)
                if in_loop and "+=" in txt:
                    if '"' in txt or "'" in txt or "`" in txt:
                        cost_patterns.append(Pattern(
                            kind="string_concat", line=line, in_loop=True,
                            detail="string += inside loop",
                        ))

            elif ntype == "call_expression":
                fn_node = n.child_by_field_name("function")
                if fn_node is not None:
                    ftxt = node_text(fn_node, src_bytes)
                    if fn_node.type == "identifier":
                        callees.add(ftxt)
                        if ftxt == fn_name:
                            is_recursive = True
                            branching_self += 1
                        if ftxt == "require":
                            args_txt = node_text(n, src_bytes)
                            for bad_mod in ("fs", "net", "http", "https", "child_process"):
                                if f"'{bad_mod}'" in args_txt or f'"{bad_mod}"' in args_txt:
                                    k = EffectKind.FILE_IO if bad_mod == "fs" else (
                                        EffectKind.SUBPROCESS if bad_mod == "child_process" else EffectKind.NETWORK
                                    )
                                    effects.append(Effect(kind=k, line=line, detail=f"require('{bad_mod}')"))
                    elif fn_node.type == "member_expression":
                        obj = fn_node.child_by_field_name("object")
                        prop = fn_node.child_by_field_name("property")
                        oname = node_text(obj, src_bytes) if obj is not None else ""
                        pname = node_text(prop, src_bytes) if prop is not None else ""
                        if pname in MUTATING_ARRAY_METHODS and oname in param_names:
                            mutated.add(oname)
                            effects.append(Effect(kind=EffectKind.ARG_MUTATION, line=line, detail=f"{oname}.{pname}()"))
                        if pname == "sort":
                            args = n.child_by_field_name("arguments")
                            named = [c for c in args.children if c.is_named] if args else []
                            sort_uses.append(Pattern(
                                kind="array_sort", line=line, in_loop=in_loop,
                                detail="custom comparator" if named else "default lexicographic sort",
                            ))
                        if in_loop and pname in ("includes", "indexOf"):
                            cost_patterns.append(Pattern(
                                kind="linear_membership", line=line, in_loop=True,
                                detail=f".{pname}() inside loop",
                            ))
                        if in_loop and pname in ("shift", "unshift", "splice"):
                            cost_patterns.append(Pattern(
                                kind="linear_shift", line=line, in_loop=True,
                                detail=f".{pname}() inside loop",
                            ))
                        if pname == "reduce":
                            args_txt = node_text(n, src_bytes)
                            if "..." in args_txt:
                                cost_patterns.append(Pattern(
                                    kind="spread_in_reduce", line=line, in_loop=True,
                                    detail="spread accumulation inside .reduce()",
                                ))
                        if oname == "console":
                            effects.append(Effect(kind=EffectKind.PRINT, line=line, detail=f"console.{pname}"))
                        if oname == "Math" and pname == "random":
                            effects.append(Effect(kind=EffectKind.RANDOM, line=line, detail="Math.random()"))
                        if oname == "Date" and pname == "now":
                            effects.append(Effect(kind=EffectKind.TIME, line=line, detail="Date.now()"))

            elif ntype == "number":
                t = node_text(n, src_bytes)
                if "." in t or "e" in t.lower():
                    if "float_literal" not in float_reasons:
                        float_reasons.append("float_literal")

            for ch in n.children:
                _visit(ch, new_depth)

        _visit(body, 0)

        functions[fn_name] = FunctionFacts(
            name=fn_name,
            lineno=span.start_line,
            end_lineno=span.end_line,
            params=params,
            returns_annotation=jsdoc_ret,
            docstring=jsdoc,
            is_generator=is_gen,
            is_async=is_async,
            is_recursive=is_recursive,
            branching_self_calls=branching_self,
            callees_external=sorted(callees),
            effects=effects,
            transitive_effect_kinds=sorted({e.kind for e in effects}, key=lambda k: k.value),
            mutated_params=sorted(mutated),
            raises=sorted(raises),
            loop_count=loop_count,
            max_loop_depth=max_loop_depth,
            float_reasons=float_reasons,
            sort_uses=sort_uses,
            cost_patterns=cost_patterns,
            may_return_input_alias=may_alias,
            extra={"language": "javascript"},
        )

    fn_names = set(functions.keys())
    for fn in functions.values():
        fn.callees_local = [c for c in fn.callees_external if c in fn_names and c != fn.name]
        fn.callees_external = [c for c in fn.callees_external if c not in fn_names]

    called = {c for f in functions.values() for c in f.callees_local}
    roots = [n for n in functions if n not in called] or list(functions.keys())

    return ModuleFacts(
        functions=functions,
        imports=imports,
        module_vars=module_vars,
        mutable_module_vars=mutable_vars,
        module_side_effects=[],
        root_functions=roots,
    )


def _jsdoc_to_valschema(ann: str | None) -> ValSchema:
    if not ann:
        return ValSchema(kind="any")
    a = ann.strip().lower().replace(" ", "")
    if a in ("number[]", "array<number>", "int[]"):
        return ValSchema(kind="list", elem=ValSchema(kind="int", lo=-50, hi=50), min_len=0, max_len=20)
    if a in ("string[]", "array<string>"):
        return ValSchema(kind="list", elem=ValSchema(kind="str"), min_len=0, max_len=20)
    if a in ("boolean[]", "array<boolean>"):
        return ValSchema(kind="list", elem=ValSchema(kind="bool"), min_len=0, max_len=20)
    if a in ("number", "int", "integer"):
        return ValSchema(kind="int", lo=-50, hi=50)
    if a in ("float", "double"):
        return ValSchema(kind="float", lo=-50.0, hi=50.0)
    if a in ("string", "str"):
        return ValSchema(kind="str")
    if a in ("boolean", "bool"):
        return ValSchema(kind="bool")
    return ValSchema(kind="any")


def _sample_for_jsdoc(ann: str | None) -> list[Any]:
    if not ann:
        return [[1, 2, 3], [], [3, 1, 2]]
    a = ann.strip().lower().replace(" ", "")
    if a in ("number[]", "array<number>", "int[]"):
        return [[2, 7, 11, 15], [], [3, 3], [-1, 0, 1, 2, -1], [5, 1, 3, 2, 4]]
    if a in ("string[]", "array<string>"):
        return [["a", "b", "a", "c"], [], ["1", "2", "10", "2"], ["x", "y", "x", "y", "z"]]
    if a in ("number", "int", "integer"):
        return [9, 0, 6, 1, 3]
    if a in ("float", "double"):
        return [1.5, 0.0, -2.5, 3.14, 10.0]
    if a in ("string", "str"):
        return ["hello", "", "ababa", "123", "🚀🔥"]
    if a in ("boolean", "bool"):
        return [True, False, True, False, True]
    return [[1, 2, 3], [], [0]]


def _js_propose_rules(intent: Any, analysis: Any) -> list[Candidate]:
    """Deterministic tree-sitter rewrite rules for JavaScript."""
    src: str = intent.source
    entry: str = intent.entry_point
    cands: list[Candidate] = []
    fn = intent.module_facts.functions.get(entry)
    if not fn:
        return cands

    patterns = {p.kind for p in fn.cost_patterns} | {b.pattern for b in (analysis.bottlenecks or [])}

    # 1. Nested loop two-sum -> Map inverted index + binary search (preserves lexicographic first pair (i, j))
    if ("nested_loop" in patterns or fn.max_loop_depth >= 2) and "two_sum" in entry.lower() or (
        len(fn.params) == 2 and "nested_loop" in patterns and "==" in src and "+" in src
    ):
        p0, p1 = fn.params[0].name, fn.params[1].name
        if re.search(rf"{re.escape(p0)}\s*\[\s*\w+\s*\]\s*\+\s*{re.escape(p0)}\s*\[\s*\w+\s*\]\s*===?\s*{re.escape(p1)}", src):
            opt_src = (
                f"function {entry}({p0}, {p1}) {{\n"
                f"  const pos = new Map();\n"
                f"  for (let idx = 0; idx < {p0}.length; idx++) {{\n"
                f"    const v = {p0}[idx];\n"
                f"    let lst = pos.get(v);\n"
                f"    if (!lst) {{ lst = []; pos.set(v, lst); }}\n"
                f"    lst.push(idx);\n"
                f"  }}\n"
                f"  for (let i = 0; i < {p0}.length; i++) {{\n"
                f"    const lst = pos.get({p1} - {p0}[i]);\n"
                f"    if (lst) {{\n"
                f"      let lo = 0, hi = lst.length;\n"
                f"      while (lo < hi) {{\n"
                f"        const mid = (lo + hi) >> 1;\n"
                f"        if (lst[mid] <= i) lo = mid + 1;\n"
                f"        else hi = mid;\n"
                f"      }}\n"
                f"      if (lo < lst.length) return [i, lst[lo]];\n"
                f"    }}\n"
                f"  }}\n"
                f"  return [];\n"
                f"}}\n"
            )
            cands.append(Candidate(
                id="js_rule_nested_map_bsearch",
                proposer="rule",
                source=opt_src,
                transform_ids=["js_nested_loop_to_map_index"],
                rationale="Transformed O(n^2) nested pair loop into Map inverted index with binary search O(n log n).",
                claimed_time="O(n log n)",
                claimed_space="O(n)",
            ))

    # 2. Linear membership (`!seen.includes(w)` where `const seen = []`) -> companion Set
    if "linear_membership" in patterns:
        m_init = re.search(r"(\b(?:const|let|var)\s+(\w+)\s*=\s*\[\s*\]\s*;)", src)
        if m_init:
            list_var = m_init.group(2)
            set_var = f"{list_var}Set"
            if re.search(rf"\b{re.escape(list_var)}\.includes\(", src):
                new_src = src.replace(
                    m_init.group(1),
                    f"{m_init.group(1)}\n  const {set_var} = new Set();",
                    1,
                )
                new_src = re.sub(
                    rf"\b{re.escape(list_var)}\.includes\(([^)]+)\)",
                    rf"{set_var}.has(\1)",
                    new_src,
                )
                new_src = re.sub(
                    rf"(\b{re.escape(list_var)}\.push\(([^)]+)\)\s*;)",
                    rf"\1 {set_var}.add(\2);",
                    new_src,
                )
                if new_src != src:
                    cands.append(Candidate(
                        id="js_rule_list_to_set_includes",
                        proposer="rule",
                        source=new_src,
                        transform_ids=["js_list_to_set_includes"],
                        rationale=f"Replaced O(n) {list_var}.includes() inside loop with O(1) Set lookup ({set_var}.has).",
                        claimed_time="O(n log n)" if fn.sort_uses else "O(n)",
                        claimed_space="O(n)",
                    ))

    # 3. Queue `.shift()` in while loop -> head index
    if "linear_shift" in patterns:
        m_shift = re.search(r"while\s*\(\s*(\w+)\.length\s*>\s*0\s*\)\s*\{[^}]*?(?:const|let|var)\s+(\w+)\s*=\s*\1\.shift\(\)\s*;", src, re.S)
        if m_shift:
            qvar, itemvar = m_shift.group(1), m_shift.group(2)
            new_src = re.sub(
                rf"while\s*\(\s*{re.escape(qvar)}\.length\s*>\s*0\s*\)",
                f"let _qHead = 0;\n  while (_qHead < {qvar}.length)",
                src,
                count=1,
            )
            new_src = re.sub(
                rf"\b{re.escape(qvar)}\.shift\(\)",
                f"{qvar}[_qHead++]",
                new_src,
                count=1,
            )
            if new_src != src:
                cands.append(Candidate(
                    id="js_rule_shift_to_head",
                    proposer="rule",
                    source=new_src,
                    transform_ids=["js_shift_queue_to_head_index"],
                    rationale=f"Replaced O(n) {qvar}.shift() queue dequeue with O(1) head index pointer.",
                    claimed_time="O(n)",
                    claimed_space="O(n)",
                ))

    return cands


class JavaScriptAdapter:
    """LanguageAdapter for JavaScript (Node 22 LTS)."""

    id: str = "javascript"
    display: str = "JavaScript (Node 22)"
    extensions: tuple[str, ...] = (".js", ".mjs", ".cjs")
    caps: Capabilities = Capabilities(
        function_mode=True,
        program_mode=False,
        isolation_required=False,
        static_types=False,
        max_evidence_tier="T2",
        perturbation="prng_seed",
    )

    # ---------- Step 1 ----------
    def analyze(self, source: str, hints: dict[str, Any]) -> ModuleFacts:
        # Prefer Babel facts.mjs if node + @babel/parser are installed; otherwise use tree-sitter analyzer
        if shutil.which("node") and JS_FACTS_SCRIPT.exists():
            try:
                with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as tf:
                    tf.write(source)
                    tmp_path = tf.name
                try:
                    proc = subprocess.run(
                        ["node", str(JS_FACTS_SCRIPT), tmp_path],
                        capture_output=True, text=True, timeout=10,
                    )
                    if proc.returncode == 0 and proc.stdout.strip().startswith("{"):
                        return ModuleFacts.model_validate_json(proc.stdout)
                finally:
                    Path(tmp_path).unlink(missing_ok=True)
            except Exception:
                pass
        return _analyze_js_treesitter(source)

    def select_entry(self, mod: ModuleFacts, requested: str | None) -> str:
        if requested:
            if requested not in mod.functions:
                raise KeyError(f"Entry function '{requested}' not found. Available: {sorted(mod.functions)}")
            return requested
        if len(mod.root_functions) == 1:
            return mod.root_functions[0]
        if len(mod.functions) == 1:
            return next(iter(mod.functions))
        raise AmbiguousEntry(sorted(mod.root_functions or mod.functions.keys()))

    def signature(self, fn: FunctionFacts) -> str:
        prefix = "async function " if fn.is_async else "function "
        params = ", ".join(
            (f"...{p.name}" if p.kind == "vararg" else p.name)
            + (f" /* {p.annotation} */" if p.annotation else "")
            for p in fn.params
        )
        return f"{prefix}{fn.name}({params})"

    def seed_inputs(self, fn: FunctionFacts, hints: dict[str, Any]) -> list[dict[str, Any]]:
        if not fn.params:
            return [{"args": [], "kwargs": {}}]
        cols = [_sample_for_jsdoc(p.annotation) for p in fn.params]
        n = min(5, max(len(c) for c in cols))
        out = []
        for i in range(n):
            args = [c[i % len(c)] for c in cols]
            out.append({"args": args, "kwargs": {}})
        return out

    def param_schema(self, fn: FunctionFacts, hints: dict[str, Any], seeds: list[Any]) -> ParamSchema | None:
        if all(p.annotation for p in fn.params) and fn.params:
            schemas = [_jsdoc_to_valschema(p.annotation) for p in fn.params]
            if all(vs.kind != "any" for vs in schemas):
                return ParamSchema(args=schemas, kwargs={})
        return None  # fall back to seed-based inference

    def prompt_pack(self) -> PromptPack:
        return JS_PROMPT_PACK

    def contract_rules(self) -> list[ContractRule]:
        return [
            ContractRule(
                aspect=Aspect.ASYNC_SEMANTICS,
                default_level=Level.MUST,
                applicable_fn=lambda fn, recs, h: fn.is_async or any(
                    (r.return_type or "").startswith("Promise") for r in recs
                ),
                rationale="JavaScript Promise vs synchronous return and rejection semantics must be preserved.",
                source=Source.STATIC,
            ),
            ContractRule(
                aspect=Aspect.KEY_ENUMERATION_ORDER,
                default_level=Level.MUST,
                applicable_fn=lambda fn, recs, h: True,
                rationale="Object integer-like key ordering differs from Map insertion order; key enumeration order must be preserved.",
                source=Source.DEFAULT,
            ),
            ContractRule(
                aspect=Aspect.PROTOTYPE_STATE,
                default_level=Level.MUST,
                applicable_fn=lambda fn, recs, h: True,
                rationale="Candidate must not mutate Object.prototype, Array.prototype, or global intrinsics.",
                source=Source.DEFAULT,
            ),
            ContractRule(
                aspect=Aspect.SORT_STABILITY,
                default_level=Level.MUST,
                applicable_fn=lambda fn, recs, h: bool(fn.sort_uses),
                rationale="ES2019+ Array.prototype.sort is guaranteed stable; equal keys must preserve relative order.",
                source=Source.STATIC,
            ),
        ]

    # ---------- Step 2 ----------
    def sandbox_profile(self, hints: dict[str, Any]) -> SandboxProfile:
        extra_files = dict((hints or {}).get("extra_files") or {})

        def run_cmd(work: Path, out: Path, docker: bool) -> list[str]:
            if docker:
                return [
                    "node", "--max-old-space-size=512",
                    "/opt/optagent/optagent/runtime/js/batch_harness.mjs",
                    "/work/target.js", "/work/cases.jsonl", "/out/out.jsonl", "/work/cfg.json",
                ]
            node_bin = shutil.which("node")
            if not node_bin:
                cand = Path.home() / ".nodejs" / "node-v20.18.0-win-x64" / "node.exe"
                node_bin = str(cand) if cand.exists() else "node"
            return [
                node_bin, "--max-old-space-size=512",
                str(JS_HARNESS),
                str(work / "target.js"), str(work / "cases.jsonl"),
                str(out / "out.jsonl"), str(work / "cfg.json"),
            ]

        def env_fn(perturb_idx: int) -> dict[str, str]:
            return {"OPT_PERTURB_IDX": str(perturb_idx), "NODE_ENV": "production"}

        return SandboxProfile(
            target_name="target.js",
            image=os.getenv("OPT_JS_DOCKER_IMAGE", "optagent-sandbox-js:latest"),
            needs_build=False,
            isolation_required=False,
            language="javascript",
            run_cmd=run_cmd,
            env=env_fn,
            extra_files=extra_files,
        )

    def build(self, source: str, entry: str, hints: dict[str, Any], workdir: Path) -> BuildResult:
        p = workdir / "target.js"
        p.write_text(source, encoding="utf-8")
        return BuildResult(ok=True, artifact_path=p)

    def executable_lines(self, source: str, mod: ModuleFacts, entry: str) -> tuple[set[int], set[str]]:
        reach, stack = {entry}, [entry]
        while stack:
            cur = stack.pop()
            fn = mod.functions.get(cur)
            if not fn:
                continue
            for c in fn.callees_local:
                if c not in reach:
                    reach.add(c)
                    stack.append(c)
        lines = executable_statement_lines(source, "javascript", reach)
        return lines, reach

    def mutation_ops(self) -> MutationOps:
        mutator = TreeSitterMutator("javascript")
        return MutationOps(
            language="javascript",
            generate=lambda source, reachable, max_m, rng: mutator.generate(source, reachable, max_m, rng),
            file_extension=".js",
        )

    def normalize_result(self, r: CaseResult) -> CaseResult:
        return r

    # ---------- Steps 3 to 7 ----------
    def cost_table(self) -> dict[str, str]:
        p = JS_DIR / "cost.yaml"
        if p.exists():
            data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
            return dict(data.get("costs") or {})
        return {}

    def rule_pack(self) -> RulePack:
        return RulePack(
            language="javascript",
            rules_yaml=JS_DIR / "rules.yaml",
            propose_fn=_js_propose_rules,
        )

    def kb_dir(self) -> Path:
        return JS_DIR

    def verify_rungs(self) -> list[Rung]:
        return []  # JS max evidence tier is T2 (no symbolic rung)

    def bench_profile(self) -> BenchProfile:
        return BenchProfile(
            language="javascript",
            warmups=5,
            reps=7,
            gc_between_reps=True,
            report_cold_and_warm=True,
            extra_flags=["--expose-gc"],
        )

    def security_profile(self) -> dict[str, Any]:
        return {
            "language": "javascript",
            "static_tools": ["eslint", "semgrep"],
            "isolation": "vm_context_plus_docker",
            "forbidden_modules": ["fs", "net", "http", "https", "child_process", "dgram", "dns", "tls", "worker_threads"],
            "runtime_flags": ["--max-old-space-size=512"],
            "sandbox_flags": ["--network", "none", "--read-only", "--cap-drop", "ALL"],
        }
