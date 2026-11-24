from __future__ import annotations
import json
from typing import Any

from pydantic import BaseModel

from ..config import Settings
from ..llm import prompts as P
from ..llm.client import LLMClient, LLMError
from ..runtime import canon
from ..schemas import CaseCheck, ExecRecord, FunctionFacts, RoundReport, Spec


class _Prediction(BaseModel):
    reasoning: str = ""
    outcome: str = "returns"
    value: Any = None
    exception_type: str | None = None


def _show(rec: ExecRecord) -> str:
    if rec.status == "exception":
        return f"raises {rec.exc_type}"
    return f"returns {json.dumps(rec.ret)[:300]}"


class SpecValidator:
    def __init__(self, llm: LLMClient, s: Settings):
        self.llm, self.s = llm, s

    def validate(self, spec: Spec, fn: FunctionFacts, records: list[ExecRecord],
                 rel_tol: float = 1e-9) -> RoundReport:
        usable = [r for r in records if r.status in ("ok", "exception") and not r.nondeterministic_fields]
        # keep a mix of normal and exceptional cases
        usable.sort(key=lambda r: r.status == "ok")
        picked = usable[: self.s.max_predictor_inputs]
        cases: list[CaseCheck] = []
        for rec in picked:
            user = P.PREDICT_USER.format(spec=P.render_spec(spec), signature=P.signature_of(fn),
                                         args=P.j(rec.args), kwargs=P.j(rec.kwargs))
            try:
                pred = self.llm.complete_json(P.PREDICT_SYSTEM, user, _Prediction)
                agree, shown = self._agree(pred, rec, rel_tol)
            except LLMError:
                agree, shown = False, "<predictor produced no valid answer>"
            cases.append(CaseCheck(args=rec.args, predicted=shown, actual=_show(rec), agree=agree))
        score = sum(c.agree for c in cases) / len(cases) if cases else 0.0
        return RoundReport(spec_version=spec.version, checked=len(cases), score=round(score, 3), cases=cases)

    @staticmethod
    def _agree(pred: _Prediction, rec: ExecRecord, tol: float) -> tuple[bool, str]:
        if pred.outcome.lower().startswith("raise"):
            shown = f"raises {pred.exception_type}"
            return rec.status == "exception" and (pred.exception_type or "") == rec.exc_type, shown
        shown = f"returns {json.dumps(pred.value)[:300]}"
        if rec.status != "ok":
            return False, shown
        try:
            return canon.loose_equal(canon.decode(pred.value), canon.decode(rec.ret), tol), shown
        except Exception:
            return False, shown