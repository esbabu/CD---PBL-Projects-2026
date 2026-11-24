"""Search controller for algorithm optimization: Pareto front and beam search."""
from __future__ import annotations

import time
from typing import Callable

from ..bench.runner import BenchmarkRunner
from ..bench.schemas import BenchmarkResult
from ..complexity.schemas import AnalysisBundle
from ..config import Settings
from ..oracle.oracle import Oracle
from ..proposers.ensemble import ProposerEnsemble
from ..proposers.schemas import Candidate
from ..verify.ladder import Ladder
from ..verify.schemas import Evidence
from .schemas import ParetoPoint, SearchBudget, SearchNode, SearchResult


def update_pareto_front(front: list[ParetoPoint], new_pt: ParetoPoint) -> list[ParetoPoint]:
    """Maintain the non-dominated Pareto front over (speedup, memory_reduction)."""
    # Check if new_pt is dominated by any existing point
    for pt in front:
        if pt.speedup >= new_pt.speedup and pt.mem_ratio <= new_pt.mem_ratio:
            if pt.speedup > new_pt.speedup or pt.mem_ratio < new_pt.mem_ratio:
                return front  # dominated, discard new_pt

    # Retain only points not dominated by new_pt
    survivors: list[ParetoPoint] = []
    for pt in front:
        if new_pt.speedup >= pt.speedup and new_pt.mem_ratio <= pt.mem_ratio:
            if new_pt.speedup > pt.speedup or new_pt.mem_ratio < pt.mem_ratio:
                continue  # existing pt is dominated by new_pt
        survivors.append(pt)

    survivors.append(new_pt)
    return survivors


class SearchController:
    """Orchestrates candidate generation, verification, and benchmarking to find optimal rewrites."""

    def __init__(
        self,
        oracle: Oracle,
        analysis: AnalysisBundle,
        proposers: ProposerEnsemble,
        ladder: Ladder,
        bench: BenchmarkRunner,
        settings: Settings | None = None,
        log: Callable = print,
    ):
        self.oracle = oracle
        self.analysis = analysis
        self.proposers = proposers
        self.ladder = ladder
        self.bench = bench
        self.s = settings or oracle.s
        self.log = log

    def run(self, budget: SearchBudget | None = None) -> SearchResult:
        """Execute the optimization search within budget constraints."""
        t0 = time.time()
        budget = budget or SearchBudget(
            max_candidates=self.s.search_max_candidates,
            max_time_s=self.s.search_budget_s,
            beam_width=self.s.search_beam_width,
        )

        intent = self.oracle.intent()
        orig_source = self.oracle.orig.read_text(encoding="utf-8")

        # Baseline point on the Pareto front
        baseline_pt = ParetoPoint(
            candidate_id="baseline",
            source=orig_source,
            speedup=1.0,
            mem_ratio=1.0,
            evidence_tier=getattr(self.oracle.b.strength, "tier", "D"),
            time_complexity=self.analysis.overall_time or "",
            space_complexity=self.analysis.overall_space or "",
            reward=1.0,
        )
        pareto_front: list[ParetoPoint] = [baseline_pt]
        evaluated_nodes: list[SearchNode] = []
        seen_sources: set[str] = {orig_source.strip()}

        iterations = 0
        stop_reason = "exhausted"
        feedback: str | None = None

        while iterations < self.s.search_max_depth:
            iterations += 1
            if time.time() - t0 > budget.max_time_s:
                stop_reason = "time_budget"
                break
            if len(evaluated_nodes) >= budget.max_candidates:
                stop_reason = "candidate_budget"
                break

            self.log(f"[search] Iteration {iterations}: proposing candidates...")
            candidates = self.proposers.propose_candidates(intent, self.analysis, feedback=feedback)
            if not candidates:
                self.log("[search] No new candidates emitted.")
                break

            new_benchmarked: list[SearchNode] = []

            for cand in candidates:
                cand_code = cand.source.strip()
                if cand_code in seen_sources:
                    continue
                seen_sources.add(cand_code)

                if len(evaluated_nodes) >= budget.max_candidates:
                    stop_reason = "candidate_budget"
                    break
                if time.time() - t0 > budget.max_time_s:
                    stop_reason = "time_budget"
                    break

                self.log(f"[search] Verifying candidate {cand.id} ({cand.proposer})...")
                evidence = self.ladder.verify(cand.source)

                if not evidence.passed:
                    self.log(f"[search] Candidate {cand.id} failed verification: {evidence.feedback[:60]}")
                    node = SearchNode(
                        candidate=cand,
                        evidence=evidence,
                        reward=0.0,
                        status="rejected",
                    )
                    evaluated_nodes.append(node)
                    feedback = evidence.feedback
                    continue

                # Candidate verified! Benchmark it
                self.log(f"[search] Candidate {cand.id} verified at tier {evidence.tier}! Benchmarking...")
                bench_res = self.bench.run(cand.source)
                self.log(f"[search] Candidate {cand.id} speedup: {bench_res.overall_speedup}x, mem: {bench_res.overall_mem_ratio}x")

                tier_mult = {"T0": 0.5, "T1": 1.0, "T2": 1.5, "T3": 2.0, "T4": 2.5}.get(evidence.tier, 1.0)
                speedup_score = max(bench_res.overall_speedup, 0.1)
                mem_score = max(0.2, 1.0 / max(bench_res.overall_mem_ratio, 0.01)) ** 0.5
                reward = round(speedup_score * mem_score * tier_mult, 3)

                node = SearchNode(
                    candidate=cand,
                    evidence=evidence,
                    bench=bench_res,
                    reward=reward,
                    status="benchmarked",
                )
                evaluated_nodes.append(node)
                new_benchmarked.append(node)

                # Update Pareto front
                pt = ParetoPoint(
                    candidate_id=cand.id,
                    source=cand.source,
                    speedup=bench_res.overall_speedup,
                    mem_ratio=bench_res.overall_mem_ratio,
                    evidence_tier=evidence.tier,
                    time_complexity=cand.claimed_time or "",
                    space_complexity=cand.claimed_space or "",
                    reward=reward,
                )
                pareto_front = update_pareto_front(pareto_front, pt)

            if not new_benchmarked:
                break

        # Select best candidate from pareto front (highest reward that improves on baseline)
        valid_points = [p for p in pareto_front if p.candidate_id != "baseline" and p.speedup > 1.0]
        if valid_points:
            best_point = max(valid_points, key=lambda p: p.reward)
            # Find the candidate matching best_point
            best_cand = next((n.candidate for n in evaluated_nodes if n.candidate.id == best_point.candidate_id), None)
        else:
            best_cand = None

        return SearchResult(
            best_candidate=best_cand,
            pareto_front=pareto_front,
            all_evaluated=evaluated_nodes,
            iterations=iterations,
            stop_reason=stop_reason,
            elapsed_s=round(time.time() - t0, 3),
        )

