"""Schemas for Step 7: Optimization report model and components."""
from __future__ import annotations

from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class ComplexityDiff(BaseModel):
    """Before/after complexity comparison with derivation."""
    model_config = ConfigDict(extra="allow")

    before_time: str = ""
    after_time: str = ""
    before_space: str = ""
    after_space: str = ""
    derivation: str = ""
    bottlenecks_resolved: list[str] = Field(default_factory=list)


class BenchmarkCurvePoint(BaseModel):
    """A point along an empirical scaling curve."""
    n: int
    orig_time_s: float
    cand_time_s: float
    speedup: float


class BenchmarkCurve(BaseModel):
    """Scaling curve for a specific family."""
    family: str
    points: list[BenchmarkCurvePoint] = Field(default_factory=list)
    crossover_n: int | None = None
    max_speedup: float = 1.0


class RejectedCandidate(BaseModel):
    """A candidate rejected during verification or search."""
    candidate_id: str
    proposer: str
    transform_ids: list[str] = Field(default_factory=list)
    reason: str = ""
    feedback: str = ""


class Report(BaseModel):
    """The complete optimization report for an algorithm."""
    model_config = ConfigDict(extra="allow")

    schema_version: str = "1"
    source_sha: str
    entry_point: str
    original_source: str
    optimized_source: str
    diff: str = ""
    complexity: ComplexityDiff = Field(default_factory=ComplexityDiff)
    evidence_tier: str = "T0"
    rungs_summary: list[dict[str, Any]] = Field(default_factory=list)
    benchmarks: list[BenchmarkCurve] = Field(default_factory=list)
    overall_speedup: float = 1.0
    overall_mem_ratio: float = 1.0
    remaining_differences: list[str] = Field(default_factory=list)
    rejected_candidates: list[RejectedCandidate] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    created_at: str = ""

