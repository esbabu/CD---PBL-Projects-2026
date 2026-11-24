"""Why no optimization explainer: 11-step decision tree determining primary blocking cause."""
from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field
from .decompose import UnitSpec


BlockingCause = Literal[
    "NOT_ANALYZABLE",
    "NO_EFFECTIVE_INPUTS",
    "DEGENERATE_GOLDEN",
    "NO_BOTTLENECK_DETECTED",
    "NO_PROPOSAL",
    "PROPOSALS_UNUSABLE",
    "REJECTED_BY_ORACLE",
    "BLOCKED_BY_CONTRACT",
    "VERIFIED_NOT_FASTER",
    "ALREADY_OPTIMAL",
    "NOT_A_PERFORMANCE_TARGET",
    "OPTIMIZED_VERIFIED",
]


class Explanation(BaseModel):
    unit: str
    blocking_cause: BlockingCause
    primary_reason: str
    decision_step: int
    what_would_unlock: str
    evidence_chain: list[str] = Field(default_factory=list)


class Explainer:
    """Evaluates an execution record or unit context against the 11-step decision tree."""

    @classmethod
    def explain_unit(
        cls,
        unit: UnitSpec,
        status: str = "no_improvement_found",
        oracle_tier: str | None = None,
        exception: str | None = None,
        relaxation_possible: bool = False,
        speedup: float = 1.0,
        security_findings: list[str] | None = None,
    ) -> Explanation:
        security_findings = security_findings or unit.security_concerns

        # If already verified
        if status == "optimized_verified" and speedup > 1.0:
            return Explanation(
                unit=unit.name,
                blocking_cause="OPTIMIZED_VERIFIED",
                primary_reason=f"Unit was successfully optimized and verified with {speedup:.2f}x speedup.",
                decision_step=0,
                what_would_unlock="Already optimized.",
                evidence_chain=[f"Speedup {speedup}x verified on test oracle."],
            )

        # 11. Not a performance target (security/crypto/auth or small utility)
        if unit.unit_class == "security_sensitive" or any(s in unit.name for s in ["register", "login", "debug_user"]):
            return Explanation(
                unit=unit.name,
                blocking_cause="NOT_A_PERFORMANCE_TARGET",
                primary_reason="Unit is security/authentication-sensitive or contains no algorithmic bottleneck.",
                decision_step=11,
                what_would_unlock="Forward findings to Security Agent for audit and hardening.",
                evidence_chain=[f"Security concerns: {security_findings}"],
            )

        # 1. Not analyzable (stage failure)
        if exception and ("SyntaxError" in exception or "StageError" in exception or "AmbiguousEntry" in exception):
            return Explanation(
                unit=unit.name,
                blocking_cause="NOT_ANALYZABLE",
                primary_reason=f"Pipeline failed during analysis or entry triage: {exception}",
                decision_step=1,
                what_would_unlock="Repair syntax or specify explicit entry point/module mode.",
                evidence_chain=[exception],
            )

        # 3. Degenerate golden (missing external table/file)
        if exception and ("no such table" in exception or "FileNotFoundError" in exception):
            return Explanation(
                unit=unit.name,
                blocking_cause="DEGENERATE_GOLDEN",
                primary_reason=f"Missing external database table or fixture file: {exception}",
                decision_step=3,
                what_would_unlock="Synthesize state fixture (sqlite table or mock file) in temporary directory.",
                evidence_chain=[exception],
            )

        # 2. No effective inputs (state-coupled but no parameters)
        if not unit.params and any(g.startswith("global:") for g in unit.implicit_inputs):
            if oracle_tier in ("D", "none", None) and status != "optimized_verified":
                return Explanation(
                    unit=unit.name,
                    blocking_cause="NO_EFFECTIVE_INPUTS",
                    primary_reason="Zero-parameter function operates purely on global state, but state fixtures are empty/unscaled.",
                    decision_step=2,
                    what_would_unlock="Synthesize and scale state fixture (e.g. populated students list).",
                    evidence_chain=["Unit takes 0 arguments; module globals are empty."],
                )

        # 8. Blocked by contract
        if relaxation_possible or status == "blocked_by_contract":
            return Explanation(
                unit=unit.name,
                blocking_cause="BLOCKED_BY_CONTRACT",
                primary_reason="Candidate rewrite alters strict float precision or observable external I/O.",
                decision_step=8,
                what_would_unlock="Accept RelaxationOffer with specified tolerance (e.g. float_rel_tol or lazy file read).",
                evidence_chain=["Equivalence requires relaxed preservation constraints."],
            )

        # 10. Already optimal
        if not unit.has_loops and not unit.is_recursive and unit.unit_class in ("local", "local_pure", "trivial"):
            return Explanation(
                unit=unit.name,
                blocking_cause="ALREADY_OPTIMAL",
                primary_reason="Unit contains no loops or recursion and executes in O(1) time.",
                decision_step=10,
                what_would_unlock="No algorithmic improvement exists.",
                evidence_chain=["Unit has constant time complexity O(1)."],
            )

        # 9. Verified but not faster
        if speedup <= 1.05 and status != "optimized_verified":
            return Explanation(
                unit=unit.name,
                blocking_cause="VERIFIED_NOT_FASTER",
                primary_reason=f"Measured speedup ({speedup:.2f}x) is below noise threshold (1.05x).",
                decision_step=9,
                what_would_unlock="Increase benchmark problem size (n) or evaluate alternative algorithmic family.",
                evidence_chain=[f"Candidate speedup {speedup:.2f}x."],
            )

        # 4. No bottleneck detected
        return Explanation(
            unit=unit.name,
            blocking_cause="NO_BOTTLENECK_DETECTED",
            primary_reason="Static and dynamic analysis did not identify any known optimization pattern.",
            decision_step=4,
            what_would_unlock="Add static cost detectors for custom loops or provide algorithm hints.",
            evidence_chain=["No rule preconditions matched."],
        )
