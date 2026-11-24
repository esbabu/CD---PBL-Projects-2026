"""Tests for Step 8: OptimizerAgent facade, FastAPI service, and integration adapter."""
from __future__ import annotations

from pathlib import Path
import pytest
from starlette.testclient import TestClient

from optagent.agent import OptimizerAgent, OptimizeRequest
from optagent.config import Settings
from optagent.integrations import adapter as adapter_module
from optagent.integrations.adapter import optimize_algorithm
from optagent.oracle.oracle import source_sha
from optagent.search.schemas import SearchBudget
import optagent.service.app as service_app

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
        search_max_candidates=3,
    )


# ---------------------------------------------------------------------------
# 1. OptimizerAgent Direct
# ---------------------------------------------------------------------------
def test_optimizer_agent_direct(tmp_path):
    s = fast_settings(tmp_path)
    src = (EX / "slow_two_sum.py").read_text(encoding="utf-8")

    agent = OptimizerAgent(s, log=lambda *a: None)
    req = OptimizeRequest(
        source=src,
        budget=SearchBudget(max_candidates=3, max_time_s=30.0),
        use_llm=False,
    )
    res = agent.run(req)

    assert res.status == "ok"
    assert res.report is not None
    assert res.report.entry_point == "two_sum"
    assert res.report.overall_speedup > 1.0
    assert "intent" in res.bundle_paths
    assert "oracle" in res.bundle_paths
    assert "report_json" in res.bundle_paths


# ---------------------------------------------------------------------------
# 2. Ambiguous Entry returns needs_input
# ---------------------------------------------------------------------------
def test_optimizer_agent_ambiguous_entry(tmp_path):
    s = fast_settings(tmp_path)
    ambiguous_code = "def foo(x):\n    return x\n\ndef bar(y):\n    return y\n"

    agent = OptimizerAgent(s, log=lambda *a: None)
    req = OptimizeRequest(source=ambiguous_code, use_llm=False)
    res = agent.run(req)

    assert res.status == "needs_input"
    assert "foo" in res.candidates and "bar" in res.candidates
    assert "Ambiguous entry point" in res.message


# ---------------------------------------------------------------------------
# 3. FastAPI Endpoints (/optimize, /runs/{sha}, /runs/{sha}/override)
# ---------------------------------------------------------------------------
def test_fastapi_endpoints(tmp_path, monkeypatch):
    import sys
    s = fast_settings(tmp_path)
    # Monkeypatch default settings in the service module
    mod = sys.modules["optagent.service.app"]
    monkeypatch.setattr(mod, "Settings", lambda: s)
    client = TestClient(mod.app)

    src = (EX / "slow_two_sum.py").read_text(encoding="utf-8")
    sha = source_sha(src)

    # 1. POST /optimize
    resp = client.post("/optimize", json={"source": src, "use_llm": False})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["report"]["overall_speedup"] > 1.0

    # 2. GET /runs/{sha}
    resp_get = client.get(f"/runs/{sha}")
    assert resp_get.status_code == 200
    data_get = resp_get.json()
    assert data_get["source_sha"] == sha
    assert data_get["report"]["entry_point"] == "two_sum"

    # 3. POST /runs/{sha}/override
    override_body = {
        "overrides": {
            "inputs": [{"args": [[1, 2, 3, 4], 5]}],
            "preservation": {"return_order": "must_preserve"},
        }
    }
    resp_ov = client.post(f"/runs/{sha}/override", json=override_body)
    assert resp_ov.status_code == 200
    data_ov = resp_ov.json()
    assert data_ov["status"] == "ok"


# ---------------------------------------------------------------------------
# 4. Universal Integration Adapter
# ---------------------------------------------------------------------------
def test_universal_adapter(tmp_path, monkeypatch):
    s = fast_settings(tmp_path)
    monkeypatch.setattr(adapter_module, "Settings", lambda: s)

    src = (EX / "slow_two_sum.py").read_text(encoding="utf-8")
    result = optimize_algorithm(src, use_llm=False)

    assert result["status"] == "ok"
    assert result["entry_point"] == "two_sum"
    assert result["overall_speedup"] > 1.0
    assert "optimized_code" in result
    assert "complexity_before" in result
