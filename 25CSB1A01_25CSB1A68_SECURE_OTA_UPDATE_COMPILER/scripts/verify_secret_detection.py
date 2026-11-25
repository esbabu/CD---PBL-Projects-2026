import subprocess
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent

print("==================================================")
print("1. RUNNING secure-clang ON tests/secure_no_secrets.c")
print("==================================================")
res_pass = subprocess.run(
    ["./secure-clang", "tests/secure_no_secrets.c", "-o", "secure_no_secrets.out"],
    cwd=repo_root,
    capture_output=True,
    text=True,
)
print(f"STDOUT:\n{res_pass.stdout}")
print(f"STDERR:\n{res_pass.stderr}")
print(f"EXIT CODE: {res_pass.returncode}")

print("\n==================================================")
print("2. RUNNING secure-clang ON tests/insecure_hardcoded_secret.c")
print("==================================================")
res_fail = subprocess.run(
    ["./secure-clang", "tests/insecure_hardcoded_secret.c", "-o", "insecure_hardcoded_secret.out"],
    cwd=repo_root,
    capture_output=True,
    text=True,
)
print(f"STDOUT:\n{res_fail.stdout}")
print(f"STDERR:\n{res_fail.stderr}")
print(f"EXIT CODE: {res_fail.returncode}")

# Cleanup
out1 = repo_root / "secure_no_secrets.out"
out2 = repo_root / "insecure_hardcoded_secret.out"
if out1.exists():
    out1.unlink()
if out2.exists():
    out2.unlink()

print("\n==================================================")
print("3. RUNNING secure-clang ON HIGH-ENTROPY API KEY")
print("==================================================")
tmp_entropy_c = repo_root / "tests" / "test_tmp_entropy.c"
tmp_entropy_c.write_text(
    'const char *api_token = "4a8f9b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0";\n'
    'int main(void) { return 0; }\n',
    encoding="utf-8"
)
res_entropy = subprocess.run(
    ["./secure-clang", str(tmp_entropy_c), "-o", "entropy.out"],
    cwd=repo_root,
    capture_output=True,
    text=True,
)
print(f"STDOUT:\n{res_entropy.stdout}")
print(f"STDERR:\n{res_entropy.stderr}")
print(f"EXIT CODE: {res_entropy.returncode}")
if tmp_entropy_c.exists():
    tmp_entropy_c.unlink()

out3 = repo_root / "entropy.out"
if out3.exists():
    out3.unlink()

if res_pass.returncode == 0 and res_fail.returncode != 0 and res_entropy.returncode != 0:
    print("\nALL VERIFICATIONS (PEM HEADER & HIGH-ENTROPY KEYS) PASSED!")
    sys.exit(0)
else:
    print("\nVERIFICATION FAILED!")
    sys.exit(1)
