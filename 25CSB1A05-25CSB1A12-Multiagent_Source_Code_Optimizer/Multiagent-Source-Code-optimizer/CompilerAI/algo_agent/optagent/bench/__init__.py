"""Step 6 Benchmarking: measurements, bootstrap confidence intervals, and crossover detection."""
from .runner import BenchmarkRunner
from .schemas import BenchmarkResult, BenchStats, FamilyBench, SizeMeasurement
from .stats import bootstrap_ci, compute_bench_stats, is_speedup_significant

__all__ = [
    "BenchmarkRunner",
    "BenchmarkResult",
    "BenchStats",
    "FamilyBench",
    "SizeMeasurement",
    "bootstrap_ci",
    "compute_bench_stats",
    "is_speedup_significant",
]

