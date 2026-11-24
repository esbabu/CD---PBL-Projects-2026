"""Shared tree-sitter byte-range mutation engine for JS, C, and C++."""
from __future__ import annotations

import random
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from tree_sitter import Node

from .editor import SourceEditor
from .parse import find_functions, node_text, parse_source, walk

_CMP_ALTS: dict[str, list[str]] = {
    "<": ["<=", ">="],
    "<=": ["<", ">"],
    ">": [">=", "<="],
    ">=": [">", "<"],
    "==": ["!="],
    "!=": ["=="],
    "===": ["==", "!=="],
    "!==": ["!=", "==="],
}

_ARITH_ALTS: dict[str, list[str]] = {
    "+": ["-"],
    "-": ["+"],
    "*": ["+", "/"],
    "/": ["*"],
    "%": ["*"],
}

_BOOL_ALTS: dict[str, list[str]] = {
    "&&": ["||"],
    "||": ["&&"],
}

_AUG_ALTS: dict[str, str] = {
    "+=": "-=",
    "-=": "+=",
}

_CALL_SWAPS: dict[str, str] = {
    "min": "max",
    "max": "min",
    "Math.min": "Math.max",
    "Math.max": "Math.min",
    "std::min": "std::max",
    "std::max": "std::min",
}


@dataclass
class MutantSite:
    op: str
    desc: str
    line: int
    start_byte: int
    end_byte: int
    replacement: str


def _stratified(sites: list[MutantSite], k: int, rng: random.Random) -> list[MutantSite]:
    groups: dict[str, list[MutantSite]] = defaultdict(list)
    for s in sites:
        groups[s.op].append(s)
    for g in groups.values():
        rng.shuffle(g)
    out: list[MutantSite] = []
    while len(out) < k and any(groups.values()):
        for g in list(groups.values()):
            if g and len(out) < k:
                out.append(g.pop())
    return out


