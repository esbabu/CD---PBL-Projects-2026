"""Data models for module mode: relaxation offers, change proposals, and module outcomes."""
from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field


class RelaxationOffer(BaseModel):
    unit: str
    blocked_aspect: str
    rewrite: str
    measured_gain: float
    error_bound_or_risk: str
    how_to_accept: dict[str, Any]


class ChangeProposal(BaseModel):
    kind: Literal["bugfix", "security_fix", "relaxation"]
    unit: str
    diff: str
    behavior_change: str
    requires_approval: bool = True


class UnitOutcome(BaseModel):
    unit: str
    unit_class: str
    status: Literal["optimized_verified", "no_improvement_found", "blocked_by_contract", "analysis_only", "error"]
    speedup: float = 1.0
    original_source: str = ""
    optimized_source: str = ""
    blocking_cause: str | None = None
    primary_reason: str = ""
    findings_for_security: list[str] = Field(default_factory=list)
    evidence_tier: str = "T0"
    must_preserve: list[str] = Field(default_factory=list)


class ModuleOutcome(BaseModel):
    units: dict[str, UnitOutcome] = Field(default_factory=dict)
    original_module: str = ""
    optimized_module: str = ""
    aggregate_diff: str = ""
    relaxation_offers: list[RelaxationOffer] = Field(default_factory=list)
    change_proposals: list[ChangeProposal] = Field(default_factory=list)
    cross_function_advice: list[str] = Field(default_factory=list)
    findings_for_security: list[str] = Field(default_factory=list)
    differential_verified: bool = False
    verified_units_count: int = 0
