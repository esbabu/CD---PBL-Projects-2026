import asyncio
import sys
from pathlib import Path
import pytest

backend_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_dir))

from app.orchestration.orchestrator import PipelineOrchestrator
from app.contracts.requests import CreateRunRequest, RunMode, InferenceMode
from app.orchestration.cancellation import CancellationToken
from app.services.result_store import result_store


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_no_duplicate_cards_for_same_line_c():
    """Verify that multiple security tools flagging line 6 in C produce exactly 1 card."""
    orch = PipelineOrchestrator()
    run_id = "test-nodupline-c"
    code = """#include <stdio.h>
#include <string.h>

void test(char* user_input) {
    char buf[64];
    gets(buf);
    printf(user_input);
}
"""
    req = CreateRunRequest(
        mode=RunMode.SECURITY,
        language="c",
        inference_mode=InferenceMode.HEURISTICS,
        source_code=code,
    )
    await orch.execute_run(run_id, req, CancellationToken(run_id))
    res = result_store.get_results(run_id)
    sec = res.get("security_result")

    assert sec is not None
    findings = sec["findings"]

    # Check line numbers of all findings with a line number
    lines = [f["line_number"] for f in findings if f.get("line_number") is not None]
    unique_lines = set(lines)

    # Invariant: Each line must have at most 1 card
    assert len(lines) == len(unique_lines), f"Duplicate cards found for the same line! Lines: {lines}"
    assert 6 in unique_lines
    assert 7 in unique_lines


@pytest.mark.anyio
async def test_no_duplicate_cards_for_same_line_cpp():
    """Verify that multiple security tools (cppcheck, clang-tidy) flagging line 8 in C++ produce exactly 1 card."""
    orch = PipelineOrchestrator()
    run_id = "test-nodupline-cpp"
    code = """#include <iostream>
#include <vector>

void leak() {
    int* ptr = new int[100];
    ptr[0] = 42;
    // Missing delete[] ptr
}
"""
    req = CreateRunRequest(
        mode=RunMode.SECURITY,
        language="cpp",
        inference_mode=InferenceMode.HEURISTICS,
        source_code=code,
    )
    await orch.execute_run(run_id, req, CancellationToken(run_id))
    res = result_store.get_results(run_id)
    sec = res.get("security_result")

    assert sec is not None
    findings = sec["findings"]

    lines = [f["line_number"] for f in findings if f.get("line_number") is not None]
    unique_lines = set(lines)

    assert len(lines) == len(unique_lines), f"Duplicate cards found for the same line! Lines: {lines}"
    assert 8 in unique_lines
    assert len(findings) == 1
