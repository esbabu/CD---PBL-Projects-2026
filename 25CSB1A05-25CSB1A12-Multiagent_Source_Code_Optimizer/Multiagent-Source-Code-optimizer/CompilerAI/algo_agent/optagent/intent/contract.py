from __future__ import annotations
import re
from typing import Any

from ..schemas import (Aspect as A, Constraints, EffectKind as K, ExecRecord, FunctionFacts,
                       Level, ModuleFacts, PreservationItem, Source, Spec)

MUST, MAY = Level.MUST, Level.MAY


def _has_float(enc: Any) -> bool:
    if isinstance(enc, float):
        return True
    if isinstance(enc, list):
        return any(_has_float(x) for x in enc)
    if isinstance(enc, dict):
        if "__float__" in enc:
            return True
        return any(_has_float(v) for v in enc.values())
    return False


def build_contract(fn: FunctionFacts, records: list[ExecRecord], constraints: Constraints,
                   overrides: dict | None = None) -> list[PreservationItem]:
    ok = [r for r in records if r.status in ("ok", "exception")]
    kinds = {e.kind for e in fn.effects} | set(fn.transitive_effect_kinds)
    dyn_mut = any(r.mutated_args for r in ok)
    dyn_out = any(r.stdout for r in ok)
    dyn_exc = any(r.status == "exception" for r in ok)
    dyn_glob = any(r.globals_changed for r in ok)
    dyn_alias = any(r.returns_input_alias for r in ok)
    nondet = [r for r in ok if r.nondeterministic_fields]
    ret_nondet = any("return" in r.nondeterministic_fields for r in nondet)
    ret_types = {r.return_type for r in ok if r.status == "ok" and r.return_type}
    floats = bool(fn.float_reasons) or any(_has_float(r.ret) for r in ok)
    nondet_static = bool(kinds & {K.RANDOM, K.TIME, K.ENV}) or fn.uses_hash_or_id
    items: list[PreservationItem] = []

    def add(aspect, level, applicable, why, src):
        items.append(PreservationItem(aspect=aspect, level=level, applicable=applicable,
                                      rationale=why, source=src))

    add(A.RETURN_VALUE, MUST, True, "Core behaviour: identical results for every valid input.", Source.DEFAULT)
    add(A.RETURN_TYPE, MUST, True,
        f"Observed return types: {sorted(ret_types) or 'n/a'}. e.g. list vs tuple, int vs float (/ vs //) must not change.",
        Source.DYNAMIC if ret_types else Source.DEFAULT)

    ordered = bool(ret_types & {"list", "tuple", "str", "dict"}) or fn.is_generator
    if ret_nondet:
        add(A.RETURN_ORDER, MAY, ordered,
            "Result varies across PYTHONHASHSEED runs: the ORIGINAL's order is already unspecified; "
            "verify as an unordered collection.", Source.DYNAMIC)
    else:
        add(A.RETURN_ORDER, MUST, ordered, "Element order of the result is observable (including dict insertion order).",
            Source.DEFAULT)

    add(A.FLOAT_EXACTNESS, MUST, floats,
        "Float results must match bit-for-bit: reassociation, FMA, or vectorised sums change low bits. "
        "Relax via constraints.float_rel_tol if acceptable.", Source.STATIC if floats else Source.DEFAULT)

    add(A.ARG_MUTATION, MUST, True,
        ("Original mutates its input(s): " + ", ".join(sorted({m for r in ok for m in r.mutated_args}) or fn.mutated_params)
         if (dyn_mut or fn.mutated_params) else
         "Original does not mutate inputs: an optimization must not start mutating them (in-place tricks!)."),
        Source.DYNAMIC if dyn_mut else Source.STATIC)

    add(A.RETURN_ALIASING, MUST if dyn_alias else MAY, dyn_alias or fn.may_return_input_alias,
        "Original returns an input object itself (identity matters to callers)." if dyn_alias else
        "Identity of the returned object is not relied upon.", Source.DYNAMIC if dyn_alias else Source.STATIC)

    printing = K.PRINT in kinds or dyn_out
    add(A.STDOUT, MUST, printing, "Printed output (text and order) is observable behaviour.",
        Source.DYNAMIC if dyn_out else Source.STATIC)

    raising = bool(fn.raises) or dyn_exc or bool(fn.implicit_raises)
    add(A.EXCEPTION_TYPE, MUST, raising,
        f"Original raises: explicit={fn.raises or 'none'}, observed={sorted({r.exc_type for r in ok if r.exc_type}) or 'none'}, "
        f"implicit={fn.implicit_raises or 'none'}. Same inputs must raise the same exception TYPE.",
        Source.DYNAMIC if dyn_exc else Source.STATIC)
    add(A.EXCEPTION_MESSAGE, MAY, raising, "Message text is rarely relied upon; raise to MUST if callers parse it.",
        Source.DEFAULT)

    add(A.GLOBAL_STATE, MUST, K.GLOBAL_WRITE in kinds or dyn_glob,
        "Module-level state is written (caches, counters). Removing or adding it changes cross-call behaviour.",
        Source.DYNAMIC if dyn_glob else Source.STATIC)
    add(A.EXTERNAL_IO, MUST, bool(kinds & {K.FILE_IO, K.NETWORK, K.SUBPROCESS, K.INPUT}),
        "File/network/process/stdin interaction must be preserved in kind and order.", Source.STATIC)

    nd = bool(nondet) or nondet_static
    add(A.DETERMINISM, MAY if nd else MUST, True,
        "Original is non-deterministic (randomness/time/hash order): verification must be seed-controlled or distributional."
        if nd else "Original is deterministic: the optimized version must be too.",
        Source.DYNAMIC if nondet else Source.STATIC)

    add(A.SORT_STABILITY, MUST, bool(fn.sort_uses),
        "Python's sort is stable; equal keys must keep original relative order. Replacing with heap/selection/"
        "unstable algorithms silently breaks this.", Source.STATIC)
    add(A.RECURSION_LIMIT, MAY, fn.is_recursive or fn.in_recursive_cycle,
        "An iterative rewrite that no longer hits RecursionError on deep inputs is an acceptable change.",
        Source.STATIC)

    for name, lvl in ((overrides or {}).get("preservation") or {}).items():
        try:
            aspect, level = A(name), Level(lvl)
        except ValueError:
            raise ValueError(f"bad override '{name}: {lvl}'. Aspects: {[a.value for a in A]}; levels: {[l.value for l in Level]}")
        for it in items:
            if it.aspect == aspect:
                it.level, it.source = level, Source.USER
                it.rationale += " [user override]"
    return items


