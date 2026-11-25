"""
Pattern Detector — Week 8
==========================
Detects code-quality patterns / code smells from IR and DFA results.

Patterns detected
-----------------
  P001  unused_variable      (warning)  — variable assigned but never read
  P002  high_complexity      (warning)  — cyclomatic complexity > 10 (very_complex)
  P003  dead_block           (info)     — basic block with no predecessors (unreachable)
  P004  no_return_value      (info)     — non-void function has no RETURN operand
  P005  deeply_nested_loops  (warning)  — function has ≥ 3 loop blocks in IR
  P006  excessive_calls      (info)     — function calls > 10 distinct callees
  P007  missing_param_load   (info)     — parameter listed but no LOAD in entry block
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ..ir.ir_nodes import IRModule, IRFunction, IROpcode
from .dfa_engine import DFAResult


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class PatternFinding:
    """
    A single finding produced by the pattern detector.

    Attributes:
        pattern_id    : Short code like ``P001``.
        severity      : ``"info"``, ``"warning"``, or ``"error"``.
        function_name : Name of the function in which the pattern was detected.
        message       : Human-readable description.
        lineno        : Approximate source line (0 = unknown).
    """
    pattern_id: str
    severity: str
    function_name: str
    message: str
    lineno: int = 0

    def __repr__(self) -> str:
        return (
            f"[{self.severity.upper()}] "
            f"{self.pattern_id} in "
            f"{self.function_name!r}: "
            f"{self.message}"
        )


@dataclass
class AnalysisReport:
    """
    Complete analysis report for all functions in an IRModule.

    Attributes:
        source_file : Path of the analysed source file.
        findings    : All pattern findings ordered by
                      (function_name, lineno).
        summary     : Aggregate counts keyed by severity and pattern_id.
    """

    source_file: str = ""

    findings: List[PatternFinding] = field(
        default_factory=list
    )

    summary: Dict[str, int] = field(
        default_factory=dict
    )

    # ============================================================
    # NEW: CODE QUALITY DISTRIBUTION
    # ============================================================

    quality_distribution: Dict[str, float] = field(
        default_factory=lambda: {
            "good": 100.0,
            "medium": 0.0,
            "poor": 0.0,
        }
    )

    # ============================================================
    # ADD FINDING
    # ============================================================

    def add(
        self,
        finding: PatternFinding
    ) -> None:

        self.findings.append(
            finding
        )

        # Update severity summary
        self.summary[finding.severity] = (
            self.summary.get(
                finding.severity,
                0
            ) + 1
        )

        # Update pattern summary
        self.summary[finding.pattern_id] = (
            self.summary.get(
                finding.pattern_id,
                0
            ) + 1
        )

    # ============================================================
    # FINDINGS FOR FUNCTION
    # ============================================================

    def findings_for(
        self,
        function_name: str
    ) -> List[PatternFinding]:

        return [
            f
            for f in self.findings
            if f.function_name == function_name
        ]

    # ============================================================
    # CODE QUALITY PERCENTAGES
    # ============================================================

    def quality_percentages(
        self,
        total_functions: Optional[int] = None,
    ) -> Dict[str, float]:
        """
        Calculate Good / Medium / Poor code-quality percentages.

        Classification:

        GOOD
            Function has 0 warning/error findings.

        MEDIUM
            Function has 1 or 2 warning/error findings.

        POOR
            Function has 3 or more warning/error findings.

        Informational findings are NOT treated as quality problems.
        """

        # Functions that appear in findings
        function_names = {
            f.function_name
            for f in self.findings
        }

        # Use actual number of functions when supplied.
        # This allows functions with no findings to be counted as GOOD.
        if total_functions is not None:
            total = total_functions
        else:
            total = len(function_names)

        # No functions
        if total <= 0:

            result = {
                "good": 0.0,
                "medium": 0.0,
                "poor": 0.0,
            }

            self.quality_distribution = result

            return result

        # Count warning/error findings per function
        function_issues: Dict[str, int] = {
            function_name: 0
            for function_name in function_names
        }

        for finding in self.findings:

            if finding.severity in (
                "warning",
                "error",
            ):

                function_issues[
                    finding.function_name
                ] = (
                    function_issues.get(
                        finding.function_name,
                        0
                    ) + 1
                )

        # Functions that have no findings are GOOD
        good = max(
            total - len(function_issues),
            0
        )

        medium = 0
        poor = 0

        # Classify functions with findings
        for count in function_issues.values():

            if count == 0:
                good += 1

            elif count <= 2:
                medium += 1

            else:
                poor += 1

        # Convert to percentages
        result = {
            "good": round(
                (good / total) * 100,
                2
            ),

            "medium": round(
                (medium / total) * 100,
                2
            ),

            "poor": round(
                (poor / total) * 100,
                2
            ),
        }

        # Make sure total is exactly 100.00
        remainder = round(
            100.0
            - result["good"]
            - result["medium"]
            - result["poor"],
            2
        )

        result["good"] = round(
            result["good"] + remainder,
            2
        )

        self.quality_distribution = result

        return result

    # ============================================================
    # REPRESENTATION
    # ============================================================

    def __repr__(self) -> str:
        return (
            f"AnalysisReport("
            f"{self.source_file!r}, "
            f"{len(self.findings)} findings)"
        )


# ---------------------------------------------------------------------------
# Individual pattern checkers
# ---------------------------------------------------------------------------

def _check_unused_variables(
    ir_func: IRFunction,
    dfa: Optional[DFAResult],
    report: AnalysisReport,
) -> None:
    """P001 — variables assigned but never read."""

    if dfa is None:
        return

    for var in dfa.unused_vars:

        report.add(
            PatternFinding(
                pattern_id="P001",
                severity="warning",
                function_name=ir_func.name,
                message=(
                    f"Temporary {var!r} is assigned "
                    "but never used as an operand."
                ),
                lineno=ir_func.source_lineno,
            )
        )


def _check_high_complexity(
    ir_func: IRFunction,
    report: AnalysisReport,
) -> None:
    """P002 — excessive number of branch/loop blocks."""

    branch_blocks = sum(
        1
        for b in ir_func.blocks
        if (
            "_cond" in b.label
            or "branch_" in b.label
            or "loop_" in b.label
        )
    )

    # Heuristic:
    # >10 branch-related blocks = high complexity
    if branch_blocks > 10:

        report.add(
            PatternFinding(
                pattern_id="P002",
                severity="warning",
                function_name=ir_func.name,
                message=(
                    f"Function has {branch_blocks} "
                    "branch/loop IR blocks — "
                    "likely very high cyclomatic "
                    "complexity (> 10)."
                ),
                lineno=ir_func.source_lineno,
            )
        )


def _check_dead_blocks(
    ir_func: IRFunction,
    report: AnalysisReport,
) -> None:
    """P003 — blocks with no predecessors."""

    for block in ir_func.blocks:

        if block.label == "entry":
            continue

        if not block.predecessors:

            report.add(
                PatternFinding(
                    pattern_id="P003",
                    severity="info",
                    function_name=ir_func.name,
                    message=(
                        f"Block {block.label!r} has "
                        "no predecessors — potentially "
                        "unreachable (dead code)."
                    ),
                    lineno=ir_func.source_lineno,
                )
            )


def _check_no_return_value(
    ir_func: IRFunction,
    report: AnalysisReport,
) -> None:
    """P004 — non-void function RETURN has no operand."""

    if ir_func.return_type in (
        None,
        "None",
        "",
    ):
        return

    for block in ir_func.blocks:

        for instr in block.instructions:

            if (
                instr.op == IROpcode.RETURN
                and not instr.operands
            ):

                report.add(
                    PatternFinding(
                        pattern_id="P004",
                        severity="info",
                        function_name=ir_func.name,
                        message=(
                            f"Function declares return "
                            f"type {ir_func.return_type!r} "
                            "but a RETURN instruction "
                            "carries no value."
                        ),
                        lineno=instr.lineno,
                    )
                )


def _check_deeply_nested_loops(
    ir_func: IRFunction,
    report: AnalysisReport,
) -> None:
    """P005 — three or more distinct loop headers."""

    loop_headers = [
        b
        for b in ir_func.blocks
        if b.label.endswith("_header")
    ]

    if len(loop_headers) >= 3:

        report.add(
            PatternFinding(
                pattern_id="P005",
                severity="warning",
                function_name=ir_func.name,
                message=(
                    f"Function contains "
                    f"{len(loop_headers)} nested "
                    "loop header blocks — "
                    "consider refactoring to "
                    "reduce loop depth."
                ),
                lineno=ir_func.source_lineno,
            )
        )


def _check_excessive_calls(
    ir_func: IRFunction,
    report: AnalysisReport,
) -> None:
    """P006 — more than 10 distinct callees."""

    callees = set()

    for instr in ir_func.all_instructions():

        if (
            instr.op == IROpcode.CALL
            and instr.meta.get("callee")
        ):

            callees.add(
                instr.meta["callee"]
            )

    if len(callees) > 10:

        report.add(
            PatternFinding(
                pattern_id="P006",
                severity="info",
                function_name=ir_func.name,
                message=(
                    f"Function makes calls to "
                    f"{len(callees)} distinct "
                    "callees — high coupling; "
                    "consider splitting responsibilities."
                ),
                lineno=ir_func.source_lineno,
            )
        )


def _check_missing_param_load(
    ir_func: IRFunction,
    report: AnalysisReport,
) -> None:
    """P007 — parameter declared but no LOAD in entry block."""

    loaded: set[str] = set()

    if ir_func.blocks:

        for instr in ir_func.blocks[0].instructions:

            if (
                instr.op == IROpcode.LOAD
                and instr.operands
            ):

                loaded.add(
                    instr.operands[0]
                )

    for param in ir_func.params:

        if (
            param not in loaded
            and param != "self"
        ):

            report.add(
                PatternFinding(
                    pattern_id="P007",
                    severity="info",
                    function_name=ir_func.name,
                    message=(
                        f"Parameter {param!r} has "
                        "no corresponding LOAD "
                        "in the entry block."
                    ),
                    lineno=ir_func.source_lineno,
                )
            )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def detect_patterns(
    ir_module: IRModule,
    dfa_results: Optional[List[DFAResult]] = None,
) -> AnalysisReport:
    """
    Run all pattern-detection checks over the IRModule.

    Args:
        ir_module:
            IRModule produced by ``ir_builder.build_ir()``.

        dfa_results:
            Optional list of DFAResult objects.

    Returns:
        AnalysisReport with all discovered findings.
    """

    report = AnalysisReport(
        source_file=ir_module.source_file
    )

    # Build lookup:
    # function name -> DFA result
    dfa_map: Dict[str, DFAResult] = {}

    if dfa_results:

        for dr in dfa_results:

            dfa_map[
                dr.function_name
            ] = dr

    # Run all pattern detectors
    for ir_func in ir_module.functions:

        dfa = dfa_map.get(
            ir_func.name
        )

        _check_unused_variables(
            ir_func,
            dfa,
            report
        )

        _check_high_complexity(
            ir_func,
            report
        )

        _check_dead_blocks(
            ir_func,
            report
        )

        _check_no_return_value(
            ir_func,
            report
        )

        _check_deeply_nested_loops(
            ir_func,
            report
        )

        _check_excessive_calls(
            ir_func,
            report
        )

        _check_missing_param_load(
            ir_func,
            report
        )

    # Sort findings
    report.findings.sort(
        key=lambda f: (
            f.function_name,
            f.lineno,
            f.pattern_id
        )
    )

    # ============================================================
    # NEW: Calculate code quality
    # ============================================================

    report.quality_distribution = (
        report.quality_percentages(
            total_functions=len(
                ir_module.functions
            )
        )
    )

    return report