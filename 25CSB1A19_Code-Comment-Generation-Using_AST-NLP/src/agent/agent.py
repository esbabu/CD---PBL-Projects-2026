"""Local Agentic Security coordinator for supported source languages.

Supported languages: Python, C, C++, Java, JavaScript, TypeScript and TSX.
This module performs static source inspection only. It never executes the
submitted program and does not claim that a clean scan proves code is safe.
"""

from __future__ import annotations

import re
from typing import Any, Dict

# IMPORTANT: Use relative imports for modules inside src.agent.
# Do NOT add: from src.agent import SecurityAgent
# That would create a circular import while src.agent.__init__ is loading.
from .tools import (
    inspect_ast,
    run_local_security_analysis,
    run_quality_analysis,
)
from .planner import SecurityPlanner
from .report import AgentReportBuilder
from .secure_alternative import SecureAlternativeBuilder
from .malware_detector import MalwareDetector

from src.multilang.universal_commenter import (
    UniversalCommenter,
    LANGUAGE_LABELS,
)
from src.multilang.security import run_multilanguage_security_analysis


class SecurityAgent:
    """Coordinate local security, quality and malware-indicator analysis."""

    LANGUAGE_ALIASES = {
        "py": "python",
        "pyw": "python",
        "c++": "cpp",
        "cc": "cpp",
        "cxx": "cpp",
        "h": "c",
        "hpp": "cpp",
        "hh": "cpp",
        "hxx": "cpp",
        "js": "javascript",
        "jsx": "javascript",
        "mjs": "javascript",
        "cjs": "javascript",
        "ts": "typescript",
        "mts": "typescript",
        "cts": "typescript",
        "tsx": "tsx",
    }

    def __init__(self) -> None:
        self.planner = SecurityPlanner()
        self.report_builder = AgentReportBuilder()
        self.alternative_builder = SecureAlternativeBuilder()
        self.malware_detector = MalwareDetector()
        self.multilang = UniversalCommenter()

    # ---------------------------------------------------------
    # Public entry point called by AgenticWorkspace
    # ---------------------------------------------------------
    def analyze(
        self,
        source_code: str,
        language: str = "python",
        filename: str = "",
    ) -> Dict[str, Any]:
        """Analyze source code and return both report and malware assessment."""

        if not isinstance(source_code, str):
            source_code = "" if source_code is None else str(source_code)
        filename = filename or ""
        language = self._normalize_language(language, filename, source_code)

        # Scan first. If later parsing/report generation fails, preserve the
        # malware assessment and never convert a failed scan into a clean one.
        malware_assessment = self._safe_malware_assessment(
            source_code, language, filename
        )

        if not source_code.strip():
            return self._error_result(
                "No source code was received from Generator.",
                language,
                malware_assessment,
            )

        try:
            if language == "python":
                return self._analyze_python(
                    source_code, language, filename, malware_assessment
                )

            if language not in LANGUAGE_LABELS:
                return self._error_result(
                    "Unsupported language "
                    f"'{language}'. Supported: Python, C, C++, Java, "
                    "JavaScript, TypeScript and TSX.",
                    language,
                    malware_assessment,
                )

            return self._analyze_other_language(
                source_code, language, filename, malware_assessment
            )

        except Exception as exc:
            return self._error_result(
                f"Agent analysis failed: {type(exc).__name__}: {exc}",
                language,
                malware_assessment,
            )

    # ---------------------------------------------------------
    # Python: existing AST, SAST, quality and secure rewrite path
    # ---------------------------------------------------------
    def _analyze_python(
        self,
        source_code: str,
        language: str,
        filename: str,
        malware_assessment: Dict[str, Any],
    ) -> Dict[str, Any]:
        ast_result = inspect_ast(source_code)

        if not ast_result.get("valid_python"):
            return self._error_result(
                ast_result.get("syntax_error", "Invalid Python source code."),
                language,
                malware_assessment,
                extra={"ast": ast_result},
            )

        plan = self.planner.create_plan(
            ast_result, source_code, language=language
        )
        security_issues = run_local_security_analysis(source_code)
        # Add the shared 500-signature catalogue to Python scans as well.
        # Keep existing AST findings and de-duplicate identical line/rule pairs.
        security_issues.extend(run_multilanguage_security_analysis(source_code, language))
        quality_findings = run_quality_analysis(source_code)
        secure_alternative = self.alternative_builder.build(
            source_code, security_issues
        )

        return self._build_success_result(
            ast_result=ast_result,
            security_issues=security_issues,
            quality_findings=quality_findings,
            plan=plan,
            secure_alternative=secure_alternative,
            malware_assessment=malware_assessment,
            language=language,
        )

    # ---------------------------------------------------------
    # Other languages: Tree-sitter/fallback structure + local rules
    # ---------------------------------------------------------
    def _analyze_other_language(
        self,
        source_code: str,
        language: str,
        filename: str,
        malware_assessment: Dict[str, Any],
    ) -> Dict[str, Any]:
        # The universal commenter parses source structure (Tree-sitter if
        # installed, otherwise its documented declaration-scan fallback).
        _annotated_source, multi_report = self.multilang.generate_comments(
            source_code,
            filename=filename,
            language=language,
        )

        targets = multi_report.get("targets", [])
        class_types = {
            "class",
            "class_declaration",
            "class_specifier",
            "struct_specifier",
            "interface_declaration",
            "enum_declaration",
        }

        functions = []
        classes = []
        for target in targets:
            target_type = str(target.get("type", "")).lower()
            item = {
                "name": target.get("name", ""),
                "line": int(target.get("start_line", 0)) + 1,
            }
            is_class = (
                target_type in class_types
                or "class" in target_type
                or "interface" in target_type
                or "struct" in target_type
                or "enum" in target_type
            )
            (classes if is_class else functions).append(item)

        ast_result = {
            "valid_python": True,  # report-builder compatibility flag only
            "language": language,
            "functions": functions,
            "classes": classes,
            "imports": [],
            "calls": [],
            "loops": len(re.findall(r"\b(?:for|while)\b", source_code)),
            "conditionals": len(
                re.findall(r"\b(?:if|switch|case)\b", source_code)
            ),
            "lines": len(source_code.splitlines()),
            "parser": multi_report.get("parser", "unknown"),
        }

        plan = [
            f"Inspect {language} source structure",
            "Identify functions, classes and declarations",
            "Run cross-language static security checks",
            "Correlate malware-behaviour indicators",
            "Prioritize findings and prepare the report",
        ]

        security_issues = run_multilanguage_security_analysis(
            source_code, language
        )
        quality_findings = self._multilang_quality_findings(
            source_code, language, targets
        )

        # Automatic source rewriting is deliberately Python-only at present.
        secure_alternative = {
            "code": "",
            "changes": [],
            "limitations": [
                "Automatic security rewrites are currently implemented only "
                "for Python. For this language, the agent provides findings "
                "and remediation guidance without changing source semantics."
            ],
        }

        return self._build_success_result(
            ast_result=ast_result,
            security_issues=security_issues,
            quality_findings=quality_findings,
            plan=plan,
            secure_alternative=secure_alternative,
            malware_assessment=malware_assessment,
            language=language,
        )

    # ---------------------------------------------------------
    # Common report builder and malware-result handoff
    # ---------------------------------------------------------
    def _build_success_result(
        self,
        ast_result,
        security_issues,
        quality_findings,
        plan,
        secure_alternative,
        malware_assessment,
        language,
    ) -> Dict[str, Any]:
        security_issues = list(security_issues or [])
        quality_findings = list(quality_findings or [])

        # Include malware findings in the combined security summary while
        # retaining the full evidence in malware_assessment.
        for finding in malware_assessment.get("findings", []):
            security_issues.append(
                {
                    "id": finding.get("id", "MALWARE"),
                    "severity": finding.get("severity", "medium"),
                    "line": finding.get("line", "?"),
                    "function": finding.get("function", "source/module"),
                    "message": finding.get("message", "Suspicious behaviour indicator."),
                    "fix": finding.get(
                        "fix", "Review the source behaviour and its context."
                    ),
                }
            )

        report = self.report_builder.build(
            ast_result,
            security_issues,
            quality_findings,
            plan,
            secure_alternative=secure_alternative,
            malware_assessment=malware_assessment,
            language=language,
        )
        report["agent_decision"] = self._make_decision(report)
        report["text"] = self.report_builder.to_text(report)

        # CRITICAL GUI CONTRACT: expose the result at the top level AND
        # inside report. AgenticWorkspace reads either location.
        return {
            "success": True,
            "report": report,
            "language": language,
            "malware_assessment": malware_assessment,
        }

    # ---------------------------------------------------------
    # Malware scan wrapper: failures become INCONCLUSIVE, not CLEAN
    # ---------------------------------------------------------
    def _safe_malware_assessment(
        self, source_code: str, language: str, filename: str
    ) -> Dict[str, Any]:
        try:
            assessment = self.malware_detector.assess(
                source_code,
                language=language,
                filename=filename,
            )
            if not isinstance(assessment, dict) or not assessment:
                raise ValueError("Malware detector returned an empty result.")

            assessment.setdefault("status", "inconclusive")
            assessment.setdefault(
                "headline", "MALWARE ASSESSMENT INCONCLUSIVE"
            )
            assessment.setdefault(
                "summary", "The scanner did not provide a summary."
            )
            assessment.setdefault("language", language)
            assessment.setdefault("filename", filename)
            assessment.setdefault("findings", [])
            assessment.setdefault(
                "scanned_lines", len(source_code.splitlines())
            )
            assessment.setdefault(
                "method", "static source inspection; code was not executed"
            )
            return assessment

        except Exception as exc:
            return {
                "status": "inconclusive",
                "headline": "MALWARE ASSESSMENT INCONCLUSIVE",
                "summary": (
                    "The malware scan failed and must not be treated as a "
                    f"clean result: {type(exc).__name__}: {exc}"
                ),
                "language": language,
                "filename": filename,
                "findings": [],
                "scanned_lines": len(source_code.splitlines()),
                "method": "static source inspection; scan did not complete",
            }

    # ---------------------------------------------------------
    # Multi-language quality observations (limited heuristics)
    # ---------------------------------------------------------
    @staticmethod
    def _multilang_quality_findings(source_code, language, targets):
        findings = []
        lines = source_code.splitlines()
        complexity_words = re.compile(
            r"\b(?:if|else\s+if|for|while|case|catch)\b"
        )
        for target in targets:
            start = int(target.get("start_line", 0))
            if 0 <= start < len(lines) and complexity_words.search(lines[start]):
                findings.append(
                    {
                        "id": "QLTX001",
                        "severity": "info",
                        "line": start + 1,
                        "function": target.get("name", "source/module"),
                        "message": (
                            "Review this declaration's control-flow complexity. "
                            "Detailed CFG/DFA analysis is currently Python-only."
                        ),
                    }
                )
        return findings

    # ---------------------------------------------------------
    # Language normalization
    # ---------------------------------------------------------
    def _normalize_language(self, language, filename, source_code):
        value = (language or "").strip().lower()
        value = self.LANGUAGE_ALIASES.get(value, value)

        if not value:
            detected = self.multilang.detect_language(filename, source_code)
            value = (detected or "python").lower()
            value = self.LANGUAGE_ALIASES.get(value, value)

        return value

    # ---------------------------------------------------------
    # Error result (keeps malware assessment available to GUI)
    # ---------------------------------------------------------
    @staticmethod
    def _error_result(message, language, malware_assessment, extra=None):
        result = {
            "success": False,
            "error": str(message),
            "language": language,
            "malware_assessment": malware_assessment,
        }
        if extra:
            result.update(extra)
        return result

    # ---------------------------------------------------------
    # Final decision text
    # ---------------------------------------------------------
    @staticmethod
    def _make_decision(report):
        critical = report.get("critical", 0)
        high = report.get("high", 0)
        medium = report.get("medium", 0)
        quality_findings = report.get("quality_findings", [])
        malware_status = report.get("malware_assessment", {}).get("status")

        if critical:
            return (
                "CRITICAL ACTION REQUIRED: Review critical findings and "
                "malware evidence before using this code."
            )
        if high:
            return (
                "HIGH RISK: Potentially dangerous behaviour or high-severity "
                "security findings need review before execution or deployment."
            )
        if medium:
            return (
                "MEDIUM RISK: Review suspicious indicators and apply the "
                "listed security recommendations."
            )
        if quality_findings:
            return (
                "No high-severity security finding was reported; review the "
                "quality observations before release."
            )
        if malware_status == "no_indicators":
            return (
                "No configured malware indicators were detected by this "
                "static scan. This is not a malware-free guarantee."
            )
        if malware_status == "inconclusive":
            return (
                "The malware assessment was inconclusive. Do not treat this "
                "as a clean result."
            )
        return (
            "The local scan did not find high-severity configured patterns. "
            "Review the report and test the program safely."
        )
