"""Unified Verification and Audit Contract for NEXUS and Specialist Swarm.

Enforces a versioned response schema (schema_version: 1) across all producers
(AuditAgent, Supervisor fallback, Runtime failure/cancellation, and deserialization).
Ensures missing keys are explicitly NOT RUN / UNKNOWN, never implicitly passed.
"""

from __future__ import annotations

import copy
import hashlib
from typing import Any, Dict, List, Literal, Optional, TypedDict

SCHEMA_VERSION = 1

AuditStatus = Literal["passed", "failed", "not_run"]
VerificationLevel = Literal["static_only", "behavioral_sandbox", "full"]


class CheckDetails(TypedDict):
    status: AuditStatus
    evidence: str
    details: str


def approval_record_for_current_code(session: Any) -> Optional[Dict[str, Any]]:
    """Return the explicit approval bound to the exact current candidate digest."""
    digest = hashlib.sha256(session.current_code.encode("utf-8")).hexdigest()
    for record in reversed(getattr(session, "approval_history", [])):
        if (
            isinstance(record, dict)
            and record.get("action") == "approve"
            and record.get("candidate_digest") == digest
        ):
            return record
    return None


class UnifiedAuditPayload(TypedDict, total=False):
    schema_version: int
    status: AuditStatus
    verification_level: VerificationLevel
    checks: Dict[str, CheckDetails]
    summary: str
    failures: List[str]
    warnings: List[str]
    static_checks: Dict[str, Any]
    behavioral_checks: Dict[str, Any]
    not_verified: List[str]
    report: str
    behaviour_change: bool
    behaviour_warnings: List[str]
    # Compatibility keys preserved for existing consumers
    passed: bool
    static_checks_passed: bool
    security_checks_passed: bool
    type_checks_passed: bool
    behavioral_tests_run: bool
    behavioral_tests_passed: bool
    semantic_equivalence_verified: bool
    human_approval_received: bool
    complete_verification: bool
    integrity: Dict[str, Any]
    structural_safety: Dict[str, Any]
    security_findings: List[Dict[str, Any]]
    security_regressions: List[Dict[str, Any]]
    type_errors: List[Dict[str, Any]]
    behavioral_results: Optional[Dict[str, Any]]
    quality: Dict[str, Any]
    diff: Dict[str, Any]
    rejection_reasons: List[str]
    acceptance_explanation: Optional[str]


def derive_overall_status(
    checks: Dict[str, CheckDetails],
    *,
    behavioral_tests_run: bool = False,
    code_changed: bool = False,
) -> AuditStatus:
    """Derive audit status from individual check statuses, never hardcoded string.

    Rules:
    - Any failed check immediately fails the overall audit.
    - Missing or not_run required checks result in 'not_run'.
    - 'passed' requires that EVERY required check explicitly passed.
    """
    for chk in checks.values():
        if chk.get("status") == "failed":
            return "failed"

    required_checks = ["syntax", "definitions", "security", "types"]
    if behavioral_tests_run:
        required_checks.append("behavior")
    if code_changed:
        required_checks.append("approval")

    for req in required_checks:
        chk = checks.get(req)
        if chk is None or chk.get("status") != "passed":
            return "not_run"

    return "passed"


