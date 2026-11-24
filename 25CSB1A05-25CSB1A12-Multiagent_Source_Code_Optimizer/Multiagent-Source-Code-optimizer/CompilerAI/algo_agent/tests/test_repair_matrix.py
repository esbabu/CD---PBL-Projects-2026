"""Acceptance Matrix test suite (`tests/test_repair_matrix.py`) covering Section 9."""
from __future__ import annotations

import json
import shutil
import socket
from pathlib import Path
import pytest

from optagent.agent import OptimizerAgent, OptimizeRequest
from optagent.config import Settings
from optagent.core.outcome import ReasonCode, SupportLevel
from optagent.core.stages import StageRunner
from optagent.intent.pipeline import IntentExtractor
from optagent.lang.registry import get_adapter
from optagent.llm.health import clear_health_cache
from optagent.oracle.builder import OracleBuilder
from optagent.oracle.oracle import Oracle
from optagent.search.schemas import SearchBudget

ROOT = Path(__file__).resolve().parent.parent
FIX = ROOT / "examples" / "repair"

HAS_NODE = bool(shutil.which("node")) or (Path.home() / ".nodejs" / "node-v20.18.0-win-x64" / "node.exe").exists()


def _fast_settings(tmp_path: Path, **kw) -> Settings:
    defaults = dict(
        sandbox_backend="local",
        runs_dir=str(tmp_path / "runs"),
        memory_db_path=str(tmp_path / "mem.db"),
        llm_mode="off",
        n_family=8,
        n_hypothesis=8,
        n_probe=2,
        n_adversarial=2,
        fuzz_budget_s=0.3,
        fuzz_max_rounds=1,
        max_mutants=3,
        scale_sizes=(10, 20),
        ladder_fresh_inputs=20,
        ladder_fuzz_budget_s=0.3,
        bench_warmups=1,
        bench_reps=2,
        search_max_depth=1,
        search_max_candidates=2,
    )
    defaults.update(kw)
    return Settings(**defaults)


@pytest.mark.parametrize(
    "fname",
    [
        "simple_fn.py",
        "decorated_cached.py",
        "generator_entry.py",
        "deep_recursion.py",
        "no_annotations_complex.py",
        "dataclass_args.py",
        "async_entry.py",
        "import_side_effects.py",
        "slow_heavy.py",
        "needs_numpy.py",
    ],
)
def test_python_fixtures_execute_never_denied(tmp_path, fname):
    s = _fast_settings(tmp_path)
    src = (FIX / "python" / fname).read_text(encoding="utf-8")
    res = OptimizerAgent(s, log=lambda *a: None).run(
        OptimizeRequest(source=src, source_name=fname, budget=SearchBudget(max_candidates=2, max_time_s=10.0), use_llm=False)
    )
    assert res.status == "ok", f"{fname} failed: {res.message}"
    assert res.outcome is not None
    assert res.outcome.support_level in (SupportLevel.FULL, SupportLevel.VERIFIED_WEAK), f"{fname}: {res.outcome}"


@pytest.mark.parametrize("stem", ["leetcode_class", "static_and_classmethods"])
def test_python_class_methods_right_passes_wrong_fails(tmp_path, stem):
    s = _fast_settings(tmp_path)
    src = (FIX / "python" / f"{stem}.py").read_text(encoding="utf-8")
    right = (FIX / "python" / f"{stem}_right.py").read_text(encoding="utf-8")
    wrong = (FIX / "python" / f"{stem}_wrong.py").read_text(encoding="utf-8")

    ad = get_adapter("python")
    intent = IntentExtractor(s, use_llm=False, adapter=ad).run(src, source_name=f"{stem}.py", auto_select=True)
    bundle = OracleBuilder(s, use_llm=False, log=lambda *a: None, adapter=ad).build(intent, run_mutation=False)
    oracle = Oracle(bundle, s, adapter=ad)

    assert oracle.check(right, shrink=False).passed is True
    vw = oracle.check(wrong, shrink=True)
    assert vw.passed is False


