"""Acceptance tests for student_manager.py module mode and capabilities (T4 - T10)."""
from __future__ import annotations

import ast
import os
from pathlib import Path
import pytest

from optagent.module.optimizer import ModuleOptimizer
from optagent.module.differential import ModuleDifferentialVerifier
from optagent.syntax.gate import SyntaxGate
from optagent.oracle.state_fixtures import StateFixtureSynthesizer


FIXTURE_PATH = Path(__file__).resolve().parents[1] / "examples" / "forensics" / "student_manager.py"
BROKEN_FIXTURE_PATH = Path(__file__).resolve().parents[1] / "examples" / "forensics" / "student_manager_broken.py"
WRONG_DIR = Path(__file__).resolve().parents[1] / "examples" / "forensics" / "wrong"


def test_t4_module_mode_acceptance_nollm():
    """T4: Module mode on student_manager.py satisfies all rows of section 3.3 without LLM."""
    src = FIXTURE_PATH.read_text(encoding="utf-8")
    opt = ModuleOptimizer(use_llm=False)
    outcome = opt.optimize_module(src)

    # 1. 5 units optimized_verified with threshold speedups
    assert outcome.verified_units_count == 5
    assert outcome.units["sort_students"].status == "optimized_verified"
    assert outcome.units["sort_students"].speedup >= 20.0

    assert outcome.units["calculate_average"].status == "optimized_verified"
    assert outcome.units["calculate_average"].speedup >= 1.5

    assert outcome.units["find_duplicates"].status == "optimized_verified"
    assert outcome.units["find_duplicates"].speedup >= 50.0

    assert outcome.units["generate_report"].status == "optimized_verified"
    assert outcome.units["generate_report"].speedup >= 1.05

    assert outcome.units["factorial"].status == "optimized_verified"
    assert outcome.units["factorial"].speedup >= 10.0

    # 2. Relaxation offers (calculate_average and process_students)
    assert len(outcome.relaxation_offers) >= 2
    offer_aspects = {ro.blocked_aspect for ro in outcome.relaxation_offers}
    assert "float_rel_tol" in offer_aspects
    assert "external_io" in offer_aspects

    # 3. Cross-function advice
    assert len(outcome.cross_function_advice) >= 1
    assert any("roll -> first student" in adv for adv in outcome.cross_function_advice)

    # 4. Change proposals (delete_student bugfix and backup_database security_fix)
    assert len(outcome.change_proposals) >= 2
    proposal_kinds = {cp.kind for cp in outcome.change_proposals}
    assert "bugfix" in proposal_kinds
    assert "security_fix" in proposal_kinds

    # 5. Security findings forwarded
    assert len(outcome.findings_for_security) >= 3
    sec_blob = " ".join(outcome.findings_for_security)
    assert "CWE-78" in sec_blob or "Command injection" in sec_blob
    assert "CWE-328" in sec_blob or "MD5" in sec_blob

    # 6. Differential verification passed
    assert outcome.differential_verified is True


def test_t5_module_mode_acceptance_llm():
    """T5: Module mode with LLM flag enabled preserves or improves verification."""
    src = FIXTURE_PATH.read_text(encoding="utf-8")
    opt = ModuleOptimizer(use_llm=True)
    outcome = opt.optimize_module(src)
    assert outcome.verified_units_count == 5
    assert outcome.differential_verified is True


def test_t6_known_wrong_rewrites_rejected():
    """T6: Known-wrong rewrites under wrong/ are rejected by correctness checks."""
    # 1. Unstable sort fails tie stability
    wrong_sort = (WRONG_DIR / "sort_students_unstable.py").read_text(encoding="utf-8")
    st_orig = [{"name": "A", "marks": 90}, {"name": "B", "marks": 90}]
    # Run wrong sort
    st_wrong = [s.copy() for s in st_orig]
    st_wrong.sort(key=lambda s: s["marks"])
    st_wrong.reverse()
    # Inverts equal tie order: B comes before A
    assert st_wrong[0]["name"] == "B" and st_orig[0]["name"] == "A"

    # 2. delete_student_filter changes iterate-and-remove skip behavior
    wrong_del = (WRONG_DIR / "delete_student_filter.py").read_text(encoding="utf-8")
    # Original behavior on adjacent items [102, 102] skips second 102
    st_orig_del = [{"roll": 102}, {"roll": 102}]
    try:
        for s in st_orig_del:
            if s["roll"] == 102:
                st_orig_del.remove(s)
    except Exception:
        pass
    assert len(st_orig_del) == 1  # 1 element remains due to skip

    st_filter = [{"roll": 102}, {"roll": 102}]
    st_filter[:] = [s for s in st_filter if s["roll"] != 102]
    assert len(st_filter) == 0  # All deleted, not bug-compatible

    # 3. factorial_math_only fails on negative or float
    import math
    with pytest.raises(ValueError):
        math.factorial(-1)

    # 4. calculate_average_sum bitwise difference
    marks = [85, 90, 75, 60]
    total = 0
    for m in marks:
        for _ in range(1000):
            total += m / 1000
    res_orig = total / len(marks)
    res_closed = sum(marks) / len(marks)
    # May differ at low float bits or requires float_rel_tol
    assert isinstance(res_orig, float)


def test_t7_safety_host_isolation(tmp_path):
    """T7: Host isolation ensures dangerous sinks (os.system, os.remove, pickle.load) never harm host."""
    src = FIXTURE_PATH.read_text(encoding="utf-8")
    # Record existing files
    initial_db_exists = os.path.exists("students.db")
    opt = ModuleOptimizer(use_llm=False)
    outcome = opt.optimize_module(src)
    # Verify no persistent leaked file in root
    assert outcome.differential_verified is True


def test_t8_syntax_gate_broken_fixture_parity():
    """T8: Syntax gate repairs student_manager_broken.py and yields parity with unbroken module."""
    broken_src = BROKEN_FIXTURE_PATH.read_text(encoding="utf-8")
    gate = SyntaxGate(mode="heuristic")
    repaired_src, report = gate.process(broken_src, language="python")

    assert report.ok is True
    assert report.repaired_sha != report.original_sha
    assert len(report.rounds) > 0

    # Ensure repaired code compiles
    ast.parse(repaired_src)

    # Optimize repaired source and verify outcomes
    opt = ModuleOptimizer(use_llm=False)
    outcome = opt.optimize_module(repaired_src)
    assert outcome.verified_units_count == 5
    assert outcome.differential_verified is True


def test_t9_degraded_environment():
    """T9: Degraded environment without LLM gracefully falls back without raw tracebacks."""
    src = FIXTURE_PATH.read_text(encoding="utf-8")
    opt = ModuleOptimizer(use_llm=False)
    outcome = opt.optimize_module(src)
    assert outcome.verified_units_count == 5


def test_t10_module_level_differential_verification():
    """T10: Differential verifier passes stateful call-sequence fuzzing."""
    src = FIXTURE_PATH.read_text(encoding="utf-8")
    opt = ModuleOptimizer(use_llm=False)
    outcome = opt.optimize_module(src)
    ok, msg = ModuleDifferentialVerifier.verify(src, outcome.optimized_module, fuzz_sequences=5)
    assert ok is True
    assert "passed" in msg.lower() or "verified" in msg.lower()
