import asyncio
import sys
from pathlib import Path

_root = Path(r"C:\Users\jaish\Desktop\TOC FINAL FOLDER\END FOLDER\Multiagent-Source-Code-Optimizer\CompilerAI")
sys.path.insert(0, str(_root / "backend"))
sys.path.insert(0, str(_root / "security_related_files (2)" / "security_related_files"))
sys.path.insert(0, str(_root / "algo_agent_groq"))

from app.agents.optimization.adapter import OptimizationAdapter
from app.agents.security.adapter import SecurityAdapter
from app.contracts.optimization import OptimizationRequest
from app.contracts.security import SecurityRequest
from app.contracts.common import SourceKind
from app.contracts.requests import InferenceMode

async def main():
    with open(r"scratch\vulnerable_samples.cpp", "r", encoding="utf-8") as f:
        cpp_code = f.read()

    events = []
    async def emit(e): events.append(e)

    # 1. Test Optimization
    opt_adapter = OptimizationAdapter(use_mock=False)
    opt_req = OptimizationRequest(
        run_id="run-preset-opt",
        source_code=cpp_code,
        language="cpp",
        inference_mode=InferenceMode.LLM,
        options={},
    )
    opt_res = await opt_adapter.run(opt_req, emit)
    print("=== OPTIMIZATION PRESET RESULT ===")
    print("Status:", opt_res.status)
    print("Complexity Before:", opt_res.metrics.get("time_complexity_before"))
    print("Complexity After:", opt_res.metrics.get("time_complexity_after"))
    print("Transformations Count:", len(opt_res.transformations))
    print("Sample Transformation 1:", opt_res.transformations[0])
    print("Optimized Code Length:", len(opt_res.optimized_code))

    # 2. Test Security
    sec_adapter = SecurityAdapter(use_mock=False)
    sec_req = SecurityRequest(
        run_id="run-preset-sec",
        source_code=cpp_code,
        language="cpp",
        source_kind=SourceKind.ORIGINAL,
        inference_mode=InferenceMode.LLM,
        options={},
    )
    sec_res = await sec_adapter.run(sec_req, emit)
    print("\n=== SECURITY PRESET RESULT ===")
    print("Status:", sec_res.status)
    print("Risk:", sec_res.raw_result.get("overall_risk"))
    print("Total Findings:", len(sec_res.findings))
    c_lines = [f.line_number for f in sec_res.findings if f.line_number is not None]
    print("Any duplicate lines?:", len(c_lines) != len(set(c_lines)))
    print("Sample Finding 1:", f"Line {sec_res.findings[0].line_number}: {sec_res.findings[0].title} [{sec_res.findings[0].rule_or_cwe}]")

asyncio.run(main())
