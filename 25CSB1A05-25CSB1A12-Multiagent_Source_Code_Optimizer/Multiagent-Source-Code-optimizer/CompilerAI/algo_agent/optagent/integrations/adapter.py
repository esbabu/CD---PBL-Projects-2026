"""Universal integration adapter for host AI agent frameworks (LangGraph, CrewAI, MCP, custom loop)."""
from __future__ import annotations

import json
from typing import Any

from ..agent import OptimizerAgent, OptimizeRequest
from ..config import Settings


def optimize_algorithm(
    source: str,
    entry: str | None = None,
    overrides: dict[str, Any] | None = None,
    budget_max_candidates: int = 10,
    use_llm: bool = False,
) -> dict[str, Any]:
    """Execute algorithm optimization and return a JSON-serializable result.

    Suitable for use as a tool in LangGraph, CrewAI, MCP server, or custom agents.
    """
    settings = Settings()
    agent = OptimizerAgent(settings)
    req = OptimizeRequest(
        source=source,
        entry=entry,
        overrides=overrides,
        use_llm=use_llm,
    )
    result = agent.run(req)

    if result.status != "ok":
        return {
            "status": result.status,
            "message": result.message,
            "candidates": result.candidates,
            "elapsed_s": result.elapsed_s,
        }

    rep = result.report
    return {
        "status": "ok",
        "entry_point": rep.entry_point if rep else "",
        "overall_speedup": rep.overall_speedup if rep else 1.0,
        "overall_mem_ratio": rep.overall_mem_ratio if rep else 1.0,
        "evidence_tier": rep.evidence_tier if rep else "T0",
        "optimized_code": rep.optimized_source if rep else source,
        "diff": rep.diff if rep else "",
        "complexity_before": rep.complexity.before_time if rep else "",
        "complexity_after": rep.complexity.after_time if rep else "",
        "derivation": rep.complexity.derivation if rep else "",
        "bundle_paths": result.bundle_paths,
        "elapsed_s": result.elapsed_s,
    }

