"""Bounded autonomous review and refinement cycle."""

import ast
import difflib
import logging
from typing import Any, Dict, List

from backend.ast_analyzer import analyze_code
from backend.code_analysis import _fallback_comment_code
from backend.code_improver import improve_code_quality
from backend.optimization_agent import detect_optimization_opportunities, optimize_code
from backend.request_utils import undefined_name_findings
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


class ProfessorStudentOrchestrator:
    """Orchestrates an iterative feedback loop between a Student generator and a Professor evaluator."""

    def __init__(self, model_client: Any = None, max_iterations: int = 5):
        self.model_client = model_client
        self.max_iterations = max(1, min(10, int(max_iterations or 5)))

    def _grade_from_score(self, score: int) -> str:
        if score >= 95:
            return "A+"
        if score >= 88:
            return "A"
        if score >= 80:
            return "B"
        if score >= 70:
            return "C"
        if score >= 60:
            return "D"
        return "F"

    def professor_evaluate(self, code: str) -> Dict[str, Any]:
        """Review correctness, security, clarity, and style evidence."""
        valid = validate_code(code)
        if valid is not True:
            return {
                "score": 0,
                "grade": "F",
                "critique": [f"Syntax Error: {valid}"],
                "passed": False,
                "security_findings": 1,
                "findings": [{
                    "id": "SYNTAX-001",
                    "category": "Quality",
                    "severity": "Critical",
                    "title": "Syntax Error",
                    "line": 1,
                    "code_snippet": "",
                    "explanation": f"Python interpreter syntax error: {valid}",
                    "why_it_matters": "Code cannot be parsed, compiled, or executed by Python.",
                    "suggested_fix": "Fix missing colons, indentation errors, or unclosed brackets.",
                }],
                "findings_by_category": {"Security": 0, "Performance": 0, "Documentation": 0, "Quality": 1},
            }

        structured_findings: List[Dict[str, Any]] = []

        # Inspect AST structure for complexity and docstrings
        ast_data = analyze_code(code)
        warnings = list(ast_data.get("warnings", []))
        warnings.extend(undefined_name_findings(check_undefined_names(code)))

        # 1. Run static security check across 14 CWE classes
        sec_result = simulate_attacks(code, model_client=self.model_client)
        sec_findings = sec_result.get("vulnerabilities_detected", 0)

        for s in sec_result.get("attack_scenarios", []):
            structured_findings.append({
                "id": s.get("id", f"SEC-{len(structured_findings)+1:02d}"),
                "category": "Security",
                "severity": s.get("severity", "high").capitalize(),
                "title": s.get("name", "Security Vulnerability"),
                "cwe": (s.get("cwe") or "").split(":")[0],
                "line": s.get("target_line", 1),
                "code_snippet": s.get("vulnerable_code", ""),
                "explanation": s.get("simulation_trace", "Vulnerable code pattern identified."),
                "why_it_matters": s.get("impact", "Potential security exploit risk if supplied untrusted data."),
                "suggested_fix": s.get("mitigation", "Use parameterized queries, safe serializers, and input sanitization."),
            })

        # 2. Check algorithmic complexity bottlenecks
        for idx, opp in enumerate(detect_optimization_opportunities(code), start=1):
            warnings.append({
                "rule_id": "OPT001",
                "severity": "warning",
                "message": f"Algorithmic complexity issue in {opp.get('target', 'code')}: {opp.get('complexity_impact')}. {opp.get('description')}",
            })
            structured_findings.append({
                "id": f"OPT-{idx:02d}",
                "category": "Performance",
                "severity": "Medium",
                "title": f"Algorithmic Bottleneck: {opp.get('target', 'Loop/Sort')}",
                "line": opp.get("line", 1),
                "code_snippet": opp.get("target", ""),
                "explanation": opp.get("description", "Algorithmic inefficiency detected."),
                "why_it_matters": f"Degrades execution speed and scalability ({opp.get('complexity_impact', 'O(n^2)')}).",
                "suggested_fix": opp.get("recommended_fix", "Use built-in Timsort, generator expressions, or direct key iteration."),
            })

        # 3. Check cyclomatic complexity & documentation
        for fn in ast_data.get("functions", []):
            fn_name = fn.get("name", "function")
            cc = fn.get("complexity", 1)
            if cc > 8:
                warnings.append({
                    "rule_id": "COMPLEX001",
                    "severity": "warning",
                    "message": f"High cyclomatic complexity in {fn_name}() (CC={cc})",
                })
                structured_findings.append({
                    "id": f"COMP-{fn_name}",
                    "category": "Quality",
                    "severity": "Medium",
                    "title": f"High Cyclomatic Complexity: {fn_name}() (CC={cc})",
                    "line": fn.get("lineno", 1),
                    "code_snippet": f"def {fn_name}(...):",
                    "explanation": f"Function '{fn_name}' has {cc} independent execution paths.",
                    "why_it_matters": "High complexity makes code harder to test, maintain, and reason about defensively.",
                    "suggested_fix": "Decompose into smaller helper functions or simplify nested conditional branches.",
                })

        for node in ast.walk(ast.parse(code)):
            if (
                isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and ast.get_docstring(node, clean=False) is None
            ):
                warnings.append({
                    "rule_id": "DOC001",
                    "severity": "warning",
                    "message": f"Missing docstring specification in function or method {node.name}()",
                })
                structured_findings.append({
                    "id": f"DOC-{node.name}-{node.lineno}",
                    "category": "Documentation",
                    "severity": "Low",
                    "title": f"Missing Docstring: {node.name}()",
                    "line": node.lineno,
                    "code_snippet": f"def {node.name}(...):",
                    "explanation": f"Function or method '{node.name}' has no docstring defining its contract.",
                    "why_it_matters": "Lacks documentation of parameters, return semantics, and error conditions.",
                    "suggested_fix": "Add PEP-257 docstring specifying args, return values, and exceptions.",
                })

        # 4. Check undefined names & code smells
        for w in warnings:
            if w.get("rule_id") not in {"OPT001", "COMPLEX001", "DOC001"}:
                structured_findings.append({
                    "id": f"QUAL-{w.get('rule_id', 'LINT')}",
                    "category": "Quality",
                    "severity": "Medium" if w.get("severity") == "error" else "Low",
                    "title": w.get("message", "Lint finding").split(":")[0],
                    "line": w.get("line", 1),
                    "code_snippet": "",
                    "explanation": w.get("message", "Quality rule finding."),
                    "why_it_matters": "Violates clean Python coding standards or indicates potential runtime bug.",
                    "suggested_fix": "Ensure all variables are initialized before use and follow PEP 8.",
                })

        quality = summarize_quality(warnings)
        base_score = quality["score"]
        deductions = sec_findings * 25
        final_score = max(0, min(100, base_score - deductions))
        grade = self._grade_from_score(final_score)

        critiques = []
        if sec_findings > 0:
            critiques.append(
                f"Security Vulnerability: Identified {sec_findings} vulnerable sink(s). Neutralize immediately."
            )
        for w in warnings[:5]:
            critiques.append(f"{w.get('rule_id', 'Lint')}: {w.get('message')}")

        if not critiques and final_score >= 90:
            critiques.append("Exemplary code structure, clean docstrings, and robust security posture.")

        categorized_counts = {
            "Security": sum(1 for f in structured_findings if f["category"] == "Security"),
            "Performance": sum(1 for f in structured_findings if f["category"] == "Performance"),
            "Documentation": sum(1 for f in structured_findings if f["category"] == "Documentation"),
            "Quality": sum(1 for f in structured_findings if f["category"] == "Quality"),
        }

        return {
            "score": final_score,
            "grade": grade,
            "critique": critiques,
            "passed": final_score >= 90 and sec_findings == 0,
            "security_findings": sec_findings,
            "warnings_count": len(warnings),
            "findings": structured_findings,
            "findings_by_category": categorized_counts,
        }

    def student_revise(self, code: str, critique: List[str], iteration: int) -> str:
        """Student synthesizes improvements addressing the Professor's critique with safety checks."""
        candidate = code

        # 1. Remediate security sinks if flagged
        if any("Security" in c for c in critique):
            try:
                fix_res = fix_attack_vulnerabilities(candidate, model_client=self.model_client)
                if fix_res.get("fixed") and fix_res.get("fixed_code"):
                    fixed = fix_res["fixed_code"]
                    if validate_code(fixed) is True:
                        candidate = fixed
            except Exception as exc:
                logger.debug("Security fix step failed: %s", exc)

        # 2. Optimize algorithmic performance & complexity if flagged
        if any("complexity" in c.lower() for c in critique):
            try:
                opt_res = optimize_code(candidate, model_client=self.model_client)
                if opt_res.get("optimized") and opt_res.get("optimized_code"):
                    optimized = opt_res["optimized_code"]
                    if validate_code(optimized) is True:
                        candidate = optimized
            except Exception as exc:
                logger.debug("Code optimizer step skipped: %s", exc)

        # 3. Improve code quality / rules
        try:
            imp_res = improve_code_quality(candidate, model_client=self.model_client)
            if imp_res.get("improved") and imp_res.get("improved_code"):
                improved = imp_res["improved_code"]
                if validate_code(improved) is True:
                    candidate = improved
        except Exception as exc:
            logger.debug("Code improver step skipped: %s", exc)

        # 4. Add AST-grounded docstrings and inline comments where possible.
        try:
            ast_info = analyze_code(candidate)
            doc_code = _fallback_comment_code(candidate, analysis=ast_info)
            documentation_validation = validate_generated_code(candidate, doc_code)
            if (
                documentation_validation.get("is_valid")
                and has_added_comments(candidate, doc_code)
            ):
                candidate = doc_code
        except Exception as exc:
            logger.debug("AST documentation generation step skipped: %s", exc)

        return candidate

    def run(self, source_code: str) -> Dict[str, Any]:
        """Execute the continuous feedback loop with monotonic best-score rollback."""
        valid = validate_code(source_code)
        if valid is not True:
            return {
                "status": "failed",
                "error": f"Initial code contains syntax errors: {valid}",
                "iterations": [],
            }

        history = []
        current_code = source_code
        best_code = current_code
        best_eval = self.professor_evaluate(current_code)
        initial_eval = best_eval
        _resolved_all = []

        for i in range(1, self.max_iterations + 1):
            eval_res = self.professor_evaluate(current_code)

            # Determine issues resolved compared to initial evaluation
            current_ids = {f["id"] for f in eval_res.get("findings", [])}
            resolved_in_turn = [f for f in initial_eval.get("findings", []) if f["id"] not in current_ids]

            history.append({
                "iteration": i,
                "code": current_code,
                "score": eval_res["score"],
                "grade": eval_res["grade"],
                "passed": eval_res["passed"],
                "critique": eval_res["critique"],
                "findings": eval_res.get("findings", []),
                "findings_by_category": eval_res.get("findings_by_category", {}),
                "resolved_count": len(resolved_in_turn),
                "remaining_count": len(eval_res.get("findings", [])),
            })

            if eval_res["score"] >= best_eval["score"]:
                best_code = current_code
                best_eval = eval_res

            if eval_res["passed"] or i >= self.max_iterations:
                break

            revised = self.student_revise(current_code, eval_res["critique"], i)
            if revised == current_code:
                # No further automated revision possible
                break

            # Validate revised syntax before accepting into loop
            if validate_code(revised) is not True:
                logger.warning("Engineering revision generated invalid syntax; reverting to the best checkpoint.")
                break

            current_code = revised

        # Ensure we return the best approved/scoring checkpoint
        final_code = best_code
        final_eval = best_eval
        final_analysis = analyze_code(final_code)
        documented_code = _fallback_comment_code(
            final_code, analysis=final_analysis
        )
        documentation_validation = validate_generated_code(
            final_code, documented_code
        )
        if (
            documentation_validation.get("is_valid")
            and has_added_comments(final_code, documented_code)
        ):
            final_code = documented_code
            final_eval = self.professor_evaluate(final_code)

        # Final tracking of resolved vs remaining
        final_ids = {f["id"] for f in final_eval.get("findings", [])}
        final_resolved = [f for f in initial_eval.get("findings", []) if f["id"] not in final_ids]
        final_remaining = final_eval.get("findings", [])

        diff = "\n".join(
            difflib.unified_diff(
                source_code.splitlines(),
                final_code.splitlines(),
                fromfile="Initial Submission",
                tofile="Reviewer-Verified Candidate",
                lineterm="",
            )
        )

        return {
            "status": "completed",
            "iterations_count": len(history),
            "approved": final_eval["passed"],
            "initial_code": source_code,
            "final_code": final_code,
            "initial_grade": initial_eval["grade"],
            "initial_score": initial_eval["score"],
            "final_grade": final_eval["grade"],
            "final_score": final_eval["score"],
            "score_delta": final_eval["score"] - initial_eval["score"],
            "code_modified": final_code != source_code,
            "diff": diff,
            "iterations": history,
            "initial_findings": initial_eval.get("findings", []),
            "resolved_issues": final_resolved,
            "remaining_issues": final_remaining,
            "resolved_count": len(final_resolved),
            "remaining_count": len(final_remaining),
            "summary": (
                f"Reviewer Agent assessed the Engineering Agent submission over {len(history)} review cycle(s): "
                f"Final Grade {final_eval['grade']} ({final_eval['score']}/100). "
                f"Resolved {len(final_resolved)} issue(s), {len(final_remaining)} issue(s) remaining."
            ),
        }
