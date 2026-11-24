import pytest
from app.agents.optimization.adapter import OptimizationAdapter
from app.agents.security.adapter import SecurityAdapter
from app.contracts.optimization import OptimizationRequest
from app.contracts.security import SecurityRequest
from app.contracts.common import InferenceMode, SourceKind
from app.contracts.events import RunEvent

@pytest.mark.anyio
async def test_mock_optimization_adapter_success():
    adapter = OptimizationAdapter(use_mock=True)
    events = []

    async def emit(evt: RunEvent):
        events.append(evt)

    req = OptimizationRequest(
        run_id="run-opt-test",
        source_code="int sumArray(int* arr, int n) { int sum; for(int i=0; i<=n; i++) sum += arr[i]; return sum; }",
        language="cpp",
        inference_mode=InferenceMode.HEURISTICS,
        options={},
    )

    result = await adapter.run(req, emit)

    assert result.run_id == "run-opt-test"
    assert result.status == "completed"
    assert result.is_demo is True
    assert result.optimized_code is not None
    assert len(result.transformations) > 0
    assert len(events) >= 4
    assert events[0].type == "agent_started"
    assert events[-1].type == "agent_completed"

@pytest.mark.anyio
async def test_mock_optimization_adapter_scripted_failure():
    adapter = OptimizationAdapter(use_mock=True)
    events = []

    async def emit(evt: RunEvent):
        events.append(evt)

    req = OptimizationRequest(
        run_id="run-opt-fail",
        source_code="int main() { return 0; }",
        language="cpp",
        inference_mode=InferenceMode.LLM,
        options={"mock_failure": True},
    )

    result = await adapter.run(req, emit)

    assert result.status == "failed"
    assert result.optimized_code is None
    assert any(e.type == "agent_failed" for e in events)

@pytest.mark.anyio
async def test_mock_security_adapter_original_and_optimized():
    adapter = SecurityAdapter(use_mock=True)
    events = []

    async def emit(evt: RunEvent):
        events.append(evt)

    # Test Original Source Assessment
    req_orig = SecurityRequest(
        run_id="run-sec-orig",
        source_code="int sumArray(int* arr, int n) { int sum; for(int i=0; i<=n; i++) sum += arr[i]; return sum; }",
        language="cpp",
        source_kind=SourceKind.ORIGINAL,
        inference_mode=InferenceMode.HEURISTICS,
        options={},
    )

    result_orig = await adapter.run(req_orig, emit)
    assert result_orig.status == "completed"
    assert result_orig.source_kind == SourceKind.ORIGINAL
    assert len(result_orig.findings) >= 2
    assert any("CWE-193" in f.rule_or_cwe for f in result_orig.findings)

    # Test Optimized Source Assessment
    events.clear()
    req_opt = SecurityRequest(
        run_id="run-sec-opt",
        source_code="// Optimized version",
        language="cpp",
        source_kind=SourceKind.OPTIMIZED,
        inference_mode=InferenceMode.HEURISTICS,
        options={},
    )

    result_opt = await adapter.run(req_opt, emit)
    assert result_opt.status == "completed"
    assert result_opt.source_kind == SourceKind.OPTIMIZED
    # Optimized code should show reduced/resolved findings
    assert len(result_opt.findings) <= len(result_orig.findings)
