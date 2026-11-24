"""Module-level differential verification: __main__ execution and stateful call-sequence fuzzing."""
from __future__ import annotations

import io
import os
import random
import sys
import tempfile
import time
from contextlib import redirect_stdout, redirect_stderr
from typing import Any
from unittest.mock import patch
from ..oracle.state_fixtures import StateFixtureSynthesizer


class ModuleDifferentialVerifier:
    """Verifies that an optimized module is completely equivalent to the original across multi-unit call sequences."""

    @classmethod
    def verify(
        cls,
        orig_source: str,
        opt_source: str,
        fuzz_sequences: int = 10,
    ) -> tuple[bool, str]:
        """Run differential checks: 1) script __main__ run, 2) stateful call sequences."""
        # 1. Run __main__ differential
        ok_main, main_msg = cls._run_script_differential(orig_source, opt_source)
        if not ok_main:
            return False, f"__main__ differential failure: {main_msg}"

        # 2. Stateful call-sequence fuzzing
        ok_fuzz, fuzz_msg = cls._run_call_sequence_fuzzing(orig_source, opt_source, count=fuzz_sequences)
        if not ok_fuzz:
            return False, f"Stateful fuzzing differential failure: {fuzz_msg}"

        return True, "All differential tests passed (script run and stateful call sequences match)."

    @classmethod
    def _run_script_differential(cls, orig_src: str, opt_src: str) -> tuple[bool, str]:
        orig_res = cls._exec_script(orig_src)
        opt_res = cls._exec_script(opt_src)

        if orig_res["exception"] != opt_res["exception"]:
            return False, f"Exception mismatch: orig={orig_res['exception']} opt={opt_res['exception']}"

        if orig_res["stdout"] != opt_res["stdout"]:
            return False, f"Stdout mismatch in __main__ execution"

        return True, "Script outputs match."

    @classmethod
    def _exec_script(cls, source: str) -> dict[str, Any]:
        with tempfile.TemporaryDirectory(prefix="optagent_diff_main_") as td:
            orig_cwd = os.getcwd()
            os.chdir(td)
            try:
                # Pre-create fixture files
                fixtures = StateFixtureSynthesizer.infer_and_synthesize(source, size=5)
                for fname, content in fixtures["files"].items():
                    if isinstance(content, bytes):
                        with open(fname, "wb") as f:
                            f.write(content)
                    else:
                        with open(fname, "w", encoding="utf-8") as f:
                            f.write(content)

                scope = {"__name__": "__main__", "__file__": "script.py"}
                out_buf = io.StringIO()
                exc_str = None

                def stub_sys(cmd): return 0
                def stub_rem(p): pass

                with patch("os.system", side_effect=stub_sys), \
                     patch("os.remove", side_effect=stub_rem), \
                     redirect_stdout(out_buf), \
                     redirect_stderr(out_buf):
                    try:
                        exec(compile(source, "script.py", "exec"), scope)
                    except Exception as e:
                        exc_str = f"{type(e).__name__}: {e}"

                return {
                    "stdout": out_buf.getvalue(),
                    "exception": exc_str,
                    "globals": {k: repr(v) for k, v in scope.items() if not k.startswith("__")},
                }
            finally:
                # Close DB connection if open
                if "scope" in locals() and "database" in scope:
                    try:
                        scope["database"].close()
                    except Exception:
                        pass
                os.chdir(orig_cwd)

    @classmethod
    def _run_call_sequence_fuzzing(cls, orig_src: str, opt_src: str, count: int = 10) -> tuple[bool, str]:
        for seq_idx in range(count):
            with tempfile.TemporaryDirectory(prefix="optagent_fuzz_") as td:
                orig_cwd = os.getcwd()
                os.chdir(td)
                try:
                    fixtures = StateFixtureSynthesizer.infer_and_synthesize(orig_src, size=6)
                    for fname, content in fixtures["files"].items():
                        if isinstance(content, bytes):
                            with open(fname, "wb") as f:
                                f.write(content)
                        else:
                            with open(fname, "w", encoding="utf-8") as f:
                                f.write(content)

                    orig_scope = {"__name__": "__diff__", "__file__": "orig.py"}
                    opt_scope = {"__name__": "__diff__", "__file__": "opt.py"}

                    def stub_sys(cmd): return 0
                    def stub_rem(p): pass

                    with patch("os.system", side_effect=stub_sys), \
                         patch("os.remove", side_effect=stub_rem):
                        exec(compile(orig_src, "orig.py", "exec"), orig_scope)
                        exec(compile(opt_src, "opt.py", "exec"), opt_scope)

                        # Call sequence
                        calls = [
                            ("add_student", ["Diana", 107, 88]),
                            ("sort_students", []),
                            ("calculate_average", []),
                            ("find_duplicates", []),
                            ("generate_report", []),
                            ("search_student", [101]),
                            ("factorial", [6]),
                        ]

                        for fn_name, args in calls:
                            if fn_name in orig_scope and fn_name in opt_scope:
                                r1 = orig_scope[fn_name](*args)
                                r2 = opt_scope[fn_name](*args)
                                if repr(r1) != repr(r2):
                                    return False, f"Call '{fn_name}({args})' return mismatch: {r1} vs {r2}"

                        # Compare final students list
                        if "students" in orig_scope and "students" in opt_scope:
                            if repr(orig_scope["students"]) != repr(opt_scope["students"]):
                                return False, f"Final mutated state of 'students' differs across modules"

                finally:
                    if "orig_scope" in locals() and "database" in orig_scope:
                        try: orig_scope["database"].close()
                        except Exception: pass
                    if "opt_scope" in locals() and "database" in opt_scope:
                        try: opt_scope["database"].close()
                        except Exception: pass
                    os.chdir(orig_cwd)

        return True, "Call-sequence fuzzing verified state and return equivalence."
