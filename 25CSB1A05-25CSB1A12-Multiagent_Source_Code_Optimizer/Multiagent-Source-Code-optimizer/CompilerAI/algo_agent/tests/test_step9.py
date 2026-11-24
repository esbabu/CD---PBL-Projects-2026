"""Tests for Step 9: Evaluation harness, benchmark adapters, metrics, ablations, and regression suite."""
from __future__ import annotations

import json
from pathlib import Path
import pytest

from optagent.config import Settings
from optagent.eval.ablation import AblationRunner, AblationVariant
from optagent.eval.adapter import (
    load_benchmark_dataset,
    load_dataset_json,
    load_dataset_jsonl,
    load_ecco_dataset,
    load_effibench_dataset,
    load_mercury_dataset,
    load_pie_dataset,
    load_task_from_files,
)
from optagent.cli_eval import render_evaluation_markdown
from optagent.eval.harness import EvalHarness
from optagent.eval.metrics import (
    build_suite_result,
    compute_distribution,
    detect_asymptotic_improvement,
)
from optagent.eval.schemas import (
    DistributionStats,
    EvalSuiteResult,
    PreferencePair,
    ProgramCost,
    TaskEvaluation,
    TaskSpec,
)
from optagent.eval.self_improve import PreferenceHarvester, reward_from_candidate
from optagent.proposers.schemas import Candidate
from optagent.search.schemas import SearchNode, SearchResult

EX = Path(__file__).resolve().parent.parent / "examples"
BENCH = EX / "benchmarks"


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
        search_max_candidates=8,
    )


# ---------------------------------------------------------------------------
# 1. Dataset Adapter Tests (PIE, EffiBench, Mercury, ECCO, Local)
# ---------------------------------------------------------------------------
def test_load_task_from_files():
    task = load_task_from_files(
        EX / "slow_two_sum.py",
        name="test_two_sum",
    )
    assert task.name == "test_two_sum"
    assert "def two_sum" in task.source


def test_load_dataset_json(tmp_path):
    data = [
        {"task_id": "t1", "source": "def f(x): return x", "entry_point": "f"},
        {"task_id": "t2", "source": "def g(y): return y + 1", "entry_point": "g"},
    ]
    p = tmp_path / "dataset.json"
    p.write_text(json.dumps(data), encoding="utf-8")

    tasks = load_dataset_json(p)
    assert len(tasks) == 2
    assert tasks[0].name == "t1"
    assert tasks[1].entry == "g"


def test_load_dataset_jsonl(tmp_path):
    lines = [
        json.dumps({"task_id": "jl1", "source": "def a(): pass"}),
        json.dumps({"task_id": "jl2", "source": "def b(): pass"}),
    ]
    p = tmp_path / "dataset.jsonl"
    p.write_text("\n".join(lines), encoding="utf-8")

    tasks = load_dataset_jsonl(p)
    assert len(tasks) == 2
    assert tasks[0].name == "jl1"
    assert tasks[1].name == "jl2"


def test_load_pie_adapter():
    tasks = load_pie_dataset(BENCH / "pie_sample.json")
    assert len(tasks) == 1
    t = tasks[0]
    assert t.benchmark == "pie"
    assert "pie_001" in t.name
    assert "def find_duplicates" in t.source
    assert t.overrides is not None
    assert "inputs" in t.overrides


def test_load_effibench_adapter():
    tasks = load_effibench_dataset(BENCH / "effibench_sample.json")
    assert len(tasks) == 1
    t = tasks[0]
    assert t.benchmark == "effibench"
    assert t.entry == "count_occurrences"
    assert "def count_occurrences" in t.source


def test_load_mercury_adapter():
    tasks = load_mercury_dataset(BENCH / "mercury_sample.json")
    assert len(tasks) == 1
    t = tasks[0]
    assert t.benchmark == "mercury"
    assert "max_subarray_sum" in t.source


