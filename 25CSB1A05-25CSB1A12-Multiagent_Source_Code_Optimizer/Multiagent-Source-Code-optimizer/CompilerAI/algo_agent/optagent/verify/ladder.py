"""Verification ladder orchestrator for OptAgent.

Executes verification rungs in ascending order of cost (fail-fast),
grades evidence into T0..T4 tiers, and caps the tier honestly by
the oracle's strength.
"""
from __future__ import annotations

import random
import time
from typing import Any, Callable

from ..config import Settings
from ..oracle.oracle import Counterexample, Oracle
from ..oracle.schemas import Case
from .diffcov import DiffCovResult
from .rungs import (
    run_r1_compile_lint,
    run_r2_golden_holdout,
    run_r3_properties,
    run_r4_differential_fuzz,
    run_r5_diffcov,
    run_r6_symbolic,
    run_r7_formal,
    run_r8_llm_reviewer,
)
from .schemas import Evidence, RungResult


class Ladder:
    """The verification ladder for candidate code transformations."""

    def __init__(self, oracle: Oracle, settings: Settings | None = None,
                 log: Callable = print):
        self.oracle = oracle
        self.s = settings or oracle.s
        self.log = log

    def verify(self, candidate_source: str, *, fresh_override: int | None = None,
               rng: random.Random | None = None) -> Evidence:
        """Run candidate through the verification ladder.

        Returns an Evidence bundle specifying the achieved tier (T0..T4 or REJECTED),
        full rung results, counterexamples if any, and capped_by if capped.
        """
        t0 = time.time()
        rungs: list[RungResult] = []
        warnings: list[str] = []
        executed_lines: set[int] = set()

        # ------------------------------------------------------------------
        # Rung 1: Compile & Lint
        # ------------------------------------------------------------------
        adapter = getattr(self.oracle, "adapter", None)
        is_foreign = adapter is not None and adapter.id != "python"
        if is_foreign:
            from ..lang.pipeline_hooks import run_language_r1
            r1 = run_language_r1(adapter, candidate_source, self.oracle.entry, getattr(self.oracle, "_hints", {}))
        else:
            r1 = run_r1_compile_lint(candidate_source, self.oracle.entry)
        rungs.append(r1)
        if not r1.passed:
            return Evidence(
                tier="REJECTED",
                raw_tier="REJECTED",
                passed=False,
                rungs=rungs,
                feedback=r1.reason,
                elapsed_s=round(time.time() - t0, 3),
            )

        # ------------------------------------------------------------------
        # Rung 2: Golden + Hold-out
        # ------------------------------------------------------------------
        r2, v2, r2_lines = run_r2_golden_holdout(self.oracle, candidate_source)
        rungs.append(r2)
        executed_lines.update(r2_lines)

        if not r2.passed:
            return Evidence(
                tier="REJECTED",
                raw_tier="T0",
                passed=False,
                rungs=rungs,
                counterexamples=v2.counterexamples,
                feedback=v2.feedback or r2.reason,
                elapsed_s=round(time.time() - t0, 3),
            )

        # ------------------------------------------------------------------
        # Rung 3: Properties
        # ------------------------------------------------------------------
        r3 = run_r3_properties(self.oracle, v2)
        rungs.append(r3)
        if not r3.passed:
            return Evidence(
                tier="REJECTED",
                raw_tier="T0",
                passed=False,
                rungs=rungs,
                feedback=r3.reason,
                elapsed_s=round(time.time() - t0, 3),
            )

        # If R1, R2, R3 pass, candidate has passed the baseline oracle!
        raw_tier = "T1"

        # ------------------------------------------------------------------
        # Rung 4: Differential Fuzzing at Scale
        # ------------------------------------------------------------------
        fresh_count = fresh_override if fresh_override is not None else self.s.ladder_fresh_inputs
        r4, ce_r4, r4_lines = run_r4_differential_fuzz(
            self.oracle,
            candidate_source,
            fresh_count=fresh_count,
            fuzz_budget_s=self.s.ladder_fuzz_budget_s,
            rng=rng,
        )
        rungs.append(r4)
        executed_lines.update(r4_lines)

        if not r4.passed:
            # Behavioral discrepancy caught during differential fuzzing!
            feedback_text = (
                f"Differential failure: {r4.reason}\n"
                f"Counterexamples:\n" +
                "\n".join(f"  - Case {ce.case_id}: {ce.violations[0].detail if ce.violations else ''}"
                          for ce in ce_r4)
            )
            return Evidence(
                tier="REJECTED",
                raw_tier="T1",
                passed=False,
                rungs=rungs,
                counterexamples=ce_r4,
                feedback=feedback_text,
                elapsed_s=round(time.time() - t0, 3),
            )

        # ------------------------------------------------------------------
        # Rung 5: Changed-Line Coverage
        # ------------------------------------------------------------------
        orig_source = self.oracle.orig.read_text(encoding="utf-8")
        r5, cov_res = run_r5_diffcov(
            orig_source,
            candidate_source,
            executed_lines,
            min_ratio=self.s.diffcov_min_ratio,
        )
        rungs.append(r5)

        # Qualification for T2:
        # T1 + >= 10^4 fresh differential inputs + 100% changed-line coverage
        # (or fresh_override if provided by caller)
        min_required_fresh = fresh_override if fresh_override is not None else 10000
        qualifies_for_t2 = (
            fresh_count >= min_required_fresh and
            r4.passed and
            r5.passed
        )

        if qualifies_for_t2:
            raw_tier = "T2"

        # ------------------------------------------------------------------
        # Rung 6+: Language-specific extra rungs (Sanitizers, CBMC) or Python symbolic
        # ------------------------------------------------------------------
        if is_foreign:
            from ..lang.pipeline_hooks import cap_tier_by_capability, run_language_extra_rungs
            extra_rungs, extra_ok, granted_tier = run_language_extra_rungs(self.oracle, candidate_source)
            rungs.extend(extra_rungs)
            if not extra_ok:
                fail_r = next((r for r in extra_rungs if not r.passed and not r.skipped), extra_rungs[-1])
                return Evidence(
                    tier="REJECTED",
                    raw_tier=raw_tier,
                    passed=False,
                    rungs=rungs,
                    feedback=fail_r.reason,
                    elapsed_s=round(time.time() - t0, 3),
                )
            if qualifies_for_t2 and granted_tier == "T3":
                raw_tier = "T3"
        else:
            r6 = run_r6_symbolic(self.oracle, candidate_source, enabled=self.s.enable_symbolic)
            rungs.append(r6)
            if qualifies_for_t2 and r6.passed and not r6.skipped:
                raw_tier = "T3"

            # ------------------------------------------------------------------
            # Rung 7: Formal Proof
            # ------------------------------------------------------------------
            r7 = run_r7_formal(enabled=self.s.enable_formal)
            rungs.append(r7)
            if raw_tier == "T3" and r7.passed and not r7.skipped:
                raw_tier = "T4"

        # ------------------------------------------------------------------
        # Rung 8: LLM Reviewer (Advisory Only)
        # ------------------------------------------------------------------
        r8, rev_warnings = run_r8_llm_reviewer(
            candidate_source,
            enabled=self.s.enable_llm_reviewer,
        )
        rungs.append(r8)
        warnings.extend(rev_warnings)

        # ------------------------------------------------------------------
        # Evidence Honesty / Oracle Strength Capping
        # ------------------------------------------------------------------
        strength_tier = getattr(self.oracle.b.strength, "tier", "D")
        final_tier = raw_tier
        capped_by = None

        if strength_tier in ("C", "D"):
            if raw_tier in ("T2", "T3", "T4"):
                final_tier = "T1"
                capped_by = f"oracle strength tier {strength_tier} (cannot exceed T1)"

        if is_foreign:
            from ..lang.pipeline_hooks import cap_tier_by_capability
            final_tier, cap_reason = cap_tier_by_capability(final_tier, adapter.caps.max_evidence_tier)
            if cap_reason:
                capped_by = cap_reason

        return Evidence(
            tier=final_tier,
            raw_tier=raw_tier,
            capped_by=capped_by,
            passed=True,
            rungs=rungs,
            counterexamples=[],
            warnings=warnings,
            feedback=f"Passed verification at tier {final_tier} (raw: {raw_tier})",
            elapsed_s=round(time.time() - t0, 3),
        )
