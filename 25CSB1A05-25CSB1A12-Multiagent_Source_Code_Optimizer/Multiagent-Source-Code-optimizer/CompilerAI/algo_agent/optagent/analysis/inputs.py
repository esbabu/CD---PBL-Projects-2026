"""Deterministic heuristic seed ladder (Workstream B7).

Runs BEFORE any LLM:
  1. Type annotations (including dataclass fields)
  2. Default parameter values
  3. Doctest / docstring examples
  4. Call sites & literals in the same file / __main__
  5. Usage-based AST type inference
  6. Stdin grammar inference (for script mode)
  7. Boundary pack per inferred type
"""
from __future__ import annotations

import ast
import re
from typing import Any

from ..core.provenance import ComponentKind, component
from ..runtime import canon
from ..schemas import FunctionFacts

_BASE = {
    "int": [5, 0, 1, -3],
    "float": [2.5, 0.0, 1.0, -1.5],
    "str": ["hello", "", "a", "aab"],
    "bool": [True, False, True, False],
}


def _g(t: ast.expr, v: int, class_fields: dict[str, list[tuple[str, str | None]]] | None = None) -> Any:
    class_fields = class_fields or {}
    if isinstance(t, ast.Name):
        n = t.id.lower()
        if n in _BASE:
            return _BASE[n][v]
        if n in ("list", "sequence"):
            return [1, 2, 3][: (3, 0, 1, 2)[v]]
        if n in ("dict", "mapping"):
            return {"a": 1, "b": 2} if v != 1 else {}
        if n in ("set", "frozenset"):
            return {1, 2} if v != 1 else set()
        if t.id in class_fields:
            fvals: dict[str, Any] = {}
            for fname, fann in class_fields[t.id]:
                try:
                    fvals[fname] = _g(ast.parse(fann or "int", mode="eval").body, v, class_fields)
                except Exception:
                    fvals[fname] = _BASE["int"][v]
            return {"__obj__": [t.id, fvals]}
        raise ValueError(t.id)
    if isinstance(t, ast.Attribute):
        return _g(ast.Name(id=t.attr), v, class_fields)
    if isinstance(t, ast.BinOp) and isinstance(t.op, ast.BitOr):
        # Python 3.10+ `X | None` union syntax
        return _g(t.left, v, class_fields)
    if isinstance(t, ast.Subscript):
        base = (t.value.id if isinstance(t.value, ast.Name) else getattr(t.value, "attr", "")).lower()
        args = t.slice.elts if isinstance(t.slice, ast.Tuple) else [t.slice]
        if base in ("list", "sequence", "set", "frozenset", "tuple") and not (
            base == "tuple"
            and len(args) == 2
            and not (isinstance(args[1], ast.Constant) and args[1].value is Ellipsis)
        ):
            pool = [_g(args[0], i, class_fields) for i in range(4)]
            items = [pool, [], [pool[0]], [pool[0], pool[0], pool[3]]][v]
            if "set" in base:
                try:
                    return set(items)
                except TypeError:
                    return list(items)
            return tuple(items) if base == "tuple" else list(items)
        if base == "tuple":
            return tuple(_g(a, v, class_fields) for a in args)
        if base in ("dict", "mapping"):
            ks = [_g(args[0], i, class_fields) for i in range(4)]
            vs = [_g(args[1], i, class_fields) for i in range(4)]
            idx = [[0, 1, 2], [], [0], [0, 3]][v]
            return {ks[i]: vs[i] for i in idx}
        if base in ("optional", "union"):
            return _g(args[0], v, class_fields)
    raise ValueError(ast.unparse(t))


def _encode_preserving_tags(val: Any) -> Any:
    """Encode a Python value with canon.encode while preserving pre-tagged `__obj__` nodes."""
    if isinstance(val, dict) and list(val.keys()) == ["__obj__"]:
        cls_name, fields = val["__obj__"]
        return {"__obj__": [cls_name, {k: _encode_preserving_tags(v) for k, v in fields.items()}]}
    if isinstance(val, list):
        return [_encode_preserving_tags(x) for x in val]
    return canon.encode(val)


@component(kind=ComponentKind.HEURISTIC, name="inputs.annotation_inputs", description="Derive seed inputs from parameter type annotations.")
def annotation_inputs(fn: FunctionFacts) -> list[dict]:
    """Up to 4 inputs (typical / empty / single / duplicates) from annotations. [] if not derivable."""
    req = [p for p in fn.params if p.kind == "positional" and p.default is None]
    if any(p.annotation is None for p in req):
        return []
    class_fields = fn.extra.get("class_fields") if isinstance(fn.extra, dict) else None
    cases = []
    for v in range(4):
        try:
            args = [_g(ast.parse(p.annotation, mode="eval").body, v, class_fields) for p in req]
        except (ValueError, KeyError, IndexError, SyntaxError):
            return []
        cases.append({"args": _encode_preserving_tags(args), "kwargs": {}})
    return cases


