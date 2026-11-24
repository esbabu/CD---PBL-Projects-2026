import pytest
from app.agents.security.adapter import SecurityAdapter
from app.agents.optimization.adapter import OptimizationAdapter
from app.contracts.security import SecurityRequest
from app.contracts.optimization import OptimizationRequest
from app.contracts.common import InferenceMode, SourceKind
from app.contracts.events import RunEvent

@pytest.mark.anyio
async def test_real_security_adapter_audits_vulnerabilities():
    adapter = SecurityAdapter(use_mock=False)
    events = []

    async def emit(evt: RunEvent):
        events.append(evt)

    # Vulnerable Python sample with Command Injection and MD5
    vulnerable_py = """
import os
import hashlib

def run_cmd(user_arg):
    os.system("ping " + user_arg)

def hash_pw(pw):
    return hashlib.md5(pw.encode()).hexdigest()
"""

    req = SecurityRequest(
        run_id="run-real-sec-test",
        source_code=vulnerable_py,
        language="python",
        source_kind=SourceKind.ORIGINAL,
        inference_mode=InferenceMode.HEURISTICS,
        options={},
    )

    result = await adapter.run(req, emit)

    assert result.status == "completed"
    assert result.is_demo is False
    assert len(result.findings) >= 2
    # Verify CWE-78 (command injection) or CWE-328 (MD5) was found
    rule_cwes = [f.rule_or_cwe for f in result.findings]
    assert any("CWE-78" in str(c) for c in rule_cwes)
    assert any("CWE-328" in str(c) for c in rule_cwes)

@pytest.mark.anyio
async def test_real_security_adapter_audits_cpp_vulnerabilities():
    adapter = SecurityAdapter(use_mock=False)
    events = []

    async def emit(evt: RunEvent):
        events.append(evt)

    # Vulnerable C++ with unsafe gets() and format string
    vulnerable_cpp = """
#include <stdio.h>
#include <stdlib.h>

void process_input(char* user_input) {
    char buffer[64];
    gets(buffer);
    printf(user_input);
}
"""

    req = SecurityRequest(
        run_id="run-real-sec-cpp",
        source_code=vulnerable_cpp,
        language="cpp",
        source_kind=SourceKind.ORIGINAL,
        inference_mode=InferenceMode.HEURISTICS,
        options={},
    )

    result = await adapter.run(req, emit)

    assert result.status == "completed"
    assert result.is_demo is False
    assert len(result.findings) >= 2
    rule_cwes = [f.rule_or_cwe for f in result.findings]
    assert any("CWE-242" in str(c) or "CWE-134" in str(c) for c in rule_cwes)

@pytest.mark.anyio
async def test_real_optimization_adapter_optimizes_two_sum():
    adapter = OptimizationAdapter(use_mock=False)
    events = []

    async def emit(evt: RunEvent):
        events.append(evt)

    two_sum_code = """
def two_sum(nums: list[int], target: int) -> list[int]:
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
"""

    req = OptimizationRequest(
        run_id="run-real-opt-test",
        source_code=two_sum_code,
        language="python",
        inference_mode=InferenceMode.HEURISTICS,
        options={},
    )

    result = await adapter.run(req, emit)

    assert result.status == "completed"
    assert result.is_demo is False
    assert result.optimized_code is not None
    assert "two_sum" in result.optimized_code
    assert float(result.metrics.get("overall_speedup", "1.0x").replace("x", "")) > 1.0
