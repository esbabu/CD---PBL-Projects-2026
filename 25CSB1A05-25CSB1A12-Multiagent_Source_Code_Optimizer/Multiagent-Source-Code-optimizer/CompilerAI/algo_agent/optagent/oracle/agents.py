from __future__ import annotations
import ast
import json

from pydantic import BaseModel

from ..intent.input_agent import _InputSet
from ..llm.client import LLMClient, LLMError
from ..llm.prompts import j, render_spec, signature_of
from ..schemas import FunctionFacts, IntentBundle
from .schemas import PropertySpec

PROP_SYSTEM = """You write executable PROPERTY CHECKS for a function, from its specification.
Each property is a python function:  def prop_<name>(f, args, kwargs, result) -> bool
  f       = the function under test (you may call f on TRANSFORMED COPIES of the input: metamorphic relations)
  args    = list of the ORIGINAL (pre-call) positional arguments; kwargs = dict of keyword arguments
  result  = what the call returned
Return True if the property holds. Pre-imported names: math, copy, itertools, collections. No other imports.
Always deep-copy before passing data to f. Write 4 to 8 properties covering: output structure/type,
relations between result and input, idempotence/invariance (e.g. permutation invariance ONLY if the spec says
order is irrelevant), monotonicity, and bounds. Never assert anything the spec does not guarantee.
Reply with ONE JSON object: {"properties": [{"name": "prop_x", "description": "...", "code": "def prop_x(f, args, kwargs, result):\\n    ..."}]}"""

PROP_USER = """Signature: {sig}

SPEC:
{spec}

SOURCE (for context; properties must follow the SPEC, not implementation accidents):
```python
{source}
```"""

ADV_SYSTEM = """You are a red-team engineer. Someone will REWRITE this function to be faster. Design inputs that
expose subtly wrong rewrites. Reply with ONE JSON object: {"inputs": [{"args": [...], "kwargs": {}, "purpose": "..."}]}
Value encoding: tuple -> {"__tuple__": [...]}, set -> {"__set__": [...]}, nan/inf -> {"__float__": "nan"}.
Keep inputs small (collections <= 30 items). Every input must supply ALL required parameters."""

ADV_USER = """Signature: {sig}

SPEC:
{spec}

SOURCE:
```python
{source}
```

Behaviours that must be preserved: {must}
Performance anti-patterns in the original (rewrites will target these): {patterns}
{extra}
Produce {n} inputs. Cover: ties/duplicates (stability, first-vs-last match), results that depend on iteration
order, early-exit boundaries and off-by-one positions, inputs where the answer is at the very start / very end /
absent, negative and zero values, 1 == 1.0 == True equality, empty and single-element inputs, repeated calls
effects (mutation of the argument), and anything that makes a hash/sort/heap based rewrite give a different answer."""


class _Props(BaseModel):
    properties: list[dict] = []


def sanitize_properties(raw: list[dict]) -> list[PropertySpec]:
    """Keep ONLY top-level `def prop_*(f, args, kwargs, result)` functions. Anything else is discarded."""
    out, seen = [], set()
    for p in raw:
        try:
            code = str(p.get("code", ""))
            tree = ast.parse(code)
        except SyntaxError:
            continue
        for node in tree.body:
            if (isinstance(node, ast.FunctionDef) and node.name.startswith("prop_")
                    and len(node.args.args) == 4 and node.name not in seen):
                seg = ast.get_source_segment(code, node)
                if seg:
                    seen.add(node.name)
                    out.append(PropertySpec(name=node.name, description=str(p.get("description", "")), code=seg))
    return out


class PropertyAgent:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def propose(self, intent: IntentBundle, fn: FunctionFacts) -> list[PropertySpec]:
        user = PROP_USER.format(sig=signature_of(fn), spec=render_spec(intent.spec), source=intent.source)
        try:
            return sanitize_properties(self.llm.complete_json(PROP_SYSTEM, user, _Props).properties)
        except LLMError:
            return []


class AdversaryAgent:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def _ask(self, intent: IntentBundle, fn: FunctionFacts, n: int, extra: str) -> list[tuple[list, dict]]:
        must = [c.aspect.value for c in intent.contract if c.level.value == "must_preserve"]
        patterns = [f"L{p.line} {p.kind}" for p in fn.cost_patterns] + [f"{x.kind}@L{x.line}" for x in fn.sort_uses]
        user = ADV_USER.format(sig=signature_of(fn), spec=render_spec(intent.spec), source=intent.source,
                               must=must, patterns=patterns or "none detected", extra=extra, n=n)
        try:
            out = self.llm.complete_json(ADV_SYSTEM, user, _InputSet)
        except LLMError:
            return []
        return [(c.args, c.kwargs) for c in out.inputs[:n]]

    def propose(self, intent, fn, n: int, uncovered: list[int]) -> list[tuple[list, dict]]:
        lines = intent.source.splitlines()
        extra = ""
        if uncovered:
            snippet = "\n".join(f"L{i}: {lines[i - 1]}" for i in uncovered[:15] if 0 < i <= len(lines))
            extra = f"These lines were NEVER executed by existing tests; make some inputs reach them:\n{snippet}\n"
        return self._ask(intent, fn, n, extra)

    def targeted(self, intent, fn, mutant_desc: str, line: int, n: int = 6) -> list[tuple[list, dict]]:
        lines = intent.source.splitlines()
        ctx = lines[line - 1] if 0 < line <= len(lines) else ""
        extra = (f"A faulty variant differs only here: line {line} `{ctx.strip()}` ({mutant_desc}). "
                 f"Produce inputs whose RESULT would differ between the correct and the faulty version.\n")
        return self._ask(intent, fn, n, extra)