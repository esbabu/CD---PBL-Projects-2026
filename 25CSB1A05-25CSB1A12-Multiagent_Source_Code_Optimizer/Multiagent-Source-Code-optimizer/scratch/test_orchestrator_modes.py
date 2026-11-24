import asyncio
from pathlib import Path
import sys

p_backend = Path('CompilerAI/backend').resolve()
if str(p_backend) not in sys.path:
    sys.path.insert(0, str(p_backend))

from app.orchestration.orchestrator import PipelineOrchestrator
from app.contracts.requests import CreateRunRequest, RunMode, InferenceMode
from app.orchestration.cancellation import cancellation_manager
from app.services.result_store import result_store

async def test_run(inf_mode: InferenceMode):
    orchestrator = PipelineOrchestrator()
    sample = """int sumArray(int* arr, int n) {
    int sum = 0;
    for (int i = 0; i < n; i++) {
        sum += arr[i];
    }
    return sum;
}"""
    req = CreateRunRequest(
        mode=RunMode.PIPELINE,
        inference_mode=inf_mode,
        language="cpp",
        source_code=sample
    )
    run_id = f"test-{inf_mode.value}"
    token = cancellation_manager.get_token(run_id)
    await orchestrator.execute_run(run_id, req, token)
    res = result_store.get_results(run_id)
    print(f"\nResult for {inf_mode.value}:")
    print("Run Status:", res.get("status"))
    print("Optimization Status:", res.get("optimization", {}).get("status"))
    print("Optimization Pipeline:", res.get("optimization", {}).get("metrics", {}).get("pipeline") or res.get("optimization", {}).get("metrics", {}).get("engine"))
    print("Security Status:", res.get("security", {}).get("status"))
    print("Security Findings:", len(res.get("security", {}).get("findings", [])))

async def main():
    await test_run(InferenceMode.HEURISTICS)
    await test_run(InferenceMode.LLM)

if __name__ == "__main__":
    asyncio.run(main())
