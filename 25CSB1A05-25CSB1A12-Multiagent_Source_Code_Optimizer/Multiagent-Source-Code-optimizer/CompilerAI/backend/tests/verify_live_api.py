import sys
import asyncio
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "algo_agent_groq"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.orchestration.orchestrator import PipelineOrchestrator
from app.contracts.requests import CreateRunRequest, RunMode, InferenceMode
from app.orchestration.cancellation import CancellationToken
from app.services.result_store import result_store


async def run_test(name: str, lang: str, code: str):
    print(f"\n========================================================")
    print(f"=== Testing {name} ({lang}) ===")
    print(f"========================================================")
    orch = PipelineOrchestrator()
    run_id = f"live-test-{lang}"
    req = CreateRunRequest(
        mode=RunMode.OPTIMIZE,
        language=lang,
        inference_mode=InferenceMode.LLM,
        source_code=code,
    )
    await orch.execute_run(run_id, req, CancellationToken(run_id))
    res = result_store.get_results(run_id)
    opt = res.get("optimization_result")
    assert opt is not None, "No optimization result returned!"
    assert opt["status"] == "completed", f"Status not completed: {opt.get('diagnostics')}"

    print(f"Run ID: {res['run_id']}")
    print(f"Overall Status: {res['status']}")
    print(f"Optimization Status: {opt['status']}")
    print(f"Complexity: {opt['metrics'].get('time_complexity_before')} -> {opt['metrics'].get('time_complexity_after')}")
    print(f"Space: {opt['metrics'].get('space_complexity_before')} -> {opt['metrics'].get('space_complexity_after')}")
    print(f"Summary: {opt['raw_result'].get('summary')}")
    print(f"Transformations: {opt.get('transformations')}")
    print(f"Optimized Code Length: {len(opt.get('optimized_code', ''))} characters")
    print(f"[VERIFIED] {name} passed successfully!\n")
    return opt


async def main():
    # 1. C Program test
    c_code = """int find_max(const int* arr, int n) {
    int m = arr[0];
    for (int i = 1; i < n; i++) {
        if (arr[i] > m) m = arr[i];
    }
    return m;
}"""
    await run_test("C Program", "c", c_code)

    # 2. C++ Four Sum program test
    cpp_foursum = """#include <vector>
#include <algorithm>

std::vector<std::vector<int>> fourSum(std::vector<int>& nums, int target) {
    std::vector<std::vector<int>> result;
    int n = nums.size();
    if (n < 4) return result;
    std::sort(nums.begin(), nums.end());
    for (int i = 0; i < n - 3; i++) {
        for (int j = i + 1; j < n - 2; j++) {
            for (int k = j + 1; k < n - 1; k++) {
                for (int l = k + 1; l < n; l++) {
                    if ((long long)nums[i] + nums[j] + nums[k] + nums[l] == target)
                        result.push_back({nums[i], nums[j], nums[k], nums[l]});
                }
            }
        }
    }
    return result;
}"""
    await run_test("C++ Four Sum", "cpp", cpp_foursum)

    # 3. JavaScript program test
    js_code = """function findDuplicates(arr) {
    let duplicates = [];
    for (let i = 0; i < arr.length; i++) {
        for (let j = i + 1; j < arr.length; j++) {
            if (arr[i] === arr[j] && !duplicates.includes(arr[i])) {
                duplicates.push(arr[i]);
            }
        }
    }
    return duplicates;
}"""
    await run_test("JavaScript Duplicates", "javascript", js_code)

    # 4. Python program test
    py_code = """def fibonacci_slow(n: int) -> int:
    if n <= 1:
        return n
    return fibonacci_slow(n - 1) + fibonacci_slow(n - 2)"""
    await run_test("Python Fibonacci", "python", py_code)

    # 5. Replaced editor content test (proving custom user input is submitted, not example/cached)
    custom_cpp = """int binarySearch(const int arr[], int left, int right, int x) {
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (arr[mid] == x) return mid;
        if (arr[mid] < x) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}"""
    opt_custom = await run_test("Replaced Editor Content (Custom Binary Search)", "cpp", custom_cpp)
    assert "binarySearch" in opt_custom["optimized_code"]


if __name__ == "__main__":
    asyncio.run(main())
