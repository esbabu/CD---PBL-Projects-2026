"""Step 3 Complexity schemas: FitResult, Recurrence, Bottleneck, FunctionComplexity, AnalysisBundle."""
from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field


class FitResult(BaseModel):
    model: str                         # e.g. "O(1)", "O(log n)", "O(n)", "O(n log n)", "O(n^2)", etc.
    formula: str = ""                  # e.g. "y = a * n^2 + b"
    r2: float = 0.0                    # coefficient of determination
    aic: float = 0.0                   # Akaike information criterion
    bic: float = 0.0                   # Bayesian information criterion
    confidence: float = 0.0            # 0.0 to 1.0 based on r2 and point count
    family: str = "unknown"
    mode: str = "unknown"
    n_points: int = 0
    points: list[tuple[int, float]] = []  # [(n, time_or_mem)]


class Recurrence(BaseModel):
    relation: str                      # e.g. "T(n) = 2T(n/2) + O(n)"
    a: float | None = None
    b: float | None = None
    d: float | None = None             # f(n) = O(n^d)
    closed_form: str = "unknown"       # e.g. "O(n log n)"
    method: Literal["master_theorem", "akra_bazzi", "iteration", "unknown"] = "unknown"


class Bottleneck(BaseModel):
    line: int
    code: str = ""
    pattern: str = ""                  # e.g. "nested_loop", "linear_membership", "sort", "hotspot"
    share_of_time: float = 0.0         # fraction of total runtime spent here (0.0 to 1.0)
    hits: int = 0                      # execution count
    claimed_complexity: str = ""       # e.g. "O(n^2)"
    measured_complexity: str = ""
    detail: str = ""


class FunctionComplexity(BaseModel):
    name: str
    static_time: str = "O(1)"
    static_space: str = "O(1)"
    empirical_time: str | None = None
    empirical_space: str | None = None
    time_fit: FitResult | None = None
    space_fit: FitResult | None = None
    reconciled_time: str = "O(1)"
    reconciled_space: str = "O(1)"
    recurrence: Recurrence | None = None
    bottlenecks: list[Bottleneck] = []
    findings: list[str] = []


class AnalysisBundle(BaseModel):
    schema_version: str = "3"
    source_sha: str
    entry_point: str
    functions: dict[str, FunctionComplexity] = {}
    overall_time: str = "O(1)"
    overall_space: str = "O(1)"
    bottlenecks: list[Bottleneck] = []
    findings: list[str] = []
    warnings: list[str] = []

