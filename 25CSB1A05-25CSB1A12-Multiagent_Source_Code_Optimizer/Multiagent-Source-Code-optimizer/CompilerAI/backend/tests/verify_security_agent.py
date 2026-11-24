import asyncio
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_dir))

from app.orchestration.orchestrator import PipelineOrchestrator
from app.contracts.requests import CreateRunRequest, RunMode, InferenceMode
from app.orchestration.cancellation import CancellationToken
from app.services.result_store import result_store


async def test_security(name: str, lang: str, code: str):
    print(f"\n==================================================")
    print(f"Testing Security Agent: {name} ({lang})")
    print(f"==================================================")
    orch = PipelineOrchestrator()
    run_id = f"sec-test-{lang}"
    req = CreateRunRequest(
        mode=RunMode.SECURITY,
        language=lang,
        inference_mode=InferenceMode.HEURISTICS,
        source_code=code,
    )
    await orch.execute_run(run_id, req, CancellationToken(run_id))
    res = result_store.get_results(run_id)
    sec = res.get("security_result")

    assert sec is not None, "No security_result in response!"
    print(f"Status: {sec['status']}")
    print(f"Overall Risk: {sec['raw_result'].get('overall_risk')}")
    print(f"Security Score: {sec['raw_result'].get('security_score')}")
    print(f"Findings Count: {len(sec['findings'])}")
    for idx, f in enumerate(sec['findings'], 1):
        print(f"  {idx}. [{f['severity'].upper()}] [{f.get('rule_or_cwe')}] Line {f.get('line_number')}: {f['title']} - {f['description'][:80]}...")
    return sec


async def main():
    # 1. C snippet with gets and format string
    c_code = """#include <stdio.h>
#include <string.h>

void test(char* user_input) {
    char buf[64];
    gets(buf);
    printf(user_input);
}
"""
    await test_security("C Vulnerable Program", "c", c_code)

    # 2. C++ snippet with memory leak and uninitialized var
    cpp_code = """#include <iostream>
#include <vector>

void leak() {
    int* ptr = new int[100];
    ptr[0] = 42;
    // Missing delete[] ptr
}

int main() {
    leak();
    return 0;
}
"""
    await test_security("C++ Memory Leak", "cpp", cpp_code)

    # 3. Python snippet with eval and md5
    py_code = """import hashlib

def run_calc(user_expr):
    val = eval(user_expr)
    token = hashlib.md5(b"secret").hexdigest()
    return val, token
"""
    await test_security("Python eval and MD5", "python", py_code)


if __name__ == "__main__":
    asyncio.run(main())
