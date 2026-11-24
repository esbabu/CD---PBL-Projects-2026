"""Algorithmic and performance optimization tool adapters for Agentic AI Layer."""

from __future__ import annotations

from typing import Any, Dict

from backend.optimization_agent import (
    detect_optimization_opportunities,
    optimize_code,
)


def _resolve_code(args: Dict[str, Any], context: Any) -> str:
    code = args.get("source_code")
    if code is not None and isinstance(code, str):
        return code
    if context and hasattr(context, "current_code"):
        return context.current_code
    raise ValueError("No source code provided in arguments or execution context.")


def detect_optimization_targets_handler(args: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Scan source code for algorithmic bottlenecks (e.g. quadratic loops, eager allocations)."""
    code = _resolve_code(args, context)
    opportunities = detect_optimization_opportunities(code)
    return {
        "opportunities_count": len(opportunities),
        "opportunities": opportunities,
    }


def synthesize_optimization_handler(args: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Propose algorithmic optimizations and complexity improvements with AST validation."""
    code = _resolve_code(args, context)
    model_client = getattr(context, "model_client", None) if context else None
    result = optimize_code(code, model_client=model_client)
    mode = result.get("mode", "deterministic_ast")
    model_configured = bool(
        model_client is not None and getattr(model_client, "chat", None)
    )
    return {
        "optimized": result.get("optimized", False),
        "optimized_code": result.get("optimized_code", code),
        "complexity_before": result.get("complexity_before", "N/A"),
        "complexity_after": result.get("complexity_after", "N/A"),
        "estimated_speedup": result.get("estimated_speedup", "1.0x"),
        "optimizations_applied": result.get("optimizations_applied", []),
        "patches": result.get("patches", []),
        "diff": result.get("diff", ""),
        "execution_mode": "model" if mode == "ai" else "deterministic",
        "fallback_reason": (
            None
            if mode == "ai"
            else "model_candidate_unavailable_or_rejected"
            if model_configured
            else "model_provider_unavailable"
        ),
    }
