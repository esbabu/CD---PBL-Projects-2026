"""Comprehensive Project Health and Quality Audit Report Generator.

Consolidates all project quality, security, and architectural dimensions into a unified report:
1. Code Quality score & breakdown
2. Security findings & resilience score
3. Test suite & coverage status
4. Cyclomatic complexity distribution
5. Dependency health (circular imports, unused imports)
6. Documentation coverage (functions, classes, modules)
7. Maintainability Index (MI) & rating
8. Verification & integrity status
"""

from __future__ import annotations

from typing import Any, Dict

from backend.project.analyzer import ProjectAnalyzer
from backend.project.code_intelligence import ProjectCodeIntelligence
from backend.project.engineering_tools import EngineeringToolsRunner
from backend.project.workspace import ProjectWorkspace


class ProjectHealthReporter:
    """Consolidates multi-file analysis into structured health metrics and downloadable reports."""

    def __init__(self, workspace: ProjectWorkspace) -> None:
        self.workspace = workspace
        self.analyzer = ProjectAnalyzer(workspace)
        self.intelligence = ProjectCodeIntelligence(workspace)
        self.tools_runner = EngineeringToolsRunner(workspace)

    def generate_health_report(self, run_tests: bool = False) -> Dict[str, Any]:
        """Generate structured project health report across all eight dimensions."""
        # 1. Code Quality & AST Analysis
        quality_res = self.intelligence.analyze_all_files()

        # 2. Architecture & Dependencies
        arch = self.analyzer.generate_project_architecture_report()
        deps = arch["dependencies"]

        # 3. Complexity & Maintainability & Documentation
        metrics = self.intelligence.calculate_project_metrics()

        # 4. Dead Code & Duplicates
        dead_code = self.intelligence.detect_dead_code()
        duplicates = self.intelligence.detect_cross_file_duplicates()

        # 5. Security & Sinks
        security_findings = []
        for file_p, f_res in quality_res["findings_by_file"].items():
            for s in f_res.get("security_problems", []):
                security_findings.append({**s, "file_path": file_p})

        # 6. Optional Test Execution
        test_results = self.tools_runner.run_pytest() if run_tests else {
            "tool": "pytest",
            "status": "not_run",
            "passed": None,
            "message": "Automated tests not executed (run_tests=False).",
        }

        # 7. Overall Health Score Calculation (weighted average)
        quality_score = quality_res["overall_quality_score"]
        sec_penalty = min(50, len(security_findings) * 10)
        circ_penalty = 20 if deps["has_circular_dependencies"] else 0
        doc_factor = metrics["documentation_coverage"]["overall_percentage"] * 0.2
        mi_factor = metrics["maintainability_index"] * 0.3

        composite_health_score = round(
            max(0.0, min(100.0, (quality_score * 0.5) + doc_factor + mi_factor - sec_penalty - circ_penalty)), 1
        )

        overall_grade = (
            "A" if composite_health_score >= 85
            else "B" if composite_health_score >= 70
            else "C" if composite_health_score >= 55
            else "D" if composite_health_score >= 40
            else "F"
        )

        return {
            "composite_health_score": composite_health_score,
            "overall_grade": overall_grade,
            "code_quality": {
                "score": quality_score,
                "blockers_present": quality_res["blockers_present"],
                "total_findings": quality_res["total_findings"],
                "summary": quality_res["summary"],
            },
            "security": {
                "findings_count": len(security_findings),
                "findings": security_findings,
                "has_critical_vulnerabilities": any(s.get("severity") in {"high", "critical"} for s in security_findings),
            },
            "test_status": test_results,
            "complexity": {
                "average_cyclomatic_complexity": metrics["average_cyclomatic_complexity"],
                "maximum_cyclomatic_complexity": metrics["maximum_cyclomatic_complexity"],
                "high_complexity_functions_count": metrics["high_complexity_functions_count"],
                "high_complexity_functions": metrics["high_complexity_functions"][:5],
            },
            "dependency_health": {
                "has_circular_dependencies": deps["has_circular_dependencies"],
                "circular_dependencies_count": len(deps["circular_dependencies"]),
                "circular_dependencies": deps["circular_dependencies"],
                "unused_imports_count": sum(len(v) for v in deps["unused_imports"].values()),
                "external_dependencies_count": len(deps["external_dependencies"]),
                "external_dependencies": deps["external_dependencies"],
            },
            "documentation_coverage": metrics["documentation_coverage"],
            "maintainability": {
                "maintainability_index": metrics["maintainability_index"],
                "maintainability_rating": metrics["maintainability_rating"],
                "dead_code_count": len(dead_code),
                "dead_code": dead_code[:5],
                "duplicate_blocks_count": len(duplicates),
                "duplicates": duplicates[:5],
            },
            "verification_status": {
                "total_python_files": len(arch["modules"]),
                "all_syntax_valid": not quality_res["blockers_present"],
                "status": "passed" if composite_health_score >= 60 and not quality_res["blockers_present"] else "attention_required",
            },
        }

    def generate_markdown_report(self, run_tests: bool = False) -> str:
        """Format the consolidated health report into an executive Markdown report."""
        report = self.generate_health_report(run_tests=run_tests)
        doc = report["documentation_coverage"]
        maint = report["maintainability"]
        sec = report["security"]
        deps = report["dependency_health"]

        lines = [
            f"# Project Health & Engineering Audit: Grade {report['overall_grade']} ({report['composite_health_score']}/100)",
            "",
            "## Executive Summary",
            f"- **Composite Health Score:** `{report['composite_health_score']}/100` (Grade: **{report['overall_grade']}**)",
            f"- **Code Quality Score:** `{report['code_quality']['score']}/100`",
            f"- **Maintainability Index:** `{maint['maintainability_index']}/100` (Rating: **{maint['maintainability_rating']}**)",
            f"- **Documentation Coverage:** `{doc['overall_percentage']}%` ({doc['documented_functions']}/{doc['total_functions']} functions, {doc['documented_classes']}/{doc['total_classes']} classes)",
            f"- **Security Findings:** `{sec['findings_count']}` issues flagged across project files",
            f"- **Circular Imports:** `{'Detected (' + str(deps['circular_dependencies_count']) + ')' if deps['has_circular_dependencies'] else 'None (Clean DAG)'}`",
            "",
            "## Complexity & Architecture",
            f"- **Average Cyclomatic Complexity:** `{report['complexity']['average_cyclomatic_complexity']}` (Max: `{report['complexity']['maximum_cyclomatic_complexity']}`)",
            f"- **High-Complexity Functions (>10):** `{report['complexity']['high_complexity_functions_count']}`",
            f"- **Dead Code Instances:** `{maint['dead_code_count']}` unreferenced symbols",
            f"- **Code Duplication Blocks:** `{maint['duplicate_blocks_count']}` cross-file duplicates",
            "",
            "## Testing & Verification",
            f"- **Test Suite Status:** `{report['test_status'].get('status', 'not_run')}`",
            f"- **Syntax Integrity:** `{'All files compiled cleanly' if report['verification_status']['all_syntax_valid'] else 'Syntax errors present'}`",
            "",
            "---",
            "*Report generated by AST Studio Software Engineering Workbench.*",
        ]
        return "\n".join(lines)
