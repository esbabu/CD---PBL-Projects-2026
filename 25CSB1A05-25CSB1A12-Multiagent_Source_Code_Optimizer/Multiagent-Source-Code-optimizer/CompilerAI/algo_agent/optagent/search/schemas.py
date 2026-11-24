"""Schemas for Step 6: Search nodes, Pareto front, and search results."""
from __future__ import annotations

from typing import Any
from pydantic import BaseModel, ConfigDict, Field

from ..bench.schemas import BenchmarkResult
from ..proposers.schemas import Candidate
from ..verify.schemas import Evidence


class SearchNode(BaseModel):
    """A node in the transformation search graph."""
    model_config = ConfigDict(extra="allow")

    candidate: Candidate
    parent_id: str | None = None
    depth: int = 0
    evidence: Evidence | None = None
    bench: BenchmarkResult | None = None
    reward: float = 0.0
    status: str = "pending"                # pending | verified | rejected | benchmarked


class ParetoPoint(BaseModel):
    """A non-dominated point on the time/space Pareto front."""
    model_config = ConfigDict(extra="allow")

    candidate_id: str
    source: str
    speedup: float = 1.0                   # > 1.0 means faster
    mem_ratio: float = 1.0                 # < 1.0 means less memory
    evidence_tier: str = "T0"
    time_complexity: str = ""
    space_complexity: str = ""
    reward: float = 0.0


class SearchBudget(BaseModel):
    """Budget constraints for the search controller."""
    max_candidates: int = 15
    max_time_s: float = 60.0
    beam_width: int = 3


class SearchResult(BaseModel):
    """Final outcome of the optimization search."""
    model_config = ConfigDict(extra="allow")

    best_candidate: Candidate | None = None
    pareto_front: list[ParetoPoint] = Field(default_factory=list)
    all_evaluated: list[SearchNode] = Field(default_factory=list)
    iterations: int = 0
    stop_reason: str = ""
    elapsed_s: float = 0.0

