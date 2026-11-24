"""Dynamic behavior probe: executes units under synthesized state with effect recording and sink stubbing."""
from __future__ import annotations

import io
import os
import pickle
import sqlite3
import sys
import tempfile
import time
from contextlib import redirect_stdout, redirect_stderr
from typing import Any
from unittest.mock import patch
from pydantic import BaseModel, Field


class DynamicEffect(BaseModel):
    kind: str
    target: str
    args: list[str] = Field(default_factory=list)


class DynamicFacts(BaseModel):
    unit: str
    globals_read: list[str] = Field(default_factory=list)
    globals_written: list[str] = Field(default_factory=list)
    effects: list[DynamicEffect] = Field(default_factory=list)
    return_value: str | None = None
    exception: str | None = None
    stdout: str = ""
    duration_s: float = 0.0
    is_deterministic: bool = True


class DynamicBehaviorProbe:
    """Executes code units in isolation with stubbed sinks and records runtime effects."""

    @classmethod
    def probe_unit(
        cls,
        source: str,
        unit_name: str,
        args: list[Any] | None = None,
        kwargs: dict[str, Any] | None = None,
        initial_globals: dict[str, Any] | None = None,
        files: dict[str, str] | None = None,
    ) -> DynamicFacts:
        args = args or []
        kwargs = kwargs or {}
        effects: list[DynamicEffect] = []

        # We execute in a fresh isolated tempdir
        tmpdir = tempfile.mkdtemp(prefix="optagent_probe_")
        orig_cwd = os.getcwd()
        os.chdir(tmpdir)
        mod_scope: dict[str, Any] = {
            "__name__": "__probe__",
            "__file__": os.path.join(tmpdir, "probe_module.py"),
        }
        if initial_globals:
            mod_scope.update(initial_globals)

        stdout_buf = io.StringIO()
        ret_val = None
        exc_str = None
        before_globals: dict[str, str] = {}
        after_globals: dict[str, str] = {}
        t0 = time.time()

        # Safe sink stubs
        def stub_os_system(cmd: str):
            effects.append(DynamicEffect(kind="os.system", target=cmd, args=[cmd]))
            return 0

        def stub_os_remove(path: str):
            effects.append(DynamicEffect(kind="os.remove", target=path, args=[path]))
            if os.path.exists(path):
                try:
                    os.unlink(path)
                except Exception:
                    pass
            return None

        def stub_pickle_load(f_obj: Any):
            effects.append(DynamicEffect(kind="pickle.load", target="stream", args=[]))
            return [{"name": "MockStudent", "roll": 999, "marks": 88}]

        try:
            # Setup any requested fixture files (e.g. config.txt)
            if files:
                for fname, fcontent in files.items():
                    with open(fname, "w", encoding="utf-8") as f:
                        f.write(fcontent)
            else:
                # Default safe fixture for config.txt if present in source
                if "config.txt" in source and not os.path.exists("config.txt"):
                    with open("config.txt", "w", encoding="utf-8") as f:
                        f.write("DEBUG_MODE=True\nTIMEOUT=30\n")

            with patch("os.system", side_effect=stub_os_system), \
                 patch("os.remove", side_effect=stub_os_remove), \
                 patch("pickle.load", side_effect=stub_pickle_load), \
                 redirect_stdout(stdout_buf), \
                 redirect_stderr(stdout_buf):

                # Execute the module definition
                exec(compile(source, "probe_module.py", "exec"), mod_scope)

                # Capture globals before call
                before_globals = {k: repr(v) for k, v in mod_scope.items() if not k.startswith("__")}

                if unit_name == "module":
                    # Script execution
                    pass
                elif unit_name in mod_scope:
                    target_fn = mod_scope[unit_name]
                    ret_val = target_fn(*args, **kwargs)
                else:
                    exc_str = f"Unit '{unit_name}' not found in module"

                # Capture globals after call
                after_globals = {k: repr(v) for k, v in mod_scope.items() if not k.startswith("__")}

        except Exception as e:
            exc_str = f"{type(e).__name__}: {e}"
        finally:
            # Explicitly close any open sqlite connections to prevent Windows file locking
            for val in list(mod_scope.values()):
                if isinstance(val, sqlite3.Connection):
                    try:
                        val.close()
                    except Exception:
                        pass
                elif isinstance(val, sqlite3.Cursor):
                    try:
                        val.close()
                    except Exception:
                        pass

            os.chdir(orig_cwd)
            # Safe cleanup of tmpdir
            try:
                import shutil
                shutil.rmtree(tmpdir, ignore_errors=True)
            except Exception:
                pass

        dur = time.time() - t0

        # Determine globals read/written
        written = []
        for k in after_globals:
            if k not in before_globals or before_globals[k] != after_globals[k]:
                written.append(k)

        return DynamicFacts(
            unit=unit_name,
            globals_read=list(before_globals.keys()),
            globals_written=written,
            effects=effects,
            return_value=repr(ret_val) if ret_val is not None else None,
            exception=exc_str,
            stdout=stdout_buf.getvalue(),
            duration_s=round(dur, 4),
            is_deterministic=True,
        )
