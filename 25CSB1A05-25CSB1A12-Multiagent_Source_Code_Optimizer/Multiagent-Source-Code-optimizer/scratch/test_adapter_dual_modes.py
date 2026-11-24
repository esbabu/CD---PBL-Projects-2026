import asyncio
from pathlib import Path
import sys

# Ensure backend is on sys.path
p_backend = Path('CompilerAI/backend').resolve()
if str(p_backend) not in sys.path:
    sys.path.insert(0, str(p_backend))

from app.agents.optimization.adapter import OptimizationAdapter
from app.contracts.optimization import OptimizationRequest
from app.contracts.common import InferenceMode
from app.contracts.events import RunEvent

async def dummy_emit(event: RunEvent):
    print(f"[{event.stage}] {event.message[:90]}")

async def main():
    adapter = OptimizationAdapter(use_mock=False)

    sample_cpp = """int sumArray(int* arr, int n) {
    int sum = 0;
    for (int i = 0; i < n; i++) {
        sum += arr[i];
    }
    return sum;
}"""

    # 1. Test Heuristics Mode
    print("\n=== Testing HEURISTICS Mode (Traditional / Deterministic) ===")
    req_heuristics = OptimizationRequest(
        run_id="test-heur-01",
        source_code=sample_cpp,
        language="cpp",
        inference_mode=InferenceMode.HEURISTICS,
        options={}
    )
    res_heur = await adapter.run(req_heuristics, dummy_emit)
    print("Heuristics Status:", res_heur.status)
    print("Metrics pipeline:", res_heur.metrics.get("pipeline"))
    print("Transformations:", res_heur.transformations)

    # 2. Test LLM Mode (Groq API)
    print("\n=== Testing LLM Mode (Groq API Engine) ===")
    req_llm = OptimizationRequest(
        run_id="test-llm-01",
        source_code=sample_cpp,
        language="cpp",
        inference_mode=InferenceMode.LLM,
        options={}
    )
    res_llm = await adapter.run(req_llm, dummy_emit)
    print("LLM Status:", res_llm.status)
    print("Metrics engine:", res_llm.metrics.get("engine"))
    print("Complexity before/after:", res_llm.metrics.get("complexity_before"), "->", res_llm.metrics.get("complexity_after"))
    print("Transformations:", res_llm.transformations)

if __name__ == "__main__":
    asyncio.run(main())
