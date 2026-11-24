"""Step 3 tests: static complexity, recurrence solving, empirical fitting, profiling, and end-to-end analysis."""
from __future__ import annotations

from pathlib import Path
import pytest

from optagent.complexity.analyzer import Analyzer
from optagent.complexity.empirical import fit_curve
from optagent.complexity.recurrence import solve_master_theorem, solve_recurrence
from optagent.complexity.schemas import AnalysisBundle
from optagent.complexity.static_cost import StaticCostAnalyzer
from optagent.config import Settings
from optagent.intent.pipeline import IntentExtractor
from optagent.oracle.builder import OracleBuilder

EX = Path(__file__).parent.parent / "examples"


def fast_settings(tmp_path, **kw):
    base = dict(
        sandbox_backend="local",
        runs_dir=str(tmp_path / "runs"),
        n_family=30,
        n_hypothesis=30,
        n_probe=5,
        fuzz_budget_s=0.0,
        max_mutants=10,
        scale_sizes=(10, 50, 100, 200, 400),
        scale_budget_s=3.0,
        case_timeout_s=2.0,
    )
    base.update(kw)
    return Settings(**base)


# ---------------------------------------------------------------------------
# 1. Synthetic Curve Fitting Tests
# ---------------------------------------------------------------------------
def test_fit_synthetic_quadratic():
    ns = [10, 50, 100, 200, 400, 800]
    ys = [0.0001 * (n ** 2) + 0.002 for n in ns]
    res = fit_curve(ns, ys)
    assert res.model == "O(n^2)"
    assert res.r2 > 0.98


def test_fit_synthetic_linear():
    ns = [10, 50, 100, 200, 400, 800]
    ys = [0.002 * n + 0.001 for n in ns]
    res = fit_curve(ns, ys)
    assert res.model == "O(n)"
    assert res.r2 > 0.98


def test_fit_synthetic_constant():
    ns = [10, 50, 100, 200, 400]
    ys = [0.05, 0.05, 0.05, 0.05, 0.05]
    res = fit_curve(ns, ys)
    assert res.model == "O(1)"
    assert res.r2 == 1.0


# ---------------------------------------------------------------------------
# 2. Recurrence Solver Tests
# ---------------------------------------------------------------------------
def test_recurrence_master_theorem():
    # Mergesort: T(n) = 2T(n/2) + O(n) => O(n log n)
    assert solve_master_theorem(2, 2, 1) == "O(n log n)"
    # Binary search: T(n) = T(n/2) + O(1) => O(log n)
    assert solve_master_theorem(1, 2, 0) == "O(log n)"
    # Strassen: T(n) = 7T(n/2) + O(n^2) => d=2 < c=log2(7)~2.81 => O(n^2.81)
    res_strassen = solve_master_theorem(7, 2, 2)
    assert "n^2.81" in res_strassen


def test_recurrence_exponential():
    rec = solve_recurrence({"a": 2, "b": 1, "d": 0})
    assert rec.closed_form == "O(2^n)"


# ---------------------------------------------------------------------------
# 3. Static Cost Analysis Tests
# ---------------------------------------------------------------------------
def test_static_cost_slow_two_sum(tmp_path):
    s = fast_settings(tmp_path)
    src = (EX / "slow_two_sum.py").read_text(encoding="utf-8")
    intent = IntentExtractor(s, use_llm=False).run(src, source_name="slow_two_sum.py")
    t_c, s_c, _ = StaticCostAnalyzer(intent).analyze_function("two_sum")
    assert t_c == "O(n^2)"
    assert s_c == "O(1)"


def test_static_cost_dedupe_rank(tmp_path):
    s = fast_settings(tmp_path)
    src = (EX / "dedupe_rank.py").read_text(encoding="utf-8")
    overrides = {"inputs": [{"args": [["apple", "banana", "apple", "cherry"], 2]}]}
    intent = IntentExtractor(s, use_llm=False).run(src, overrides=overrides, source_name="dedupe_rank.py")
    t_c, s_c, findings = StaticCostAnalyzer(intent).analyze_function("dedupe_rank")
    assert t_c == "O(n^2)"
    assert s_c == "O(n)"
    assert any("linear membership" in f for f in findings)


# ---------------------------------------------------------------------------
# 4. End-to-End Analyzer Tests
# ---------------------------------------------------------------------------
def test_analyzer_end_to_end_slow_two_sum(tmp_path):
    s = fast_settings(tmp_path)
    src = (EX / "slow_two_sum.py").read_text(encoding="utf-8")
    intent = IntentExtractor(s, use_llm=False).run(src, source_name="slow_two_sum.py")
    oracle = OracleBuilder(s, use_llm=False, log=lambda *a: None).build(intent, run_mutation=False)

    analyzer = Analyzer(s, log=lambda *a: None)
    bundle = analyzer.analyze(intent, oracle)

    assert bundle.overall_time == "O(n^2)"
    assert bundle.overall_space == "O(1)"
    assert len(bundle.bottlenecks) > 0
    top = bundle.bottlenecks[0]
    assert top.pattern in ("nested_loop", "hotspot")
    assert top.line in (3, 4, 5)

    # Check persistence
    p = tmp_path / "runs" / intent.source_sha / "analysis" / "analysis.json"
    assert p.exists()
    roundtrip = AnalysisBundle.model_validate_json(p.read_text(encoding="utf-8"))
    assert roundtrip.source_sha == intent.source_sha


def test_analyzer_end_to_end_dedupe_rank(tmp_path):
    s = fast_settings(tmp_path)
    src = (EX / "dedupe_rank.py").read_text(encoding="utf-8")
    overrides = {"inputs": [{"args": [["apple", "banana", "apple", "cherry", "date"], 2]}]}
    intent = IntentExtractor(s, use_llm=False).run(src, overrides=overrides, source_name="dedupe_rank.py")
    oracle = OracleBuilder(s, use_llm=False, log=lambda *a: None).build(intent, run_mutation=False)

    analyzer = Analyzer(s, log=lambda *a: None)
    bundle = analyzer.analyze(intent, oracle)

    assert bundle.overall_time in ("O(n^2)", "O(n log n)")
    assert any(b.pattern == "linear_membership" for b in bundle.bottlenecks)
