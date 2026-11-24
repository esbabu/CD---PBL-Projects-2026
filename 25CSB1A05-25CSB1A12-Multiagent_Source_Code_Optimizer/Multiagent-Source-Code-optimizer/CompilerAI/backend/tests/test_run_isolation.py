import pytest
from app.contracts.requests import CreateRunRequest, RunMode, InferenceMode
from app.contracts.optimization import OptimizationResult
from app.contracts.security import SecurityResult
from app.contracts.common import SourceKind
from app.services.result_store import result_store
from app.orchestration.cancellation import cancellation_manager

def test_run_result_isolation():
    # Setup two distinct runs
    req1 = CreateRunRequest(
        mode=RunMode.OPTIMIZE,
        source_code="int a = 1;",
        language="cpp",
        inference_mode=InferenceMode.HEURISTICS,
    )
    req2 = CreateRunRequest(
        mode=RunMode.SECURITY,
        source_code="int b = 2;",
        language="cpp",
        inference_mode=InferenceMode.HEURISTICS,
    )

    result_store.create_run("run-iso-1", req1, "2026-11-18T12:00:00Z")
    result_store.create_run("run-iso-2", req2, "2026-11-18T12:01:00Z")

    opt_res = OptimizationResult(
        run_id="run-iso-1",
        status="completed",
        optimized_code="int a_opt = 1;",
        transformations=["inline"],
        metrics={},
        raw_result={},
        diagnostics=[],
        duration_ms=40,
        is_demo=True,
    )
    result_store.set_optimization_result("run-iso-1", opt_res)

    sec_res = SecurityResult(
        run_id="run-iso-2",
        status="completed",
        source_kind=SourceKind.ORIGINAL,
        findings=[],
        raw_result={},
        diagnostics=[],
        duration_ms=40,
        is_demo=True,
    )
    result_store.set_security_result("run-iso-2", sec_res)

    # Verify run 1 only has optimization result
    res1 = result_store.get_results("run-iso-1")
    assert res1["optimization_result"] is not None
    assert res1["security_result"] is None
    assert res1["optimization_result"]["optimized_code"] == "int a_opt = 1;"

    # Verify run 2 only has security result
    res2 = result_store.get_results("run-iso-2")
    assert res2["optimization_result"] is None
    assert res2["security_result"] is not None
    assert res2["security_result"]["source_kind"] == "original"

def test_cancellation_manager():
    token = cancellation_manager.get_token("run-cancel-test")
    assert token.is_cancelled is False

    success = cancellation_manager.cancel("run-cancel-test")
    assert success is True
    assert token.is_cancelled is True

    cancellation_manager.remove("run-cancel-test")


@pytest.mark.anyio
async def test_event_bus_assigns_monotonic_sequence_numbers():
    from app.services.event_bus import EventBus
    from app.contracts.events import RunEvent

    bus = EventBus()
    for i in range(5):
        await bus.publish(
            RunEvent(
                run_id="run-seq-test",
                seq=1,  # Deliberately pass duplicate seq=1
                type="agent_log",
                timestamp="2026-11-18T12:00:00Z",
                message=f"msg {i}",
            )
        )

    events = bus.get_events("run-seq-test")
    assert [e.seq for e in events] == [1, 2, 3, 4, 5]
