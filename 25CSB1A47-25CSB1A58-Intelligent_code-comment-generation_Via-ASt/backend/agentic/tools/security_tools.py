"""Security probing, hardening, and guardrail tool adapters for Agentic AI Layer."""

from __future__ import annotations

from typing import Any, Dict

from backend.attack_guard import detect_attack
from backend.security_attack_agent import simulate_attacks
from backend.security_fixing_agent import fix_attack_vulnerabilities


def _resolve_code(args: Dict[str, Any], context: Any) -> str:
    code = args.get("source_code")
    if code is not None and isinstance(code, str):
        return code
    if context and hasattr(context, "current_code"):
        return context.current_code
    raise ValueError("No source code provided in arguments or execution context.")


def probe_security_vulnerabilities_handler(args: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Audit Python source code statically for 7 CWE vulnerability classes without code execution."""
    code = _resolve_code(args, context)
    simulation = simulate_attacks(code)
    return {
        "vulnerabilities_detected": simulation.get("vulnerabilities_detected", 0),
        "resilience_score": simulation.get("resilience_score", 100),
        "total_checks_run": simulation.get("total_checks_run", 0),
        "scenarios": simulation.get("attack_scenarios", []),
        "risk_breakdown": simulation.get("risk_breakdown", {}),
    }


def synthesize_defensive_patch_handler(args: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Synthesize hardened code remediating detected static security findings."""
    code = _resolve_code(args, context)
    findings = args.get("findings", [])
    if not isinstance(findings, list) or not all(
        isinstance(item, dict) for item in findings
    ):
        raise ValueError("findings must be a list of structured finding objects.")
    model_client = getattr(context, "model_client", None) if context else None
    result = fix_attack_vulnerabilities(code, model_client=model_client)
    mode = result.get("mode", "deterministic_ast")
    model_configured = bool(
        model_client is not None and getattr(model_client, "chat", None)
    )
    return {
        "fixed": result.get("fixed", False),
        "fixed_code": result.get("fixed_code", code),
        "neutralized_count": result.get("neutralized_count", 0),
        "remaining_count": result.get("remaining_count", 0),
        "defensive_controls": result.get("defensive_controls", []),
        "post_fix_resilience_score": result.get("post_fix_resilience_score", 100),
        "patches": result.get("patches", []),
        "diff": result.get("diff", ""),
        "reported_finding_ids": [
            item.get("finding_id") for item in findings if item.get("finding_id")
        ],
        "reported_findings_count": len(findings),
        "execution_mode": "model" if mode == "ai" else "deterministic",
        "fallback_reason": (
            None
            if mode == "ai" or result.get("status") == "already_secure"
            else "model_candidate_unavailable_or_rejected"
            if model_configured
            else "model_provider_unavailable"
        ),
    }


def evaluate_attack_guardrail_handler(args: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Test text or source code against deterministic prompt-injection and data exfiltration guards."""
    text = args.get("text") or _resolve_code(args, context)
    content_type = args.get("content_type", "prompt")
    scan = detect_attack(text, content_type=content_type)
    return {
        "detected": scan.get("detected", False),
        "decision": scan.get("decision", "allow"),
        "severity": scan.get("severity", "none"),
        "categories": scan.get("categories", []),
        "reasons": scan.get("reasons", []),
    }
