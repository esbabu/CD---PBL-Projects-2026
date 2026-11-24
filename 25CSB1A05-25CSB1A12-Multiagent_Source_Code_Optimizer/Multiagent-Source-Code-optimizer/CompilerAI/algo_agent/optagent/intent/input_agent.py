from __future__ import annotations
import json

from pydantic import BaseModel

from ..llm import prompts as P
from ..llm.client import LLMClient
from ..schemas import FunctionFacts, Spec


class _Case(BaseModel):
    args: list = []
    kwargs: dict = {}
    purpose: str = ""


class _InputSet(BaseModel):
    inputs: list[_Case] = []


class InputAgent:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def generate(self, fn: FunctionFacts, spec: Spec, n: int) -> list[dict]:
        user = P.INPUT_USER.format(signature=P.signature_of(fn), spec=P.render_spec(spec), n=n)
        out = self.llm.complete_json(P.INPUT_SYSTEM, user, _InputSet)
        return [{"args": c.args, "kwargs": c.kwargs} for c in out.inputs[:n]]


def dedupe(cases: list[dict]) -> list[dict]:
    seen, out = set(), []
    for c in cases:
        k = json.dumps([c["args"], c.get("kwargs", {})], sort_keys=True)
        if k not in seen:
            seen.add(k)
            out.append(c)
    return out