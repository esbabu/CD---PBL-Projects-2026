from __future__ import annotations
import json

from ..llm import prompts as P
from ..llm.client import LLMClient
from ..schemas import CaseCheck, Spec, SpecDraft


class SpecAgent:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def draft(self, source: str, entry: str, facts_text: str) -> Spec:
        user = P.SPEC_USER.format(entry=entry, source=source, facts=facts_text, skeleton=P.SPEC_SKELETON)
        d = self.llm.complete_json(P.SPEC_SYSTEM, user, SpecDraft)
        return Spec(**d.model_dump(), entry_point=entry, version=1)

    def refine(self, spec: Spec, source: str, entry: str, facts_text: str,
               bad_cases: list[CaseCheck]) -> Spec:
        cases = "\n".join(f"- args={P.j(c.args)}\n  spec-reader predicted: {c.predicted}\n  ACTUAL: {c.actual}"
                          for c in bad_cases[:6])
        user = P.REFINE_USER.format(entry=entry, source=source, facts=facts_text,
                                    spec=P.render_spec(spec), cases=cases, skeleton=P.SPEC_SKELETON)
        d = self.llm.complete_json(P.SPEC_SYSTEM, user, SpecDraft)
        return Spec(**d.model_dump(), entry_point=entry, version=spec.version + 1)