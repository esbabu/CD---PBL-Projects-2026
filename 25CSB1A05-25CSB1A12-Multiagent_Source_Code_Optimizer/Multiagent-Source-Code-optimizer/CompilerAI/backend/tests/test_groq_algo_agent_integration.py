"""
Comprehensive Integration Verification Tests for the Groq-Powered Algo Agent.
Verifies all 7 tests specified in Section 11 of the Master Implementation Prompt:
- Test 1: LLM mode routing and execution
- Test 2: Heuristic mode routing to the SAME new Algo Agent (old heuristic never invoked)
- Test 3: C and C++ language handling and validation
- Test 4: JavaScript language handling
- Test 5: Structured error and failure handling without server crashes
- Test 6: Data mapping and UI compatibility fields
- Test 7: Strict architectural bypass of old optimizer
"""
import sys
from pathlib import Path
import pytest
from unittest.mock import MagicMock, patch

from app.orchestration.orchestrator import PipelineOrchestrator
from app.contracts.requests import CreateRunRequest, RunMode, InferenceMode
from app.contracts.common import StageStatus
from app.orchestration.cancellation import CancellationToken
from app.services.result_store import result_store
from app.agents.optimization.adapter import OptimizationAdapter
from app.contracts.optimization import OptimizationRequest
from app.contracts.events import RunEvent


MOCK_GROQ_PYTHON_RESPONSE = {
    "optimized_code": "def two_sum(nums: list[int], target: int) -> list[int]:\n    lookup = {}\n    for i, n in enumerate(nums):\n        if target - n in lookup:\n            return [lookup[target - n], i]\n        lookup[n] = i\n    return []\n",
    "time_complexity_before": "O(N^2)",
    "time_complexity_after": "O(N)",
    "space_complexity_before": "O(1)",
    "space_complexity_after": "O(N)",
    "summary": "Replaced nested loops with a hash map lookup for linear time complexity.",
    "changes": [
        "Constructed a hash map for seen values",
        "Reduced time complexity from O(N^2) to O(N)",
    ],
}

MOCK_GROQ_CPP_RESPONSE = {
    "optimized_code": "int sumArray(const int* arr, int n) {\n    int sum = 0;\n    int i = 0;\n    for (; i + 3 < n; i += 4) {\n        sum += arr[i] + arr[i+1] + arr[i+2] + arr[i+3];\n    }\n    for (; i < n; ++i) sum += arr[i];\n    return sum;\n}\n",
    "time_complexity_before": "O(N)",
    "time_complexity_after": "O(N)",
    "space_complexity_before": "O(1)",
    "space_complexity_after": "O(1)",
    "summary": "Applied 4x loop unrolling to maximize CPU pipelining.",
    "changes": ["Unrolled loop by a factor of 4"],
}

MOCK_GROQ_C_RESPONSE = {
    "optimized_code": "int contains(const int values[], int size, int target) {\n    int left = 0, right = size - 1;\n    while (left <= right) {\n        int mid = left + (right - left) / 2;\n        if (values[mid] == target) return 1;\n        if (values[mid] < target) left = mid + 1;\n        else right = mid - 1;\n    }\n    return 0;\n}\n",
    "time_complexity_before": "O(N)",
    "time_complexity_after": "O(log N)",
    "space_complexity_before": "O(1)",
    "space_complexity_after": "O(1)",
    "summary": "Replaced linear scan with binary search for sorted input.",
    "changes": ["Optimized linear search to binary search"],
}

MOCK_GROQ_JS_RESPONSE = {
    "optimized_code": "function twoSum(nums, target) {\n  const map = new Map();\n  for (let i = 0; i < nums.length; i++) {\n    const comp = target - nums[i];\n    if (map.has(comp)) return [map.get(comp), i];\n    map.set(nums[i], i);\n  }\n  return [];\n}\n",
    "time_complexity_before": "O(N^2)",
    "time_complexity_after": "O(N)",
    "space_complexity_before": "O(1)",
    "space_complexity_after": "O(N)",
    "summary": "Optimized twoSum from O(N^2) to O(N) using Map lookup.",
    "changes": ["Switched nested loops to Map hash table lookup"],
}


