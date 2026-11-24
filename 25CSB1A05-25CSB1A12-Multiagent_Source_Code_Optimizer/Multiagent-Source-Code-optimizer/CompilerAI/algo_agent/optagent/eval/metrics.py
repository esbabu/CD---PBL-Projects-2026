"""Metrics calculation and statistical aggregation for benchmark evaluations."""
from __future__ import annotations

import math
from typing import Sequence
import numpy as np

from .schemas import DistributionStats, EvalSuiteResult, ProgramCost, TaskEvaluation


COMPLEXITY_ORDER = {
    "O(1)": 1,
    "O(log n)": 2,
    "O(n)": 3,
    "O(n log n)": 4,
    "O(n^2)": 5,
    "O(n^2 log n)": 6,
    "O(n^3)": 7,
    "O(2^n)": 8,
    "O(n!)": 9,
}


def compute_distribution(values: Sequence[float]) -> DistributionStats:
    """Compute statistical percentiles, mean, and geometric mean for a sample."""
    if not values:
        return DistributionStats()

    arr = np.array(values, dtype=float)
    min_val = float(np.min(arr))
    max_val = float(np.max(arr))
    mean_val = float(np.mean(arr))
    p25_val = float(np.percentile(arr, 25))
    median_val = float(np.median(arr))
    p75_val = float(np.percentile(arr, 75))
    p90_val = float(np.percentile(arr, 90))

    # Geometric mean on positive numbers (clamped to 1e-4)
    pos_arr = np.maximum(arr, 1e-4)
    geom_mean_val = float(np.exp(np.mean(np.log(pos_arr))))

    return DistributionStats(
        min=round(min_val, 3),
        p25=round(p25_val, 3),
        median=round(median_val, 3),
        p75=round(p75_val, 3),
        p90=round(p90_val, 3),
        max=round(max_val, 3),
        mean=round(mean_val, 3),
        geom_mean=round(geom_mean_val, 3),
    )


def detect_asymptotic_improvement(before: str, after: str) -> bool:
    """Check if after is strictly lower complexity than before."""
    b = before.strip()
    a = after.strip()
    if b == a or not b or not a:
        return False

    order_b = COMPLEXITY_ORDER.get(b, None)
    order_a = COMPLEXITY_ORDER.get(a, None)
    if order_b is not None and order_a is not None:
        return order_a < order_b

    # Fallback heuristic
    if "n^2" in b and ("n log n" in a or a == "O(n)" or a == "O(1)"):
        return True
    if "n^3" in b and ("n^2" in a or "n log n" in a or a == "O(n)"):
        return True
    if "2^n" in b and ("n^" in a or "n" in a):
        return True
    return False


def aggregate_costs(evals: list[TaskEvaluation]) -> ProgramCost:
    """Aggregate total cost metrics across task evaluations."""
    if not evals:
        return ProgramCost()
    total_explored = sum(e.cost.candidates_explored for e in evals)
    total_time = sum(e.elapsed_s for e in evals)
    total_llm = sum(e.cost.llm_calls for e in evals)
    total_prompt = sum(e.cost.llm_tokens_prompt for e in evals)
    total_comp = sum(e.cost.llm_tokens_completion for e in evals)
    total_usd = sum(e.cost.estimated_cost_usd for e in evals)
    n = len(evals)

    return ProgramCost(
        candidates_explored=round(total_explored / n),
        elapsed_s=round(total_time / n, 3),
        llm_calls=round(total_llm / n, 1),
        llm_tokens_prompt=round(total_prompt / n),
        llm_tokens_completion=round(total_comp / n),
        estimated_cost_usd=round(total_usd / n, 4),
    )


def build_suite_result(
    evals: list[TaskEvaluation],
    elapsed_s: float,
    ablations: list | None = None,
    preference_pairs: list | None = None,
) -> EvalSuiteResult:
    """Construct a full EvalSuiteResult model with statistical distributions."""
    total = len(evals)
    if total == 0:
        return EvalSuiteResult(elapsed_s=round(elapsed_s, 3))

    correct_count = sum(1 for e in evals if e.passed_oracle)
    correctness_rate = round(correct_count / total, 4)

    # Speedups for tasks that actually preserved correctness
    speedups = [e.speedup for e in evals if e.passed_oracle]
    speedup_dist = compute_distribution(speedups if speedups else [1.0])
    avg_speedup = speedup_dist.geom_mean if speedups else 1.0

    # Memory ratios
    mem_ratios = [e.mem_ratio for e in evals if e.passed_oracle]
    mem_dist = compute_distribution(mem_ratios if mem_ratios else [1.0])

    # Asymptotic improvements
    asymp_evals = [e for e in evals if e.asymptotic_improved]
    asymp_rate = round(len(asymp_evals) / total, 4)
    transitions = [f"{e.name}: {e.complexity_before} -> {e.complexity_after}" for e in asymp_evals]

    # False claims: speedup claimed (>1.05) or marked verified but failed oracle
    false_claims = sum(1 for e in evals if e.false_claim)
    false_claim_rate = round(false_claims / total, 4)

    avg_cost = aggregate_costs(evals)

    return EvalSuiteResult(
        total_tasks=total,
        correctness_rate=correctness_rate,
        avg_speedup=avg_speedup,
        speedup_distribution=speedup_dist,
        memory_distribution=mem_dist,
        asymptotic_improvement_rate=asymp_rate,
        asymptotic_transitions=transitions,
        false_claim_rate=false_claim_rate,
        task_evaluations=evals,
        avg_cost_per_program=avg_cost,
        ablations=ablations or [],
        preference_pairs=preference_pairs or [],
        elapsed_s=round(elapsed_s, 3),
    )