def test_load_ecco_adapter():
    tasks = load_ecco_dataset(BENCH / "ecco_sample.json")
    assert len(tasks) == 1
    t = tasks[0]
    assert t.benchmark == "ecco"
    assert t.expected_asymptotic_improvement
    assert "common_elements" in t.source


def test_load_benchmark_dataset_auto():
    # Auto-detection on all 4 benchmark files
    pie_tasks = load_benchmark_dataset(BENCH / "pie_sample.json")
    assert pie_tasks[0].benchmark == "pie"

    effi_tasks = load_benchmark_dataset(BENCH / "effibench_sample.json")
    assert effi_tasks[0].benchmark == "effibench"

    merc_tasks = load_benchmark_dataset(BENCH / "mercury_sample.json")
    assert merc_tasks[0].benchmark == "mercury"

    ecco_tasks = load_benchmark_dataset(BENCH / "ecco_sample.json")
    assert ecco_tasks[0].benchmark == "ecco"


# ---------------------------------------------------------------------------
# 2. Metric and Distribution Computation Tests
# ---------------------------------------------------------------------------
def test_compute_distribution():
    samples = [1.0, 2.0, 3.0, 4.0, 5.0, 10.0]
    dist = compute_distribution(samples)
    assert dist.min == 1.0
    assert dist.max == 10.0
    assert 3.0 <= dist.median <= 4.0
    assert dist.geom_mean > 1.0


def test_detect_asymptotic_improvement():
    assert detect_asymptotic_improvement("O(n^2)", "O(n log n)")
    assert detect_asymptotic_improvement("O(n^2)", "O(n)")
    assert detect_asymptotic_improvement("O(n^3)", "O(n^2)")
    assert detect_asymptotic_improvement("O(2^n)", "O(n^2)")
    assert not detect_asymptotic_improvement("O(n)", "O(n)")
    assert not detect_asymptotic_improvement("O(n)", "O(n^2)")


def test_build_suite_result():
    ev1 = TaskEvaluation(
        name="task1",
        verified=True,
        passed_oracle=True,
        speedup=4.0,
        mem_ratio=0.8,
        asymptotic_improved=True,
        complexity_before="O(n^2)",
        complexity_after="O(n)",
    )
    ev2 = TaskEvaluation(
        name="task2",
        verified=True,
        passed_oracle=True,
        speedup=2.0,
        mem_ratio=1.0,
    )
    res = build_suite_result([ev1, ev2], elapsed_s=5.0)
    assert res.total_tasks == 2
    assert res.correctness_rate == 1.0
    assert res.avg_speedup > 2.5
    assert res.asymptotic_improvement_rate == 0.5
    assert len(res.asymptotic_transitions) == 1


# ---------------------------------------------------------------------------
# 3. Ablation Runner Tests
# ---------------------------------------------------------------------------
def test_ablation_runner():
    runner = AblationRunner(Settings())
    task = TaskSpec(name="dummy", source="def f(x): return x")

    var_rule = AblationVariant(
        id="prop_rules_only",
        name="Rules Only",
        category="proposer",
        disabled_components=["llm_proposer"],
    )

    def fake_eval(t: TaskSpec, s: Settings) -> TaskEvaluation:
        return TaskEvaluation(
            name=t.name,
            verified=True,
            passed_oracle=True,
            speedup=2.5,
            elapsed_s=0.1,
        )

    res = runner.run_variant([task], var_rule, fake_eval)
    assert res.variant.id == "prop_rules_only"
    assert res.correctness_rate == 1.0
    assert res.avg_speedup == 2.5


