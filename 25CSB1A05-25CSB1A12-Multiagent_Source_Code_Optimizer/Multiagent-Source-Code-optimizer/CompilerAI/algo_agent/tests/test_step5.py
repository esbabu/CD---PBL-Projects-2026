"""Tests for Step 5: Verification ladder and evidence tiers."""
from __future__ import annotations

from pathlib import Path
import pytest
import yaml

from optagent.config import Settings
from optagent.intent.pipeline import IntentExtractor
from optagent.oracle.builder import OracleBuilder
from optagent.oracle.oracle import Oracle, source_sha
from optagent.verify.diffcov import compute_changed_lines, evaluate_diffcov
from optagent.verify.ladder import Ladder
from optagent.verify.schemas import Evidence, RungResult

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
    )


@pytest.fixture(scope="module")
def two_sum_oracle(tmp_path_factory):
    td = tmp_path_factory.mktemp("step5_two_sum")
    s = fast_settings(td)
    src = (EX / "slow_two_sum.py").read_text(encoding="utf-8")
    intent = IntentExtractor(s, use_llm=False).run(src, source_name="slow_two_sum.py")
    bundle = OracleBuilder(s, use_llm=False, log=lambda *a: None).build(intent, run_mutation=True)
    return Oracle(bundle, s)


# ---------------------------------------------------------------------------
# 1. R1 Compile & Lint failure
# ---------------------------------------------------------------------------
def test_compile_lint_failure(two_sum_oracle):
    ladder = Ladder(two_sum_oracle, log=lambda *a: None)
    
    # Syntax error
    ev1 = ladder.verify("def two_sum(nums, target): return [")
    assert not ev1.passed
    assert ev1.tier == "REJECTED"
    assert ev1.rungs[0].rung == "R1_compile"
    assert not ev1.rungs[0].passed

    # Missing entry point
    ev2 = ladder.verify("def other_function(nums, target):\n    return []\n")
    assert not ev2.passed
    assert ev2.tier == "REJECTED"
    assert not ev2.rungs[0].passed


# ---------------------------------------------------------------------------
# 2. Wrong candidate rejected with counterexample
# ---------------------------------------------------------------------------
def test_wrong_candidate_rejected_with_counterexample(two_sum_oracle):
    ladder = Ladder(two_sum_oracle, log=lambda *a: None)
    wrong_src = (EX / "fast_two_sum_wrong.py").read_text(encoding="utf-8")
    ev = ladder.verify(wrong_src, fresh_override=50)

    assert not ev.passed
    assert ev.tier == "REJECTED"
    assert ev.raw_tier == "T0"
    assert len(ev.counterexamples) >= 1
    assert "returned value differs" in ev.feedback or "difference" in ev.feedback
    assert any(r.rung == "R2_golden_holdout" and not r.passed for r in ev.rungs)


# ---------------------------------------------------------------------------
# 3. Right candidate reaches T2
# ---------------------------------------------------------------------------
def test_right_candidate_reaches_t2(two_sum_oracle):
    ladder = Ladder(two_sum_oracle, log=lambda *a: None)
    right_src = (EX / "fast_two_sum_right.py").read_text(encoding="utf-8")
    ev = ladder.verify(right_src, fresh_override=50)

    assert ev.passed
    assert ev.tier == "T2"
    assert ev.raw_tier == "T2"
    assert ev.capped_by is None
    
    # Verify rung passes
    rung_map = ev.rung_map
    assert rung_map["R1_compile"].passed
    assert rung_map["R2_golden_holdout"].passed
    assert rung_map["R3_properties"].passed
    assert rung_map["R4_differential_fuzz"].passed
    assert rung_map["R5_changed_line_coverage"].passed


# ---------------------------------------------------------------------------
# 4. Tier cap by oracle strength (C/D cannot exceed T1)
# ---------------------------------------------------------------------------
def test_tier_cap_by_oracle_strength(two_sum_oracle):
    # Temporarily set strength tier to C
    orig_tier = two_sum_oracle.b.strength.tier
    try:
        two_sum_oracle.b.strength.tier = "C"
        ladder = Ladder(two_sum_oracle, log=lambda *a: None)
        right_src = (EX / "fast_two_sum_right.py").read_text(encoding="utf-8")
        ev = ladder.verify(right_src, fresh_override=50)

        assert ev.passed
        assert ev.raw_tier == "T2"
        # Honesty rule: C caps at T1!
        assert ev.tier == "T1"
        assert ev.capped_by is not None
        assert "oracle strength tier C" in ev.capped_by

        # Also test with tier D
        two_sum_oracle.b.strength.tier = "D"
        ev_d = ladder.verify(right_src, fresh_override=50)
        assert ev_d.tier == "T1"
        assert "oracle strength tier D" in ev_d.capped_by
    finally:
        two_sum_oracle.b.strength.tier = orig_tier


# ---------------------------------------------------------------------------
# 5. Diffcov partial vs full coverage
# ---------------------------------------------------------------------------
def test_diffcov_partial_coverage():
    orig = "def foo(x):\n    a = 1\n    b = 2\n    return a + b\n"
    cand = "def foo(x):\n    a = 10\n    b = 20\n    if x > 0:\n        return a\n    return a + b\n"

    changed = compute_changed_lines(orig, cand)
    assert len(changed) > 0

    # 100% coverage
    full_cov = evaluate_diffcov(orig, cand, executed_lines=changed, min_ratio=1.0)
    assert full_cov.passed
    assert full_cov.coverage_ratio == 1.0

    # Partial coverage: omit one line
    partial_lines = set(list(changed)[:-1])
    partial_cov = evaluate_diffcov(orig, cand, executed_lines=partial_lines, min_ratio=1.0)
    assert not partial_cov.passed
    assert partial_cov.coverage_ratio < 1.0
    assert len(partial_cov.missing_lines) == 1


# ---------------------------------------------------------------------------
# 6. Evidence model roundtrip
# ---------------------------------------------------------------------------
def test_evidence_model_roundtrip():
    r1 = RungResult(rung="R1_compile", passed=True, elapsed_s=0.01)
    ev = Evidence(
        tier="T2",
        raw_tier="T2",
        passed=True,
        rungs=[r1],
        feedback="All checks passed.",
        elapsed_s=0.05,
    )
    dumped = ev.model_dump_json()
    loaded = Evidence.model_validate_json(dumped)
    assert loaded.tier == ev.tier
    assert loaded.passed == ev.passed
    assert len(loaded.rungs) == 1
    assert loaded.rungs[0].rung == "R1_compile"

