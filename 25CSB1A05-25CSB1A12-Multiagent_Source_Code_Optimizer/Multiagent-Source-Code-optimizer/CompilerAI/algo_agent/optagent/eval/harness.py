"""Evaluation harness for benchmark suites, regression tracking, ablations, and self-improvement."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Callable

from ..agent import OptimizerAgent, OptimizeRequest
from ..config import Settings
from .ablation import AblationRunner
from .metrics import build_suite_result, detect_asymptotic_improvement
from .schemas import (
    AblationResult,
    AblationVariant,
    EvalSuiteResult,
    PreferencePair,
    ProgramCost,
    TaskEvaluation,
    TaskSpec,
)
from .self_improve import PreferenceHarvester

EXAMPLES_DIR = Path(__file__).resolve().parents[2] / "examples"


class EvalHarness:
    """Evaluates the algorithm optimization pipeline across standard benchmarks."""

    def __init__(self, settings: Settings | None = None, log: Callable = print):
        self.s = settings or Settings()
        self.log = log

    def evaluate_task(self, task: TaskSpec, custom_settings: Settings | None = None) -> TaskEvaluation:
        """Run optimization on a task and calculate correctness, speedup, and false claims."""
        t0 = time.time()
        self.log(f"[eval] Evaluating task: {task.name} ({task.benchmark})...")
        s = custom_settings or self.s
        agent = OptimizerAgent(s, log=lambda *a: None)
        req = OptimizeRequest(
            source=task.source,
            entry=task.entry,
            overrides=task.overrides,
            use_llm=False,
        )
        res = agent.run(req)
        elapsed = round(time.time() - t0, 3)

        if res.status != "ok" or not res.report:
            return TaskEvaluation(
                name=task.name,
                benchmark=task.benchmark,
                verified=False,
                evidence_tier="REJECTED",
                speedup=1.0,
                mem_ratio=1.0,
                asymptotic_improved=False,
                false_claim=False,
                elapsed_s=elapsed,
                passed_oracle=False,
                cost=ProgramCost(candidates_explored=1, elapsed_s=elapsed),
                failure_reason=res.message or "Pipeline returned error status",
            )

        rep = res.report
        passed_oracle = rep.evidence_tier in ("T1", "T2", "T3", "T4")
        verified = passed_oracle and rep.overall_speedup > 1.0

        b_time = rep.complexity.before_time
        a_time = rep.complexity.after_time
        asymp = detect_asymptotic_improvement(b_time, a_time)

        # False claim detection: speedup claimed (>1.0) but failed oracle
        false_claim = (rep.overall_speedup > 1.05 and not passed_oracle)

        # Calculate exploration cost
        candidates_count = len(rep.rejected_candidates) + (1 if rep.evidence_tier != "REJECTED" else 0)
        cost = ProgramCost(
            candidates_explored=max(candidates_count, 1),
            elapsed_s=elapsed,
            llm_calls=0,
            estimated_cost_usd=0.0,
        )

        return TaskEvaluation(
            name=task.name,
            benchmark=task.benchmark,
            verified=verified,
            evidence_tier=rep.evidence_tier,
            speedup=rep.overall_speedup,
            mem_ratio=rep.overall_mem_ratio,
            asymptotic_improved=asymp,
            complexity_before=b_time,
            complexity_after=a_time,
            false_claim=false_claim,
            elapsed_s=elapsed,
            passed_oracle=passed_oracle,
            cost=cost,
        )

    def run_suite(
        self,
        tasks: list[TaskSpec],
        custom_settings: Settings | None = None,
        run_ablations: bool = False,
        harvest_prefs: bool = False,
    ) -> EvalSuiteResult:
        """Run evaluation across all tasks in the suite, with optional ablations and preference harvesting."""
        t0 = time.time()
        evals: list[TaskEvaluation] = []
        for t in tasks:
            evals.append(self.evaluate_task(t, custom_settings=custom_settings))

        total_elapsed = round(time.time() - t0, 3)

        ablations_res: list[AblationResult] = []
        if run_ablations:
            ab_runner = AblationRunner(custom_settings or self.s, log=self.log)
            ablations_res = ab_runner.run_ablation_study(
                tasks,
                eval_fn=lambda t, s: self.evaluate_task(t, custom_settings=s),
            )

        prefs: list[PreferencePair] = []
        if harvest_prefs:
            harvester = PreferenceHarvester()
            for t in tasks:
                # Run search to get trajectories
                agent = OptimizerAgent(custom_settings or self.s, log=lambda *a: None)
                req = OptimizeRequest(source=t.source, entry=t.entry, overrides=t.overrides, use_llm=False)
                res = agent.run(req)
                if res.status == "ok" and res.report:
                    # In a full run, search_res can be passed; synthesize if not directly exposed
                    pass

        return build_suite_result(
            evals,
            elapsed_s=total_elapsed,
            ablations=ablations_res,
            preference_pairs=prefs,
        )

    def run_ablation_study(
        self,
        tasks: list[TaskSpec],
        variants: list[AblationVariant] | None = None,
    ) -> list[AblationResult]:
        """Execute ablation experiments on proposers and verifier ladder rungs."""
        runner = AblationRunner(self.s, log=self.log)
        return runner.run_ablation_study(
            tasks,
            eval_fn=lambda t, s: self.evaluate_task(t, custom_settings=s),
            variants=variants,
        )

    @classmethod
    def get_regression_suite(cls) -> list[TaskSpec]:
        """Permanent regression suite from project examples."""
        from .adapter import load_task_from_files

        two_sum_task = load_task_from_files(
            EXAMPLES_DIR / "slow_two_sum.py",
            name="slow_two_sum",
            benchmark="regression",
        )
        two_sum_task.expected_speedup_min = 2.0
        two_sum_task.expected_asymptotic_improvement = True

        dedupe_task = load_task_from_files(
            EXAMPLES_DIR / "dedupe_rank.py",
            overrides_path=EXAMPLES_DIR / "dedupe_rank_overrides.yaml",
            name="dedupe_rank",
            benchmark="regression",
        )
        dedupe_task.expected_speedup_min = 2.0

        return [two_sum_task, dedupe_task]

    @staticmethod
    def save_suite_result(result: EvalSuiteResult, path: str | Path) -> None:
        """Serialize evaluation suite result to disk."""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(result.model_dump_json(indent=2), encoding="utf-8")

    @staticmethod
    def load_suite_result(path: str | Path) -> EvalSuiteResult:
        """Load evaluation suite result from disk."""
        p = Path(path)
        return EvalSuiteResult.model_validate_json(p.read_text(encoding="utf-8"))
