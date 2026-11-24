import sys, time
sys.path.insert(0, ".")

from src.error_capture import ErrorCapture, _ISOLATED_RUNNER

print("=== Isolated runner starts with: ===")
print("\n".join(_ISOLATED_RUNNER.strip().splitlines()[:8]))
print("=== (verify: no unguarded 'import resource') ===\n")

e = ErrorCapture()

print("TEST 1: infinite loop")
t0 = time.time()
res = e._run_isolated_python("while True: pass", timeout=3.0)
elapsed = time.time() - t0
print(f"  elapsed: {elapsed:.2f}s")
print(f"  result: {res}")
assert elapsed < 5.0, f"TIMEOUT DID NOT FIRE (elapsed {elapsed:.2f}s)"
assert res["error_type"] == "TimeoutError", f"Expected TimeoutError, got {res.get('error_type')}"
print("  PASS\n")

print("TEST 2: ZeroDivisionError")
res = e._run_isolated_python("x = 1/0")
print(f"  result: {res}")
assert res["error_type"] == "ZeroDivisionError", f"Got {res.get('error_type')}"
print("  PASS\n")

print("TEST 3: SyntaxError")
res = e._run_isolated_python("def f(:\n  pass")
print(f"  result: {res}")
assert res["error_type"] == "SyntaxError", f"Got {res.get('error_type')}"
print("  PASS\n")

print("TEST 4: successful run")
res = e._run_isolated_python("print(1+1)")
print(f"  result: {res}")
assert res["ok"] is True, f"Got ok={res.get('ok')}"
assert "2" in res["stdout"], f"Expected '2' in stdout, got {res['stdout']!r}"
print("  PASS\n")

print("ALL TESTS PASSED")