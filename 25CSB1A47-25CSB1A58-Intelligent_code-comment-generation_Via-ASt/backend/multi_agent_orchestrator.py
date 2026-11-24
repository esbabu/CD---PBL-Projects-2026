"""Coordinate 6-stage AI multi-agent orchestration for Python code analysis and security."""

import ast
import datetime
import difflib
import logging
import time
import tokenize
from io import StringIO
from typing import Any, Dict, List

from backend.ast_analyzer import analyze_code
from backend.code_analysis import build_smart_ast_explanations, _fallback_comment_code
from backend.code_improver import _definition_names, _warnings_for
from backend.optimization_agent import optimize_code
from backend.rules import summarize_quality
from backend.security_attack_agent import simulate_attacks
from backend.security_fixing_agent import fix_attack_vulnerabilities
from backend.validator import (
    check_undefined_names,
    has_added_comments,
    validate_code,
    validate_generated_code,
)

logger = logging.getLogger(__name__)


def _callable_docstring_findings(source_code: str) -> List[Dict[str, Any]]:
    findings = []

    class CallableVisitor(ast.NodeVisitor):
        def __init__(self):
            self.scope = []

        def visit_ClassDef(self, node):
            self.scope.append(node.name)
            self.generic_visit(node)
            self.scope.pop()

        def _visit_function(self, node):
            name = ".".join([*self.scope, node.name])
            if ast.get_docstring(node, clean=False) is None:
                findings.append({"function": name, "line": node.lineno})
            self.scope.append(node.name)
            self.generic_visit(node)
            self.scope.pop()

        def visit_FunctionDef(self, node):
            self._visit_function(node)

        def visit_AsyncFunctionDef(self, node):
            self._visit_function(node)

    CallableVisitor().visit(ast.parse(source_code))
    return findings


def _documentation_item_counts(source_code: str) -> tuple[int, int]:
    tree = ast.parse(source_code)
    docstring_count = sum(
        ast.get_docstring(node, clean=False) is not None
        for node in ast.walk(tree)
        if isinstance(
            node,
            (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef),
        )
    )
    comment_count = sum(
        token.type == tokenize.COMMENT
        for token in tokenize.generate_tokens(StringIO(source_code).readline)
    )
    return docstring_count, comment_count


