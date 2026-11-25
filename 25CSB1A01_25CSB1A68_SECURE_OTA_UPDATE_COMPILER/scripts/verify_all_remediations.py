import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TESTS_DIR = REPO_ROOT / "tests"
root_drive = str(REPO_ROOT)[0].lower()
root_rest = str(REPO_ROOT)[2:].replace("\\", "/")
WSL_REPO = f"/mnt/{root_drive}{root_rest}"

def compile_c(code: str):
    with tempfile.NamedTemporaryFile(suffix=".c", delete=False, mode="w", encoding="utf-8") as f:
        f.write(code)
        temp_path = f.name

    if sys.platform == "win32":
        drive = temp_path[0].lower()
        rest = temp_path[2:].replace("\\", "/")
        wsl_src = f"/mnt/{drive}{rest}"
        wsl_out = f"{wsl_src}.out"
        cmd = ["wsl", "bash", "-c", f"cd {WSL_REPO} && ./secure-clang {wsl_src} -o {wsl_out}"]
    else:
        out_path = f"{temp_path}.out"
        cmd = [str(REPO_ROOT / "secure-clang"), temp_path, "-o", out_path]

    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.returncode == 0, (res.stdout + res.stderr).strip()

sys.path.insert(0, str(REPO_ROOT / "web-demo"))
from advisory_copilot import synthesize_remediated_code


scenarios = [
    ("Secure Baseline", "secure.c"),
    ("Signature Missing", "insecure_rule_signature_missing.c"),
    ("Rollback Violation", "insecure_rule_rollback_missing.c"),
    ("Weak Crypto", "insecure_rule_weak_md5.c"),
    ("Logging Leak", "insecure_rule_logging_puts.c"),
    ("Hardcoded Secret", "insecure_hardcoded_secret.c"),
]

print("==================================================")
print("TESTING REMEDIATION FOR ALL 6 DEMO CASES")
print("==================================================")

all_passed = True
for name, filename in scenarios:
    orig_code = (TESTS_DIR / filename).read_text(encoding="utf-8")
    
    orig_ok, orig_out = compile_c(orig_code)
    expected_orig = (name == "Secure Baseline")
    print(f"\n[{name}] Original compiles ok: {orig_ok} (Expected: {expected_orig})")
    
    _, remediated = synthesize_remediated_code(orig_code)
    rem_ok, rem_out = compile_c(remediated)
    print(f"[{name}] Remediated compiles ok: {rem_ok} (Must be: True)")
    
    if not rem_ok:
        print(f"[{name}] Remediated output/errors:\n{rem_out}")
        all_passed = False

if all_passed:
    print("\n>>> ALL 6 REMEDIATED CASES COMPILED AND PASSED SECURE-CLANG PERFECTLY! <<<")
else:
    print("\n>>> SOME REMEDIATED CASES FAILED! <<<")
