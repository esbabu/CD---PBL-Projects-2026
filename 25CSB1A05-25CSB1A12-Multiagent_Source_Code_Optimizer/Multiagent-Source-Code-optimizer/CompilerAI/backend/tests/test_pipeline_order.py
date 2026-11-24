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
async def test_full_pipeline_sequential_order_and_artifact_handoff():
    call_order = []

    async def mock_opt_run(req, emit):
        call_order.append("optimization")
        return OptimizationResult(
            run_id=req.run_id,
            status="completed",
            optimized_code="// EXACT OPTIMIZED CODE ARTIFACT",
            transformations=["loop unrolling"],
            metrics={},
            raw_result={},
            diagnostics=[],
            duration_ms=50,
            is_demo=True,
        )

    async def mock_sec_run(req, emit):
        call_order.append("security")
        # Validate that Security received the exact output from Optimization
        assert req.source_code == "// EXACT OPTIMIZED CODE ARTIFACT"
        assert req.source_kind == SourceKind.OPTIMIZED
        return SecurityResult(
            run_id=req.run_id,
            status="completed",
            source_kind=SourceKind.OPTIMIZED,
            findings=[],
            raw_result={},
            diagnostics=[],
            duration_ms=50,
            is_demo=True,
        )

    opt_mock = AsyncMock()
    opt_mock.run.side_effect = mock_opt_run
    sec_mock = AsyncMock()
    sec_mock.run.side_effect = mock_sec_run

    orchestrator = PipelineOrchestrator(
        optimization_adapter=opt_mock,
        security_adapter=sec_mock,
    )

    req = CreateRunRequest(
        mode=RunMode.PIPELINE,
        source_code="int main() { return 0; }",
        language="cpp",
        inference_mode=InferenceMode.HEURISTICS,
        options={},
    )
    token = CancellationToken("run-pipe-seq")

    await orchestrator.execute_run("run-pipe-seq", req, token)

    # Strictly sequential: optimization executed before security
    assert call_order == ["optimization", "security"]

    record = result_store.get_run("run-pipe-seq")
    assert record.status == "completed"
    assert record.optimization_result is not None
    assert record.security_result is not None

@pytest.mark.anyio
async def test_full_pipeline_optimization_failure_halts_security():
    opt_mock = AsyncMock()
    opt_mock.run.return_value = OptimizationResult(
        run_id="run-opt-fail",
        status="failed",
        optimized_code=None,
        transformations=[],
        metrics={},
        raw_result={"error": "Syntax error"},
        diagnostics=["Syntax error in input"],
        duration_ms=50,
        is_demo=True,
    )
    sec_mock = AsyncMock()

    orchestrator = PipelineOrchestrator(
        optimization_adapter=opt_mock,
        security_adapter=sec_mock,
    )

    req = CreateRunRequest(
        mode=RunMode.PIPELINE,
        source_code="int main() { return 0; }",
        language="cpp",
        inference_mode=InferenceMode.HEURISTICS,
        options={},
    )
    token = CancellationToken("run-opt-fail")

    await orchestrator.execute_run("run-opt-fail", req, token)

    assert opt_mock.run.call_count == 1
    # Security MUST NOT be called when Optimization fails
    assert sec_mock.run.call_count == 0

    record = result_store.get_run("run-opt-fail")
    assert record.status == "failed"
    assert record.security_result is None

@pytest.mark.anyio
async def test_full_pipeline_missing_optimized_code_halts_security():
    opt_mock = AsyncMock()
    # Optimization completed, but produced no code artifact
    opt_mock.run.return_value = OptimizationResult(
        run_id="run-opt-nocode",
        status="completed",
        optimized_code=None,
        transformations=[],
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
        mode=RunMode.PIPELINE,
        source_code="int main() { return 0; }",
        language="cpp",
        inference_mode=InferenceMode.HEURISTICS,
        options={},
    )
    token = CancellationToken("run-opt-nocode")

    await orchestrator.execute_run("run-opt-nocode", req, token)

    assert opt_mock.run.call_count == 1
    # Security MUST NOT be called on missing or guessed code
    assert sec_mock.run.call_count == 0

    record = result_store.get_run("run-opt-nocode")
    assert record.status == "partially_completed"
    assert "Missing optimized code" in record.failure_reason

@pytest.mark.anyio
async def test_full_pipeline_security_failure_preserves_optimization_artifact():
    opt_mock = AsyncMock()
    opt_mock.run.return_value = OptimizationResult(
        run_id="run-sec-fail",
        status="completed",
        optimized_code="// Good optimized code",
        transformations=["loop unroll"],
        metrics={},
        raw_result={},
        diagnostics=[],
        duration_ms=50,
        is_demo=True,
    )
    sec_mock = AsyncMock()
    sec_mock.run.return_value = SecurityResult(
        run_id="run-sec-fail",
        status="failed",
        source_kind=SourceKind.OPTIMIZED,
        findings=[],
        raw_result={"error": "Scanner crash"},
        diagnostics=["Static analyzer crash"],
        duration_ms=50,
        is_demo=True,
    )

    orchestrator = PipelineOrchestrator(
        optimization_adapter=opt_mock,
        security_adapter=sec_mock,
    )

    req = CreateRunRequest(
        mode=RunMode.PIPELINE,
        source_code="int main() { return 0; }",
        language="cpp",
        inference_mode=InferenceMode.HEURISTICS,
        options={},
    )
    token = CancellationToken("run-sec-fail")

    await orchestrator.execute_run("run-sec-fail", req, token)

    assert opt_mock.run.call_count == 1
    assert sec_mock.run.call_count == 1

    record = result_store.get_run("run-sec-fail")
    # Honest partial completion state
    assert record.status == "partially_completed"
    # Optimization artifact MUST be preserved
    assert record.optimization_result is not None
    assert record.optimization_result.optimized_code == "// Good optimized code"
    assert record.security_result is not None
    assert record.security_result.status == "failed"
