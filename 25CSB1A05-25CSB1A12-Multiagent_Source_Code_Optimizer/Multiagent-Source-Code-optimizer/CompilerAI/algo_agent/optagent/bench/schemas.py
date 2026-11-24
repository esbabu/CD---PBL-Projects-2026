"""Schemas for Step 6: Benchmark measurements, statistics, and results."""
from __future__ import annotations

from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class BenchStats(BaseModel):
    """Statistical summary of multiple benchmark repetitions."""
    model_config = ConfigDict(extra="allow")

    mean: float = 0.0
    median: float = 0.0
    std: float = 0.0
    p5: float = 0.0
    p95: float = 0.0
    ci_low: float = 0.0
    ci_high: float = 0.0
    n_samples: int = 0


class SizeMeasurement(BaseModel):
    """Benchmark point for a specific (family, n) configuration."""
    model_config = ConfigDict(extra="allow")

    family: str
    n: int
    orig_time_s: float
    cand_stats: BenchStats
    speedup: float = 1.0
    is_significant: bool = False
    cand_mem_bytes: int = 0
    orig_mem_bytes: int = 0
    mem_ratio: float = 1.0


class FamilyBench(BaseModel):
    """Collection of benchmark points for one scaling family."""
    model_config = ConfigDict(extra="allow")

    family: str
    points: list[SizeMeasurement] = Field(default_factory=list)
    crossover_n: int | None = None
    max_n_speedup: float = 1.0


class BenchmarkResult(BaseModel):
    """Overall benchmark outcome for a candidate."""
    model_config = ConfigDict(extra="allow")

    families: dict[str, FamilyBench] = Field(default_factory=dict)
    overall_speedup: float = 1.0
    overall_mem_ratio: float = 1.0
    crossover_n: int | None = None
    is_significant: bool = False
    noise_rejected: bool = False
    elapsed_s: float = 0.0