# ---------------------------------------------------------------------------
# 4. Self-Improvement & DPO Preference Harvesting Tests
# ---------------------------------------------------------------------------
def test_preference_harvester_and_export(tmp_path):
    harvester = PreferenceHarvester()
    c_chosen = Candidate(id="c_best", source="def two_sum(): return hash_map", transform_ids=["hash"])
    c_rej = Candidate(id="c_slow", source="def two_sum(): return nested", transform_ids=["nested"])

    n_chosen = SearchNode(candidate=c_chosen, status="verified", speedup=5.0)
    n_rej = SearchNode(candidate=c_rej, status="rejected", speedup=0.0)

    search_res = SearchResult(
        source_sha="test_sha",
        entry_point="two_sum",
        best_candidate=c_chosen,
        all_evaluated=[n_chosen, n_rej],
    )

    pairs = harvester.harvest_from_search(
        task_name="test_twosum",
        entry_point="two_sum",
        original_code="def two_sum(): pass",
        search_res=search_res,
    )

    assert len(pairs) == 1
    assert pairs[0].chosen_code == c_chosen.source
    assert pairs[0].rejected_code == c_rej.source
    assert pairs[0].margin > 0.0

    out_file = tmp_path / "prefs.jsonl"
    count = PreferenceHarvester.export_dpo_jsonl(pairs, out_file)
    assert count == 1
    assert out_file.exists()
    content = json.loads(out_file.read_text(encoding="utf-8"))
    assert content["task"] == "test_twosum"
    assert content["chosen"] == c_chosen.source


def test_reward_from_candidate():
    assert reward_from_candidate("REJECTED", 0.0, passed=False) == 0.0
    rew_t2 = reward_from_candidate("T2", 4.0, passed=True)
    assert rew_t2 > 1.5


# ---------------------------------------------------------------------------
# 5. Single Task Evaluation
# ---------------------------------------------------------------------------
def test_eval_single_task(tmp_path):
    s = fast_settings(tmp_path)
    harness = EvalHarness(s, log=lambda *a: None)

    task = TaskSpec(
        name="slow_two_sum",
        source=(EX / "slow_two_sum.py").read_text(encoding="utf-8"),
    )
    evaluation = harness.evaluate_task(task)

    assert isinstance(evaluation, TaskEvaluation)
    assert evaluation.passed_oracle
    assert evaluation.verified
    assert evaluation.speedup > 1.0
    assert not evaluation.false_claim


# ---------------------------------------------------------------------------
# 6. Permanent Regression Suite: 100% Correctness & 0% False Claims
# ---------------------------------------------------------------------------
def test_regression_suite_correctness_and_false_claims(tmp_path):
    s = fast_settings(tmp_path)
    harness = EvalHarness(s, log=lambda *a: None)

    tasks = EvalHarness.get_regression_suite()
    suite_res = harness.run_suite(tasks)

    assert suite_res.total_tasks == 2
    # Correctness rate must be 100%
    assert suite_res.correctness_rate == 1.0
    # False-claim rate must be 0%
    assert suite_res.false_claim_rate == 0.0
    # Both tasks achieved speedup > 1.0
    assert suite_res.avg_speedup > 1.0
    for e in suite_res.task_evaluations:
        assert e.verified
        assert e.evidence_tier in ("T1", "T2")


# ---------------------------------------------------------------------------
# 7. Model Roundtrip & Markdown Rendering
# ---------------------------------------------------------------------------
def test_eval_suite_result_roundtrip():
    ev = TaskEvaluation(
        name="t1",
        verified=True,
        evidence_tier="T2",
        speedup=3.4,
        mem_ratio=0.8,
        asymptotic_improved=True,
    )
    dist = DistributionStats(min=3.4, median=3.4, max=3.4, mean=3.4, geom_mean=3.4)
    suite = EvalSuiteResult(
        total_tasks=1,
        correctness_rate=1.0,
        avg_speedup=3.4,
        speedup_distribution=dist,
        asymptotic_improvement_rate=1.0,
        false_claim_rate=0.0,
        task_evaluations=[ev],
        elapsed_s=2.5,
    )
    dumped = suite.model_dump_json()
    loaded = EvalSuiteResult.model_validate_json(dumped)
    assert loaded.total_tasks == 1
    assert loaded.correctness_rate == 1.0
    assert loaded.avg_speedup == 3.4
    assert loaded.speedup_distribution.median == 3.4

    md = render_evaluation_markdown(loaded)
    assert "# OptAgent Step 9: Evaluation Suite Report" in md
    assert "`t1`" in md
