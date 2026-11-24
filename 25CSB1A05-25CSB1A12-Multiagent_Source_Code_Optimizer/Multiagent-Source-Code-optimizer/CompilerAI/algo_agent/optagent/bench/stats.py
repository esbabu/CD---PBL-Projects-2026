"""Statistical utilities for benchmark analysis: medians, bootstrap CI, and significance."""
from __future__ import annotations

import numpy as np
from .schemas import BenchStats


def bootstrap_ci(
    data: list[float] | np.ndarray,
    n_boot: int = 1000,
    ci: float = 0.95,
    rng: np.random.Generator | None = None,
) -> tuple[float, float]:
    """Compute empirical bootstrap confidence interval for the median."""
    arr = np.asarray(data, dtype=float)
    if len(arr) == 0:
        return 0.0, 0.0
    if len(arr) == 1:
        return float(arr[0]), float(arr[0])

    if rng is None:
        rng = np.random.default_rng(20240607)

    n = len(arr)
    # Resample with replacement
    indices = rng.integers(0, n, size=(n_boot, n))
    samples = arr[indices]
    medians = np.median(samples, axis=1)

    low_p = (1.0 - ci) / 2.0 * 100.0
    high_p = (1.0 + ci) / 2.0 * 100.0

    low_val = float(np.percentile(medians, low_p))
    high_val = float(np.percentile(medians, high_p))
    return low_val, high_val


def compute_bench_stats(samples: list[float]) -> BenchStats:
    """Compute statistical metrics over multiple runtime repetitions."""
    if not samples:
        return BenchStats()

    arr = np.asarray(samples, dtype=float)
    mean_val = float(np.mean(arr))
    median_val = float(np.median(arr))
    std_val = float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0
    p5_val = float(np.percentile(arr, 5))
    p95_val = float(np.percentile(arr, 95))
    ci_low, ci_high = bootstrap_ci(arr)

    return BenchStats(
        mean=round(mean_val, 6),
        median=round(median_val, 6),
        std=round(std_val, 6),
        p5=round(p5_val, 6),
        p95=round(p95_val, 6),
        ci_low=round(ci_low, 6),
        ci_high=round(ci_high, 6),
        n_samples=len(samples),
    )


def is_speedup_significant(
    orig_time: float,
    cand_stats: BenchStats,
    noise_threshold: float = 0.05,
) -> bool:
    """Check if speedup is statistically significant beyond the noise threshold.
    
    A speedup is significant if the upper confidence bound of the candidate runtime
    is strictly below the original runtime with noise margin.
    """
    if orig_time <= 0 or cand_stats.median <= 0:
        return False

    # Check that candidate's high CI is below orig_time by at least noise_threshold
    threshold_time = orig_time * (1.0 - noise_threshold)
    return cand_stats.ci_high < threshold_time

