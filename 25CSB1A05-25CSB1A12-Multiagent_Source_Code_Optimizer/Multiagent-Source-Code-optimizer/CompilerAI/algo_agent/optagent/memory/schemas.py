"""Schemas for Step 7: Persistent rewrite memory library."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class MemoryEntry(BaseModel):
    """An entry in the verified rewrite library (positive or negative)."""
    model_config = ConfigDict(extra="allow")

    id: str
    pattern_key: str
    conditions: list[str] = Field(default_factory=list)
    original_snippet: str
    rewrite_snippet: str
    transform_ids: list[str] = Field(default_factory=list)
    speedup: float = 1.0
    mem_ratio: float = 1.0
    evidence_tier: str = "T1"
    is_positive: bool = True               # False = negative example (failed verification)
    failure_reason: str = ""
    timestamp: str = ""

