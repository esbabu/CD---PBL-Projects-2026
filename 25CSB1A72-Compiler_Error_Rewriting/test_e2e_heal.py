__test__ = False

# -*- coding: utf-8 -*-
"""
End-to-end smoke test for the new HealingAgent.
Tests: missing semicolon, missing include, missing brace.
Does NOT use QThread - runs purely in Python.
"""
import sys, os, shutil, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from heal_agent import HealingAgent, make_compiler, VERDICT_FIXED_AND_VERIFIED, VERDICT_COMPILES_UNVERIFIED, VERDICT_ALREADY_CLEAN
from heal_loop import _pre_scan
from error_classifier import get_default_classifier

classifier = get_default_classifier()

def classify_fn(msg):
    return classifier.predict(msg)

CASES = [
    ("missing_semicolon", """\
#include <iostream>
using namespace std;
int main() {
    int x = 5
    cout << x << endl;
    return 0;
}
"""),
    ("missing_include", """\
int main() {
    cout << "hello" << endl;
    return 0;
}
"""),
    ("missing_brace", """\
#include <iostream>
using namespace std;
int main() {
    int x = 5;
    cout << x << endl;
    return 0;

"""),
    ("already_clean", """\
#include <iostream>
using namespace std;
int main() {
    int x = 5;
    std::cout << x << std::endl;
    return 0;
}
"""),
]


def run_case(name, source):
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")
    work_dir = tempfile.mkdtemp(prefix="heal_test_")
    try:
        compile_fn = make_compiler(working_dir=work_dir)
        agent = HealingAgent(
            source,
            compile_fn=compile_fn,
            pre_scan=_pre_scan,
            max_attempts=4,
            classify_fn=classify_fn,
        )

        attempt_log = []

        def on_attempt(attempt):
            attempt_log.append(attempt)
            print(f"  Attempt {attempt.number}: {attempt.strategy}")
            print(f"    Observed : {attempt.observed}")
            print(f"    Action   : {attempt.action}")
            print(f"    Outcome  : {attempt.outcome}")
            print(f"    Changed  : {attempt.changed}")
            # Show the actual diff
            diff_lines = [l for l in attempt.diff.splitlines() if l.startswith(('+', '-')) and not l.startswith(('+++', '---'))]
            for dl in diff_lines:
                print(f"    DIFF     : {dl}")

        result = agent.run(on_attempt=on_attempt)

        print(f"\nVERDICT: {result.verdict_label}")
        print(f"Changed: {result.changed}")
        if result.changed:
            print(f"Fixed lines: {result.lines_fixed}")
            diff = result.diff()
            for dl in diff.splitlines():
                if dl.startswith(('+', '-')) and not dl.startswith(('+++', '---')):
                    print(f"  {dl}")
        if result.manual_fix:
            print(f"Manual fix hint: {result.manual_fix[:120]}")

        # Assertions
        if name == "already_clean":
            assert result.verdict == VERDICT_ALREADY_CLEAN, f"Expected already_clean, got {result.verdict}"
            assert not result.changed
            print("  [PASS] already clean")
        else:
            assert result.verdict in (VERDICT_FIXED_AND_VERIFIED, VERDICT_COMPILES_UNVERIFIED), \
                f"Expected fixed verdict, got {result.verdict}"
            assert result.changed, "Source was not changed"
            assert result.source != source, "Healed source is identical to original!"
            print("  [PASS] source changed and compiles")

    except AssertionError as e:
        print(f"  [FAIL] {e}")
    except Exception as e:
        import traceback
        print(f"  [ERROR] {e}")
        traceback.print_exc()
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


if __name__ == "__main__":
    print("Running end-to-end healing tests...")
    for name, source in CASES:
        run_case(name, source)
    print("\n\nAll tests finished.")
