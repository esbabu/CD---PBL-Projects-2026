import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "web-demo"))

from app import app

def run_tests():
    client = app.test_client()
    
    samples_to_test = [
        ("Secure Baseline", "secure.c", True),
        ("Signature Missing", "insecure_rule_signature_missing.c", False),
        ("Rollback Violation", "insecure_rule_rollback_missing.c", False),
        ("Weak Crypto", "insecure_rule_weak_md5.c", False),
        ("Logging Leak", "insecure_rule_logging_puts.c", False),
        ("Hardcoded Secret", "insecure_hardcoded_secret.c", False),
    ]

    print("==================================================================")
    print("END-TO-END REMEDIATION & COMPILATION TEST (ALL 6 CASES)")
    print("==================================================================")
    
    all_ok = True
    for label, filename, expected_init_ok in samples_to_test:
        print(f"\n--- Testing Scenario: {label} ({filename}) ---")
        
        # 1. Load sample (without compiling, as per user requirement)
        sample_res = client.get(f"/api/samples/{filename}")
        assert sample_res.status_code == 200, f"Failed to load sample: {sample_res.data}"
        initial_code = sample_res.json["code"]
        print(f"[1] Loaded sample successfully ({len(initial_code)} chars).")

        # 2. Check initial compilation status
        init_comp_res = client.post("/api/compile", json={
            "code": initial_code,
            "filename": filename,
            "policy": "original_protocol.json",
            "energy": False
        })
        init_comp = init_comp_res.json
        print(f"[2] Initial secure-clang compile ok: {init_comp.get('ok')} (Expected: {expected_init_ok})")
        if init_comp.get('ok') != expected_init_ok:
            print(f"    Initial compile mismatch: {init_comp}")

        # 3. Request Advisory Copilot Audit
        copilot_res = client.post("/api/advisory-copilot", json={
            "code": initial_code,
            "filename": filename,
            "policy": "original_protocol.json",
            "violations": init_comp.get("violations", []),
            "hints": init_comp.get("hints", []),
            "rawOutput": init_comp.get("rawOutput", "")
        })
        assert copilot_res.status_code == 200, f"Advisory Copilot failed: {copilot_res.data}"
        copilot_data = copilot_res.json
        assert copilot_data.get("ok") is True, f"Copilot ok is not True: {copilot_data}"
        
        full_code = copilot_data.get("full_code")
        assert full_code, f"full_code missing from Copilot response for {filename}!"
        print(f"[3] Advisory Copilot generated full_code ({len(full_code)} chars). Verdict: {copilot_data.get('verdict')}")

        # 4. Simulate user clicking 'Replace in Editor' and then 'Run secure-clang'
        remediated_comp_res = client.post("/api/compile", json={
            "code": full_code,
            "filename": filename,
            "policy": "original_protocol.json",
            "energy": False
        })
        rem_comp = remediated_comp_res.json
        rem_ok = rem_comp.get("ok")
        violations = rem_comp.get("violations", [])
        
        print(f"[4] Remediated secure-clang compile ok: {rem_ok} (Violations: {len(violations)})")
        if not rem_ok or len(violations) > 0:
            print(f"    ERROR: Remediated code failed secure-clang!")
            print(f"    Message: {rem_comp.get('message')}")
            print(f"    Violations: {violations}")
            print(f"    Raw Output:\n{rem_comp.get('rawOutput')}")
            all_ok = False
        else:
            print(f"    SUCCESS: Passed secure-clang with 0 violations!")

    print("\n==================================================================")
    if all_ok:
        print(">>> ALL 6 SCENARIOS PASSED THE FULL PIPELINE SUCCESSFULLY! <<<")
    else:
        print(">>> SOME SCENARIOS FAILED! <<<")
    print("==================================================================")
    return all_ok

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
