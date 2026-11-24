"""Bounded AI-driven code-quality improvement with static validation."""

import ast
import logging
from collections import Counter

from backend.assistant import (
    _contains_prompt_injection,
    _contains_unsafe_execution,
    _sanitize_model_text,
)
from backend.ast_analyzer import analyze_code
from backend.attack_guard import detect_attack
from backend.request_utils import undefined_name_findings
from backend import model_provider
from backend.rules import summarize_quality
from backend.validator import check_undefined_names, validate_code

MAX_IMPROVEMENT_ITERATIONS = 3
logger = logging.getLogger(__name__)


def _warnings_for(source_code):
    warnings = analyze_code(source_code)["warnings"]
    warnings.extend(undefined_name_findings(check_undefined_names(source_code)))
    return warnings


def _security_finding_counts(warnings):
    """Count security findings by rule and message, ignoring line shifts."""
    return Counter(
        (warning.get("rule_id"), warning.get("message"))
        for warning in warnings
        if str(warning.get("rule_id", "")).startswith("SEC")
    )


def _definition_names(source_code):
    tree = ast.parse(source_code)
    return sorted(
        (type(node).__name__, node.name)
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    )


def _model_source(response):
    choices = getattr(response, "choices", None)
    if not choices:
        raise ValueError("The AI model returned no code candidate.")
    message = getattr(choices[0], "message", None)
    content = getattr(message, "content", None)
    candidate = _sanitize_model_text(content)
    if _contains_prompt_injection(candidate) or _contains_unsafe_execution(candidate):
        detection = detect_attack(candidate)
        logger.warning(
            "Rejected AI improvement output categories=%s",
            ",".join(detection["categories"]) or "unsafe_execution",
        )
        raise ValueError(
            "The model output contained prompt-injection or unsafe execution content and was rejected."
        )
    if candidate.startswith("```"):
        lines = candidate.splitlines()
        if len(lines) < 3 or not lines[-1].strip().startswith("```"):
            raise ValueError("The AI model returned an incomplete code block.")
        candidate = "\n".join(lines[1:-1])
    return candidate.strip()


def improve_code_quality(source_code, model_client):
    """Run up to three measurable improvement iterations without executing code."""
    current_code = source_code
    current_warnings = _warnings_for(current_code)
    initial_summary = summarize_quality(current_warnings)
    initial_score = initial_summary["score"]
    current_score = initial_score
    iterations = 0
    last_rejection = None

    if current_score == 100:
        return {
            "status": "already_at_target",
            "improved": False,
            "code": source_code,
            "initial_score": initial_score,
            "final_score": current_score,
            "iterations": 0,
            "warnings": current_warnings,
            "reached_target": True,
        }

    if not model_client or not getattr(model_client, "chat", None):
        return {
            "status": "no_client",
            "improved": False,
            "code": source_code,
            "initial_score": initial_score,
            "final_score": initial_score,
            "iterations": 0,
            "warnings": current_warnings,
            "reached_target": False,
            "rejection_reason": "AI model client is not configured or unavailable.",
        }

    for _ in range(MAX_IMPROVEMENT_ITERATIONS):
        response = model_client.chat.completions.create(
            model=model_provider.MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a conservative Python code-quality improvement agent. "
                        "Address the supplied static-analysis findings with the smallest "
                        "reasonable changes. Preserve intended behavior, do not remove "
                        "checks or hide findings, do not add new dependencies, and never "
                        "execute the source. Return the complete revised Python source "
                        "only, with no markdown or commentary."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Current heuristic static-quality score: {current_score}/100\n"
                        f"Findings: {current_warnings}\n\n"
                        f"Python source:\n{current_code}"
                    ),
                },
            ],
            max_tokens=6000,
            temperature=0.1,
            extra_body=model_provider.provider_extra_body(),
        )
        try:
            candidate = _model_source(response)
        except ValueError as exc:
            last_rejection = str(exc)
            break
        if current_code.endswith(("\n", "\r")) and not candidate.endswith(("\n", "\r")):
            candidate += "\n"
        iterations += 1
        valid = validate_code(candidate)
        if valid is not True:
            last_rejection = (
                f"Candidate rejected because it has invalid Python syntax: {valid}"
            )
            break

        if _definition_names(candidate) != _definition_names(source_code):
            last_rejection = "Candidate rejected because it removed, renamed, or added a function or class."
            break

        current_attack_categories = set(
            detect_attack(current_code, content_type="code")["categories"]
        )
        candidate_attack_categories = set(
            detect_attack(candidate, content_type="code")["categories"]
        )
        if candidate_attack_categories - current_attack_categories:
            logger.warning(
                "Rejected AI improvement candidate with new security categories=%s",
                ",".join(
                    sorted(candidate_attack_categories - current_attack_categories)
                ),
            )
            last_rejection = (
                "Candidate rejected because it introduced additional security findings "
                "or a new security risk."
            )
            break

        candidate_warnings = _warnings_for(candidate)
        candidate_summary = summarize_quality(candidate_warnings)
        candidate_score = candidate_summary["score"]
        previous_security_findings = _security_finding_counts(current_warnings)
        candidate_security_findings = _security_finding_counts(candidate_warnings)
        if candidate_security_findings - previous_security_findings:
            last_rejection = (
                "Candidate rejected because it introduced additional security findings."
            )
            break
        if candidate_score <= current_score:
            last_rejection = (
                "Candidate rejected because its measured quality score did not improve."
            )
            break

        current_code = candidate
        current_warnings = candidate_warnings
        current_score = candidate_score
        if current_score == 100:
            break

    return {
        "status": "improved" if current_score > initial_score else "no_improvement",
        "improved": current_score > initial_score,
        "code": current_code,
        "initial_score": initial_score,
        "final_score": current_score,
        "iterations": iterations,
        "warnings": current_warnings,
        "reached_target": current_score == 100,
        "rejection_reason": last_rejection,
    }
