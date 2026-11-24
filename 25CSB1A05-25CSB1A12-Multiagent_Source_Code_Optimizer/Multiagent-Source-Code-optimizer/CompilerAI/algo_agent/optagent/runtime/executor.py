from __future__ import annotations
import json
import os
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

from ..config import Settings
from ..schemas import ExecRecord

HARNESS = Path(__file__).with_name("harness.py")
PKG_ROOT = Path(__file__).resolve().parents[2]        # directory that contains optagent/


def _limiter(mem_mb: int, cpu_s: int):
    def f():
        try:
            import resource
            resource.setrlimit(resource.RLIMIT_CPU, (cpu_s, cpu_s))
            resource.setrlimit(resource.RLIMIT_AS, (mem_mb << 20, mem_mb << 20))
        except Exception:
            pass
    return f


class Executor:
    """Step-1 sandbox: separate process, wall/CPU/memory limits, scrubbed env.
    NOT a security boundary (no network/FS isolation). Step 2 swaps in Docker."""

    def __init__(self, s: Settings):
        self.s = s

    def _once(self, src_path, entry, args, kwargs, hashseed: int) -> dict:
        with tempfile.TemporaryDirectory() as td:
            payload, out = Path(td) / "in.json", Path(td) / "out.json"
            payload.write_text(json.dumps({"entry": entry, "args": args, "kwargs": kwargs}))
            env = {"PATH": os.environ.get("PATH", ""), "PYTHONHASHSEED": str(hashseed),
                   "PYTHONDONTWRITEBYTECODE": "1"}
            for k in ("SYSTEMROOT", "TEMP", "TMP", "HOME", "VIRTUAL_ENV", "LD_LIBRARY_PATH"):
                if k in os.environ:
                    env[k] = os.environ[k]
            cmd = [sys.executable, str(HARNESS), str(PKG_ROOT), str(Path(src_path).resolve()), str(payload), str(out)]
            kw = {}
            if os.name == "posix":
                kw = dict(start_new_session=True,
                          preexec_fn=_limiter(self.s.exec_mem_mb, int(self.s.exec_timeout_s) + 2))
            p = subprocess.Popen(cmd, cwd=td, env=env, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, text=True, **kw)
            try:
                _, err = p.communicate(timeout=self.s.exec_timeout_s)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(p.pid, signal.SIGKILL) if os.name == "posix" else p.kill()
                except Exception:
                    p.kill()
                p.communicate()
                return {"status": "timeout"}
            if not out.exists():
                return {"status": "crash", "exc_msg": (err or "")[-500:]}
            return json.loads(out.read_text())

    def run_case(self, src_path, entry, args, kwargs, origin: str) -> ExecRecord:
        a = self._once(src_path, entry, args, kwargs, hashseed=0)
        diff: list[str] = []
        if a["status"] in ("ok", "exception"):
            b = self._once(src_path, entry, args, kwargs, hashseed=1)
            diff = [k for k in ("status", "return", "exc_type", "stdout") if a.get(k) != b.get(k)]
        return ExecRecord(
            origin=origin, args=args, kwargs=kwargs, status=a["status"], ret=a.get("return"),
            return_type=a.get("return_type"), exc_type=a.get("exc_type"), exc_msg=a.get("exc_msg"),
            stdout=a.get("stdout", ""), mutated_args=a.get("mutated_args", []),
            globals_changed=a.get("globals_changed", []),
            returns_input_alias=a.get("returns_input_alias", []),
            elapsed_s=a.get("elapsed_s"), generator=a.get("generator", False),
            nondeterministic_fields=diff)