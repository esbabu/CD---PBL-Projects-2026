import os
import sys
import shutil

# Ensure src is in sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from heal_loop import _compile, _pre_scan, _classify_errors, _pick_fix_target, HealWorker
from auto_healer import attempt_fix, attempt_fix_detailed, UNFIXABLE_CATEGORIES
from error_classifier import get_default_classifier

TEST_CPP = "test_semicolon.cpp"

def run_diagnosis():
    print("=" * 60, flush=True)
    print("PHASE 1 DIAGNOSIS: ISOLATED HEALER TEST", flush=True)
    print("=" * 60, flush=True)

    with open(TEST_CPP, "r", encoding="utf-8") as f:
        input_code = f.read()

    print("\n--- EXACT INPUT CODE ---", flush=True)
    print(input_code, flush=True)
    print("------------------------", flush=True)

    # Step 1: Compiler run
    print("\nRunning _compile...", flush=True)
    errors, stderr = _compile(TEST_CPP)
    pre_errors = _pre_scan(input_code)
    all_errors = pre_errors + errors

    print(f"\n[1] Compiler raw stderr:\n{stderr.strip()}", flush=True)
    print(f"\n[2] Parsed errors ({len(errors)}):", flush=True)
    for idx, err in enumerate(errors):
        print(f"    ({idx+1}) line {err.get('line')}, col {err.get('column')}: [{err.get('type')}] {err.get('message')}", flush=True)

    # Step 2: Classifier
    print("\nLoading classifier...", flush=True)
    classifier = get_default_classifier()
    print("Classifying errors...", flush=True)
    _classify_errors(all_errors, classifier)
    print(f"\n[3] Classified errors:", flush=True)
    for idx, err in enumerate(all_errors):
        print(f"    ({idx+1}) category='{err.get('category')}', conf={err.get('confidence')} -> '{err.get('message')}'", flush=True)

    # Step 3: Pick fix target
    print("\nPicking fix target...", flush=True)
    target = _pick_fix_target(all_errors)
    print(f"\n[4] Picked target: {target}", flush=True)

    # Step 4: Call attempt_fix_detailed directly
    print("\nCalling attempt_fix_detailed...", flush=True)
    patch_detailed = attempt_fix_detailed(input_code, target)
    print(f"\n[5] attempt_fix_detailed result:", flush=True)
    if patch_detailed:
        print(f"    Strategy: {patch_detailed.strategy}", flush=True)
        print(f"    Rationale: {patch_detailed.rationale}", flush=True)
        print(f"    Line modified: {patch_detailed.line_no}", flush=True)
        print(f"    Confidence: {patch_detailed.confidence}", flush=True)
    else:
        print("    Returned None!", flush=True)

    # Step 5: Call attempt_fix directly
    print("\nCalling attempt_fix...", flush=True)
    fixed_code = attempt_fix(input_code, target)

    print("\n--- EXACT RETURNED 'FIXED' CODE ---", flush=True)
    if fixed_code is None:
        print("None (no fix generated)", flush=True)
    else:
        print(fixed_code, flush=True)
    print("-----------------------------------", flush=True)

    is_diff = (fixed_code is not None) and (fixed_code != input_code)
    print(f"\n[6] Are input and returned fixed code actually different strings? {is_diff}", flush=True)

    # Step 6: Test HealWorker on a copy to observe HealWorker behavior
    print("\nTesting HealWorker._heal() on a copy...", flush=True)
    copy_path = "test_semicolon_heal_test.cpp"
    shutil.copyfile(TEST_CPP, copy_path)
    try:
        worker = HealWorker(copy_path, classifier)
        
        events = []
        worker.attempt_started.connect(lambda num, err: events.append(("attempt_started", num, err)))
        worker.diff_ready.connect(lambda num, diff: events.append(("diff_ready", num, diff)))
        worker.compile_clean.connect(lambda: events.append(("compile_clean",)))
        worker.give_up.connect(lambda hist: events.append(("give_up", hist)))
        worker.error_signal.connect(lambda msg: events.append(("error_signal", msg)))

        print("Calling worker._heal()...", flush=True)
        telemetry = worker._heal()

        with open(copy_path, "r", encoding="utf-8") as f:
            final_worker_code = f.read()

        print("\n[7] HealWorker._heal() execution events:", flush=True)
        for ev in events:
            ev_name = ev[0]
            if ev_name == "attempt_started":
                print(f"    -> attempt_started: attempt #{ev[1]}, error={ev[2].get('message')}", flush=True)
            elif ev_name == "diff_ready":
                print(f"    -> diff_ready: attempt #{ev[1]}", flush=True)
            elif ev_name == "compile_clean":
                print(f"    -> compile_clean: Clean compile reached!", flush=True)
            elif ev_name == "give_up":
                print(f"    -> give_up: History length {len(ev[1])}, entries: {ev[1]}", flush=True)
            elif ev_name == "error_signal":
                print(f"    -> error_signal: {ev[1]}", flush=True)

        print(f"\n[8] File content after HealWorker._heal():", flush=True)
        print(final_worker_code, flush=True)
        print(f"    Did HealWorker modify file? {final_worker_code != input_code}", flush=True)
    finally:
        if os.path.exists(copy_path):
            os.remove(copy_path)

if __name__ == "__main__":
    run_diagnosis()
