"""Step 4 Proposer schemas: Candidate model."""
from __future__ import annotations

import hashlib
from typing import Any
from pydantic import BaseModel, Field


def candidate_id(source: str, proposer: str) -> str:
    h = hashlib.sha1(source.strip().encode("utf-8")).hexdigest()[:12]
    return f"{proposer}_{h}"


class Candidate(BaseModel):
    id: str
    source: str
    parent_id: str | None = None
    proposer: str = "ensemble"         # rule_engine | llm | ensemble | egraph
    transform_ids: list[str] = Field(default_factory=list)
    rationale: str = ""
    claimed_time: str = ""             # e.g. "O(n)" or "O(n log n)"
    claimed_space: str = ""            # e.g. "O(n)" or "O(1)"

    @classmethod
    def make(
        cls,
        source: str,
        proposer: str,
        parent_id: str | None = None,
        transform_ids: list[str] | None = None,
        rationale: str = "",
        claimed_time: str = "",
        claimed_space: str = "",
    ) -> "Candidate":
        cid = candidate_id(source, proposer)
        return cls(
            id=cid,
            source=source,
            parent_id=parent_id,
            proposer=proposer,
            transform_ids=transform_ids or [],
            rationale=rationale,
            claimed_time=claimed_time,
            claimed_space=claimed_space,
        )