@pytest.mark.anyio
async def test_1_llm_mode_python_execution(monkeypatch):
    """Test 1: LLM mode routes to new Algo Agent, queries Groq, returns optimized code."""
    from algo_agent.llm import GroqClient
    monkeypatch.setattr(GroqClient, "generate_json", lambda self, sys, usr: MOCK_GROQ_PYTHON_RESPONSE)

    orch = PipelineOrchestrator()
    run_id = "test-groq-llm-py"
    req = CreateRunRequest(
        mode=RunMode.OPTIMIZE,
        language="python",
        inference_mode=InferenceMode.LLM,
        source_code="def two_sum(nums, target):\n    for i in range(len(nums)):\n        for j in range(i+1, len(nums)):\n            if nums[i] + nums[j] == target:\n                return [i, j]\n    return []\n",
    )

    await orch.execute_run(run_id, req, CancellationToken(run_id))
    results = result_store.get_results(run_id)

    assert results["status"] == "completed"
    opt = results["optimization_result"]
    assert opt is not None
    assert opt["status"] == "completed"
    assert "lookup" in opt["optimized_code"]
    assert opt["metrics"]["time_complexity_before"] == "O(N^2)"
    assert opt["metrics"]["time_complexity_after"] == "O(N)"
    assert opt["metrics"]["selected_mode"] == "llm"
    assert opt["metrics"]["code_changed"] is True
    assert len(opt["transformations"]) > 0


@pytest.mark.anyio
async def test_2_heuristic_mode_routes_to_same_algo_agent(monkeypatch):
    """Test 2: Heuristic mode routes to the SAME new Algo Agent and produces output."""
    from algo_agent.llm import GroqClient
    called = []

    def mock_generate(self, sys, usr):
        called.append("GroqClient.generate_json")
        return MOCK_GROQ_PYTHON_RESPONSE

    monkeypatch.setattr(GroqClient, "generate_json", mock_generate)

    orch = PipelineOrchestrator()
    run_id = "test-groq-heuristic-py"
    req = CreateRunRequest(
        mode=RunMode.OPTIMIZE,
        language="python",
        inference_mode=InferenceMode.HEURISTICS,
        source_code="def two_sum(nums, target):\n    for i in range(len(nums)):\n        for j in range(i+1, len(nums)):\n            if nums[i] + nums[j] == target:\n                return [i, j]\n    return []\n",
    )

    await orch.execute_run(run_id, req, CancellationToken(run_id))
    results = result_store.get_results(run_id)

    assert len(called) == 1
    assert called[0] == "GroqClient.generate_json"
    assert results["status"] == "completed"
    opt = results["optimization_result"]
    assert opt["metrics"]["selected_mode"] == "heuristics"
    assert opt["metrics"]["time_complexity_after"] == "O(N)"
    assert "optagent" not in sys.modules


@pytest.mark.anyio
async def test_3_c_and_cpp_language_support(monkeypatch):
    """Test 3: C and C++ programs are handled with correct language detection & validation."""
    from algo_agent.llm import GroqClient

    def mock_generate(self, sys_prompt, usr_prompt):
        if "c++" in usr_prompt.lower() or "cpp" in usr_prompt.lower():
            return MOCK_GROQ_CPP_RESPONSE
        return MOCK_GROQ_C_RESPONSE

    monkeypatch.setattr(GroqClient, "generate_json", mock_generate)
    orch = PipelineOrchestrator()

    # C program
    run_c = "test-groq-c"
    req_c = CreateRunRequest(
        mode=RunMode.OPTIMIZE,
        language="c",
        inference_mode=InferenceMode.LLM,
        source_code="int contains(const int values[], int size, int target) {\n    for (int i = 0; i < size; ++i) {\n        if (values[i] == target) return 1;\n    }\n    return 0;\n}\n",
    )
    await orch.execute_run(run_c, req_c, CancellationToken(run_c))
    res_c = result_store.get_results(run_c)
    assert res_c["status"] == "completed"
    assert res_c["optimization_result"]["metrics"]["language"] == "c"
    assert "binary search" in res_c["optimization_result"]["transformations"][0].lower() or "mid" in res_c["optimization_result"]["optimized_code"]

    # C++ program
    run_cpp = "test-groq-cpp"
    req_cpp = CreateRunRequest(
        mode=RunMode.OPTIMIZE,
        language="cpp",
        inference_mode=InferenceMode.LLM,
        source_code="int sumArray(int* arr, int n) {\n    int sum = 0;\n    for(int i=0; i<n; i++) sum += arr[i];\n    return sum;\n}\n",
    )
    await orch.execute_run(run_cpp, req_cpp, CancellationToken(run_cpp))
    res_cpp = result_store.get_results(run_cpp)
    assert res_cpp["status"] == "completed"
    assert res_cpp["optimization_result"]["metrics"]["language"] == "cpp"
    assert "unrolling" in res_cpp["optimization_result"]["transformations"][0].lower() or "i + 3" in res_cpp["optimization_result"]["optimized_code"]