class TreeSitterMutator:
    """Generates syntax-valid mutants via tree-sitter byte-range replacements."""

    def __init__(self, lang: str):
        self.lang = lang.lower()
        self.is_js = self.lang in ("js", "javascript")
        self.is_native = self.lang in ("c", "cpp", "c++", "cxx")

    def _collect_sites(self, root: Node, src_bytes: bytes) -> list[MutantSite]:
        sites: list[MutantSite] = []

        for node in walk(root):
            line = node.start_point[0] + 1
            ntype = node.type

            # 1. Binary expressions: relational, arithmetic, boolean
            if ntype == "binary_expression":
                op_node = node.child_by_field_name("operator")
                if op_node is None and len(node.children) == 3:
                    op_node = node.children[1]
                if op_node is not None:
                    op_txt = node_text(op_node, src_bytes)
                    if op_txt in _CMP_ALTS:
                        for alt in _CMP_ALTS[op_txt]:
                            if not self.is_js and alt in ("===", "!=="):
                                continue
                            sites.append(MutantSite(
                                "compare", f"{op_txt} -> {alt}", line,
                                op_node.start_byte, op_node.end_byte, alt,
                            ))
                    elif op_txt in _ARITH_ALTS:
                        for alt in _ARITH_ALTS[op_txt]:
                            sites.append(MutantSite(
                                "arith", f"{op_txt} -> {alt}", line,
                                op_node.start_byte, op_node.end_byte, alt,
                            ))
                    elif op_txt in _BOOL_ALTS:
                        for alt in _BOOL_ALTS[op_txt]:
                            sites.append(MutantSite(
                                "boolop", f"{op_txt} -> {alt}", line,
                                op_node.start_byte, op_node.end_byte, alt,
                            ))

            # 2. Unary `!` removal
            elif ntype == "unary_expression":
                op_node = node.child_by_field_name("operator")
                arg_node = node.child_by_field_name("argument")
                if op_node is not None and arg_node is not None and node_text(op_node, src_bytes) == "!":
                    sites.append(MutantSite(
                        "not-removal", "`!` removed", line,
                        node.start_byte, node.end_byte, node_text(arg_node, src_bytes),
                    ))

            # 3. Update expression (++ <-> --)
            elif ntype == "update_expression":
                txt = node_text(node, src_bytes)
                if "++" in txt:
                    sites.append(MutantSite(
                        "arith", "++ -> --", line,
                        node.start_byte, node.end_byte, txt.replace("++", "--", 1),
                    ))
                elif "--" in txt:
                    sites.append(MutantSite(
                        "arith", "-- -> ++", line,
                        node.start_byte, node.end_byte, txt.replace("--", "++", 1),
                    ))

            # 4. Condition negation on if/while
            elif ntype in ("if_statement", "while_statement"):
                cond = node.child_by_field_name("condition")
                if cond is not None:
                    ctxt = node_text(cond, src_bytes)
                    if ctxt.startswith("(") and ctxt.endswith(")"):
                        inner = ctxt[1:-1]
                        repl = f"(!({inner}))"
                    else:
                        repl = f"!({ctxt})"
                    sites.append(MutantSite(
                        "negate-cond", "condition negated", line,
                        cond.start_byte, cond.end_byte, repl,
                    ))

            # 5. Break / continue swap
            elif ntype == "break_statement":
                sites.append(MutantSite(
                    "loop-ctl", "break -> continue", line,
                    node.start_byte, node.end_byte, "continue;",
                ))
            elif ntype == "continue_statement":
                sites.append(MutantSite(
                    "loop-ctl", "continue -> break", line,
                    node.start_byte, node.end_byte, "break;",
                ))

            # 6. Return statement value mutation
            elif ntype == "return_statement":
                txt = node_text(node, src_bytes).strip()
                if txt not in ("return;", "return 0;", "return null;", "return undefined;"):
                    repl = "return undefined;" if self.is_js else "return 0;"
                    sites.append(MutantSite(
                        "return-zero", f"{txt[:30]} -> {repl}", line,
                        node.start_byte, node.end_byte, repl,
                    ))

            # 7. Constants (numbers, booleans, strings)
            elif ntype in ("number", "number_literal"):
                txt = node_text(node, src_bytes).strip()
                if re.fullmatch(r"\d+", txt):
                    val = int(txt)
                    for nv in (val + 1, max(0, val - 1)):
                        if nv != val:
                            sites.append(MutantSite(
                                "const", f"{val} -> {nv}", line,
                                node.start_byte, node.end_byte, str(nv),
                            ))
                    if val != 0:
                        sites.append(MutantSite(
                            "const", f"{val} -> 0", line,
                            node.start_byte, node.end_byte, "0",
                        ))
            elif ntype in ("true", "false"):
                alt = "false" if ntype == "true" else "true"
                sites.append(MutantSite(
                    "const", f"{ntype} -> {alt}", line,
                    node.start_byte, node.end_byte, alt,
                ))

            # 8. Augmented assignment (+= <-> -=) and statement deletion
            elif ntype in ("augmented_assignment_expression", "assignment_expression"):
                txt = node_text(node, src_bytes)
                for sym, alt in _AUG_ALTS.items():
                    if sym in txt:
                        sites.append(MutantSite(
                            "arith", f"{sym} -> {alt}", line,
                            node.start_byte, node.end_byte, txt.replace(sym, alt, 1),
                        ))
                        break

            elif ntype == "expression_statement":
                txt = node_text(node, src_bytes).strip()
                if txt and txt != ";":
                    sites.append(MutantSite(
                        "stmt-delete", "statement deleted", line,
                        node.start_byte, node.end_byte, ";",
                    ))

            # 9. Subscript off-by-one: a[i] -> a[(i) + 1], a[(i) - 1]
            elif ntype in ("subscript_expression",):
                idx = node.child_by_field_name("index")
                if idx is None and len(node.children) >= 3:
                    idx = node.children[-2]
                if idx is not None:
                    itxt = node_text(idx, src_bytes)
                    if itxt and itxt not in ("[", "]"):
                        sites.append(MutantSite(
                            "index", "index + 1", line,
                            idx.start_byte, idx.end_byte, f"({itxt} + 1)",
                        ))
                        sites.append(MutantSite(
                            "index", "index - 1", line,
                            idx.start_byte, idx.end_byte, f"({itxt} - 1)",
                        ))

            # 10. Calls: min/max swap, JS .slice() removal, C memcpy length +/- 1
            elif ntype == "call_expression":
                fn_node = node.child_by_field_name("function")
                if fn_node is not None:
                    fn_txt = node_text(fn_node, src_bytes)
                    if fn_txt in _CALL_SWAPS:
                        alt = _CALL_SWAPS[fn_txt]
                        sites.append(MutantSite(
                            "call-swap", f"{fn_txt} -> {alt}", line,
                            fn_node.start_byte, fn_node.end_byte, alt,
                        ))
                    if self.is_js and fn_node.type == "member_expression":
                        prop = fn_node.child_by_field_name("property")
                        obj = fn_node.child_by_field_name("object")
                        args = node.child_by_field_name("arguments")
                        if prop is not None and obj is not None and node_text(prop, src_bytes) == "slice":
                            if args is not None and node_text(args, src_bytes).strip() == "()":
                                sites.append(MutantSite(
                                    "alias", ".slice() removed (aliasing)", line,
                                    node.start_byte, node.end_byte, node_text(obj, src_bytes),
                                ))
                    if self.is_native and fn_txt in ("memcpy", "memmove", "memset"):
                        args = node.child_by_field_name("arguments")
                        if args is not None:
                            named_args = [c for c in args.children if c.is_named]
                            if len(named_args) == 3:
                                len_arg = named_args[2]
                                ltxt = node_text(len_arg, src_bytes)
                                sites.append(MutantSite(
                                    "memcpy-len", f"{fn_txt} len - 1", line,
                                    len_arg.start_byte, len_arg.end_byte, f"(({ltxt}) > 0 ? ({ltxt}) - 1 : 0)",
                                ))

            # 11. Language-specific: JS `new Map()` -> `{}` (key_enumeration_order)
            elif self.is_js and ntype == "new_expression":
                txt = node_text(node, src_bytes).strip()
                if txt == "new Map()":
                    sites.append(MutantSite(
                        "map-to-obj", "new Map() -> {}", line,
                        node.start_byte, node.end_byte, "{}",
                    ))

            # 12. Language-specific: C/C++ `const` removal & signed/unsigned swap
            elif self.is_native and ntype == "type_qualifier":
                if node_text(node, src_bytes) == "const":
                    sites.append(MutantSite(
                        "drop-const", "const qualifier removed", line,
                        node.start_byte, node.end_byte, "",
                    ))
            elif self.is_native and ntype == "primitive_type":
                txt = node_text(node, src_bytes)
                if txt == "int":
                    sites.append(MutantSite(
                        "signedness", "int -> unsigned int", line,
                        node.start_byte, node.end_byte, "unsigned int",
                    ))

        return sites

    def generate(
        self,
        source: str,
        reachable: set[str],
        max_mutants: int = 60,
        rng: random.Random | None = None,
    ) -> list[dict[str, Any]]:
        rng = rng or random.Random(20240607)
        tree, src_bytes = parse_source(source, self.lang)
        spans = find_functions(tree, src_bytes, self.lang)

        all_sites: list[MutantSite] = []
        target_nodes = [spans[n].body_node or spans[n].node for n in reachable if n in spans]
        if not target_nodes:
            target_nodes = [tree.root_node]
        for tn in target_nodes:
            all_sites.extend(self._collect_sites(tn, src_bytes))

        chosen = _stratified(all_sites, max_mutants * 2, rng)
        seen: set[str] = {source}
        out: list[dict[str, Any]] = []
        for site in chosen:
            if len(out) >= max_mutants:
                break
            try:
                msrc = SourceEditor(source).replace(site.start_byte, site.end_byte, site.replacement).apply()
            except Exception:
                continue
            if msrc in seen:
                continue
            # Filter syntax-broken mutants via tree-sitter
            mtree, _ = parse_source(msrc, self.lang)
            if mtree.root_node.has_error:
                continue
            seen.add(msrc)
            out.append({
                "id": len(out),
                "op": site.op,
                "desc": site.desc,
                "line": site.line,
                "source": msrc,
            })
        return out
