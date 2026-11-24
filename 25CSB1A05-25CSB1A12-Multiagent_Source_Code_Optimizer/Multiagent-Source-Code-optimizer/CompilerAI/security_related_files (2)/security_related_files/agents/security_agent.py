"""
Security Agent — Final Security Assessment, Vulnerability Auditing, and Score Generation.

Upgrades:
  1. Conventional tool family integration (Clang/Clang++, Clang-Tidy, Cppcheck, ASan, UBSan)
  2. Evaluates the actual candidate from the optimization-verification loop (no silent revert)
  3. Reassesses original findings and identifies newly introduced vulnerabilities
  4. Generates rubric-based final security score (0-100) using local LLM with range validation
  5. Initial-to-final score comparison (initial score, final score, score change, explanation)
  6. Truthful failure handling when Ollama or tools are unavailable (no fabricated scores)
"""

import json
import logging
import os
import re
import shutil
import sys
from typing import Any, Dict, List, Optional, Tuple

_this_dir = os.path.dirname(os.path.abspath(__file__))
_pkg_dir = os.path.abspath(os.path.join(_this_dir, ".."))
_root_dir = os.path.abspath(os.path.join(_this_dir, "..", ".."))

for p in [_pkg_dir, _root_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

for cand in [
    os.path.join(os.path.expanduser("~"), "Desktop", "modified-main (2)", "modified-main"),
    r"C:\Users\user\Desktop\modified-main (2)\modified-main",
]:
    if os.path.isdir(cand) and cand not in sys.path:
        sys.path.append(cand)

try:
    from agent_framework import BaseAgent, ContextManager
except ImportError:
    class ContextManager:
        def __init__(self, max_versions: int = 10):
            self._context: Dict[str, Any] = {}
        def get(self, key: str, default: Any = None) -> Any:
            return self._context.get(key, default)
        def set(self, key: str, value: Any) -> None:
            self._context[key] = value
        def append(self, key: str, value: Any) -> None:
            self._context.setdefault(key, []).append(value)

    class BaseAgent:
        def __init__(self, agent_id: str, agent_type: str, context_manager: ContextManager):
            self.agent_id = agent_id
            self.agent_type = agent_type
            self.context = context_manager
            self.logger = logging.getLogger(f"Agent.{agent_id}")

try:
    from analysis_and_detection.finding_schema import Finding, deduplicate_findings, canonical_defect_family
except ImportError:
    try:
        from src.analysis.finding_schema import Finding, deduplicate_findings, canonical_defect_family
    except ImportError:
        from finding_schema import Finding, deduplicate_findings, canonical_defect_family

try:
    from rules_and_scanners.security_rules import (
        SECURITY_PATTERNS,
        scan_security_rules,
        detect_use_after_free,
    )
except ImportError:
    try:
        from src.analysis.security_rules import (
            SECURITY_PATTERNS,
            scan_security_rules,
            detect_use_after_free,
        )
    except ImportError:
        from security_rules import (
            SECURITY_PATTERNS,
            scan_security_rules,
            detect_use_after_free,
        )

try:
    from analysis_and_detection.tool_runner import ToolRunner, ToolStatus
except ImportError:
    try:
        from src.analysis.tool_runner import ToolRunner, ToolStatus
    except ImportError:
        from tool_runner import ToolRunner, ToolStatus

try:
    from rules_and_scanners.prompt_templates import SecurityPromptTemplate, SecurityScoringPromptTemplate
except ImportError:
    try:
        from src.llm.prompt_templates import SecurityPromptTemplate, SecurityScoringPromptTemplate
    except ImportError:
        from prompt_templates import SecurityPromptTemplate, SecurityScoringPromptTemplate

try:
    from src.llm.llm_client import LLMClient
except ImportError:
    class LLMClient:
        def __init__(self, model: str = "qwen2.5-coder:7b", base_url: str = "http://localhost:11434"):
            self.model = model
            self.base_url = base_url
            self._available = False
        def is_available(self) -> bool:
            return False
        def generate(self, prompt: str, system_prompt: str = "") -> str:
            return "(LLM offline stub)"
        def is_stub(self, text: str) -> bool:
            return "(LLM offline stub)" in str(text) or "offline stub" in str(text)

try:
    from src.reasoning.cot_validator import CoTValidator, CoTResult
except ImportError:
    from dataclasses import dataclass

    @dataclass
    class CoTResult:
        is_valid: bool
        reasoning_steps: List[str]
        findings: List[Dict[str, Any]]
        conclusion: str
        confidence: float
        raw_json: Optional[Dict[str, Any]] = None

    class CoTValidator:
        _FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)```", re.IGNORECASE)

        def extract_json(self, text: str) -> Optional[Dict[str, Any]]:
            m = self._FENCE_RE.search(text)
            raw = m.group(1) if m else text
            try:
                return json.loads(raw)
            except Exception:
                return None

        def validate(self, text: str) -> CoTResult:
            data = self.extract_json(text)
            if not isinstance(data, dict):
                return CoTResult(False, [], [], "Invalid output", 0.0)
            return CoTResult(
                is_valid=True,
                reasoning_steps=data.get("reasoning_steps", []),
                findings=data.get("findings", []),
                conclusion=data.get("conclusion", ""),
                confidence=float(data.get("confidence", 0.8)),
                raw_json=data,
            )

logger = logging.getLogger(__name__)


class SecurityAgent(BaseAgent):
    """
    Security Agent: performs final security assessment of the candidate code,
    detects new vulnerabilities, reassesses original findings, and generates final score.
    """

    # ── Layer 1: Unsafe function & vulnerability patterns across CWE spectrum ───
    _UNSAFE_FUNCTIONS = list(SECURITY_PATTERNS)

    def __init__(
        self,
        agent_id: str,
        context_manager: ContextManager,
        llm_client: Optional[LLMClient] = None,
        tool_runner: Optional[ToolRunner] = None,
    ):
        self.tool_runner = tool_runner or ToolRunner()
        self.llm = llm_client or LLMClient()
        self.cot_val = CoTValidator()
        self._cppcheck_available = bool(self.tool_runner.find_executable("cppcheck"))
        super().__init__(agent_id, "security", context_manager)

    def get_capabilities(self) -> List[str]:
        caps = [
            "buffer_overflow_detection",
            "format_string_detection",
            "use_after_free_detection",
            "double_free_detection",
            "integer_overflow_detection",
            "null_dereference_detection",
            "injection_vulnerability_detection",
            "crypto_authentication_auditing",
            "memory_safety_auditing",
            "concurrency_flaw_detection",
            "cwe_sast_pattern_scanning",
            "taint_flow_heuristics",
            "security_rollback",
            "llm_security_analysis",
            "final_security_scoring",
            "score_comparison",
            "conventional_tool_integration",
            "clang_tidy_security_analysis",
            "asan_ubsan_runtime_sanitizers",
        ]
        if self._cppcheck_available:
            caps.append("cppcheck_static_analysis")
        return caps

    def audit_code(self, source_code: str, file_path: str = "<source>") -> Dict[str, Any]:
        """Convenience method to perform a standalone security audit on a single source code file."""
        return self.process({
            "original_code": source_code,
            "optimized_code": source_code,
            "file_path": file_path,
        })

    @staticmethod
    def _check_cppcheck() -> bool:
        """Check if cppcheck executable is available on PATH or standard install dirs."""
        if shutil.which("cppcheck"):
            return True
        for p in [r"C:\Program Files\Cppcheck\cppcheck.exe", r"C:\Program Files (x86)\Cppcheck\cppcheck.exe"]:
            if os.path.isfile(p):
                return True
        return False

    def _cppcheck_scan(self, code: str, filename: str = "test.cpp") -> List[Dict[str, Any]]:
        """Run cppcheck and return findings list (backward compatibility helper)."""
        res = self.tool_runner.run_cppcheck(code, filename)
        findings = []
        for f in res.findings:
            raw_type = f.get("type", "finding")
            t_name = raw_type if raw_type.startswith("cppcheck_") else f"cppcheck_{raw_type}"
            findings.append({
                "type": t_name,
                "severity": f.get("severity", "medium"),
                "description": f.get("description", ""),
                "source": "cppcheck",
                "cwe_id": f.get("cwe_id", "CWE-398"),
                "line": f.get("line", 1),
            })
        return findings

    def _is_llm_ready(self) -> bool:
        if self.llm is None:
            return False
        if hasattr(self.llm, "_available") and not self.llm._available:
            return False
        if hasattr(self.llm, "is_available"):
            try:
                res = self.llm.is_available()
                if isinstance(res, bool):
                    return res
            except Exception:
                pass
        return bool(getattr(self.llm, "_available", True))

    def _is_stub(self, text: str) -> bool:
        if not text:
            return False
        is_stub_fn = getattr(self.llm, "is_stub", None)
        if callable(is_stub_fn):
            try:
                res = is_stub_fn(text)
                if isinstance(res, bool):
                    return res
            except Exception:
                pass
        return "(LLM offline stub)" in str(text) or "offline stub" in str(text)

    def _call_llm(self, prompt: str, system_prompt: str = "") -> Tuple[str, Dict[str, Any]]:
        if hasattr(self.llm, "generate_with_meta"):
            try:
                res = self.llm.generate_with_meta(prompt, system_prompt=system_prompt)
                if isinstance(res, tuple) and len(res) == 2:
                    return res
            except Exception:
                pass
        if hasattr(self.llm, "generate"):
            try:
                text = self.llm.generate(prompt, system_prompt=system_prompt)
                if isinstance(text, str):
                    is_stub = self._is_stub(text)
                    return text, {"status": "stub" if is_stub else "genuine", "is_genuine": not is_stub}
            except Exception as e:
                return "", {"status": "error", "is_genuine": False, "error": str(e)}
        return "", {"status": "unavailable", "is_genuine": False}

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive security assessment on the final candidate code."""
        original_code = input_data.get("original_code") or self.context.get("original_code") or ""
        optimized_code = input_data.get("optimized_code") or self.context.get("current_candidate") or original_code
        file_path = input_data.get("file_path") or self.context.get("source_file") or "<unknown>"

        initial_report = (
            input_data.get("initial_analysis_report")
            or input_data.get("analysis_report")
            or self.context.get("initial_analysis_report")
            or self.context.get("analysis_report")
            or self.context.get("analysis_results")
            or {}
        )
        initial_score = input_data.get("initial_score", initial_report.get("security_score"))
        if initial_score is None:
            initial_score = self.context.get("initial_security_score")

        unresolved_input = input_data.get("unresolved_findings") or self.context.get("unresolved_findings") or []

        if not optimized_code.strip():
            logger.error("SecurityAgent: no code provided for security audit")
            return {
                "file_path": file_path,
                "error": "No code provided",
                "status": "PASS",
                "overall_risk": "none",
                "security_score": None,
                "all_vulnerabilities": [],
                "new_vulnerabilities": [],
            }

        logger.info(
            f"SecurityAgent: auditing candidate '{os.path.basename(file_path)}' "
            f"({len(optimized_code)} chars)"
        )

        sources: List[str] = []
        assessment_limitations: List[str] = []

        # ── 1. Layer 1: Rule-based scan ───────────────────────────────────────
        orig_rule = self._rule_scan(original_code, file_path)
        opt_rule = self._rule_scan(optimized_code, file_path)
        sources.append("rules")

        # ── 2. Layer 2: Heuristic scan ────────────────────────────────────────
        orig_heuristic, _ = self._heuristic_scan(original_code)
        opt_heuristic, opt_scores = self._heuristic_scan(optimized_code)
        sources.append("heuristics")

        # ── 3. Layer 3: Conventional Tool Runner on Candidate ─────────────────
        tool_results = self.tool_runner.run_all_tools_concurrently(
            source_code=optimized_code,
            file_path=file_path,
        )
        tool_statuses: Dict[str, str] = {}
        tool_findings: List[Dict[str, Any]] = []

        for tname, tres in tool_results.items():
            tool_statuses[tname] = tres.status
            if tres.findings:
                tool_findings.extend(tres.findings)
            if tres.limitations:
                assessment_limitations.extend(tres.limitations)
            if tres.status == ToolStatus.UNAVAILABLE:
                assessment_limitations.append(f"{tname} is unavailable on this system.")

        if any(tres.status in (ToolStatus.PASSED, ToolStatus.FINDINGS) for tres in tool_results.values()):
            sources.append("conventional_tools")

        # ── 4. Layer 4: LLM Semantic Scan ─────────────────────────────────────
        orig_all_base = orig_rule + orig_heuristic
        baseline_types = list({f["type"] for f in orig_all_base})
        llm_findings, llm_reasoning, llm_conclusion, llm_conf = self._llm_scan(
            optimized_code=optimized_code,
            original_code=original_code,
            baseline_types=baseline_types,
            tool_findings=tool_findings,
            tool_statuses=tool_statuses,
        )
        if llm_findings:
            sources.append("llm")

        # ── 5. Consolidate and Deduplicate Security Agent Vulnerabilities ─────
        # Security Agent discovers vulnerabilities exclusively through its own rule scanner,
        # heuristic detector, conventional security tools, and security LLM.
        raw_opt_vulns = opt_rule + opt_heuristic + tool_findings + llm_findings
        candidate_vulns, opt_dedup_summary = deduplicate_findings(raw_opt_vulns)

        if original_code.strip() == optimized_code.strip():
            all_vulns = candidate_vulns
            dedup_summary = opt_dedup_summary
            new_vulns = []
            resolved_findings = []
            unresolved_findings = candidate_vulns
        else:
            # Retain security flaws found exclusively by SecurityAgent across original & candidate
            all_sec_findings = orig_all_base + raw_opt_vulns
            all_vulns, dedup_summary = deduplicate_findings(all_sec_findings)
            new_vulns = self._find_new_vulnerabilities(orig_all_base, candidate_vulns)
            resolved_findings, unresolved_findings = self._partition_resolved(
                orig_all_base,
                candidate_vulns,
            )

        # ── 7. Overall Risk Assessment ────────────────────────────────────────
        overall_risk = self._compute_risk(all_vulns)

        # ── 8. Final Security Scoring (0 to 100) ──────────────────────────────
        if initial_score is None and original_code.strip() and original_code.strip() != optimized_code.strip():
            base_score, _, _, _, _ = self._generate_final_score(
                candidate_code=original_code,
                all_vulns=orig_all_base,
                new_vulns=[],
                resolved_findings=[],
                unresolved_findings=orig_all_base,
                tool_statuses=tool_statuses,
                initial_score=None,
            )
            initial_score = base_score

        final_score, score_rationale, score_conf, completeness, extra_limits = self._generate_final_score(
            candidate_code=optimized_code,
            all_vulns=all_vulns,
            new_vulns=new_vulns,
            resolved_findings=resolved_findings,
            unresolved_findings=unresolved_findings,
            tool_statuses=tool_statuses,
            initial_score=initial_score,
        )
        if extra_limits:
            assessment_limitations.extend(extra_limits)
        assessment_limitations = list(dict.fromkeys(assessment_limitations))

        # ── 9. Score Comparison ───────────────────────────────────────────────
        score_change = None
        score_explanation = ""
        if initial_score is not None and final_score is not None:
            score_change = final_score - initial_score
            if score_change > 0:
                score_explanation = f"Security score improved by +{score_change} points after resolving vulnerabilities."
            elif score_change < 0:
                score_explanation = f"Security score decreased by {score_change} points due to introduced or remaining risks."
            else:
                score_explanation = "Security score remained unchanged."
        elif initial_score is not None and final_score is None:
            score_explanation = "Initial score was available, but final LLM security score could not be completed."
        else:
            score_explanation = "Scores are not directly comparable because LLM scoring was unavailable for one or both phases."

        # ── 10. Rollback / Decision Logic ─────────────────────────────────────
        rollback_triggers = [
            v for v in new_vulns
            if v.get("severity") in ("high", "critical")
            and (
                v.get("source_tool") in ("rule", "heuristic", "conventional_tools", "asan", "ubsan", "clang-tidy", "cppcheck")
                or v.get("source") in ("rule", "heuristic", "conventional_tools", "asan", "ubsan", "clang-tidy", "cppcheck")
            )
            and v.get("confidence", 0) >= 0.8
        ]

        if rollback_triggers:
            logger.warning(
                f"SecurityAgent: {len(rollback_triggers)} new high-severity defect(s) detected in candidate."
            )
            status = "ROLLBACK"
        else:
            status = "PASS"

        # ── 11. Final Summary ─────────────────────────────────────────────────
        summary = self._build_summary(
            file_path=file_path,
            all_vulns=all_vulns,
            new_vulns=new_vulns,
            risk=overall_risk,
            status=status,
            final_score=final_score,
            initial_score=initial_score,
            score_change=score_change,
            completeness=completeness,
        )

        result = {
            "file_path": file_path,
            "security_score": final_score,
            "initial_score": initial_score,
            "score_change": score_change,
            "score_explanation": score_explanation,
            "score_rationale": score_rationale,
            "score_confidence": score_conf,
            "assessment_completeness": completeness,
            "all_vulnerabilities": all_vulns,
            "candidate_vulnerabilities": candidate_vulns,
            "new_vulnerabilities": new_vulns,
            "resolved_findings": resolved_findings,
            "unresolved_findings": unresolved_findings,
            "heuristic_scores": opt_scores,
            "tool_statuses": tool_statuses,
            "overall_risk": overall_risk,
            "status": status,
            "rollback_triggers": rollback_triggers,
            "llm_reasoning": llm_reasoning,
            "llm_conclusion": llm_conclusion,
            "assessment_limitations": assessment_limitations,
            "deduplication_summary": dedup_summary,
            "sources": sources,
            "summary": summary,
        }

        # Store in shared context
        self.context.set("security_report", result)
        self.context.set("security_findings", result)
        self.context.set("final_security_score", final_score)

        # ── 12. Display Results on Terminal ──────────────────────────────────
        if input_data.get("terminal_output", True):
            try:
                self.print_terminal_report(result)
            except Exception as exc:
                logger.debug(f"Terminal output formatting notice: {exc}")

        logger.info(
            f"SecurityAgent: audit complete — status={status}, risk={overall_risk}, "
            f"score={final_score if final_score is not None else 'N/A'}/100"
        )
        return result

    # ── Final Score Generation ────────────────────────────────────────────────

    def _generate_final_score(
        self,
        candidate_code: str,
        all_vulns: List[Dict[str, Any]],
        new_vulns: List[Dict[str, Any]],
        resolved_findings: List[Dict[str, Any]],
        unresolved_findings: List[Dict[str, Any]],
        tool_statuses: Dict[str, str],
        initial_score: Optional[int],
    ) -> Tuple[Optional[int], str, float, str, List[str]]:
        """Generate final security score (0-100) using Ollama and rubric."""
        if not self._is_llm_ready():
            return (
                None,
                "Final security score could not be completed because Ollama was offline.",
                0.0,
                "partial - conventional tools only",
                ["Ollama unavailable for final security score; score not fabricated."],
            )

        prompt = SecurityPromptTemplate.build(
            optimized_code=candidate_code,
            tool_findings=all_vulns,
            tool_statuses=tool_statuses,
            unresolved_findings=unresolved_findings,
            initial_score=initial_score,
        )

        raw, meta = self._call_llm(
            prompt,
            system_prompt=SecurityPromptTemplate.SYSTEM,
        )

        if not meta.get("is_genuine") or self._is_stub(raw):
            return (
                None,
                "Final security score could not be completed (Ollama returned stub or connection failed).",
                0.0,
                "partial - conventional tools only",
                ["Ollama unavailable or returned synthetic stub; score not fabricated."],
            )

        parsed = self.cot_val.extract_json(raw)
        if not parsed or "security_score" not in parsed:
            return (
                None,
                "Final LLM security scoring output could not be parsed as valid JSON.",
                0.0,
                "incomplete",
                ["Malformed LLM scoring response."],
            )

        raw_score = parsed["security_score"]
        # Explicitly reject booleans (True/False are subclasses of int in Python)
        if isinstance(raw_score, bool):
            return (
                None,
                "LLM returned boolean value for security score instead of an integer.",
                0.0,
                "invalid_type",
                ["Boolean score received from LLM."],
            )
        # Reject floating point values that are not exact integers
        if isinstance(raw_score, float) and not raw_score.is_integer():
            return (
                None,
                f"LLM returned fractional float value {raw_score} for security score.",
                0.0,
                "invalid_type",
                ["Floating point score cannot be silently truncated to integer."],
            )

        try:
            score_val = int(raw_score)
            if not (0 <= score_val <= 100):
                logger.warning(f"Final score {score_val} outside [0, 100] – rejecting.")
                return (
                    None,
                    f"LLM final score {score_val} was outside valid range [0, 100].",
                    0.0,
                    "invalid_range",
                    ["LLM returned out-of-range final security score."],
                )
        except (ValueError, TypeError):
            return (
                None,
                "LLM returned non-integer final security score.",
                0.0,
                "invalid_type",
                ["Non-numeric score received from LLM."],
            )

        rationale = str(parsed.get("score_rationale", "Evidence-based final security rubric score."))
        raw_conf = parsed.get("score_confidence", 0.8)
        try:
            conf = float(raw_conf)
            if not (0.0 <= conf <= 1.0):
                conf = max(0.0, min(1.0, conf))
        except (ValueError, TypeError):
            conf = 0.8
        completeness = str(parsed.get("assessment_completeness", "full"))
        extra_limits = [str(x) for x in parsed.get("assessment_limitations", [])]

        return score_val, rationale, conf, completeness, extra_limits

    # ── Layer 1: Rule-based scan ───────────────────────────────────────────────

    def _rule_scan(self, code: str, file_path: str = "<source>") -> List[Dict[str, Any]]:
        """Run comprehensive 6-domain static security pattern scanning."""
        if not code or not code.strip():
            return []
        return scan_security_rules(code, file_path)

    def _detect_use_after_free(self, code: str, lines: List[str]) -> List[Dict[str, Any]]:
        findings: List[Dict[str, Any]] = []
        dealloc_re = re.compile(
            r"\bfree\s*\(\s*(\w+)\s*\)"
            r"|\bdelete\s*\[\s*\]\s*(\w+)"
            r"|\bdelete\s+(\w+)",
            re.MULTILINE,
        )

        freed_vars: Dict[str, int] = {}
        for m in dealloc_re.finditer(code):
            var = m.group(1) or m.group(2) or m.group(3)
            freed_vars[var] = code[: m.start()].count("\n") + 1

        for var, free_line in freed_vars.items():
            deref_re = re.compile(
                rf"\*\s*{re.escape(var)}\b"
                rf"|{re.escape(var)}\s*->\s*\w+"
                rf"|{re.escape(var)}\s*\["
            )
            direct_assign_re = re.compile(
                rf"(?<![*\[])\b{re.escape(var)}\s*=\s*(?!=)"
            )
            for ln_no, line in enumerate(lines, 1):
                if ln_no <= free_line:
                    continue
                if re.search(
                    rf"\bfree\s*\(\s*{re.escape(var)}\s*\)"
                    rf"|\bdelete(?:\s*\[\s*\])?\s+{re.escape(var)}",
                    line,
                ):
                    break
                if direct_assign_re.search(line) and "->" not in line and not re.search(rf"\*\s*{re.escape(var)}", line):
                    break
                if deref_re.search(line):
                    findings.append(Finding(
                        type="use_after_free",
                        category="security",
                        severity="high",
                        line=ln_no,
                        description=f"Variable '{var}' dereferenced at line {ln_no} after deallocation at line {free_line}.",
                        cwe_id="CWE-416",
                        recommendation=f"Set '{var} = NULL/nullptr' immediately after deallocation.",
                        confidence=0.9,
                        source_tool="rule",
                        status="confirmed",
                        is_confirmed=True,
                    ).to_dict())
                    break

        return findings

    # ── Layer 2: Heuristic scan ────────────────────────────────────────────────

    def _heuristic_scan(self, code: str) -> Tuple[List[Dict[str, Any]], Dict[str, float]]:
        findings: List[Dict[str, Any]] = []
        scores: Dict[str, float] = {}

        if not code.strip():
            return findings, scores

        h1, h1_line = self._h_taint_flow(code)
        scores["taint_flow"] = h1
        if h1 >= 0.5 and h1_line is not None:
            findings.append(Finding(
                type="taint_flow_risk",
                category="security",
                severity="high" if h1 >= 0.8 else "medium",
                line=h1_line,
                start_line=h1_line,
                end_line=h1_line,
                description="User input flows into buffer write without apparent size check.",
                cwe_id="CWE-120",
                recommendation="Validate input length before copying into fixed buffers.",
                confidence=h1,
                source_tool="heuristic",
                status="suspicious",
            ).to_dict())

        h2, h2_line = self._h_unchecked_malloc(code)
        scores["unchecked_malloc"] = h2
        if h2 >= 0.6 and h2_line is not None:
            findings.append(Finding(
                type="unchecked_malloc",
                category="security",
                severity="medium",
                line=h2_line,
                start_line=h2_line,
                end_line=h2_line,
                description="malloc/calloc return value not checked for NULL before use.",
                cwe_id="CWE-476",
                recommendation="Always check: if (!ptr) { /* handle error */ }",
                confidence=h2,
                source_tool="heuristic",
                status="potential",
            ).to_dict())

        h3, h3_line = self._h_signed_unsigned(code)
        scores["signed_unsigned_mismatch"] = h3
        if h3 >= 0.6 and h3_line is not None:
            findings.append(Finding(
                type="signed_unsigned_mismatch",
                category="security",
                severity="medium",
                line=h3_line,
                start_line=h3_line,
                end_line=h3_line,
                description="Signed integer used as array index or malloc size expression.",
                cwe_id="CWE-195",
                recommendation="Use size_t or unsigned types for sizes and array indices.",
                confidence=h3,
                source_tool="heuristic",
                status="potential",
            ).to_dict())

        h4, h4_line = self._h_int_overflow_malloc(code)
        scores["int_overflow_malloc"] = h4
        if h4 >= 0.7:
            findings.append(Finding(
                type="integer_overflow_malloc",
                category="security",
                severity="high",
                line=h4_line,
                description="malloc() called with multiplication expression — may overflow before allocation (CWE-190).",
                cwe_id="CWE-190",
                recommendation="Check multiplication bounds before calling malloc().",
                confidence=h4,
                source_tool="heuristic",
                status="potential",
            ).to_dict())

        h5, h5_line = self._h_buffer_loop_write(code)
        scores["unbounded_loop_write"] = h5
        if h5 >= 0.7:
            findings.append(Finding(
                type="unbounded_loop_write",
                category="security",
                severity="high",
                line=h5_line,
                description="Buffer write in loop bounded by variable without apparent size guard (CWE-120).",
                cwe_id="CWE-120",
                recommendation="Ensure loop termination bound does not exceed buffer capacity.",
                confidence=h5,
                source_tool="heuristic",
                status="potential",
            ).to_dict())

        return findings, scores

    def _h_taint_flow(self, code: str) -> Tuple[float, Optional[int]]:
        input_sources = [
            # C/C++ sources
            r"\bscanf\b", r"\bfgets\b", r"\bread\b", r"\bargv\[", r"\bcin\b",
            # Python sources
            r"\binput\s*\(", r"\bsys\.argv\b", r"\brequest\.(?:args|form|values|json|data)\b", r"\bos\.environ\b",
            # Java sources
            r"\bScanner\b", r"\bBufferedReader\b", r"\brequest\.getParameter\b", r"\bargs\[", r"\bSystem\.getenv\b",
        ]
        sink_fns = [
            # C/C++ sinks
            r"\bstrcpy\b", r"\bstrcat\b", r"\bsprintf\b", r"\bmemcpy\b",
            # Python sinks
            r"\bos\.system\b", r"\bos\.popen\b", r"\bsubprocess\b", r"\beval\b", r"\bexec\b", r"\bcursor\.execute\b", r"\bpickle\.loads?\b",
            # Java sinks
            r"\bRuntime\.getRuntime\s*\(\s*\)\.exec\b", r"\bexecuteQuery\b", r"\bexecuteUpdate\b", r"\bObjectInputStream\b",
        ]
        has_src = any(re.search(p, code) for p in input_sources)
        if not has_src:
            return 0.0, None
        sink_match = None
        for p in sink_fns:
            m = re.search(p, code)
            if m:
                sink_match = m
                break
        if not sink_match:
            return 0.0, None
        ln = code[: sink_match.start()].count("\n") + 1
        has_len_check = bool(re.search(
            r"if\s*\([^)]*(?:strlen|sizeof|length|\bcount\b|max_len|\blen\s*\()[^)]*[><=]", code
        ))
        return (0.5 if has_len_check else 0.85), ln

    def _h_unchecked_malloc(self, code: str) -> Tuple[float, Optional[int]]:
        alloc_match = re.search(r"(\w+)\s*=\s*(?:\([^)]*\)\s*)?malloc\s*\(", code)
        if not alloc_match:
            return 0.0, None
        var = alloc_match.group(1)
        is_checked = (
            bool(re.search(rf"if\s*\(\s*!?\s*{re.escape(var)}\b", code))
            or bool(re.search(rf"assert\s*\(\s*{re.escape(var)}\b", code))
        )
        if is_checked:
            return 0.0, None
        ln = code[: alloc_match.start()].count("\n") + 1
        return 0.75, ln

    def _h_signed_unsigned(self, code: str) -> Tuple[float, Optional[int]]:
        lines = code.splitlines()
        for i, line in enumerate(lines):
            m = re.search(r"\bint\s+(\w+)\s*;", line)
            if m:
                var = m.group(1)
                subsequent = "\n".join(lines[i + 1: i + 20])
                if re.search(rf"\b\w+\[\s*{re.escape(var)}\s*\]", subsequent) or \
                   re.search(rf"\bmalloc\s*\([^)]*\b{re.escape(var)}\b", subsequent):
                    return 0.7, (i + 1)
        return 0.0, None

    def _h_int_overflow_malloc(self, code: str) -> Tuple[float, Optional[int]]:
        pattern = re.compile(r"\bmalloc\s*\(\s*(\w+)\s*\*\s*(\w+)\s*\)")
        for m in pattern.finditer(code):
            ln = code[: m.start()].count("\n") + 1
            preceding = code[: m.start()][-500:]
            has_guard = bool(re.search(
                r"if\s*\([^)]*>\s*(?:SIZE_MAX|INT_MAX|UINT_MAX)", preceding
            ))
            if not has_guard:
                return 0.85, ln
        return 0.0, None

    def _h_buffer_loop_write(self, code: str) -> Tuple[float, Optional[int]]:
        buf_match = re.search(r"\b(?:char|int|short|long|uint8_t|int8_t)\s+(\w+)\s*\[\s*(\d+)\s*\]", code)
        if buf_match:
            buf_name = buf_match.group(1)
            loop_match = re.search(r"for\s*\([^;]*;\s*(\w+)\s*<\s*([a-zA-Z_]\w*)\s*;", code)
            if loop_match:
                idx_var = loop_match.group(1)
                if re.search(rf"\b{re.escape(buf_name)}\s*\[\s*{re.escape(idx_var)}\s*\]\s*=", code):
                    ln = code[: loop_match.start()].count("\n") + 1
                    return 0.85, ln
        return 0.0, None

    # ── Layer 4: LLM scan ─────────────────────────────────────────────────────

    def _llm_scan(
        self,
        optimized_code: str,
        original_code: str,
        baseline_types: List[str],
        tool_findings: List[Dict[str, Any]],
        tool_statuses: Dict[str, str],
    ) -> Tuple[List[Dict[str, Any]], List[str], str, float]:
        if not self._is_llm_ready():
            return [], ["LLM is offline; security audit based on conventional tools and rules."], "LLM skipped.", 0.0

        prompt = SecurityPromptTemplate.build(
            optimized_code=optimized_code,
            original_code=original_code,
            baseline_types=baseline_types,
            tool_findings=tool_findings,
            tool_statuses=tool_statuses,
        )

        raw, meta = self._call_llm(prompt, system_prompt=SecurityPromptTemplate.SYSTEM)
        if not meta.get("is_genuine") or self._is_stub(raw):
            return [], ["LLM returned synthetic stub or connection failed."], "LLM analysis skipped.", 0.0

        cot = self.cot_val.validate(raw)
        if cot.is_valid:
            normalized_findings = []
            for f in cot.findings:
                f_norm = Finding(
                    type=f.get("type", "llm_security_risk"),
                    category="security",
                    description=f.get("description", ""),
                    line=f.get("line"),
                    severity=f.get("severity", "medium").lower(),
                    confidence=min(0.70, cot.confidence),
                    source_tool="llm",
                    recommendation=f.get("recommendation", "Review code logic."),
                    cwe_id=f.get("cwe_id"),
                    status="potential",
                ).to_dict()
                normalized_findings.append(f_norm)
            return normalized_findings, cot.reasoning_steps, cot.conclusion, cot.confidence

        return [], ["LLM security response invalid JSON."], "LLM analysis failed.", 0.0

    # ── Comparison Helpers ────────────────────────────────────────────────────

    def _find_new_vulnerabilities(
        self, orig_findings: List[Dict[str, Any]], opt_findings: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        orig_types = {f.get("type") for f in orig_findings if f.get("type")}

        def _fam(x: Dict[str, Any]) -> str:
            val = x.get("canonical_defect_family")
            return canonical_defect_family(x) if (not val or val == "other") else val

        new_vulns = []
        for f in opt_findings:
            ftype = f.get("type")
            if not ftype:
                continue
            if ftype in orig_types:
                continue
            line = f.get("line")
            f_fam = _fam(f)
            # If the finding is a conventional tool check belonging to the same defect family
            # and line as a pre-existing finding, it is residual rather than newly introduced.
            if any(
                orig.get("line") == line and _fam(orig) == f_fam
                for orig in orig_findings
            ):
                continue
            new_vulns.append(f)
        return new_vulns

    def _partition_resolved(
        self, orig_findings: List[Dict[str, Any]], opt_findings: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        opt_types = {f.get("type") for f in opt_findings if f.get("type")}
        resolved = []
        unresolved = []
        for f in orig_findings:
            if f.get("type") in opt_types:
                unresolved.append(f)
            else:
                resolved.append(f)
        return resolved, unresolved

    def _compute_risk(self, findings: List[Dict[str, Any]]) -> str:
        if not findings:
            return "none"
        sevs = [f.get("severity", "low").lower() for f in findings]
        if "critical" in sevs:
            return "critical"
        if "high" in sevs:
            return "critical" if sevs.count("high") >= 3 else "high"
        if "medium" in sevs:
            return "medium"
        return "low"

    def _build_summary(
        self,
        file_path: str,
        all_vulns: List[Dict[str, Any]],
        new_vulns: List[Dict[str, Any]],
        risk: str,
        status: str,
        final_score: Optional[int],
        initial_score: Optional[int],
        score_change: Optional[int],
        completeness: str,
    ) -> str:
        high = sum(1 for v in all_vulns if v.get("severity") in ("high", "critical"))
        med = sum(1 for v in all_vulns if v.get("severity") == "medium")
        low = sum(1 for v in all_vulns if v.get("severity") in ("low", "info"))

        score_line = f"Score: {final_score}/100" if final_score is not None else "Score: N/A (LLM offline)"
        if score_change is not None:
            sign = "+" if score_change > 0 else ""
            score_line += f" (Change: {sign}{score_change} from initial {initial_score}/100)"

        lines = [
            f"Security Report: {file_path}",
            f"Overall Status: {status} | Final {score_line} | Completeness: {completeness}",
            f"Overall Risk  : {risk.upper()}",
            f"Vulnerabilities: {len(all_vulns)} (High/Crit: {high}, Med: {med}, Low: {low})",
            f"New Flaws     : {len(new_vulns)} introduced by optimization",
        ]
        if new_vulns:
            lines.append("Newly introduced vulnerabilities:")
            for v in new_vulns:
                ln = f" [line {v['line']}]" if v.get("line") else ""
                cwe = f" {v['cwe_id']}" if v.get("cwe_id") else ""
                lines.append(f"  ! [{v.get('severity','?').upper()}]{ln}{cwe} {v.get('type')}: {v.get('description')}")
        return "\n".join(lines)

    # ── Terminal Output Formatting & Presentation ────────────────────────────

    @staticmethod
    def format_terminal_report(result: Dict[str, Any], use_color: Optional[bool] = None) -> str:
        """
        Format comprehensive security agent audit results for terminal display.
        Uses ANSI colors when outputting to an interactive terminal or when requested.
        """
        if use_color is None:
            use_color = (
                hasattr(sys.stdout, "isatty")
                and sys.stdout.isatty()
                and os.environ.get("NO_COLOR") is None
                and os.environ.get("TERM") != "dumb"
            ) or bool(os.environ.get("FORCE_COLOR"))

        if use_color:
            R = "\033[0m"
            BOLD = "\033[1m"
            DIM = "\033[2m"
            CYAN = "\033[96m"
            GREEN = "\033[92m"
            YELLOW = "\033[93m"
            RED = "\033[91m"
            WHITE = "\033[97m"
        else:
            R = BOLD = DIM = CYAN = GREEN = YELLOW = RED = WHITE = ""

        file_path = result.get("file_path", "<unknown>")
        status = str(result.get("status", "PASS")).upper()
        risk = str(result.get("overall_risk", "none")).upper()
        final_score = result.get("security_score")
        initial_score = result.get("initial_score")
        score_change = result.get("score_change")
        score_expl = result.get("score_explanation", "")

        all_vulns = result.get("all_vulnerabilities", [])
        new_vulns = result.get("new_vulnerabilities", [])
        resolved = result.get("resolved_findings", [])
        triggers = result.get("rollback_triggers", [])
        tool_statuses = result.get("tool_statuses", {})
        sources = result.get("sources", [])

        status_col = GREEN if status == "PASS" else RED
        risk_col = {
            "CRITICAL": RED,
            "HIGH": RED,
            "MEDIUM": YELLOW,
            "LOW": GREEN,
            "NONE": GREEN,
        }.get(risk, DIM)

        sev_colors = {
            "critical": RED,
            "high": RED,
            "medium": YELLOW,
            "low": GREEN,
        }

        ext = os.path.splitext(file_path)[1].lower()
        lang_label = {
            ".py": "PYTHON",
            ".pyw": "PYTHON",
            ".java": "JAVA",
            ".cpp": "C++",
            ".cxx": "C++",
            ".cc": "C++",
            ".hpp": "C++",
            ".c": "C",
            ".h": "C/C++",
        }.get(ext, "AUTO")

        W = 76
        border_top = f"{CYAN}{'═' * W}{R}"
        border_mid = f"{CYAN}{'─' * W}{R}"
        border_bottom = f"{CYAN}{'═' * W}{R}"

        out_lines = [
            "",
            border_top,
            f"{BOLD}{CYAN}  SECURITY AGENT AUDIT REPORT{R}",
            border_mid,
            f"  {BOLD}Target File     :{R} {WHITE}{file_path}{R}  [{CYAN}{lang_label}{R}]",
            f"  {BOLD}Audit Status    :{R} {status_col}{BOLD}[{status}]{R}",
            f"  {BOLD}Overall Risk    :{R} {risk_col}{BOLD}{risk}{R}",
        ]

        if final_score is not None:
            score_color = GREEN if final_score >= 80 else (YELLOW if final_score >= 60 else RED)
            score_str = f"{score_color}{BOLD}{final_score}/100{R}"
            if initial_score is not None:
                delta_str = f"({'+' if (score_change or 0) > 0 else ''}{score_change or 0})"
                delta_color = GREEN if (score_change or 0) > 0 else (RED if (score_change or 0) < 0 else DIM)
                out_lines.append(f"  {BOLD}Security Score  :{R} {score_str}  [Initial: {initial_score}/100 | Delta: {delta_color}{delta_str}{R}]")
            else:
                out_lines.append(f"  {BOLD}Security Score  :{R} {score_str}")
        else:
            out_lines.append(f"  {BOLD}Security Score  :{R} {DIM}N/A (offline or conventional-tools only){R}")

        if score_expl:
            out_lines.append(f"  {BOLD}Score Summary   :{R} {DIM}{score_expl}{R}")

        n_all = len(all_vulns)
        n_new = len(new_vulns)
        n_res = len(resolved)
        count_str = f"{YELLOW}{BOLD}{n_all}{R} total"
        if n_new:
            count_str += f" | {RED}{BOLD}{n_new} new{R}"
        if n_res:
            count_str += f" | {GREEN}{BOLD}{n_res} resolved{R}"
        out_lines.append(f"  {BOLD}Vulnerabilities :{R} {count_str}")
        if sources:
            out_lines.append(f"  {BOLD}Scan Engines    :{R} {DIM}{', '.join(sources)}{R}")

        if status == "ROLLBACK":
            out_lines.append(border_mid)
            out_lines.append(f"  {RED}{BOLD}⚠ ROLLBACK TRIGGERED{R}")
            out_lines.append(f"  {RED}The candidate code introduced {len(triggers)} new high/critical vulnerability(ies).{R}")
            out_lines.append(f"  {RED}Candidate discarded; original code preserved safely.{R}")

        out_lines.append(border_mid)
        if all_vulns:
            out_lines.append(f"{BOLD}  DETECTED VULNERABILITIES & SECURITY RISKS ({n_all}){R}")
            out_lines.append("")
            for idx, v in enumerate(all_vulns, 1):
                sev = str(v.get("severity", "medium")).lower()
                scol = sev_colors.get(sev, YELLOW)
                cwe = v.get("cwe_id") or "CWE-UNKNOWN"
                line_no = v.get("line") or "?"
                vtype = v.get("type", "finding")
                engine = v.get("source_tool") or v.get("detection_engine") or v.get("source") or "rule"
                is_new = v in new_vulns

                new_badge = f" {RED}{BOLD}[NEW]{R}" if is_new else ""
                out_lines.append(f"  {DIM}{idx:>2}.{R} {scol}{BOLD}[{sev.upper()}]{R} {BOLD}[{cwe}]{R} Line {WHITE}{line_no}{R}  (Engine: {DIM}{engine}{R}){new_badge}")
                out_lines.append(f"      {BOLD}Type       :{R} {vtype}")
                out_lines.append(f"      {BOLD}Description:{R} {v.get('description', '')}")
                if v.get("evidence"):
                    out_lines.append(f"      {BOLD}Evidence   :{R} {DIM}{str(v.get('evidence')).strip()}{R}")
                if v.get("recommendation"):
                    out_lines.append(f"      {BOLD}Remediation:{R} {GREEN}→ {v.get('recommendation')}{R}")
                out_lines.append("")
        else:
            out_lines.append(f"  {GREEN}{BOLD}✔ No vulnerabilities detected. Code passes security audit cleanly.{R}")

        if tool_statuses:
            out_lines.append(border_mid)
            out_lines.append(f"{BOLD}  TOOL EXECUTION SUMMARY{R}")
            for tname, tstatus in tool_statuses.items():
                st_color = GREEN if tstatus in ("passed", "PASS") else (
                    YELLOW if tstatus in ("findings", "inconclusive") else (
                        DIM if tstatus in ("skipped", "unavailable") else RED
                    )
                )
                out_lines.append(f"  • {tname:<18}: {st_color}{tstatus.upper()}{R}")

        out_lines.append(border_bottom)
        out_lines.append("")
        return "\n".join(out_lines)

    @classmethod
    def print_terminal_report(cls, result: Dict[str, Any], stream: Optional[Any] = None) -> None:
        """Render and print the security audit report directly to terminal."""
        out_stream = stream if stream is not None else sys.stdout
        text = cls.format_terminal_report(result)
        out_stream.write(text + "\n")
        out_stream.flush()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Security Agent — Vulnerability Audit & Security Scoring")
    parser.add_argument("file", help="Path to input source file (C/C++, Java, or Python)")
    parser.add_argument("--optimized", help="Path to optimized candidate file (differential audit)")
    parser.add_argument("--no-llm", action="store_true", help="Disable LLM (rule-based SAST only)")
    args = parser.parse_args()

    if not os.path.isfile(args.file):
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    with open(args.file, "r", encoding="utf-8", errors="replace") as f:
        orig_code = f.read()

    opt_code = orig_code
    if args.optimized:
        if not os.path.isfile(args.optimized):
            print(f"Error: Optimized file not found: {args.optimized}", file=sys.stderr)
            sys.exit(1)
        with open(args.optimized, "r", encoding="utf-8", errors="replace") as f:
            opt_code = f.read()

    ctx = ContextManager()
    llm = LLMClient()
    if args.no_llm:
        llm._available = False

    sec_agent = SecurityAgent("security_cli", ctx, llm_client=llm)
    sec_agent.process({
        "original_code": orig_code,
        "optimized_code": opt_code,
        "file_path": os.path.abspath(args.file),
        "terminal_output": True,
    })

