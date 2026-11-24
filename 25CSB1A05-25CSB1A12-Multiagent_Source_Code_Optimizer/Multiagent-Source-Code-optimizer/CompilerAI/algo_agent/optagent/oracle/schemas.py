"""Step 2 oracle data-model: all pydantic models that live in oracle/."""
from __future__ import annotations

import hashlib
import json
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from ..runtime import canon
from ..schemas import Constraints, PreservationItem


# ---------------------------------------------------------------------------
# Case – a single (args, kwargs) test vector
# ---------------------------------------------------------------------------
def _case_id(args: list, kwargs: dict) -> str:
    payload = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True,
                         separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha1(payload.encode()).hexdigest()[:16]


def split_of(case: "Case", holdout_pct: int) -> str:
    """Deterministic visible/holdout assignment keyed by case id."""
    if case.origin in ("user", "seed", "annotation"):
        return "visible"
    n = int(case.id[:4], 16) % 100
    return "holdout" if n < holdout_pct else "visible"


class Case(BaseModel):
    id: str
    args: list[Any]
    kwargs: dict[str, Any] = {}
    origin: str = "unknown"           # user | seed | family | hypothesis | llm | fresh | probe | …
    category: str = "valid"           # valid | adversarial | hypothesis | …
    kind: str = "valid"               # valid | probe | shrunk | …
    size: int = 0                     # rough element count, used for ordering

    @classmethod
    def make(cls, args, kwargs=None, origin: str = "unknown",
             category: str = "valid", kind: str = "valid") -> "Case":
        a = canon.encode(list(args))
        k = {kk: canon.encode(vv) for kk, vv in (kwargs or {}).items()}
        cid = _case_id(a, k)
        sz = sum(len(x) if isinstance(x, (list, tuple, str, bytes)) else 1
                 for x in (args or []))
        return cls(id=cid, args=a, kwargs=k, origin=origin, category=category, kind=kind, size=sz)

    def py(self) -> tuple[list, dict]:
        """Decode back to Python objects."""
        return canon.decode(self.args), {k: canon.decode(v) for k, v in self.kwargs.items()}


# ---------------------------------------------------------------------------
# CaseResult – what the sandbox returns for one case
# ---------------------------------------------------------------------------
class CaseResult(BaseModel):
    idx: int = 0
    status: Literal["ok", "exception", "timeout", "crash", "load_error"] = "ok"
    ret: Any = None
    ret_digest: str | None = None
    return_type: str | None = None
    exc_type: str | None = None
    exc_msg: str | None = None
    stdout: str = ""
    mut: dict[str, Any] = {}       # mutated args (encoded or digest)
    glob: dict[str, Any] = {}      # changed module globals (encoded)
    alias: list[int] = []          # arg indices that the return value aliases
    edges: list[str] = []          # coverage edges from the tracer (cleared after golden)
    prop_failures: list[str] = []  # property names that failed
    elapsed_s: float | None = None
    generator: bool = False
    sanitizer: str | None = None
    signal: str | None = None
    build_log: str | None = None


# ---------------------------------------------------------------------------
# GoldenRecord – authoritative behaviour for one Case
# ---------------------------------------------------------------------------
class GoldenRecord(BaseModel):
    case_id: str
    result: CaseResult          # hash-seed 0 run
    unstable: list[str] = []   # fields that differ between seed-0 and seed-1
    alt: CaseResult | None = None   # seed-1 run (only kept when "ret" is in unstable)


# ---------------------------------------------------------------------------
# Violation – a behavioural difference found by the Comparator
# ---------------------------------------------------------------------------
class Violation(BaseModel):
    aspect: str
    detail: str = ""
    expected: str = ""
    actual: str = ""
    severity: Literal["error", "warn"] = "error"


# ---------------------------------------------------------------------------
# PropertySpec – an LLM-proposed property function (validated against original)
# ---------------------------------------------------------------------------
class PropertySpec(BaseModel):
    name: str
    code: str            # full Python function source, starts with `def prop_<name>(`
    description: str = ""


# ---------------------------------------------------------------------------
# ScalePoint – one (family, mode, n) timing point from the scaling set
# ---------------------------------------------------------------------------
class ScalePoint(BaseModel):
    family: str
    mode: str                           # e.g. "random", "sorted", "few_unique"
    n: int
    args: list[Any]
    kwargs: dict[str, Any] = {}
    status: Literal["ok", "exception", "timeout", "crash"] = "ok"
    orig_time_s: float | None = None
    digest: str = ""                    # sha1[:16] of scale_digest(CaseResult)


# ---------------------------------------------------------------------------
# Mutation testing
# ---------------------------------------------------------------------------
class MutantInfo(BaseModel):
    model_config = ConfigDict(extra="allow")   # mutation.py sets .aspect and other fields dynamically

    id: str | int   # mutation.py uses int ids; str form also accepted
    op: str
    desc: str
    line: int
    status: Literal["killed", "survived", "timeout", "error"] = "survived"
    killed_by: str | None = None
    aspect: str | None = None           # which aspect caught the mutant
    by_visible: bool = True
    likely_equivalent: bool = False
    hunted: bool = False
    line_covered: bool = False


class MutationReport(BaseModel):
    model_config = ConfigDict(extra="allow")

    total: int = 0
    killed: int = 0
    survived: int = 0
    invalid: int = 0
    score: float = 0.0
    score_visible_only: float = 0.0
    survivors_on_covered_lines: int = 0
    survivors_on_uncovered_lines: int = 0
    prop_kills: dict[str, int] = {}
    mutants: list[MutantInfo] = []


# ---------------------------------------------------------------------------
# Coverage info
# ---------------------------------------------------------------------------
class CoverageInfo(BaseModel):
    lines_total: int = 0
    lines_covered: int = 0
    uncovered: list[int] = []
    arcs_observed: int = 0


# ---------------------------------------------------------------------------
# Oracle strength grading
# ---------------------------------------------------------------------------
class StrengthReport(BaseModel):
    tier: str = "D"               # A | B | C | D
    line_coverage: float = 0.0
    mutation_score: float | None = None
    n_cases: int = 0
    n_visible: int = 0
    n_holdout: int = 0
    n_probes: int = 0
    notes: list[str] = []


# ---------------------------------------------------------------------------
# OracleBundle – the full oracle artefact
# ---------------------------------------------------------------------------
class OracleBundle(BaseModel):
    schema_version: str = "2"
    language: str = "python"
    source_sha: str
    entry_point: str
    param_schema: dict[str, Any]       # ParamSchema.model_dump()
    contract: list[PreservationItem] = []
    constraints: Constraints = Field(default_factory=Constraints)
    cases: list[Case]
    golden: dict[str, GoldenRecord]
    properties: list[PropertySpec] = []
    scaling: list[ScalePoint] = []
    coverage: CoverageInfo = Field(default_factory=CoverageInfo)
    mutation: MutationReport | None = None
    strength: StrengthReport = Field(default_factory=StrengthReport)
    multiset_returns: bool = False
    warnings: list[str] = []
