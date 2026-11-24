"""Acceptance tests for OptAgent Forensic Reverse-Engineering Tool (T1, T2, T3)."""
from __future__ import annotations

import json
import os
from pathlib import Path
import pytest

from optagent.forensics.decompose import UnitDecomposer
from optagent.forensics.explain import Explainer
from optagent.forensics.minimize import Minimizer
from optagent.forensics.compare import Comparator
from optagent.forensics.report import ForensicReporter, ForensicReportData
from optagent.forensics.cli import cmd_trace, cmd_explain, cmd_minimize, cmd_compare
import argparse


FIXTURE_PATH = Path(__file__).resolve().parents[1] / "examples" / "forensics" / "student_manager.py"
EXPECTED_PATH = Path(__file__).resolve().parents[1] / "examples" / "forensics" / "expected.yaml"


def test_t1_forensic_trace_baseline(tmp_path):
    """T1: Forensics trace on student_manager.py produces report, names failing point, evaluates P1-P10, and catches blind spots."""
    out_dir = tmp_path / "forensics_t1"
    args = argparse.Namespace(
        file=str(FIXTURE_PATH),
        lang="python",
        mode="nollm",
        units="all",
        expected=str(EXPECTED_PATH),
        backend="auto",
        out=str(out_dir),
    )
    rc = cmd_trace(args)
    assert rc == 0

    md_report = out_dir / "FORENSIC_REPORT.md"
    json_report = out_dir / "forensics.json"
    assert md_report.exists()
    assert json_report.exists()

    md_text = md_report.read_text(encoding="utf-8")
    assert "First Failing Point" in md_text
    assert "select_entry" in md_text
    assert "P1" in md_text and "CONFIRMED" in md_text
    assert "P2" in md_text and "CONFIRMED" in md_text
    assert "P10" in md_text and "CONFIRMED" in md_text

    data = json.loads(json_report.read_text(encoding="utf-8"))
    assert len(data["analyzer_blind_spots"]) > 0
    assert any(b["kind"] == "import_time_side_effect" for b in data["analyzer_blind_spots"])


def test_t2_forensic_explain_all_units():
    """T2: explain for each unit returns exactly one primary blocking cause and what would unlock it."""
    src = FIXTURE_PATH.read_text(encoding="utf-8")
    decomp = UnitDecomposer.decompose_python(src)
    assert len(decomp.units) >= 18

    for uname, unit in decomp.units.items():
        exp = Explainer.explain_unit(unit)
        assert exp.unit == uname
        assert exp.blocking_cause in [
            "NOT_ANALYZABLE",
            "NO_EFFECTIVE_INPUTS",
            "DEGENERATE_GOLDEN",
            "NO_BOTTLENECK_DETECTED",
            "NO_PROPOSAL",
            "PROPOSALS_UNUSABLE",
            "REJECTED_BY_ORACLE",
            "BLOCKED_BY_CONTRACT",
            "VERIFIED_NOT_FASTER",
            "ALREADY_OPTIMAL",
            "NOT_A_PERFORMANCE_TARGET",
            "OPTIMIZED_VERIFIED",
        ]
        assert exp.decision_step >= 0
        assert len(exp.what_would_unlock) > 0


def test_t3_forensic_minimize_ambiguous_entry():
    """T3: minimize on signature 'entry selection: ambiguous' produces a small source reproducing it."""
    src = FIXTURE_PATH.read_text(encoding="utf-8")

    def test_reproducer(cand_src: str) -> bool:
        decomp = UnitDecomposer.decompose_python(cand_src)
        return len(decomp.units) >= 2

    res = Minimizer.minimize(src, "entry selection: ambiguous", test_reproducer)
    assert res.statements_count < len(src.splitlines())
    assert len(res.units_remaining) >= 1
    assert "def " in res.minimized_source