_PURE_CLAIM = re.compile(r"(no side effects?|pure function|does not (modify|mutate)|without modifying|unchanged)", re.I)


def reconcile_spec(spec: Spec, fn: FunctionFacts, records: list[ExecRecord]) -> Spec:
    """Ground truth (dynamic > static) overrides the LLM's claims; contradictions are recorded."""
    kinds = {e.kind for e in fn.effects} | set(fn.transitive_effect_kinds)
    ok = [r for r in records if r.status in ("ok", "exception")]
    notes: list[str] = []
    se = [f"{e.kind.value}: {e.detail} (line {e.line}, {e.certainty})" for e in fn.effects]
    if any(r.mutated_args for r in ok):
        m = sorted({x for r in ok for x in r.mutated_args})
        se.append(f"observed at runtime: mutates {m}")
    if any(r.globals_changed for r in ok):
        se.append("observed at runtime: changes module globals " + str(sorted({g for r in ok for g in r.globals_changed})))
    spec.side_effects = se
    claims = " ".join(spec.postconditions + spec.invariants + [spec.summary])
    if (fn.mutated_params or any(r.mutated_args for r in ok)) and _PURE_CLAIM.search(claims):
        notes.append("Spec claims the inputs are untouched, but analysis/execution shows mutation. Mutation is the truth.")
    if any(r.nondeterministic_fields for r in ok) or kinds & {K.RANDOM, K.TIME, K.ENV} or fn.uses_hash_or_id:
        spec.determinism = "nondeterministic"
    else:
        spec.determinism = "deterministic" if ok else "unknown"
    spec.reconciliation_notes = notes
    return spec