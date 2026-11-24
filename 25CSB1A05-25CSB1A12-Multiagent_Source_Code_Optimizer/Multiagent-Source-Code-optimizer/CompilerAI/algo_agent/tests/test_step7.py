"""Tests for Step 7: Reporter and persistent rewrite memory."""
from __future__ import annotations

import json
from pathlib import Path
import pytest

from optagent.bench.runner import BenchmarkRunner
from optagent.complexity.analyzer import Analyzer
from optagent.config import Settings
from optagent.intent.pipeline import IntentExtractor
from optagent.memory.schemas import MemoryEntry
from optagent.memory.store import MemoryStore
from optagent.oracle.builder import OracleBuilder
from optagent.oracle.oracle import Oracle
from optagent.proposers.ensemble import ProposerEnsemble
from optagent.report.builder import ReportBuilder
from optagent.report.render import render_json, render_markdown
from optagent.report.schemas import (
    BenchmarkCurve,
    BenchmarkCurvePoint,
    ComplexityDiff,
    Report,
)
from optagent.search.controller import SearchController
from optagent.search.schemas import SearchBudget
from optagent.verify.ladder import Ladder

EX = Path(__file__).resolve().parent.parent / "examples"


def fast_settings(tmp_path: Path) -> Settings:
    return Settings(
        sandbox_backend="local",
        runs_dir=str(tmp_path / "runs"),
        memory_db_path=str(tmp_path / "test_memory.db"),
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
        bench_reps=2,
        search_max_depth=2,
        search_max_candidates=4,
    )


# ---------------------------------------------------------------------------
# 1. Report rendering markdown & json
# ---------------------------------------------------------------------------
def test_report_rendering_markdown_and_json():
    rep = Report(
        source_sha="abc123def456",
        entry_point="two_sum",
        original_source="def two_sum(): pass",
        optimized_source="def two_sum(): return []",
        diff="- def two_sum(): pass\n+ def two_sum(): return []",
        complexity=ComplexityDiff(
            before_time="O(n^2)",
            after_time="O(n log n)",
            before_space="O(1)",
            after_space="O(n)",
            derivation="Replaced nested loop with hash lookup.",
        ),
        evidence_tier="T2",
        overall_speedup=5.25,
        overall_mem_ratio=1.0,
        benchmarks=[
            BenchmarkCurve(
                family="random",
                points=[
                    BenchmarkCurvePoint(n=10, orig_time_s=0.001, cand_time_s=0.0005, speedup=2.0),
                    BenchmarkCurvePoint(n=100, orig_time_s=0.01, cand_time_s=0.001, speedup=10.0),
                ],
                crossover_n=10,
                max_speedup=10.0,
            )
        ],
        created_at="2026-11-18 12:00:00 UTC",
    )

    md = render_markdown(rep)
    assert "# OptAgent Optimization Report: `two_sum`" in md
    assert "**5.25x**" in md
    assert "O(n^2)" in md
    assert "O(n log n)" in md
    assert "```diff" in md

    js = render_json(rep)
    loaded = json.loads(js)
    assert loaded["entry_point"] == "two_sum"
    assert loaded["overall_speedup"] == 5.25


# ---------------------------------------------------------------------------
# 2. ReportBuilder End-to-End
# ---------------------------------------------------------------------------
def test_report_builder_end_to_end(tmp_path):
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
    search_res = controller.run(SearchBudget(max_candidates=3, max_time_s=30.0))

    builder = ReportBuilder(s)
    report = builder.build(intent, oracle, analysis, search_res)

    assert report.entry_point == "two_sum"
    assert report.evidence_tier in ("T1", "T2")
    assert report.overall_speedup > 1.0

    # Verify artifacts exist on disk
    run_dir = tmp_path / "runs" / oracle.b.source_sha
    assert (run_dir / "report.json").exists()
    assert (run_dir / "report.md").exists()