def test_python_stdin_script_mode(tmp_path):
    s = _fast_settings(tmp_path)
    src = (FIX / "python" / "stdin_script.py").read_text(encoding="utf-8")
    res = OptimizerAgent(s, log=lambda *a: None).run(
        OptimizeRequest(source=src, source_name="stdin_script.py", budget=SearchBudget(max_candidates=2, max_time_s=10.0), use_llm=False)
    )
    assert res.status == "ok"
    assert res.outcome is not None
    assert res.outcome.strategy == "script"
    assert res.outcome.support_level in (SupportLevel.FULL, SupportLevel.VERIFIED_WEAK)


def test_python_missing_dependency_degrades_to_analysis_only(tmp_path):
    s = _fast_settings(tmp_path)
    src = "import nonexistent_quantum_pkg_xyz as q\n\ndef solve(x: int) -> int:\n    return q.run(x)\n"
    res = OptimizerAgent(s, log=lambda *a: None).run(OptimizeRequest(source=src, use_llm=False))
    assert res.status == "ok"
    assert res.outcome is not None
    assert res.outcome.support_level == SupportLevel.ANALYSIS_ONLY
    assert any(r.code == ReasonCode.MISSING_DEPENDENCY for r in res.outcome.reasons)
    assert res.outcome.unverified is True


def test_python_multi_function_ambiguous_auto_selects(tmp_path):
    s = _fast_settings(tmp_path)
    src = (FIX / "python" / "multi_function_ambiguous.py").read_text(encoding="utf-8")
    res = OptimizerAgent(s, log=lambda *a: None).run(
        OptimizeRequest(source=src, source_name="multi_function_ambiguous.py", budget=SearchBudget(max_candidates=2, max_time_s=10.0), use_llm=False)
    )
    assert res.status == "ok"
    assert res.outcome is not None
    assert res.outcome.entry_point == "compute_pipeline"
    assert any(r.code == ReasonCode.ENTRY_AUTO_SELECTED for r in res.outcome.reasons)


@pytest.mark.skipif(not HAS_NODE, reason="Node.js not available on host")
@pytest.mark.parametrize("fname", ["two_sum.js", "esm_export.mjs", "async_fn.js"])
def test_js_fixtures_end_to_end(tmp_path, fname):
    s = _fast_settings(tmp_path)
    src = (FIX / "js" / fname).read_text(encoding="utf-8")
    res = OptimizerAgent(s, log=lambda *a: None).run(
        OptimizeRequest(source=src, language="javascript", source_name=fname, budget=SearchBudget(max_candidates=2, max_time_s=12.0), use_llm=False)
    )
    assert res.status == "ok", f"{fname} failed: {res.message}"
    assert res.language == "javascript"
    assert res.outcome is not None
    assert res.outcome.language == "javascript"
    assert res.outcome.support_level in (SupportLevel.FULL, SupportLevel.VERIFIED_WEAK)


@pytest.mark.skipif(not HAS_NODE, reason="Node.js not available on host")
def test_js_two_sum_right_passes_wrong_caught(tmp_path):
    s = _fast_settings(tmp_path)
    ad = get_adapter("javascript")
    src = (FIX / "js" / "two_sum.js").read_text(encoding="utf-8")
    right = (FIX / "js" / "two_sum_right.js").read_text(encoding="utf-8")
    wrong = (FIX / "js" / "two_sum_wrong.js").read_text(encoding="utf-8")

    intent = IntentExtractor(s, use_llm=False, adapter=ad).run(src, source_name="two_sum.js", language="javascript")
    bundle = OracleBuilder(s, use_llm=False, log=lambda *a: None, adapter=ad).build(intent, run_mutation=False)
    oracle = Oracle(bundle, s, adapter=ad)
    assert oracle.check(right, shrink=False).passed is True
    assert oracle.check(wrong, shrink=True).passed is False