def build_unified_audit(
    *,
    integrity_result: Optional[Dict[str, Any]] = None,
    security_findings: Optional[List[Dict[str, Any]]] = None,
    security_regressions: Optional[List[Dict[str, Any]]] = None,
    type_errors: Optional[List[Dict[str, Any]]] = None,
    behavioral_results: Optional[Dict[str, Any]] = None,
    is_approved: Optional[bool] = None,
    code_changed: bool = False,
    quality_result: Optional[Dict[str, Any]] = None,
    diff_data: Optional[Dict[str, Any]] = None,
    missing_tools: Optional[List[str]] = None,
    security_checked: bool = True,
    types_checked: bool = True,
    approval_record: Optional[Dict[str, Any]] = None,
    behaviour_change: Optional[bool] = None,
    behaviour_warnings: Optional[List[str]] = None,
    behaviour_preservation: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Construct a canonical versioned verification audit record from tool outputs."""
    integrity = integrity_result or {}
    sec_findings = list(security_findings or [])
    sec_regressions = list(security_regressions or [])
    t_errors = list(type_errors or [])
    b_results = behavioral_results or {}
    quality = quality_result or {}
    diff = diff_data or {}
    missing = list(missing_tools or [])

    # Behaviour preservation extraction
    b_pres = behaviour_preservation if behaviour_preservation is not None else integrity.get("behaviour_preservation", {})
    if behaviour_change is not None:
        b_change = bool(behaviour_change)
    else:
        b_change = bool(b_pres.get("behaviour_change") or integrity.get("behaviour_change", False))

    if behaviour_warnings is not None:
        b_warns = list(behaviour_warnings)
    else:
        b_warns = list(b_pres.get("warnings") or integrity.get("behaviour_warnings") or [])

    # 1. Syntax Check
    syntax_val = integrity.get("syntax_valid")
    if syntax_val is True:
        syntax_check: CheckDetails = {
            "status": "passed",
            "evidence": "AST parsed successfully without syntax errors.",
            "details": "Valid Python 3 syntax verified.",
        }
    elif syntax_val is False:
        syntax_check = {
            "status": "failed",
            "evidence": str(integrity.get("error", "AST parsing encountered syntax error.")),
            "details": "Code contains syntax violations.",
        }
    else:
        syntax_check = {
            "status": "not_run",
            "evidence": "Syntax validation was not executed.",
            "details": "Check missing or skipped.",
        }

    # 2. Definitions Check
    defs_val = integrity.get("definitions_preserved")
    if defs_val is True:
        defs_check: CheckDetails = {
            "status": "passed",
            "evidence": "All declared functions, classes, and callable signatures preserved.",
            "details": "Structural symbol integrity preserved.",
        }
    elif defs_val is False:
        dropped = integrity.get("dropped_definitions", [])
        defs_check = {
            "status": "failed",
            "evidence": f"Declared definitions dropped or signature altered: {dropped if dropped else 'Definitions modified'}",
            "details": "Symbol definition regression detected.",
        }
    else:
        defs_check = {
            "status": "not_run",
            "evidence": "Definition preservation verification was not executed.",
            "details": "Check missing or skipped.",
        }

    # 3. Security Check
    if security_checked:
        if sec_regressions:
            sec_check: CheckDetails = {
                "status": "failed",
                "evidence": f"{len(sec_regressions)} security regression(s) introduced by candidate changes.",
                "details": f"New flaws: {[r.get('name', r.get('cwe')) for r in sec_regressions]}",
            }
        elif sec_findings:
            sec_check = {
                "status": "failed",
                "evidence": f"{len(sec_findings)} unmitigated vulnerability finding(s) detected.",
                "details": f"Flaws: {[f.get('name', f.get('cwe')) for f in sec_findings]}",
            }
        else:
            sec_check = {
                "status": "passed",
                "evidence": "Zero security vulnerabilities detected across static CWE check suite.",
                "details": "Static security heuristics clean.",
            }
    else:
        sec_check = {
            "status": "not_run",
            "evidence": "Security vulnerability probing was not performed.",
            "details": "Check missing or skipped.",
        }

    # 4. Types Check
    if types_checked:
        if t_errors:
            type_check: CheckDetails = {
                "status": "failed",
                "evidence": f"{len(t_errors)} definite static type error(s) detected.",
                "details": f"Type errors: {t_errors[:3]}",
            }
        else:
            type_check = {
                "status": "passed",
                "evidence": "Zero definite static type errors identified.",
                "details": "Static type consistency verified.",
            }
    else:
        type_check = {
            "status": "not_run",
            "evidence": "Static type inference check was not performed.",
            "details": "Check missing or skipped.",
        }

    # 5. Behavior Check
    b_run = bool(b_results.get("behavioral_tests_run", False))
    b_passed = bool(b_results.get("behavioral_tests_passed", False))
    if b_run:
        if b_passed:
            behavior_check: CheckDetails = {
                "status": "passed",
                "evidence": "All behavioral assertions passed in isolated disposable sandbox.",
                "details": str(b_results.get("summary", "Sandbox assertions passed.")),
            }
        else:
            behavior_check = {
                "status": "failed",
                "evidence": str(b_results.get("error", "Behavioral sandbox test suite failed.")),
                "details": "Test assertions did not pass in sandbox.",
            }
    else:
        behavior_check = {
            "status": "not_run",
            "evidence": "Behavioral testing skipped (static analysis mode).",
            "details": "Runtime execution sandbox was not run.",
        }

    # 6. Approval Check
    if not code_changed:
        approval_check: CheckDetails = {
            "status": "passed",
            "evidence": "Read-only inspection; operator approval not required for unmodified code.",
            "details": "No code modifications proposed.",
        }
    elif is_approved is True:
        evidence = "Operator approved candidate code modification."
        details: Any = "Approval granted."
        if approval_record:
            approver = approval_record.get("approver", "operator")
            ts = approval_record.get("timestamp", "")
            digest = approval_record.get("candidate_digest", "")
            evidence = f"Approved by {approver} at {ts}" + (f" for candidate {digest[:12]}." if digest else ".")
            details = approval_record
        approval_check = {
            "status": "passed",
            "evidence": evidence,
            "details": details,
        }
    elif is_approved is False:
        evidence = "Operator rejected candidate code modification."
        details = "Approval rejected."
        if approval_record:
            approver = approval_record.get("approver", "operator")
            ts = approval_record.get("timestamp", "")
            evidence = f"Rejected by {approver} at {ts}."
            details = approval_record
        approval_check = {
            "status": "failed",
            "evidence": evidence,
            "details": details,
        }
    else:
        approval_check = {
            "status": "not_run",
            "evidence": "Awaiting explicit operator approval.",
            "details": "Pending operator review.",
        }

    checks: Dict[str, CheckDetails] = {
        "syntax": syntax_check,
        "definitions": defs_check,
        "security": sec_check,
        "types": type_check,
        "behavior": behavior_check,
        "approval": approval_check,
    }

    # Derive overall status
    overall_status = derive_overall_status(
        checks,
        behavioral_tests_run=b_run,
        code_changed=code_changed,
    )

    # Verification level
    if b_run and b_passed and overall_status == "passed":
        verification_level: VerificationLevel = "full"
    elif b_run:
        verification_level = "behavioral_sandbox"
    else:
        verification_level = "static_only"

    # Collect failures and warnings
    failures = [
        f"{name.upper()}: {chk['evidence']}"
        for name, chk in checks.items()
        if chk["status"] == "failed"
    ]
    if missing:
        failures.extend([f"TOOL: Required verification tool failed or missing: {t}" for t in missing])
        if overall_status == "passed":
            overall_status = "failed"

    warnings = [
        f"{name.upper()}: {chk['evidence']}"
        for name, chk in checks.items()
        if chk["status"] == "not_run" and name != "behavior"
    ]
    for bw in b_warns:
        warning_msg = f"BEHAVIOUR: {bw}"
        if warning_msg not in warnings:
            warnings.append(warning_msg)
    if b_change and not b_warns:
        warnings.append("BEHAVIOUR: Remediation modifies runtime behaviour or return contract.")

    static_passed = bool(
        syntax_check["status"] == "passed"
        and defs_check["status"] == "passed"
        and sec_check["status"] == "passed"
        and type_check["status"] == "passed"
    )

    rejection_reasons = list(failures)
    acceptance_explanation = (
        f"Candidate verified and accepted ({verification_level.upper().replace('_', ' ')}): "
        f"syntax valid, definitions preserved, zero regressions, and "
        f"{'behavioral sandbox tests passed' if b_run else 'static verification satisfied (STATIC ONLY)'}."
        if overall_status == "passed"
        else None
    )

    summary = (
        f"Independent verification: {overall_status.upper()}. "
        f"Level: {verification_level.upper().replace('_', ' ')}. "
        f"Syntax: {syntax_check['status']}, "
        f"Definitions: {defs_check['status']}, "
        f"Security: {sec_check['status']}, "
        f"Types: {type_check['status']}, "
        f"Behavior: {behavior_check['status']}, "
        f"Approval: {approval_check['status']}."
    )
    if b_change:
        warn_text = "; ".join(b_warns) if b_warns else "Remediation changes exception/return behavior"
        summary += f" [WARNING: Behaviour contract altered: {warn_text}]"

    static_checks: Dict[str, Any] = {
        "status": "passed" if static_passed else "failed",
        "passed": static_passed,
        "syntax": syntax_check["status"],
        "definitions": defs_check["status"],
        "security": sec_check["status"],
        "types": type_check["status"],
        "details": {
            "syntax": syntax_check,
            "definitions": defs_check,
            "security": sec_check,
            "types": type_check,
        },
    }

    behavioral_checks: Dict[str, Any] = {
        "status": behavior_check["status"],
        "run": b_run,
        "passed": b_passed if b_run else False,
        "details": behavior_check,
        "behaviour_change_detected": b_change,
        "behaviour_warnings": b_warns,
        "summary": behavior_check["evidence"],
    }

    not_verified: List[str] = []
    if not b_run:
        not_verified.append("Runtime behavioural assertions (static analysis mode; sandbox execution skipped)")
    if b_change:
        not_verified.append(
            f"Behavioural equivalence: remediation altered return/exception contract ({'; '.join(b_warns) if b_warns else 'contract modified'})"
        )
    if code_changed and not (is_approved is True or approval_record):
        not_verified.append("Human operator approval for proposed code changes")
    if syntax_check["status"] == "not_run":
        not_verified.append("Syntax validation was not executed")
    if defs_check["status"] == "not_run":
        not_verified.append("Definition preservation was not executed")
    if sec_check["status"] == "not_run":
        not_verified.append("Security vulnerability probing was not executed")
    if type_check["status"] == "not_run":
        not_verified.append("Static type inference was not executed")
    if not not_verified:
        not_verified.append("Dynamic execution side-effects outside sandboxed test boundaries")

    report_lines = [
        "=== VERITY VERIFICATION REPORT ===",
        "",
        "1. STATIC CHECKS PASSED:" if static_passed else "1. STATIC CHECKS:",
        f"  - Syntax: {syntax_check['status'].upper()} ({syntax_check['evidence']})",
        f"  - Definitions: {defs_check['status'].upper()} ({defs_check['evidence']})",
        f"  - Security: {sec_check['status'].upper()} ({sec_check['evidence']})",
        f"  - Types: {type_check['status'].upper()} ({type_check['evidence']})",
        "",
        "2. BEHAVIOURAL CHECKS:",
    ]
    if b_run:
        report_lines.append(f"  - Status: RUN ({behavior_check['status'].upper()})")
        report_lines.append(f"  - Evidence: {behavior_check['evidence']}")
    else:
        report_lines.append("  - Status: NOT RUN")
        report_lines.append(f"  - Evidence: {behavior_check['evidence']}")
    if b_change:
        report_lines.append("  - WARNING: Behaviour contract alterations detected:")
        for bw in b_warns:
            report_lines.append(f"    * {bw}")

    report_lines.append("")
    report_lines.append("3. WHAT WAS NOT VERIFIED:")
    for nv in not_verified:
        report_lines.append(f"  - {nv}")

    report = "\n".join(report_lines)

    return {
        "schema_version": SCHEMA_VERSION,
        "status": overall_status,
        "verification_level": verification_level,
        "checks": checks,
        "summary": summary,
        "failures": failures,
        "warnings": warnings,
        "static_checks": static_checks,
        "behavioral_checks": behavioral_checks,
        "not_verified": not_verified,
        "report": report,
        "behaviour_change": b_change,
        "behaviour_warnings": b_warns,
        # Legacy compatibility keys
        "passed": overall_status == "passed",
        "static_checks_passed": static_passed,
        "security_checks_passed": sec_check["status"] == "passed",
        "type_checks_passed": type_check["status"] == "passed",
        "behavioral_tests_run": b_run,
        "behavioral_tests_passed": b_passed,
        "semantic_equivalence_verified": bool(integrity.get("executable_code_preserved", False)),
        "human_approval_received": bool(is_approved),
        "complete_verification": verification_level == "full",
        "integrity": integrity,
        "structural_safety": integrity.get("structural_safety", {}),
        "security_findings": sec_findings,
        "security_regressions": sec_regressions,
        "type_errors": t_errors,
        "behavioral_results": b_results if b_run else None,
        "quality": quality,
        "diff": diff,
        "rejection_reasons": rejection_reasons,
        "acceptance_explanation": acceptance_explanation,
    }


def create_not_run_audit(
    reason: str = "Verification was not executed.",
    *,
    session: Optional[Any] = None,
) -> Dict[str, Any]:
    """Return a schema_version 1 audit record explicitly stating the audit did not run."""
    checks: Dict[str, CheckDetails] = {
        "syntax": {"status": "not_run", "evidence": "Not run", "details": reason},
        "definitions": {"status": "not_run", "evidence": "Not run", "details": reason},
        "security": {"status": "not_run", "evidence": "Not run", "details": reason},
        "types": {"status": "not_run", "evidence": "Not run", "details": reason},
        "behavior": {"status": "not_run", "evidence": "Not run", "details": reason},
        "approval": {"status": "not_run", "evidence": "Not run", "details": reason},
    }
    static_checks = {
        "status": "not_run",
        "passed": False,
        "syntax": "not_run",
        "definitions": "not_run",
        "security": "not_run",
        "types": "not_run",
        "details": checks,
    }
    behavioral_checks = {
        "status": "not_run",
        "run": False,
        "passed": False,
        "details": checks["behavior"],
        "behaviour_change_detected": False,
        "behaviour_warnings": [],
        "summary": "Runtime execution sandbox was not run.",
    }
    not_verified = [
        "All static checks (syntax, definitions, security, types)",
        "Runtime behavioral execution assertions",
        "Operator approval verification",
    ]
    report = "\n".join([
        "=== VERITY VERIFICATION REPORT ===",
        "",
        "1. STATIC CHECKS:",
        "  - Status: NOT RUN",
        "",
        "2. BEHAVIOURAL CHECKS:",
        "  - Status: NOT RUN",
        f"  - Reason: {reason}",
        "",
        "3. WHAT WAS NOT VERIFIED:",
        "  - All checks (audit was not executed)",
    ])
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "not_run",
        "verification_level": "static_only",
        "checks": checks,
        "summary": f"Independent verification: NOT RUN. {reason}",
        "failures": [],
        "warnings": [reason],
        "static_checks": static_checks,
        "behavioral_checks": behavioral_checks,
        "not_verified": not_verified,
        "report": report,
        "behaviour_change": False,
        "behaviour_warnings": [],
        "passed": False,
        "static_checks_passed": False,
        "security_checks_passed": False,
        "type_checks_passed": False,
        "behavioral_tests_run": False,
        "behavioral_tests_passed": False,
        "semantic_equivalence_verified": False,
        "human_approval_received": False,
        "complete_verification": False,
        "integrity": {},
        "structural_safety": {},
        "security_findings": [],
        "security_regressions": [],
        "type_errors": [],
        "behavioral_results": None,
        "quality": {},
        "diff": {},
        "rejection_reasons": [reason],
        "acceptance_explanation": None,
    }


def create_failed_audit(
    reason: str,
    *,
    session: Optional[Any] = None,
) -> Dict[str, Any]:
    """Return a schema_version 1 audit record explicitly representing a failed workflow/audit."""
    checks: Dict[str, CheckDetails] = {
        "syntax": {"status": "failed", "evidence": reason, "details": "Execution failure"},
        "definitions": {"status": "not_run", "evidence": "Aborted due to failure", "details": reason},
        "security": {"status": "not_run", "evidence": "Aborted due to failure", "details": reason},
        "types": {"status": "not_run", "evidence": "Aborted due to failure", "details": reason},
        "behavior": {"status": "not_run", "evidence": "Aborted due to failure", "details": reason},
        "approval": {"status": "not_run", "evidence": "Aborted due to failure", "details": reason},
    }
    static_checks = {
        "status": "failed",
        "passed": False,
        "syntax": "failed",
        "definitions": "not_run",
        "security": "not_run",
        "types": "not_run",
        "details": checks,
    }
    behavioral_checks = {
        "status": "not_run",
        "run": False,
        "passed": False,
        "details": checks["behavior"],
        "behaviour_change_detected": False,
        "behaviour_warnings": [],
        "summary": "Runtime execution sandbox was not run due to prior failure.",
    }
    not_verified = [
        "Checks aborted due to failure: " + reason,
    ]
    report = "\n".join([
        "=== VERITY VERIFICATION REPORT ===",
        "",
        "1. STATIC CHECKS:",
        f"  - Status: FAILED ({reason})",
        "",
        "2. BEHAVIOURAL CHECKS:",
        "  - Status: NOT RUN (aborted)",
        "",
        "3. WHAT WAS NOT VERIFIED:",
        f"  - Aborted due to failure: {reason}",
    ])
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "failed",
        "verification_level": "static_only",
        "checks": checks,
        "summary": f"Independent verification: FAILED. {reason}",
        "failures": [reason],
        "warnings": [],
        "static_checks": static_checks,
        "behavioral_checks": behavioral_checks,
        "not_verified": not_verified,
        "report": report,
        "behaviour_change": False,
        "behaviour_warnings": [],
        "passed": False,
        "static_checks_passed": False,
        "security_checks_passed": False,
        "type_checks_passed": False,
        "behavioral_tests_run": False,
        "behavioral_tests_passed": False,
        "semantic_equivalence_verified": False,
        "human_approval_received": False,
        "complete_verification": False,
        "integrity": {},
        "structural_safety": {},
        "security_findings": [],
        "security_regressions": [],
        "type_errors": [],
        "behavioral_results": None,
        "quality": {},
        "diff": {},
        "rejection_reasons": [reason],
        "acceptance_explanation": None,
    }


def migrate_legacy_audit(raw: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Safely migrate legacy or partial audit payloads into schema_version 1.

    Rule: Missing keys are NOT RUN/UNKNOWN, NEVER implicitly true.
    Do not use value !== false to determine a pass.
    """
    if not raw or not isinstance(raw, dict):
        return create_not_run_audit("No audit payload recorded.")

    # Already valid schema_version 1
    if raw.get("schema_version") == SCHEMA_VERSION and isinstance(raw.get("checks"), dict):
        checks = raw["checks"]
        required = ["syntax", "definitions", "security", "types", "behavior", "approval"]
        if all(k in checks and isinstance(checks[k], dict) and "status" in checks[k] for k in required):
            copy_audit = copy.deepcopy(raw)
            # Re-derive status to protect against inconsistent serialized status
            b_run = bool(copy_audit.get("behavioral_tests_run", False))
            c_changed = bool(copy_audit.get("code_changed", False))
            copy_audit["status"] = derive_overall_status(
                copy_audit["checks"],
                behavioral_tests_run=b_run,
                code_changed=c_changed,
            )
            copy_audit["passed"] = copy_audit["status"] == "passed"
            if "static_checks" not in copy_audit:
                copy_audit["static_checks"] = {
                    "status": "passed" if copy_audit.get("static_checks_passed") else "failed",
                    "passed": bool(copy_audit.get("static_checks_passed")),
                    "syntax": checks.get("syntax", {}).get("status", "not_run"),
                    "definitions": checks.get("definitions", {}).get("status", "not_run"),
                    "security": checks.get("security", {}).get("status", "not_run"),
                    "types": checks.get("types", {}).get("status", "not_run"),
                    "details": checks,
                }
            if "behavioral_checks" not in copy_audit:
                copy_audit["behavioral_checks"] = {
                    "status": checks.get("behavior", {}).get("status", "not_run"),
                    "run": b_run,
                    "passed": bool(copy_audit.get("behavioral_tests_passed")),
                    "details": checks.get("behavior", {}),
                    "behaviour_change_detected": bool(copy_audit.get("behaviour_change", False)),
                    "behaviour_warnings": list(copy_audit.get("behaviour_warnings", [])),
                    "summary": checks.get("behavior", {}).get("evidence", ""),
                }
            if "not_verified" not in copy_audit:
                copy_audit["not_verified"] = list(copy_audit.get("warnings", []))
            if "report" not in copy_audit:
                copy_audit["report"] = copy_audit.get("summary", "")
            if "behaviour_change" not in copy_audit:
                copy_audit["behaviour_change"] = False
            if "behaviour_warnings" not in copy_audit:
                copy_audit["behaviour_warnings"] = []
            return copy_audit

    # Legacy translation
    integrity = raw.get("integrity") if isinstance(raw.get("integrity"), dict) else {}
    sec_findings = raw.get("security_findings") if isinstance(raw.get("security_findings"), list) else None
    sec_regressions = raw.get("security_regressions") if isinstance(raw.get("security_regressions"), list) else None
    type_errors = raw.get("type_errors") if isinstance(raw.get("type_errors"), list) else None
    b_results = raw.get("behavioral_results") if isinstance(raw.get("behavioral_results"), dict) else None

    # Determine what was actually checked in legacy payload
    syntax_valid = integrity.get("syntax_valid") if "syntax_valid" in integrity else raw.get("syntax_valid")
    definitions_preserved = (
        integrity.get("definitions_preserved")
        if "definitions_preserved" in integrity
        else raw.get("definitions_preserved")
    )

    security_checked = (
        "security_checks_passed" in raw
        or sec_findings is not None
        or sec_regressions is not None
    )
    types_checked = "type_checks_passed" in raw or type_errors is not None

    b_run = bool(raw.get("behavioral_tests_run", False))
    b_passed = bool(raw.get("behavioral_tests_passed", False))
    if b_results is None and b_run:
        b_results = {"behavioral_tests_run": b_run, "behavioral_tests_passed": b_passed}

    human_approval = raw.get("human_approval_received")

    return build_unified_audit(
        integrity_result={
            "syntax_valid": syntax_valid,
            "definitions_preserved": definitions_preserved,
            "executable_code_preserved": raw.get("semantic_equivalence_verified", False),
        },
        security_findings=sec_findings or [],
        security_regressions=sec_regressions or [],
        type_errors=type_errors or [],
        behavioral_results=b_results,
        is_approved=human_approval,
        code_changed=bool(raw.get("code_changed", False)),
        quality_result=raw.get("quality") or {},
        diff_data=raw.get("diff") or {},
        missing_tools=raw.get("missing_or_failed_tools") or [],
        security_checked=security_checked,
        types_checked=types_checked,
    )