def run_multi_agent_workflow(
    source_code: str,
    model_client: Any = None,
    full_pipeline: bool = False,
    include_docstrings: bool = False,
) -> Dict[str, Any]:
    """Run professional 6-agent collaborative orchestration workflow.

    Stages:
    1. ATLAS — Architecture Intelligence Agent
    2. FORGE — Code Engineering Agent
    3. SENTINEL — Security Intelligence Agent
    4. REMEDY — Code Remediation Agent
    5. SCRIBE — Documentation Intelligence Agent
    6. VERITY — Quality & Verification Agent
    """
    valid = validate_code(source_code)
    if valid is not True:
        raise ValueError(f"Invalid Python source code: {valid}")

    initial_warnings = _warnings_for(source_code)
    initial_quality = summarize_quality(initial_warnings)
    initial_score = initial_quality["score"]

    all_stages: List[Dict[str, Any]] = []

    # -------------------------------------------------------------
    # STAGE 1: Architect Agent
    # -------------------------------------------------------------
    t0 = time.perf_counter()
    start_iso_1 = datetime.datetime.now(datetime.timezone.utc).isoformat()
    ast_info = analyze_code(source_code)
    func_count = len(ast_info.get("functions", []))
    class_count = len(ast_info.get("classes", []))
    import_count = len(ast_info.get("imports", []))
    file_cc = ast_info.get("cyclomatic_complexity", 1)
    undefined_names = check_undefined_names(source_code)
    missing_callable_docs = _callable_docstring_findings(source_code)
    callable_count = sum(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        for node in ast.walk(ast.parse(source_code))
    )

    architect_findings = []
    if file_cc > 8:
        architect_findings.append(f"Elevated file cyclomatic complexity ({file_cc}) indicates multiple branching paths.")
    if func_count == 0:
        architect_findings.append("Module consists of flat top-level script statements without modular functional encapsulation.")
    else:
        architect_findings.append(f"Analyzed {func_count} function definition(s) and {class_count} class definition(s).")
    if undefined_names:
        undefined_labels = [
            (
                f"{item.get('name')} (line {item.get('lineno')})"
                if isinstance(item, dict)
                else str(item)
            )
            for item in undefined_names[:3]
        ]
        architect_findings.append(
            f"Identified {len(undefined_names)} potential undefined reference(s): "
            f"{', '.join(undefined_labels)}."
        )

    missing_doc_count = len(missing_callable_docs)
    if missing_doc_count > 0:
        architect_findings.append(
            f"{missing_doc_count} of {callable_count} function or method(s) lack formal docstring documentation."
        )

    plan_steps = [
        "1. ATLAS: Map AST topology and decompose the analysis plan",
        "2. FORGE: Analyze algorithmic complexity, nested loops, and memory allocation",
        "3. SENTINEL: Run safe AST static security checks",
        "4. REMEDY: Synthesize parameterized defenses and defensive sanitizers",
        "5. SCRIBE: Ground docstrings and parameter contracts in AST semantics",
        "6. VERITY: Verify non-regression, symbol preservation, and score delta",
    ]

    dur_1 = round((time.perf_counter() - t0) * 1000, 2)
    end_iso_1 = datetime.datetime.now(datetime.timezone.utc).isoformat()

    architect_result = {
        "agent": "architect_agent",
        "agent_name": "ATLAS — Architecture Intelligence Agent",
        "status": "completed",
        "action": "AST Topology, Modular Decomposition & Plan Orchestration",
        "topology": {
            "functions": func_count,
            "classes": class_count,
            "imports": import_count,
            "cyclomatic_complexity": file_cc,
            "missing_docstrings": missing_doc_count,
            "undefined_names": undefined_names,
        },
        "execution_plan": plan_steps,
        "findings": architect_findings,
        "duration_ms": dur_1,
    }

    architect_stage = {
        "stage": 1,
        "agent_id": "architect",
        "agent": "ATLAS — Architecture Intelligence Agent",
        "agent_name": "ATLAS — Architecture Intelligence Agent",
        "action": "AST Topology, Modular Decomposition & Plan Orchestration",
        "status": "completed",
        "start_time": start_iso_1,
        "end_time": end_iso_1,
        "duration_ms": dur_1,
        "findings_count": len(architect_findings),
        "findings": architect_findings,
        "details": (
            f"Decomposed module topology: {func_count} function(s), {class_count} class(es), "
            f"{import_count} import(s), CC={file_cc}. Generated 6-stage execution plan."
        ),
        "summary": f"Analyzed AST structure ({func_count} functions, CC={file_cc}) and established orchestrator context.",
        "code_modified": False,
    }
    all_stages.append(architect_stage)

    # -------------------------------------------------------------
    # STAGE 2: Code Optimizer Agent
    # -------------------------------------------------------------
    t0 = time.perf_counter()
    start_iso_2 = datetime.datetime.now(datetime.timezone.utc).isoformat()
    opt_result = optimize_code(source_code, model_client=model_client)
    dur_2 = round((time.perf_counter() - t0) * 1000, 2)
    end_iso_2 = datetime.datetime.now(datetime.timezone.utc).isoformat()

    working_code = opt_result["optimized_code"] if opt_result["optimized"] else source_code

    optimizer_stage = {
        "stage": 2,
        "agent_id": "optimizer",
        "agent": "FORGE — Code Engineering Agent",
        "agent_name": "FORGE — Code Engineering Agent",
        "action": "AST Performance & Algorithmic Complexity Analysis",
        "status": "completed",
        "start_time": start_iso_2,
        "end_time": end_iso_2,
        "duration_ms": dur_2,
        "findings_count": opt_result.get("opportunities_found", 0),
        "findings": opt_result.get("opportunities", []),
        "details": (
            f"Complexity transition: {opt_result['complexity_before']} -> {opt_result['complexity_after']}. "
            f"Estimated speedup: {opt_result['estimated_speedup']}. "
            f"Found {opt_result['opportunities_found']} optimization opportunity(ies)."
        ),
        "summary": (
            f"Optimized complexity {opt_result['complexity_before']} -> {opt_result['complexity_after']} "
            f"with estimated speedup {opt_result['estimated_speedup']}."
            if opt_result["optimized"]
            else "Algorithmic audit passed. No performance bottlenecks identified."
        ),
        "code_modified": opt_result["optimized"],
    }
    all_stages.append(optimizer_stage)

    # -------------------------------------------------------------
    # STAGE 3: SENTINEL Security Intelligence Agent
    # -------------------------------------------------------------
    t0 = time.perf_counter()
    start_iso_3 = datetime.datetime.now(datetime.timezone.utc).isoformat()
    sim_result = simulate_attacks(working_code, model_client=model_client)
    dur_3 = round((time.perf_counter() - t0) * 1000, 2)
    end_iso_3 = datetime.datetime.now(datetime.timezone.utc).isoformat()

    red_team_stage = {
        "stage": 3,
        "agent_id": "red_team",
        "agent": "SENTINEL — Security Intelligence Agent",
        "agent_name": "SENTINEL — Security Intelligence Agent",
        "action": "AST Defensive Vulnerability Probing (14 CWE Classes)",
        "status": "completed",
        "start_time": start_iso_3,
        "end_time": end_iso_3,
        "duration_ms": dur_3,
        "findings_count": sim_result["vulnerabilities_detected"],
        "findings": sim_result.get("attack_scenarios", []),
        "vulnerabilities_found": sim_result["vulnerabilities_detected"],
        "details": (
            f"Completed {sim_result['total_checks_run']} static checks. "
            f"Identified {sim_result['vulnerabilities_detected']} potential finding(s). "
            f"Static risk score: {sim_result['resilience_score']}/100."
        ),
        "summary": (
            f"Identified {sim_result['vulnerabilities_detected']} potential vulnerability sink(s) across 14 CWE checks."
            if sim_result["vulnerabilities_detected"] > 0
            else "Static defensive security audit clean. Zero vulnerability sinks detected."
        ),
        "code_modified": False,
    }
    all_stages.append(red_team_stage)

    # -------------------------------------------------------------
    # STAGE 4: REMEDY Code Remediation Agent
    # -------------------------------------------------------------
    t0 = time.perf_counter()
    start_iso_4 = datetime.datetime.now(datetime.timezone.utc).isoformat()
    fix_result = fix_attack_vulnerabilities(
        working_code,
        attack_simulation=sim_result,
        model_client=model_client,
    )
    dur_4 = round((time.perf_counter() - t0) * 1000, 2)
    end_iso_4 = datetime.datetime.now(datetime.timezone.utc).isoformat()

    post_fix_code = fix_result["fixed_code"] if fix_result["fixed"] else working_code

    blue_team_stage = {
        "stage": 4,
        "agent_id": "blue_team",
        "agent": "REMEDY — Code Remediation Agent",
        "agent_name": "REMEDY — Code Remediation Agent",
        "action": "Defensive Remediation & Parameterized Query Hardening",
        "status": "completed",
        "start_time": start_iso_4,
        "end_time": end_iso_4,
        "duration_ms": dur_4,
        "findings_count": fix_result.get("neutralized_count", 0),
        "findings": fix_result.get("defensive_controls", []),
        "details": (
            f"Addressed {fix_result.get('neutralized_count', 0)} reported finding(s). "
            f"Applied defensive controls: {', '.join(fix_result.get('defensive_controls', [])) or 'None required'}. "
            f"Post-remediation static risk score: {fix_result.get('post_fix_resilience_score', 100)}/100."
        ),
        "summary": (
            f"Synthesized patches neutralizing {fix_result.get('neutralized_count', 0)} finding(s)."
            if fix_result.get("fixed")
            else "No defensive code changes required."
        ),
        "code_modified": fix_result.get("fixed", False),
    }
    all_stages.append(blue_team_stage)

    # -------------------------------------------------------------
    # STAGE 5: Documentation Agent
    # -------------------------------------------------------------
    t0 = time.perf_counter()
    start_iso_5 = datetime.datetime.now(datetime.timezone.utc).isoformat()
    doc_code_candidate = post_fix_code
    docs_generated = 0
    doc_findings = []
    doc_validation_issues = []

    ast_post_fix = analyze_code(post_fix_code)
    missing_callable_docs = _callable_docstring_findings(post_fix_code)
    for item in missing_callable_docs:
        doc_findings.append({
            **item,
            "issue": f"Missing docstring specification in {item['function']}()",
        })

    documentation_enabled = full_pipeline or include_docstrings
    if documentation_enabled:
        synthesized_docs = _fallback_comment_code(post_fix_code, analysis=ast_post_fix)
        validation = validate_generated_code(post_fix_code, synthesized_docs)
        doc_validation_issues = validation.get("issues", [])
        added_docstrings = 0
        added_inline_comments = 0
        if (
            validation.get("is_valid")
            and _definition_names(synthesized_docs) == _definition_names(post_fix_code)
            and has_added_comments(post_fix_code, synthesized_docs)
        ):
            original_docstrings, original_comments = _documentation_item_counts(
                post_fix_code
            )
            generated_docstrings, generated_comments = _documentation_item_counts(
                synthesized_docs
            )
            added_docstrings = max(0, generated_docstrings - original_docstrings)
            added_inline_comments = max(0, generated_comments - original_comments)
            doc_code_candidate = synthesized_docs
            docs_generated = added_docstrings + added_inline_comments
            if added_inline_comments:
                doc_findings.append({
                    "issue": "Added AST-anchored inline comments",
                    "count": added_inline_comments,
                })
        else:
            logger.warning(
                "Documentation candidate rejected by validation: %s",
                "; ".join(doc_validation_issues) or "definition preservation failed",
            )

    smart_explanations = build_smart_ast_explanations(doc_code_candidate)
    dur_5 = round((time.perf_counter() - t0) * 1000, 2)
    end_iso_5 = datetime.datetime.now(datetime.timezone.utc).isoformat()

    docstring_result = {
        "agent": "documentation_agent",
        "agent_name": "SCRIBE — Documentation Intelligence Agent",
        "status": "completed",
        "action": "AST-Grounded Semantic Docstrings & Explanations",
        "missing_docstrings": len(missing_callable_docs),
        "docs_generated": docs_generated,
        "docstrings_added": added_docstrings if documentation_enabled else 0,
        "inline_comments_added": added_inline_comments if documentation_enabled else 0,
        "validation_issues": doc_validation_issues,
        "smart_explanations_count": len(smart_explanations),
        "explanations": smart_explanations,
        "duration_ms": dur_5,
    }

    docstring_stage = {
        "stage": 5,
        "agent_id": "docstring",
        "agent": "SCRIBE — Documentation Intelligence Agent",
        "agent_name": "SCRIBE — Documentation Intelligence Agent",
        "action": "AST-Grounded Semantic Docstrings & Explanations",
        "status": "completed",
        "start_time": start_iso_5,
        "end_time": end_iso_5,
        "duration_ms": dur_5,
        "findings_count": len(doc_findings),
        "findings": doc_findings,
        "details": (
            f"Analyzed docstring coverage ({len(missing_callable_docs)} missing). "
            f"Grounded {len(smart_explanations)} AST semantic explanation(s)."
        ),
        "summary": (
            f"Generated {added_docstrings if documentation_enabled else 0} docstring(s) "
            f"and {added_inline_comments if documentation_enabled else 0} inline AST comment(s); "
            f"produced {len(smart_explanations)} semantic explanation(s)."
        ),
        "code_modified": doc_code_candidate != post_fix_code,
    }
    all_stages.append(docstring_stage)

    # Determine final candidate code
    final_code = doc_code_candidate if documentation_enabled else post_fix_code

    # -------------------------------------------------------------
    # STAGE 6: Synthesis & Audit Agent
    # -------------------------------------------------------------
    t0 = time.perf_counter()
    start_iso_6 = datetime.datetime.now(datetime.timezone.utc).isoformat()
    final_warnings = _warnings_for(final_code)
    final_quality = summarize_quality(final_warnings)
    final_score = final_quality["score"]

    final_sim = simulate_attacks(final_code)
    is_resilient = final_sim["vulnerabilities_detected"] == 0
    syntax_is_valid = validate_code(final_code) is True
    defs_preserved = _definition_names(final_code) == _definition_names(source_code)
    all_passed = is_resilient and syntax_is_valid and defs_preserved
    dur_6 = round((time.perf_counter() - t0) * 1000, 2)
    end_iso_6 = datetime.datetime.now(datetime.timezone.utc).isoformat()

    verifier_result = {
        "agent": "verification_agent",
        "agent_name": "VERITY — Quality & Verification Agent",
        "status": "completed",
        "action": "AST Integrity, Security Non-Regression & Quality Audit",
        "syntax_valid": syntax_is_valid,
        "definitions_preserved": defs_preserved,
        "all_checks_passed": all_passed,
        "initial_quality_score": initial_score,
        "final_quality_score": final_score,
        "quality_delta": final_score - initial_score,
        "initial_resilience_score": sim_result["resilience_score"],
        "final_resilience_score": final_sim["resilience_score"],
        "resilience_delta": final_sim["resilience_score"] - sim_result["resilience_score"],
        "duration_ms": dur_6,
        "audit_report": {
            "code_integrity_verified": defs_preserved and syntax_is_valid,
            "security_regressions": final_sim["vulnerabilities_detected"],
            "remaining_vulnerabilities": final_sim["vulnerabilities_detected"],
            "optimizations_retained": len(opt_result.get("optimizations_applied", [])),
            "findings_remediated": fix_result.get("neutralized_count", 0),
        },
    }

    audit_stage = {
        "stage": 6,
        "agent_id": "audit",
        "agent": "VERITY — Quality & Verification Agent",
        "agent_name": "VERITY — Quality & Verification Agent",
        "action": "AST Integrity, Security Non-Regression & Quality Audit",
        "status": "completed",
        "start_time": start_iso_6,
        "end_time": end_iso_6,
        "duration_ms": dur_6,
        "findings_count": final_sim["vulnerabilities_detected"],
        "findings": final_sim.get("attack_scenarios", []),
        "details": (
            f"Final quality score: {initial_score}/100 -> {final_score}/100. "
            f"Final security resilience: {final_sim['resilience_score']}/100. "
            f"Syntax valid: {syntax_is_valid}, Definitions preserved: {defs_preserved}."
        ),
        "summary": (
            f"Integrity verified (passed={all_passed}). Score delta: {final_score - initial_score:+d}. "
            f"Resilience delta: {final_sim['resilience_score'] - sim_result['resilience_score']:+d}."
        ),
        "all_checks_passed": all_passed,
        "code_modified": False,
    }
    all_stages.append(audit_stage)

    # Generate unified diff showing complete modifications made across pipeline
    diff_lines = list(difflib.unified_diff(
        source_code.splitlines(keepends=True),
        final_code.splitlines(keepends=True),
        fromfile="original.py",
        tofile="hardened_optimized.py",
        n=3,
    ))
    diff_text = "".join(diff_lines)

    benchmark_statistics = {
        "before": {
            "quality_score": initial_score,
            "resilience_score": sim_result["resilience_score"],
            "vulnerabilities": sim_result["vulnerabilities_detected"],
            "algorithmic_complexity": opt_result.get("complexity_before", "N/A"),
            "critical_risks": sim_result.get("risk_breakdown", {}).get("critical", 0),
            "high_risks": sim_result.get("risk_breakdown", {}).get("high", 0),
        },
        "after": {
            "quality_score": final_score,
            "resilience_score": final_sim["resilience_score"],
            "vulnerabilities": final_sim["vulnerabilities_detected"],
            "algorithmic_complexity": opt_result.get("complexity_after", "N/A"),
            "critical_risks": final_sim.get("risk_breakdown", {}).get("critical", 0),
            "high_risks": final_sim.get("risk_breakdown", {}).get("high", 0),
        },
        "improvements": {
            "quality_delta": final_score - initial_score,
            "resilience_delta": final_sim["resilience_score"] - sim_result["resilience_score"],
            "findings_remediated": fix_result.get("neutralized_count", 0),
            "speedup_factor": opt_result.get("estimated_speedup", "1.0x"),
        },
    }

    # Backward compatibility: legacy timeline with 4 items for tests that strictly assert len(timeline) == 4
    legacy_timeline = [
        {
            "stage": 1,
            "agent": "AI Code Optimization Agent",
            "action": "AST Performance & Algorithmic Complexity Analysis",
            "status": "completed",
            "details": (
                f"Complexity transition: {opt_result['complexity_before']} -> {opt_result['complexity_after']}. "
                f"Estimated speedup: {opt_result['estimated_speedup']}. "
                f"Found {opt_result['opportunities_found']} optimization opportunity(ies)."
            ),
            "code_modified": opt_result["optimized"],
        },
        {
            "stage": 2,
            "agent": "Static Python Security Analyzer",
            "action": "AST-based security checks; source code is not executed",
            "status": "completed",
            "details": (
                f"Completed {sim_result['total_checks_run']} static checks. "
                f"Identified {sim_result['vulnerabilities_detected']} potential finding(s). "
                f"Static risk score: {sim_result['resilience_score']}/100."
            ),
            "vulnerabilities_found": sim_result["vulnerabilities_detected"],
        },
        {
            "stage": 3,
            "agent": "REMEDY — Code Remediation Agent",
            "action": "Defensive remediation of reported static findings",
            "status": "completed",
            "details": (
                f"Addressed {fix_result.get('neutralized_count', 0)} reported finding(s). "
                f"Applied defensive controls: {', '.join(fix_result.get('defensive_controls', [])) or 'None required'}. "
                f"Post-remediation static risk score: {fix_result.get('post_fix_resilience_score', 100)}/100."
            ),
            "code_modified": fix_result.get("fixed", False),
        },
        {
            "stage": 4,
            "agent": "AI Verification & Synthesis Agent",
            "action": "AST Integrity, Security Non-Regression & Quality Audit",
            "status": "completed",
            "details": (
                f"Final quality score: {initial_score}/100 -> {final_score}/100. "
                f"Final security resilience: {final_sim['resilience_score']}/100. "
                f"Syntax valid: {syntax_is_valid}, Definitions preserved: {defs_preserved}."
            ),
            "all_checks_passed": all_passed,
        },
    ]

    return {
        "workflow": "multi_agent_collaboration",
        "status": "completed",
        "initial_code": source_code,
        "optimized_code": opt_result["optimized_code"],
        "final_hardened_code": final_code,
        "code_changed": final_code.strip() != source_code.strip(),
        "diff": diff_text,
        "summary": {
            "initial_quality_score": initial_score,
            "final_quality_score": final_score,
            "initial_resilience_score": sim_result["resilience_score"],
            "final_resilience_score": final_sim["resilience_score"],
            "optimizations_applied": len(opt_result["optimizations_applied"]),
            "static_checks_run": sim_result["total_checks_run"],
            "findings_remediated": fix_result["neutralized_count"],
            "remaining_vulnerabilities": final_sim["vulnerabilities_detected"],
            "overall_health": (
                "No Static Findings (not a security certification)"
                if is_resilient
                else "Potential Findings Remain"
            ),
            "benchmark_statistics": benchmark_statistics,
            "stages_count": 6,
        },
        "agents": {
            "architect": architect_result,
            "optimizer": opt_result,
            "attack_simulator": sim_result,
            "red_team": sim_result,
            "security_fixer": fix_result,
            "blue_team": fix_result,
            "docstring": docstring_result,
            "verifier": verifier_result,
            "audit": verifier_result,
        },
        "stages": all_stages,
        "timeline": all_stages if full_pipeline else legacy_timeline,
    }
