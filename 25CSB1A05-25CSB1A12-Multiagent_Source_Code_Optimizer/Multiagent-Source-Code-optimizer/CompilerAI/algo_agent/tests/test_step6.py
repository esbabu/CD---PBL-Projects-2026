"""Tests for Step 6: Benchmark runner and search controller."""
from __future__ import annotations

from pathlib import Path
import pytest

from optagent.bench.runner import BenchmarkRunner
from optagent.bench.schemas import BenchmarkResult
from optagent.bench.stats import bootstrap_ci, compute_bench_stats, is_speedup_significant
from optagent.complexity.analyzer import Analyzer
from optagent.config import Settings
from optagent.intent.pipeline import IntentExtractor
from optagent.oracle.builder import OracleBuilder
from optagent.oracle.oracle import Oracle, source_sha
from optagent.proposers.ensemble import ProposerEnsemble
from optagent.search.controller import SearchController, update_pareto_front
from optagent.search.schemas import ParetoPoint, SearchBudget, SearchResult
from optagent.verify.ladder import Ladder

EX = Path(__file__).resolve().parent.parent / "examples"


def fast_settings(tmp_path: Path) -> Settings:
    return Settings(
        sandbox_backend="local",
        runs_dir=str(tmp_path / "runs"),
        n_family=10,
        n_hypothesis=10,
        n_probe=4,
        n_adversarial=4,
        fuzz_budget_s=0.5,
        fuzz_max_rounds=2,
        max_mutants=4,
        scale_sizes=(10, 30),
        ladder_fresh_inputs=50,
        ladder_fuzz_budget_s=0.5,
        bench_warmups=1,
        bench_reps=3,
        search_max_depth=2,
        search_max_candidates=4,
    )


# ---------------------------------------------------------------------------
# 1. Bootstrap CI and Bench Stats
# ---------------------------------------------------------------------------
def test_bootstrap_ci():
    samples = [0.10, 0.11, 0.105, 0.095, 0.102, 0.098]
    low, high = bootstrap_ci(samples, n_boot=200, ci=0.95)
    assert 0.09 <= low <= 0.11
    assert 0.09 <= high <= 0.12
    assert low <= high

    stats = compute_bench_stats(samples)
    assert stats.n_samples == 6
    assert 0.09 <= stats.median <= 0.11
    assert stats.ci_low <= stats.ci_high


def test_bench_stats_and_significance():
    samples = [0.05, 0.052, 0.048, 0.051]
    stats = compute_bench_stats(samples)

    # Orig time 0.10s -> speedup ~2x, significant
    assert is_speedup_significant(orig_time=0.10, cand_stats=stats, noise_threshold=0.05)
    # Orig time 0.053s -> speedup ~1.04x, within noise
    assert not is_speedup_significant(orig_time=0.053, cand_stats=stats, noise_threshold=0.05)


# ---------------------------------------------------------------------------
# 2. Pareto Front maintenance
# ---------------------------------------------------------------------------
def test_pareto_front_updates():
    p1 = ParetoPoint(candidate_id="c1", source="", speedup=2.0, mem_ratio=1.0)
    p2 = ParetoPoint(candidate_id="c2", source="", speedup=1.5, mem_ratio=0.5)
    p3 = ParetoPoint(candidate_id="c3", source="", speedup=1.2, mem_ratio=1.2)  # Dominated by p1 and p2

    front = update_pareto_front([], p1)
    assert len(front) == 1

    front = update_pareto_front(front, p2)
    # p1 and p2 are mutually non-dominating: p1 has better speedup, p2 has better memory
    assert len(front) == 2

    front = update_pareto_front(front, p3)
    # p3 is strictly worse than p1 in speedup and memory -> discarded
    assert len(front) == 2
    assert {p.candidate_id for p in front} == {"c1", "c2"}

    # New point dominating p1:
    p4 = ParetoPoint(candidate_id="c4", source="", speedup=3.0, mem_ratio=0.9)
    front = update_pareto_front(front, p4)
    # p4 dominates p1 (faster and less memory)
    assert "c1" not in {p.candidate_id for p in front}
    assert "c4" in {p.candidate_id for p in front}


# ---------------------------------------------------------------------------
# 3. BenchmarkRunner on Two-Sum
# ---------------------------------------------------------------------------
def test_benchmark_runner_on_two_sum(tmp_path):
    s = fast_settings(tmp_path)
    src = (EX / "slow_two_sum.py").read_text(encoding="utf-8")
    intent = IntentExtractor(s, use_llm=False).run(src, source_name="slow_two_sum.py")
    bundle = OracleBuilder(s, use_llm=False, log=lambda *a: None).build(intent, run_mutation=True)
    oracle = Oracle(bundle, s)

    runner = BenchmarkRunner(oracle, s, log=lambda *a: None)
    cand_src = (EX / "fast_two_sum_right.py").read_text(encoding="utf-8")
    res = runner.run(cand_src, reps=2, warmups=1)

    assert isinstance(res, BenchmarkResult)
    assert res.overall_speedup > 0.0
    assert len(res.families) > 0


# ---------------------------------------------------------------------------
# 4. SearchController End-to-End
# ---------------------------------------------------------------------------
def test_search_controller_end_to_end(tmp_path):
    s = fast_settings(tmp_path)
    src = (EX / "slow_two_sum.py").read_text(encoding="utf-8")
    intent = IntentExtractor(s, use_llm=False).run(src, source_name="slow_two_sum.py")
    bundle = OracleBuilder(s, use_llm=False, log=lambda *a: None).build(intent, run_mutation=True)
    oracle = Oracle(bundle, s)

    analyzer = Analyzer(s, log=lambda *a: None)
    analysis = analyzer.analyze(intent, oracle)

    proposers = ProposerEnsemble(s, use_llm=False)
    ladder = Ladder(oracle, s, log=lambda *a: None)
    bench = BenchmarkRunner(oracle, s, log=lambda *a: None)

    controller = SearchController(oracle, analysis, proposers, ladder, bench, s, log=lambda *a: None)
    budget = SearchBudget(max_candidates=3, max_time_s=30.0)
    search_res = controller.run(budget)

    assert isinstance(search_res, SearchResult)
    assert len(search_res.pareto_front) >= 1
    assert len(search_res.all_evaluated) >= 1
    # Check that best candidate is chosen and verified
    assert search_res.best_candidate is not None
    assert search_res.best_candidate.proposer == "rule_engine"


# ---------------------------------------------------------------------------
# 5. SearchResult model roundtrip
# ---------------------------------------------------------------------------
def test_search_result_model_roundtrip():
    pt = ParetoPoint(candidate_id="c1", source="pass", speedup=2.5, mem_ratio=0.8, evidence_tier="T2")
    res = SearchResult(
        best_candidate=None,
        pareto_front=[pt],
        iterations=1,
        stop_reason="candidate_budget",
        elapsed_s=1.23,
    )
    dumped = res.model_dump_json()
    loaded = SearchResult.model_validate_json(dumped)
    assert loaded.iterations == 1
    assert len(loaded.pareto_front) == 1
    assert loaded.pareto_front[0].speedup == 2.5

