"""Verification, diffing, and audit tool adapters for Agentic AI Layer."""

from __future__ import annotations

import difflib
from typing import Any, Dict

from backend.ast_analyzer import analyze_code
from backend.behavioral_verifier import (
    check_remediation_behaviour_preservation,
    run_isolated_behavioral_tests,
)
from backend.code_improver import _definition_names
from backend.patch_safety import validate_patch_structural_safety
from backend.rules import summarize_quality
from backend.validator import validate_code, validate_generated_code


def verify_code_integrity_handler(args: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Verify that a candidate code string compiles cleanly, preserves definitions, and meets safety criteria."""
    original = args.get("original_code")
    candidate = args.get("candidate_code")

    if not original and context and hasattr(context, "original_code"):
        original = context.original_code
    if not candidate and context and hasattr(context, "current_code"):
        candidate = context.current_code

    if not candidate:
        raise ValueError("Missing candidate code for verification.")
    original = original or candidate

    syntax_valid = validate_code(candidate) is True
    defs_original = _definition_names(original)
    defs_candidate = _definition_names(candidate)
    defs_preserved = defs_original == defs_candidate

    gen_val = validate_generated_code(original, candidate)
    allow_executable_changes = args.get("allow_executable_changes", False)
    if not isinstance(allow_executable_changes, bool):
        raise ValueError("allow_executable_changes must be a boolean.")

    # Deep structural safety validation
    structural_safety = validate_patch_structural_safety(original, candidate)

    # Behaviour preservation validation (e.g. os.system -> subprocess.run contract)
    behaviour_preservation = check_remediation_behaviour_preservation(original, candidate)

    all_passed = (
        syntax_valid
        and defs_preserved
        and structural_safety.get("is_safe", False)
        and (gen_val.get("is_valid", False) or allow_executable_changes)
    )

    return {
        "syntax_valid": syntax_valid,
        "definitions_preserved": defs_preserved,
        "signatures_compatible": structural_safety.get("checks", {}).get("signatures_compatible", True),
        "classes_preserved": structural_safety.get("checks", {}).get("classes_preserved", True),
        "imports_valid": structural_safety.get("checks", {}).get("imports_valid", True),
        "missing_definitions": list(set(defs_original) - set(defs_candidate)),
        "added_definitions": list(set(defs_candidate) - set(defs_original)),
        "executable_code_preserved": gen_val.get("is_valid", False),
        "executable_change_allowed": allow_executable_changes,
        "structural_safety": structural_safety,
        "behaviour_preservation": behaviour_preservation,
        "behaviour_change": behaviour_preservation.get("behaviour_change", False),
        "behaviour_warnings": behaviour_preservation.get("warnings", []),
        "all_passed": all_passed,
    }


def run_isolated_behavioral_tests_handler(args: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Execute behavioral verification in a disposable, restricted subprocess sandbox."""
    candidate = args.get("candidate_code")
    test_code = args.get("test_code")
    timeout = float(args.get("timeout_seconds", 5.0))
    enabled = bool(args.get("enabled", True))

    if not candidate and context and hasattr(context, "current_code"):
        candidate = context.current_code
    if not candidate:
        raise ValueError("Missing candidate code for behavioral testing.")

    return run_isolated_behavioral_tests(
        candidate_code=candidate,
        test_code=test_code,
        timeout_seconds=timeout,
        enabled=enabled,
    )


def evaluate_quality_handler(args: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Run deterministic quality rules against the current candidate."""
    code = args.get("source_code")
    if code is None and context and hasattr(context, "current_code"):
        code = context.current_code
    if not isinstance(code, str):
        raise ValueError("No source code provided for quality evaluation.")
    findings = analyze_code(code).get("warnings", [])
    return {
        "score": summarize_quality(findings).get("score", 0),
        "findings": findings,
    }


def compute_unified_diff_handler(args: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Compute unified diff between original code and candidate code."""
    original = args.get("original_code")
    candidate = args.get("candidate_code")

    if not original and context and hasattr(context, "original_code"):
        original = context.original_code
    if not candidate and context and hasattr(context, "current_code"):
        candidate = context.current_code

    original_lines = (original or "").splitlines(keepends=True)
    candidate_lines = (candidate or "").splitlines(keepends=True)

    diff = list(
        difflib.unified_diff(
            original_lines,
            candidate_lines,
            fromfile=args.get("from_file", "original.py"),
            tofile=args.get("to_file", "candidate.py"),
            n=args.get("context_lines", 3),
        )
    )
    diff_text = "".join(diff)
    return {
        "has_changes": bool(diff_text.strip()),
        "diff": diff_text,
        "added_lines": sum(1 for line in diff if line.startswith("+") and not line.startswith("+++")),
        "removed_lines": sum(1 for line in diff if line.startswith("-") and not line.startswith("---")),
    }