def _doctest_inputs(fn: FunctionFacts) -> list[dict]:
    """Step 3: Extract `>>> fn_name(...)` examples from the function docstring."""
    if not fn.docstring:
        return []
    short = fn.name.split(".")[-1]
    out: list[dict] = []
    rx = re.compile(rf">>>\s*(?:\w+\.)?{re.escape(short)}\s*\(([^)]*)\)")
    for m in rx.finditer(fn.docstring):
        try:
            call_node = ast.parse(f"_f({m.group(1)})", mode="eval").body
            if isinstance(call_node, ast.Call):
                args = [ast.literal_eval(a) for a in call_node.args]
                kwargs = {kw.arg: ast.literal_eval(kw.value) for kw in call_node.keywords if kw.arg}
                out.append({"args": canon.encode(args), "kwargs": canon.encode(kwargs)})
        except Exception:
            continue
    return out


def _call_site_inputs(fn: FunctionFacts, source: str) -> list[dict]:
    """Step 4: Extract literal call-site arguments in the same module / `__main__`."""
    if not source:
        return []
    short = fn.name.split(".")[-1]
    out: list[dict] = []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fname = None
            if isinstance(node.func, ast.Name):
                fname = node.func.id
            elif isinstance(node.func, ast.Attribute):
                fname = node.func.attr
            if fname == short and (node.args or node.keywords):
                try:
                    args = [ast.literal_eval(a) for a in node.args]
                    kwargs = {kw.arg: ast.literal_eval(kw.value) for kw in node.keywords if kw.arg}
                    out.append({"args": canon.encode(args), "kwargs": canon.encode(kwargs)})
                except Exception:
                    continue
    return out


def infer_param_types_from_usage(fn: FunctionFacts, source: str) -> dict[str, str]:
    """Step 5: Usage-based AST type inference for unannotated parameters."""
    inferred: dict[str, str] = {}
    if not source:
        return inferred
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return inferred

    short = fn.name.split(".")[-1]
    target_node = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == short:
            if node.lineno == fn.lineno or target_node is None:
                target_node = node
    if target_node is None:
        return inferred

    pnames = {p.name for p in fn.params if p.kind == "positional"}
    scores: dict[str, dict[str, int]] = {p: {"list[int]": 0, "str": 0, "dict[str, int]": 0, "int": 0, "float": 0} for p in pnames}

    for sub in ast.walk(target_node):
        # Iterating over p or calling len(p)
        if isinstance(sub, (ast.For, ast.AsyncFor)) and isinstance(sub.iter, ast.Name) and sub.iter.id in pnames:
            scores[sub.iter.id]["list[int]"] += 4
        if isinstance(sub, ast.comprehension) and isinstance(sub.iter, ast.Name) and sub.iter.id in pnames:
            scores[sub.iter.id]["list[int]"] += 4
        if isinstance(sub, ast.Call):
            if isinstance(sub.func, ast.Name) and sub.args and isinstance(sub.args[0], ast.Name) and sub.args[0].id in pnames:
                p = sub.args[0].id
                if sub.func.id in ("len", "sum", "sorted", "min", "max", "enumerate", "set", "list"):
                    scores[p]["list[int]"] += 3
                elif sub.func.id in ("range", "abs"):
                    scores[p]["int"] += 4
            if isinstance(sub.func, ast.Attribute) and isinstance(sub.func.value, ast.Name) and sub.func.value.id in pnames:
                p, m = sub.func.value.id, sub.func.attr
                if m in ("append", "extend", "sort", "pop", "insert", "remove", "reverse"):
                    scores[p]["list[int]"] += 5
                elif m in ("split", "strip", "lower", "upper", "startswith", "endswith", "replace", "join"):
                    scores[p]["str"] += 5
                elif m in ("get", "keys", "values", "items", "setdefault", "update"):
                    scores[p]["dict[str, int]"] += 5
        if isinstance(sub, ast.Subscript) and isinstance(sub.value, ast.Name) and sub.value.id in pnames:
            p = sub.value.id
            if isinstance(sub.slice, ast.Constant) and isinstance(sub.slice.value, str):
                scores[p]["dict[str, int]"] += 4
            else:
                scores[p]["list[int]"] += 2
        if isinstance(sub, ast.BinOp):
            for side in (sub.left, sub.right):
                if isinstance(side, ast.Name) and side.id in pnames:
                    if isinstance(sub.op, (ast.Sub, ast.Mult, ast.FloorDiv, ast.Mod)):
                        scores[side.id]["int"] += 3
                    elif isinstance(sub.op, ast.Div):
                        scores[side.id]["float"] += 2
        if isinstance(sub, ast.Compare) and isinstance(sub.left, ast.Name) and sub.left.id in pnames:
            p = sub.left.id
            for c in sub.comparators:
                if isinstance(c, ast.Constant):
                    if isinstance(c.value, str):
                        scores[p]["str"] += 3
                    elif isinstance(c.value, int):
                        scores[p]["int"] += 3
                    elif isinstance(c.value, float):
                        scores[p]["float"] += 3

    for p in pnames:
        best_type, best_score = max(scores[p].items(), key=lambda kv: kv[1])
        if best_score > 0:
            inferred[p] = best_type
        else:
            # Name-based gentle fallback
            low = p.lower()
            if any(tok in low for tok in ("nums", "arr", "items", "list", "vals", "data", "xs", "words")):
                inferred[p] = "list[str]" if "word" in low else "list[int]"
            elif any(tok in low for tok in ("str", "text", "name", "mode", "key", "word", "s")):
                inferred[p] = "str"
            else:
                inferred[p] = "int"
    return inferred