@pytest.mark.anyio
async def test_4_javascript_language_support(monkeypatch):
    """Test 4: JavaScript program is handled with language detection & Map optimization."""
    from algo_agent.llm import GroqClient
    monkeypatch.setattr(GroqClient, "generate_json", lambda self, sys, usr: MOCK_GROQ_JS_RESPONSE)

    orch = PipelineOrchestrator()
    run_id = "test-groq-js"
    req = CreateRunRequest(
        mode=RunMode.OPTIMIZE,
        language="javascript",
        inference_mode=InferenceMode.LLM,
        source_code="function twoSum(nums, target) { for (let i = 0; i < nums.length; i++) { for (let j = i + 1; j < nums.length; j++) { if (nums[i] + nums[j] === target) return [i, j]; } } return []; }\n",
    )
    await orch.execute_run(run_id, req, CancellationToken(run_id))
    res = result_store.get_results(run_id)

    assert res["status"] == "completed"
    opt = res["optimization_result"]
    assert opt["metrics"]["language"] == "javascript"
    assert "Map" in opt["optimized_code"]


@pytest.mark.anyio
async def test_5_failure_handling_and_resilience():
    """Test 5: Missing API key, syntax error, and API errors are handled without crashes."""
    adapter = OptimizationAdapter()
    events = []

    async def emit(evt: RunEvent):
        events.append(evt)

    # 5a: Missing API key handling
    req_missing_key = OptimizationRequest(
        run_id="run-fail-key",
        source_code="def foo():\n    return 42\n",
        language="python",
        inference_mode=InferenceMode.LLM,
        options={},
    )
    with patch("algo_agent.llm.GroqClient.generate_json", side_effect=RuntimeError("LLM API key is missing")):
        res = await adapter.run(req_missing_key, emit)
        assert res.status == "failed"
        assert res.optimized_code is None
        # Must not crash, returns clean error message
        assert any(e.type == "agent_failed" for e in events)
        assert "API key" in res.diagnostics[0]
        # Sensitive credentials must not be exposed
        assert "Bearer" not in res.diagnostics[0]

    # 5b: Syntax error in source code
    events.clear()
    req_syntax_err = OptimizationRequest(
        run_id="run-fail-syntax",
        source_code="def broken_syntax(:\n    return 42",
        language="python",
        inference_mode=InferenceMode.LLM,
        options={},
    )
    res_syntax = await adapter.run(req_syntax_err, emit)
    assert res_syntax.status == "failed"
    assert "syntax" in res_syntax.diagnostics[0].lower()


@pytest.mark.anyio
async def test_6_ui_data_mapping_fields(monkeypatch):
    """Test 6: All fields required by the UI are cleanly populated."""
    from algo_agent.llm import GroqClient
    monkeypatch.setattr(GroqClient, "generate_json", lambda self, sys, usr: MOCK_GROQ_PYTHON_RESPONSE)

    adapter = OptimizationAdapter()
    events = []

    async def emit(evt: RunEvent):
        events.append(evt)

    req = OptimizationRequest(
        run_id="run-ui-mapping",
        source_code="def two_sum(nums, target):\n    pass\n",
        language="python",
        inference_mode=InferenceMode.LLM,
        options={},
    )
    res = await adapter.run(req, emit)

    # Verify every field expected by the UI
    assert res.optimized_code is not None
    assert isinstance(res.transformations, list)
    assert len(res.transformations) > 0
    assert "time_complexity_before" in res.metrics
    assert "time_complexity_after" in res.metrics
    assert "space_complexity_before" in res.metrics
    assert "space_complexity_after" in res.metrics
    assert "elapsed_seconds" in res.metrics
    assert "code_changed" in res.metrics
    assert "evidence_tier" in res.metrics
    assert "support_level" in res.metrics
    assert "outcome" in res.raw_result
    assert isinstance(res.raw_result["outcome"]["stages"], list)
    assert len(res.diagnostics) > 0


def test_7_old_optimizer_completely_bypassed():
    """Test 7: Verify that the old optimization agent (optagent) is not imported or used."""
    import app.agents.optimization.adapter as adapter_module
    module_source = Path(adapter_module.__file__).read_text(encoding="utf-8")

    assert "from optagent" not in module_source
    assert "import optagent" not in module_source
    assert "OptimizerAgent" not in module_source
    assert "http://127.0.0.1:11434/api/generate" not in module_source
    assert "algo_agent_groq" in module_source or "algo_agent" in module_source
