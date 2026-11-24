"""Benchmark runner for measuring runtime speedup and memory reduction."""
from __future__ import annotations

import math
import time
from collections import defaultdict
from pathlib import Path
from typing import Callable

from ..complexity.profiler import ProfileSandbox
from ..config import Settings
from ..oracle.oracle import Oracle
from ..oracle.scaling import scale_case
from ..oracle.schemas import ScalePoint
from ..runtime.sandbox import RunOpts
from .schemas import BenchmarkResult, FamilyBench, SizeMeasurement
from .stats import compute_bench_stats, is_speedup_significant


class BenchmarkRunner:
    """Executes high-precision benchmarks comparing a verified candidate to the original."""

    def __init__(self, oracle: Oracle, settings: Settings | None = None,
                 log: Callable = print):
        self.oracle = oracle
        self.s = settings or oracle.s
        self.log = log
        self.prof_sb = ProfileSandbox(self.s)

    def run(self, candidate_source: str, *, reps: int | None = None,
            warmups: int | None = None) -> BenchmarkResult:
        """Run benchmark scaling tests on candidate against the original.

        Uses single-process execution (run_batch) to prevent multiprocess timing distortion.
        """
        t0 = time.time()
        s = self.s
        reps = reps if reps is not None else s.bench_reps
        warmups = warmups if warmups is not None else s.bench_warmups

        cand_path = self.oracle._path_for(candidate_source)
        scaling_pts = [p for p in self.oracle.b.scaling if p.status in ("ok", "exception") and p.orig_time_s]

        # Group scaling points by family
        by_family: dict[str, list[ScalePoint]] = defaultdict(list)
        for p in scaling_pts:
            by_family[p.family].append(p)

        families_res: dict[str, FamilyBench] = {}
        max_n_speedups: list[float] = []
        crossovers: list[int] = []

        largest_cases = []

        for fam, pts in by_family.items():
            pts_sorted = sorted(pts, key=lambda x: x.n)
            measurements: list[SizeMeasurement] = []
            fam_crossover: int | None = None

            for p in pts_sorted:
                case = scale_case(self.oracle.ps, p)
                if p == pts_sorted[-1]:
                    largest_cases.append(case)

                # Warmup runs (single process)
                for _ in range(warmups):
                    self.oracle.sb.run_batch(cand_path, self.oracle.entry, [case],
                                             RunOpts(timeout=s.scale_timeout_s))

                # Timed repetitions
                times: list[float] = []
                for _ in range(reps):
                    res = self.oracle.sb.run_batch(cand_path, self.oracle.entry, [case],
                                                   RunOpts(timeout=s.scale_timeout_s))
                    if res and res[0].status == "ok" and res[0].elapsed_s is not None:
                        times.append(res[0].elapsed_s)

                if not times:
                    continue

                stats = compute_bench_stats(times)
                speedup = (p.orig_time_s / stats.median) if stats.median > 0 else 1.0
                is_sig = is_speedup_significant(p.orig_time_s, stats, s.bench_noise_threshold)

                measurements.append(
                    SizeMeasurement(
                        family=fam,
                        n=p.n,
                        orig_time_s=p.orig_time_s,
                        cand_stats=stats,
                        speedup=round(speedup, 3),
                        is_significant=is_sig,
                    )
                )

                if fam_crossover is None and speedup > 1.0 and is_sig:
                    fam_crossover = p.n

            if measurements:
                max_sp = measurements[-1].speedup
                max_n_speedups.append(max_sp)
                if fam_crossover is not None:
                    crossovers.append(fam_crossover)

                families_res[fam] = FamilyBench(
                    family=fam,
                    points=measurements,
                    crossover_n=fam_crossover,
                    max_n_speedup=max_sp,
                )

        # Memory evaluation on largest inputs (Python tracemalloc profiler only)
        overall_mem_ratio = 1.0
        is_python = getattr(self.oracle.b, "language", "python") == "python"
        if largest_cases and is_python and self.oracle.entry != "__script__":
            orig_prof = self.prof_sb.run_profile_batch(self.oracle.orig, self.oracle.entry, largest_cases[:2])
            cand_prof = self.prof_sb.run_profile_batch(cand_path, self.oracle.entry, largest_cases[:2])
            if orig_prof and cand_prof:
                o_mem = max((r.get("peak_memory_bytes") or 0) for r in orig_prof)
                c_mem = max((r.get("peak_memory_bytes") or 0) for r in cand_prof)
                if o_mem > 0:
                    overall_mem_ratio = round(c_mem / o_mem, 3)

        # Overall speedup: geometric mean across families at max n
        if max_n_speedups:
            log_sum = sum(math.log(max(sp, 0.001)) for sp in max_n_speedups)
            overall_speedup = round(math.exp(log_sum / len(max_n_speedups)), 3)
        else:
            overall_speedup = 1.0

        min_crossover = min(crossovers) if crossovers else None

        # Noise check: reject speedups within the noise threshold margin
        is_significant = overall_speedup > (1.0 + s.bench_noise_threshold)
        noise_rejected = not is_significant and overall_speedup > 1.0

        return BenchmarkResult(
            families=families_res,
            overall_speedup=overall_speedup,
            overall_mem_ratio=overall_mem_ratio,
            crossover_n=min_crossover,
            is_significant=is_significant,
            noise_rejected=noise_rejected,
            elapsed_s=round(time.time() - t0, 3),
        )

