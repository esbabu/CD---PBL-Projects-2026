"""Pydantic schemas for Step 5: Verification ladder and evidence tiers."""
from __future__ import annotations

from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class RungResult(BaseModel):
    """Result of evaluating a single verification rung."""
    model_config = ConfigDict(extra="allow")

    rung: str                              # e.g. "R1_compile", "R2_golden_holdout", ...
    passed: bool
    skipped: bool = False
    reason: str = ""
    details: dict[str, Any] = Field(default_factory=dict)
    elapsed_s: float = 0.0


class Evidence(BaseModel):
    """Graded evidence produced by the verification ladder."""
    model_config = ConfigDict(extra="allow")

    tier: str = "T0"                       # T0 | T1 | T2 | T3 | T4 | REJECTED
    raw_tier: str = "T0"                   # Tier before oracle strength capping
    capped_by: str | None = None           # e.g. "oracle strength tier C (cannot exceed T1)"
    passed: bool = False                   # True if candidate passed (tier >= T1)
    rungs: list[RungResult] = Field(default_factory=list)
    counterexamples: list[Any] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    feedback: str = ""
    elapsed_s: float = 0.0

    @property
    def rung_map(self) -> dict[str, RungResult]:
        return {r.rung: r for r in self.rungs}