# ---------------------------------------------------------------------------
# 3. MemoryStore Positive and Negative Entries
# ---------------------------------------------------------------------------
def test_memory_store_positive_and_negative(tmp_path):
    db_file = tmp_path / "mem.db"
    store = MemoryStore(db_file)

    pos_entry = MemoryEntry(
        id="mem_pos_001",
        pattern_key="nested_loop_pairwise_sum",
        conditions=["pure", "list_indexed"],
        original_snippet="for i in range(n):\n    for j in range(i+1, n):",
        rewrite_snippet="pos = {}\nfor idx, v in enumerate(nums):",
        transform_ids=["nested_loop_to_hash_index"],
        speedup=6.5,
        mem_ratio=1.0,
        evidence_tier="T2",
        is_positive=True,
    )
    store.store_positive(pos_entry)

    neg_entry = MemoryEntry(
        id="mem_neg_001",
        pattern_key="nested_loop_pairwise_sum",
        conditions=["pure"],
        original_snippet="for i in range(n):\n    for j in range(i+1, n):",
        rewrite_snippet="seen = {}\nfor j, v in enumerate(nums): if target - v in seen: return [seen[target-v], j]",
        transform_ids=["single_pass_hash_inverted"],
        speedup=7.0,
        mem_ratio=1.0,
        evidence_tier="T0",
        is_positive=False,
        failure_reason="Violated return_value order: returned pair with smaller j instead of smaller i",
    )
    store.store_negative(neg_entry)

    # Retrieval of positive
    ret_pos = store.retrieve(pattern_key="nested_loop_pairwise_sum", is_positive=True)
    assert len(ret_pos) == 1
    assert ret_pos[0].id == "mem_pos_001"
    assert ret_pos[0].speedup == 6.5

    # Retrieval of negative
    ret_neg = store.retrieve(pattern_key="nested_loop_pairwise_sum", is_positive=False)
    assert len(ret_neg) == 1
    assert ret_neg[0].id == "mem_neg_001"
    assert "Violated return_value" in ret_neg[0].failure_reason


# ---------------------------------------------------------------------------
# 4. Memory Retrieval on Similar Function
# ---------------------------------------------------------------------------
def test_memory_retrieval_on_similar_function(tmp_path):
    db_file = tmp_path / "mem.db"
    store = MemoryStore(db_file)

    pos_entry = MemoryEntry(
        id="mem_twosum_rule",
        pattern_key="nested_loop_pairwise_sum",
        conditions=["list_numbers"],
        original_snippet="def find_pair(elements, goal):\n    for i in range(len(elements)):\n        for j in range(i + 1, len(elements)):\n            if elements[i] + elements[j] == goal:\n                return [i, j]",
        rewrite_snippet="def find_pair(elements, goal):\n    lookup = {}\n    for i, val in enumerate(elements):\n        diff = goal - val\n        if diff in lookup:\n            return [lookup[diff], i]\n        lookup[val] = i",
        speedup=8.0,
        evidence_tier="T2",
        is_positive=True,
    )
    store.store_positive(pos_entry)

    # Query with a similar two-sum function
    similar_src = "def two_sum(nums, target):\n    for i in range(len(nums)):\n        for j in range(i + 1, len(nums)):\n            if nums[i] + nums[j] == target:\n                return [i, j]"
    results = store.retrieve_similar(similar_src, is_positive=True, top_k=3)

    assert len(results) >= 1
    assert results[0].id == "mem_twosum_rule"
    assert "lookup" in results[0].rewrite_snippet


# ---------------------------------------------------------------------------
# 5. Report Model Roundtrip
# ---------------------------------------------------------------------------
def test_report_model_roundtrip():
    rep = Report(
        source_sha="1234567890ab",
        entry_point="test_fn",
        original_source="def test_fn(): pass",
        optimized_source="def test_fn(): return 42",
        evidence_tier="T1",
        overall_speedup=2.0,
    )
    dumped = rep.model_dump_json()
    loaded = Report.model_validate_json(dumped)
    assert loaded.source_sha == rep.source_sha
    assert loaded.evidence_tier == rep.evidence_tier
    assert loaded.overall_speedup == 2.0

