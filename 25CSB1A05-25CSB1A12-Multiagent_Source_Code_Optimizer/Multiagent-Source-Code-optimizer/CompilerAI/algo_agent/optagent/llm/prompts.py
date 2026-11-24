from __future__ import annotations
import json

from ..schemas import FunctionFacts, ModuleFacts, Spec

SPEC_SYSTEM = """You are a senior program-analysis engineer writing a BEHAVIOURAL SPECIFICATION of a function.
Rules:
1. Describe observable behaviour only: what it returns, mutates, raises, prints, and in what order.
2. Never suggest optimizations and never comment on efficiency.
3. Be exact about edge cases: empty input, duplicates, ties, negatives, None, very large values.
4. Document quirks and bugs faithfully. A faithful spec of a buggy function is correct. Do NOT 'fix' behaviour.
5. STATIC FACTS provided are ground truth. Never contradict them.
6. Reply with ONE JSON object and nothing else."""

SPEC_SKELETON = """{
  "summary": "one or two sentences",
  "parameters": [{"name": "", "type": "", "description": "", "constraints": ""}],
  "return_type": "", "return_description": "",
  "preconditions": [""], "postconditions": [""], "invariants": [""],
  "error_behavior": ["<ExceptionType>: <exact condition>"],
  "ordering_semantics": "order guarantees of the result, tie-breaking, stability",
  "numeric_semantics": "integer/float behaviour, rounding, overflow",
  "quirks": ["surprising behaviour a rewrite must not 'fix'"]
}"""

SPEC_USER = """Entry point: {entry}

SOURCE:
```python
{source}
```

STATIC FACTS (ground truth):
{facts}

Write the specification as JSON with exactly this shape:
{skeleton}"""

REFINE_USER = """Entry point: {entry}

SOURCE:
```python
{source}
```

STATIC FACTS (ground truth):
{facts}

YOUR PREVIOUS SPEC:
{spec}

A reader who saw ONLY that spec mispredicted these real executions (actual output is ground truth):
{cases}

Rewrite the WHOLE spec so a reader would predict these outputs correctly. Be more precise about the
behaviours that were mispredicted. Same JSON shape:
{skeleton}"""

INPUT_SYSTEM = """You design test inputs for a function. Reply with ONE JSON object:
{"inputs": [{"args": [...], "kwargs": {}, "purpose": "..."}]}
Value encoding (JSON): tuple -> {"__tuple__": [...]}, set -> {"__set__": [...]},
nan/inf -> {"__float__": "nan"}, bytes -> {"__bytes__": "<hex>"}. Plain JSON for everything else.
Keep inputs small (collections <= 30 items, ints < 10**6) so they run fast."""

INPUT_USER = """Function: {signature}

SPEC:
{spec}

Produce {n} inputs covering: typical cases; empty/minimal; single element; duplicates and ties;
negative / zero / boundary values; unsorted vs sorted vs reverse-sorted; one case with ~25 elements;
and 2 inputs that deliberately VIOLATE a precondition (to observe the error behaviour).
Every input must supply ALL required parameters."""

PREDICT_SYSTEM = """You simulate a program from its specification ONLY. You do not have its source code.
Follow the spec literally to work out the result for the given input. Reply with ONE JSON object:
{"reasoning": "short step-by-step", "outcome": "returns" | "raises",
 "value": <the returned value as JSON, or null>, "exception_type": <name or null>}
Encoding: tuple -> {"__tuple__": [...]}, set -> {"__set__": [...]}, nan/inf -> {"__float__": "nan"}."""

PREDICT_USER = """SPEC:
{spec}

Signature: {signature}
Call arguments (JSON): {args}
Keyword arguments (JSON): {kwargs}

Predict what the call returns or raises."""


def signature_of(fn: FunctionFacts) -> str:
    parts = []
    for p in fn.params:
        s = {"vararg": "*", "kwarg": "**"}.get(p.kind, "") + p.name
        if p.annotation:
            s += f": {p.annotation}"
        if p.default:
            s += f" = {p.default}"
        parts.append(s)
    return f"def {fn.name}({', '.join(parts)})" + (f" -> {fn.returns_annotation}" if fn.returns_annotation else "")


def render_facts(fn: FunctionFacts, mod: ModuleFacts) -> str:
    L = [f"signature: {signature_of(fn)}"]
    if fn.docstring:
        L.append(f"docstring: {fn.docstring[:300]}")
    L.append(f"generator: {fn.is_generator}; recursive: {fn.is_recursive or fn.in_recursive_cycle}")
    L.append(f"parameters mutated in place: {fn.mutated_params or 'none detected'}")
    effs = [f"{e.kind.value}@L{e.line} ({e.certainty}): {e.detail}" for e in fn.effects
            if e.kind.value != "arg_mutation"]
    L.append("side effects: " + ("; ".join(effs) if effs else "none detected"))
    L.append(f"explicit raises: {fn.raises or 'none'}; handled/swallowed: {fn.handled_exceptions or 'none'}; "
             f"implicit possible: {fn.implicit_raises or 'none'}")
    L.append(f"loops: {fn.loop_count} (max syntactic nesting {fn.max_loop_depth})")
    if fn.float_reasons:
        L.append(f"floating point involved: {fn.float_reasons}")
    if fn.sort_uses:
        L.append("sorting: " + "; ".join(f"{s.kind}@L{s.line} {s.detail}" for s in fn.sort_uses))
    if fn.unordered_iterations:
        L.append("ORDER DEPENDS ON HASHING at: " + "; ".join(f"L{p.line}" for p in fn.unordered_iterations))
    if fn.uses_hash_or_id:
        L.append("uses hash()/id(): result may vary across runs")
    if fn.reads_globals:
        L.append(f"reads module-level names: {fn.reads_globals}")
    return "\n".join(L)


def render_spec(spec: Spec) -> str:
    d = lambda xs: "\n".join(f"  - {x}" for x in xs) or "  (none)"
    params = "\n".join(f"  - {p.name}: {p.type}. {p.description} {p.constraints}".strip() for p in spec.parameters) or "  (none)"
    return (f"Summary: {spec.summary}\nParameters:\n{params}\n"
            f"Returns: {spec.return_type}. {spec.return_description}\n"
            f"Preconditions:\n{d(spec.preconditions)}\nPostconditions:\n{d(spec.postconditions)}\n"
            f"Invariants:\n{d(spec.invariants)}\nErrors:\n{d(spec.error_behavior)}\n"
            f"Ordering: {spec.ordering_semantics}\nNumeric: {spec.numeric_semantics}\n"
            f"Quirks:\n{d(spec.quirks)}")


def j(x) -> str:
    return json.dumps(x, ensure_ascii=False)