@component(kind=ComponentKind.HEURISTIC, name="inputs.infer_stdin_seeds", description="Infer bounded stdin test inputs from script input() patterns.")
def infer_stdin_seeds(source: str) -> list[dict]:
    """Step 6: Stdin grammar heuristic for scripts reading via `input()` / `sys.stdin`."""
    uses_t_loop = bool(re.search(r"for\s+\w+\s+in\s+range\s*\(\s*int\s*\(\s*input\s*\(\s*\)\s*\)", source))
    n_int_inputs = len(re.findall(r"int\s*\(\s*input\s*\(\s*\)\s*\)", source))
    has_split_ints = bool(re.search(r"map\s*\(\s*int\s*,\s*input\s*\(\s*\)\.split", source)) or "sys.stdin" in source

    samples: list[str] = []
    if uses_t_loop:
        samples = [
            "2\n3\n1 2 1\n4\n1 2 3 4\n",
            "1\n1\n5\n",
            "2\n5\n2 2 2 3 3\n2\n0 0\n",
        ]
    elif n_int_inputs >= 1 and has_split_ints:
        samples = [
            "5\n1 2 1 3 2\n",
            "1\n42\n",
            "4\n1 1 1 1\n",
            "6\n-3 0 5 -3 2 0\n",
        ]
    elif has_split_ints:
        samples = [
            "1 2 3 2 1\n",
            "5\n",
            "10 20 30 40\n",
            "0 -1 1 0\n",
        ]
    elif n_int_inputs >= 2:
        samples = ["5\n3\n", "0\n0\n", "10\n4\n", "1\n1\n"]
    elif n_int_inputs == 1:
        samples = ["5\n", "0\n", "1\n", "10\n"]
    else:
        samples = ["hello world\n", "1 2 3\n", "a b a\n", "\n"]

    return [{"args": [{"stdin": s, "argv": []}], "kwargs": {}, "origin": "stdin_grammar"} for s in samples]


@component(kind=ComponentKind.HEURISTIC, name="inputs.heuristic_seed_inputs", description="7-step deterministic heuristic seed input ladder.")
def heuristic_seed_inputs(
    fn: FunctionFacts | None,
    source: str = "",
    strategy: str = "function",
) -> list[dict]:
    """Run all deterministic heuristic seed steps (1..7) and return deduplicated seeds."""
    if strategy == "script" or fn is None:
        return infer_stdin_seeds(source)

    seeds: list[dict] = []
    # Step 1: Type annotations
    seeds.extend(annotation_inputs(fn))

    # Step 3: Doctests
    seeds.extend(_doctest_inputs(fn))

    # Step 4: Call sites in same file / __main__
    seeds.extend(_call_site_inputs(fn, source))

    # Steps 2, 5, 7: Defaults + usage-based type inference + boundary pack
    if not seeds:
        inferred = infer_param_types_from_usage(fn, source)
        class_fields = fn.extra.get("class_fields") if isinstance(fn.extra, dict) else None
        req = [p for p in fn.params if p.kind == "positional" and p.default is None]
        opt = [p for p in fn.params if p.kind == "positional" and p.default is not None]
        for v in range(4):
            args: list[Any] = []
            ok = True
            for p in req:
                t_str = p.annotation or inferred.get(p.name, "int")
                try:
                    args.append(_g(ast.parse(t_str, mode="eval").body, v, class_fields))
                except Exception:
                    args.append(_BASE["int"][v])
            # Also include one variant exercising default args on v == 0
            if v == 0 and opt:
                try:
                    opt_vals = [ast.literal_eval(p.default) for p in opt if p.default is not None]
                    if len(opt_vals) == len(opt):
                        seeds.append({"args": _encode_preserving_tags(args + opt_vals), "kwargs": {}})
                except Exception:
                    pass
            if ok:
                seeds.append({"args": _encode_preserving_tags(args), "kwargs": {}})

    return seeds
