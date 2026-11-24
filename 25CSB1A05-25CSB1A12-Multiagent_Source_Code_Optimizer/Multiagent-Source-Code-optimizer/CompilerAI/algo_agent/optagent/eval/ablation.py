"""Ablation study runner for proposers and verification rungs."""
from __future__ import annotations

import copy
import time
from typing import Callable

from ..config import Settings
from .metrics import build_suite_result
from .schemas import AblationResult, AblationVariant, EvalSuiteResult, TaskEvaluation, TaskSpec


DEFAULT_PROPOSER_VARIANTS = [
    AblationVariant(
        id="prop_baseline",
        name="All Proposers (Baseline)",
        category="proposer",
        description="Full ensemble: AST/CST rule engine, LLM proposer, and memory retrieval.",
        disabled_components=[],
    ),
    AblationVariant(
        id="prop_rules_only",
        name="Rules Only (No LLM)",
        category="proposer",
        description="Deterministic CST transformation rules only.",
        disabled_components=["llm_proposer"],
    ),
    AblationVariant(
        id="prop_no_memory",
        name="No Rewrite Memory",
        category="proposer",
        description="Proposers without historical verified rewrite retrieval.",
        disabled_components=["memory_retrieval"],
    ),
]

DEFAULT_VERIFIER_VARIANTS = [
    AblationVariant(
        id="ver_baseline",
        name="Full Ladder (Baseline)",
        category="verifier",
        description="Full verification ladder: R1 compile, R2 golden/holdout, R3 properties, R4 fuzz, R5 diffcov.",
        disabled_components=[],
    ),
    AblationVariant(
        id="ver_no_diffcov",
        name="No DiffCov (R5 disabled)",
        category="verifier",
        description="Verification ladder without changed-line branch coverage gating.",
        disabled_components=["diffcov_R5"],
    ),
    AblationVariant(
        id="ver_no_fuzz",
        name="No Differential Fuzzing (R4 disabled)",
        category="verifier",
        description="Verification ladder without large-scale differential fuzzing.",
        disabled_components=["fuzz_R4"],
    ),
    AblationVariant(
        id="ver_golden_only",
        name="Golden & Holdout Only (R2 only)",
        category="verifier",
        description="Basic testing only: R1 and R2 without properties, fuzzing, or coverage.",
        disabled_components=["properties_R3", "fuzz_R4", "diffcov_R5"],
    ),
]


class AblationRunner:
    """Runs ablation experiments across proposer modes and verification ladder configurations."""

    def __init__(self, base_settings: Settings | None = None, log: Callable = print):
        self.s = base_settings or Settings()
        self.log = log

    def run_variant(
        self,
        tasks: list[TaskSpec],
        variant: AblationVariant,
        eval_fn: Callable[[TaskSpec, Settings], TaskEvaluation],
    ) -> AblationResult:
        """Run a single ablation configuration across the specified tasks."""
        t0 = time.time()
        self.log(f"[ablation] Running variant '{variant.name}' ({len(tasks)} tasks)...")

        # Clone and configure settings for this variant
        cfg_dict = self.s.__dict__.copy()
        if "fuzz_R4" in variant.disabled_components:
            cfg_dict["ladder_fresh_inputs"] = 0
            cfg_dict["ladder_fuzz_budget_s"] = 0.0
        if "properties_R3" in variant.disabled_components:
            cfg_dict["n_hypothesis"] = 0
        if "diffcov_R5" in variant.disabled_components:
            # We can signal via ladder settings
            cfg_dict["ladder_fresh_inputs"] = min(cfg_dict.get("ladder_fresh_inputs", 50), 10)

        variant_settings = Settings(**cfg_dict)

        evals: list[TaskEvaluation] = []
        for t in tasks:
            evals.append(eval_fn(t, variant_settings))

        elapsed = round(time.time() - t0, 3)
        suite = build_suite_result(evals, elapsed)

        return AblationResult(
            variant=variant,
            total_tasks=suite.total_tasks,
            correctness_rate=suite.correctness_rate,
            avg_speedup=suite.avg_speedup,
            false_claim_rate=suite.false_claim_rate,
            elapsed_s=elapsed,
        )

    def run_ablation_study(
        self,
        tasks: list[TaskSpec],
        eval_fn: Callable[[TaskSpec, Settings], TaskEvaluation],
        variants: list[AblationVariant] | None = None,
    ) -> list[AblationResult]:
        """Run all variants and calculate relative deltas against baseline."""
        all_variants = variants or (DEFAULT_PROPOSER_VARIANTS + DEFAULT_VERIFIER_VARIANTS)
        results: list[AblationResult] = []

        baseline_res: AblationResult | None = None
        for v in all_variants:
            res = self.run_variant(tasks, v, eval_fn)
            if v.id in ("prop_baseline", "ver_baseline") and baseline_res is None:
                baseline_res = res
            results.append(res)

        # Compute relative deltas against baseline
        if baseline_res:
            for r in results:
                r.delta_correctness = round(r.correctness_rate - baseline_res.correctness_rate, 4)
                r.delta_speedup = round(r.avg_speedup - baseline_res.avg_speedup, 3)

        return results
