"""End-to-end audit regression tests covering C++, C, Python, JavaScript, and failure modes."""
import time
import pytest
from starlette.testclient import TestClient

from app.main import app
from app.orchestration.orchestrator import PipelineOrchestrator
from app.contracts.requests import CreateRunRequest, RunMode, InferenceMode
from app.orchestration.cancellation import CancellationToken
from app.services.result_store import result_store


def test_health_probes_ollama_without_attribute_error():
    client = TestClient(app)
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    ollama = data["ollama"]
    assert ollama["reason_kind"] in ("ok", "unreachable", "no_models")
    assert "ollama_base_url" not in (ollama.get("remediation") or "")
    assert "javascript" in data["supported_languages"]
    assert "python" in data["toolchains"]
    assert "javascript" in data["toolchains"]


async def _run_pipeline(run_id: str, mode: RunMode, language: str, inference: InferenceMode, source: str):
    orch = PipelineOrchestrator()
    req = CreateRunRequest(
        mode=mode,
        language=language,
        inference_mode=inference,
        source_code=source,
    )
    await orch.execute_run(run_id, req, CancellationToken(run_id))
    return result_store.get_results(run_id)


@pytest.mark.anyio
async def test_cpp_pipeline_degrades_honestly_and_audits_original_source():
    cpp_vuln = """#include <stdio.h>
#include <stdlib.h>

void process_input(char* user_input) {
    char buffer[64];
    gets(buffer);
    printf(user_input);
}
"""
    res = await _run_pipeline("audit-cpp-1", RunMode.PIPELINE, "cpp", InferenceMode.LLM, cpp_vuln)
    assert res["status"] == "partially_completed"
    opt = res["optimization_result"]
    assert opt["metrics"]["support_level"] == "analysis_only"
    assert opt["metrics"]["unverified"] is True
    assert opt["metrics"]["code_changed"] is False
    # Zero duplicate reason-code diagnostics
    toolchain_diags = [d for d in opt["diagnostics"] if "[TOOLCHAIN_MISSING]" in d]
    assert len(toolchain_diags) == 1
    # Security honestly audited ORIGINAL source and found real vulnerabilities
    sec = res["security_result"]
    assert sec["source_kind"] == "original"
    assert len(sec["findings"]) >= 2


@pytest.mark.anyio
async def test_c_pipeline_degrades_honestly_and_finds_cwe121_cwe134():
    c_vuln = """#include <stdio.h>
#include <string.h>

void copy_input(const char* user_input) {
    char buf[64];
    strcpy(buf, user_input);
    printf(buf);
}
"""
    res = await _run_pipeline("audit-c-1", RunMode.PIPELINE, "c", InferenceMode.HEURISTICS, c_vuln)
    assert res["status"] == "partially_completed"
    assert res["optimization_result"]["metrics"]["unverified"] is True
    assert res["security_result"]["source_kind"] == "original"
    cwes = {f["rule_or_cwe"] for f in res["security_result"]["findings"]}
    assert "CWE-121" in cwes or "CWE-134" in cwes


@pytest.mark.anyio
async def test_python_optimal_function_does_not_claim_applied_transformations():
    py_opt = "def add(a: int, b: int) -> int:\n    return a + b\n"
    res = await _run_pipeline("audit-py-opt", RunMode.OPTIMIZE, "python", InferenceMode.HEURISTICS, py_opt)
    assert res["status"] == "completed"
    opt = res["optimization_result"]
    assert opt["metrics"]["code_changed"] is False
    assert any("no faster verified candidate found" in t.lower() for t in opt["transformations"])
    assert not any("hotspot" in t.lower() for t in opt["transformations"])


@pytest.mark.anyio
async def test_python_class_based_method_executes_without_denial():
    py_cls = """class Solution:
    def two_sum(self, nums: list[int], target: int) -> list[int]:
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                if nums[i] + nums[j] == target:
                    return [i, j]
        return []
"""
    res = await _run_pipeline("audit-py-cls", RunMode.OPTIMIZE, "python", InferenceMode.HEURISTICS, py_cls)
    assert res["status"] == "completed"
    opt = res["optimization_result"]
    assert opt["metrics"]["unverified"] is False
    assert opt["metrics"]["support_level"] in ("full", "verified_weak")


@pytest.mark.anyio
async def test_javascript_function_and_script_modes():
    js_script = """const fs = require('fs');
const data = fs.readFileSync(0, 'utf8').trim().split(/\\s+/).map(Number);
console.log(data.reduce((a, b) => a + b, 0));
"""
    res = await _run_pipeline("audit-js-script", RunMode.OPTIMIZE, "javascript", InferenceMode.HEURISTICS, js_script)
    assert res["status"] == "partially_completed"
    opt = res["optimization_result"]
    assert opt["metrics"]["support_level"] == "analysis_only"
    assert any("UNSUPPORTED_ENTRY_KIND" in d for d in opt["diagnostics"])


@pytest.mark.anyio
async def test_failure_modes_syntax_missing_dep_and_timeout_fast_fail():
    # 1. Unrepairable syntax error -> failed cleanly
    res_syn = await _run_pipeline("audit-fail-syn", RunMode.OPTIMIZE, "python", InferenceMode.HEURISTICS, "def bad( = 1:\n  pass\n")
    assert res_syn["status"] == "failed"
    assert any("SYNTAX_ERROR" in d for d in res_syn["optimization_result"]["diagnostics"])

    # 2. Missing dependency -> Analysis-Only with MISSING_DEPENDENCY
    res_dep = await _run_pipeline(
        "audit-fail-dep",
        RunMode.OPTIMIZE,
        "python",
        InferenceMode.HEURISTICS,
        "import nonexistent_pkg_xyz_999\ndef f(x: int) -> int:\n    return x\n",
    )
    assert res_dep["status"] == "partially_completed"
    assert any("MISSING_DEPENDENCY" in d for d in res_dep["optimization_result"]["diagnostics"])

    # 3. Infinite loop -> fast-fails cleanly in < 35s (not 210s!)
    t0 = time.time()
    res_hang = await _run_pipeline(
        "audit-fail-hang",
        RunMode.OPTIMIZE,
        "python",
        InferenceMode.HEURISTICS,
        "def hang(x: int) -> int:\n    while True:\n        pass\n",
    )
    elapsed = time.time() - t0
    assert elapsed < 35.0, f"Infinite loop took too long: {elapsed:.1f}s"
    assert res_hang["status"] == "partially_completed"
    assert res_hang["optimization_result"]["metrics"]["unverified"] is True
    assert any("timed out" in d.lower() for d in res_hang["optimization_result"]["diagnostics"])
