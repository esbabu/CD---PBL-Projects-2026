import pytest
from unittest.mock import AsyncMock
from app.orchestration.orchestrator import PipelineOrchestrator
from app.contracts.requests import CreateRunRequest, RunMode, InferenceMode
from app.contracts.optimization import OptimizationResult
from app.contracts.security import SecurityResult
from app.contracts.common import SourceKind
from app.orchestration.cancellation import CancellationToken
from app.services.result_store import result_store

@pytest.mark.anyio
async def test_optimize_mode_calls_only_optimization():
    opt_mock = AsyncMock()
    opt_mock.run.return_value = OptimizationResult(
        run_id="run-opt-only",
        status="completed",
        optimized_code="// optimized code",
        transformations=["unroll"],
        metrics={},
        raw_result={},
        diagnostics=[],
        duration_ms=50,
        is_demo=True,
    )
    sec_mock = AsyncMock()

    orchestrator = PipelineOrchestrator(
        optimization_adapter=opt_mock,
        security_adapter=sec_mock,
    )

    req = CreateRunRequest(
        mode=RunMode.OPTIMIZE,
        source_code="int main() { return 0; }",
        language="cpp",
        inference_mode=InferenceMode.HEURISTICS,
        options={},
    )
    token = CancellationToken("run-opt-only")

    await orchestrator.execute_run("run-opt-only", req, token)

    # Optimization MUST be called exactly once
    assert opt_mock.run.call_count == 1
    # Security MUST NOT be called in Optimize mode
    assert sec_mock.run.call_count == 0

    record = result_store.get_run("run-opt-only")
    assert record is not None
    assert record.status == "completed"
    assert record.optimization_result is not None
    assert record.security_result is None

@pytest.mark.anyio
async def test_security_mode_calls_only_security():
    opt_mock = AsyncMock()
    sec_mock = AsyncMock()
    sec_mock.run.return_value = SecurityResult(
        run_id="run-sec-only",
        status="completed",
        source_kind=SourceKind.ORIGINAL,
        findings=[],
        raw_result={},
        diagnostics=[],
        duration_ms=50,
        is_demo=True,
    )

    orchestrator = PipelineOrchestrator(
        optimization_adapter=opt_mock,
        security_adapter=sec_mock,
    )

    req = CreateRunRequest(
        mode=RunMode.SECURITY,
        source_code="int main() { return 0; }",
        language="cpp",
        inference_mode=InferenceMode.LLM,
        options={},
    )
    token = CancellationToken("run-sec-only")

    await orchestrator.execute_run("run-sec-only", req, token)

    # Optimization MUST NOT be called in Security mode
    assert opt_mock.run.call_count == 0
    # Security MUST be called exactly once
    assert sec_mock.run.call_count == 1

    # Verify input source kind is ORIGINAL
    call_args = sec_mock.run.call_args[0]
    sec_req = call_args[0]
    assert sec_req.source_kind == SourceKind.ORIGINAL

    record = result_store.get_run("run-sec-only")
    assert record is not None
    assert record.status == "completed"
    assert record.security_result is not None
    assert record.optimization_result is None

@pytest.mark.anyio
async def test_validation_rejects_empty_source():
    opt_mock = AsyncMock()
    sec_mock = AsyncMock()
    orchestrator = PipelineOrchestrator(optimization_adapter=opt_mock, security_adapter=sec_mock)

    req = CreateRunRequest(
        mode=RunMode.PIPELINE,
        source_code="   ",
        language="cpp",
        inference_mode=InferenceMode.HEURISTICS,
        options={},
    )
    token = CancellationToken("run-empty")

    await orchestrator.execute_run("run-empty", req, token)

    assert opt_mock.run.call_count == 0
    assert sec_mock.run.call_count == 0
    record = result_store.get_run("run-empty")
    assert record.status == "failed"
    assert "Empty source code" in record.failure_reason

@pytest.mark.anyio
async def test_validation_rejects_unsupported_language():
    opt_mock = AsyncMock()
    sec_mock = AsyncMock()
    orchestrator = PipelineOrchestrator(optimization_adapter=opt_mock, security_adapter=sec_mock)

    req = CreateRunRequest(
        mode=RunMode.PIPELINE,
        source_code="print('hi')",
        language="fortran",
        inference_mode=InferenceMode.HEURISTICS,
        options={},
    )
    token = CancellationToken("run-bad-lang")

    await orchestrator.execute_run("run-bad-lang", req, token)

    assert opt_mock.run.call_count == 0
    assert sec_mock.run.call_count == 0
    record = result_store.get_run("run-bad-lang")
    assert record.status == "failed"
    assert "Unsupported language" in record.failure_reason