@pytest.mark.parametrize(
    "lang,fname,expected_code",
    [
        ("c", "two_sum.c", ReasonCode.TOOLCHAIN_MISSING),
        ("c", "static_fn.c", ReasonCode.TOOLCHAIN_MISSING),
        ("c", "sum_overflow.c", ReasonCode.TOOLCHAIN_MISSING),
        ("c", "main_only.c", ReasonCode.UNSUPPORTED_ENTRY_KIND),
        ("cpp", "dedupe_rank.cpp", ReasonCode.TOOLCHAIN_MISSING),
        ("cpp", "class_method.cpp", ReasonCode.TOOLCHAIN_MISSING),
        ("cpp", "template_fn.cpp", ReasonCode.UNSUPPORTED_ENTRY_KIND),
        ("javascript", "stdin_script.js", ReasonCode.UNSUPPORTED_ENTRY_KIND),
    ],
)
def test_native_and_script_degraded_outcomes_never_crash(tmp_path, lang, fname, expected_code):
    s = _fast_settings(tmp_path)
    sub = "js" if lang == "javascript" else lang
    src = (FIX / sub / fname).read_text(encoding="utf-8")
    res = OptimizerAgent(s, log=lambda *a: None).run(
        OptimizeRequest(source=src, language=lang, source_name=fname, use_llm=False)
    )
    assert res.status == "ok"
    assert res.outcome is not None
    # When compiler is absent on host, must degrade to ANALYSIS_ONLY with typed reason
    if res.outcome.support_level == SupportLevel.ANALYSIS_ONLY:
        assert res.outcome.unverified is True
        assert any(r.code == expected_code for r in res.outcome.reasons), f"Expected {expected_code}, got {res.outcome.reasons}"


def test_ollama_unreachable_assist_mode_completes_with_warning(tmp_path):
    clear_health_cache()
    s = _fast_settings(tmp_path, ollama_base="http://127.0.0.1:19998", llm_mode="assist", llm_connect_timeout_s=0.4)
    src = (FIX / "python" / "simple_fn.py").read_text(encoding="utf-8")
    res = OptimizerAgent(s, log=lambda *a: None).run(
        OptimizeRequest(source=src, use_llm=True, llm_mode="assist", budget=SearchBudget(max_candidates=2, max_time_s=10.0))
    )
    assert res.status == "ok"
    assert res.outcome is not None
    assert res.outcome.support_level in (SupportLevel.FULL, SupportLevel.VERIFIED_WEAK)
    assert any(r.code == ReasonCode.LLM_UNAVAILABLE for r in res.outcome.reasons)
    assert len(res.outcome.provenance.fallbacks) >= 1


def test_ollama_unreachable_required_mode_fails_cleanly_no_traceback(tmp_path):
    clear_health_cache()
    s = _fast_settings(tmp_path, ollama_base="http://127.0.0.1:19998", llm_mode="required", llm_connect_timeout_s=0.4)
    src = (FIX / "python" / "simple_fn.py").read_text(encoding="utf-8")
    res = OptimizerAgent(s, log=lambda *a: None).run(OptimizeRequest(source=src, use_llm=True, llm_mode="required"))
    assert res.status == "error"
    assert res.outcome is not None
    assert res.outcome.support_level == SupportLevel.REFUSED
    assert any(r.code == ReasonCode.LLM_UNAVAILABLE for r in res.outcome.reasons)
    assert "Traceback" not in res.message


def test_stage_exception_isolated_and_persisted_to_diagnostics_json(tmp_path):
    run_dir = tmp_path / "run_diag"
    runner = StageRunner(run_dir)

    def _boom():
        raise RuntimeError("injected stage failure")

    val, sr = runner.run_stage("complexity", _boom, fallback=lambda exc: "degraded_ok")
    assert val == "degraded_ok"
    assert sr.status == "degraded"
    assert any(r.code == ReasonCode.STAGE_ERROR for r in runner.reasons)
    diag_file = run_dir / "diagnostics.json"
    assert diag_file.exists()
    diags = json.loads(diag_file.read_text(encoding="utf-8"))
    assert diags[0]["stage"] == "complexity"
    assert "injected stage failure" in diags[0]["traceback"]
