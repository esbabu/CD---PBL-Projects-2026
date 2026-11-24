"""Syntax Gate data models and report schemas."""
from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field


class SyntaxEdit(BaseModel):
    """A single atomic edit made during syntax repair."""
    line: int
    old: str
    new: str
    method: Literal["heuristic", "llm"]
    fixer: str
    reason: str


class SyntaxRound(BaseModel):
    """One repair round (heuristic or LLM)."""
    error: dict[str, Any]
    method: str
    edits: list[SyntaxEdit] = Field(default_factory=list)
    accepted: bool
    reject_reason: str | None = None


class SyntaxReport(BaseModel):
    """Aggregate report from the Syntax Gate."""
    ok: bool
    language: str
    rounds: list[SyntaxRound] = Field(default_factory=list)
    original_sha: str
    repaired_sha: str | None = None
    diff: str = ""
    tokens_changed: int = 0
    llm_calls: int = 0
