from __future__ import annotations
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

from ..config import Settings
from ..oracle.schemas import CaseResult

HARNESS = Path(__file__).with_name("batch_harness.py")
PKG_ROOT = Path(__file__).resolve().parents[2]        # directory containing optagent/


class SandboxError(RuntimeError):
    pass


@dataclass
class SandboxProfile:
    """Language-specific execution profile for Sandbox (default = Python)."""
    target_name: str = "target.py"
    image: str | None = None
    build_cmd: Callable[[Path, Path, bool], list[str]] | None = None
    run_cmd: Callable[[Path, Path, bool], list[str]] | None = None
    env: Callable[[int], dict[str, str]] | None = None
    needs_build: bool = False
    isolation_required: bool = False
    language: str = "python"
    extra_files: dict[str, str] = field(default_factory=dict)
    build_hook: Callable[[Path, Path, str, "Settings", bool], tuple[bool, str]] | None = None


def _python_env(perturb_idx: int) -> dict[str, str]:
    return {"PYTHONHASHSEED": str(perturb_idx), "PYTHONDONTWRITEBYTECODE": "1"}


PYTHON_PROFILE = SandboxProfile(
    target_name="target.py",
    image=None,
    build_cmd=None,
    run_cmd=None,
    env=_python_env,
    needs_build=False,
    isolation_required=False,
    language="python",
)


@dataclass
class RunOpts:
    hashseed: int = 0
    cov: bool = False
    props_path: str | None = None
    timeout: float | None = None
    digest: str = "off"            # off | exact | multiset (scaling runs: no big payloads)


@lru_cache(maxsize=4)
def docker_ok(image: str) -> bool:
    try:
        if subprocess.run(["docker", "info"], capture_output=True, timeout=10).returncode != 0:
            return False
        return subprocess.run(["docker", "image", "inspect", image],
                              capture_output=True, timeout=10).returncode == 0
    except Exception:
        return False


def _limiter(mem_mb: int, cpu_s: int):
    def f():
        try:
            import resource
            resource.setrlimit(resource.RLIMIT_CPU, (cpu_s, cpu_s))
            resource.setrlimit(resource.RLIMIT_AS, (mem_mb << 20, mem_mb << 20))
        except Exception:
            pass
    return f


class Sandbox:
    def __init__(self, s: Settings, backend: str | None = None,
                 profile: SandboxProfile | None = None):
        self.profile = profile or PYTHON_PROFILE
        img = self.profile.image or s.docker_image
        b = backend or s.sandbox_backend
        if b == "auto":
            b = "docker" if docker_ok(img) else "local"
        elif b == "docker" and not docker_ok(img):
            raise SandboxError(f"docker backend requested but Docker/image '{img}' is unavailable "
                               f"(run: docker pull {img})")
        if b == "local" and self.profile.isolation_required:
            allow_local = getattr(s, "allow_local_native", False) or os.getenv("OPT_ALLOW_LOCAL_NATIVE") == "1"
            if not allow_local:
                raise SandboxError(
                    f"Docker isolation is required for {self.profile.language} code. "
                    f"Install Docker and build '{img}', or set OPT_ALLOW_LOCAL_NATIVE=1 to override."
                )
        self.s, self.backend, self._image = s, b, img

    @property
    def is_isolated(self) -> bool:
        return self.backend == "docker"

    # ---------- public: chunked + parallel ----------
    def run(self, src_path, entry: str, cases, opts: RunOpts | None = None) -> list[CaseResult]:
        opts = opts or RunOpts()
        bs = self.s.batch_size
        chunks = [(i, cases[i:i + bs]) for i in range(0, len(cases), bs)]

        def work(item):
            off, chunk = item
            rs = self.run_batch(src_path, entry, chunk, opts)
            for r in rs:
                r.idx += off
            return off, rs

        if len(chunks) <= 1 or self.s.workers <= 1:
            outs = [work(c) for c in chunks]
        else:
            with ThreadPoolExecutor(self.s.workers) as ex:
                outs = list(ex.map(work, chunks))
        results: list = [None] * len(cases)
        for off, rs in outs:
            results[off:off + len(rs)] = rs
        return results

    # ---------- one container/process, with crash + timeout recovery ----------
    def run_batch(self, src_path, entry: str, cases, opts: RunOpts | None = None) -> list[CaseResult]:
        opts = opts or RunOpts()
        n = len(cases)
        if n == 0:
            return []
        timeout = opts.timeout or self.s.case_timeout_s
        docker = self.backend == "docker"
        results: list[CaseResult | None] = [None] * n
        with tempfile.TemporaryDirectory(prefix="optagent_") as td:
            root = Path(td)
            work, out = root / "work", root / "out"
            work.mkdir()
            out.mkdir()
            shutil.copy(src_path, work / self.profile.target_name)
            for fname, fcontent in (self.profile.extra_files or {}).items():
                ep = work / fname
                ep.parent.mkdir(parents=True, exist_ok=True)
                ep.write_text(fcontent, encoding="utf-8")
            if opts.props_path:
                shutil.copy(opts.props_path, work / "props.py")
            with open(work / "cases.jsonl", "w", encoding="utf-8") as f:
                for c in cases:
                    f.write(json.dumps({"args": c.args, "kwargs": c.kwargs}) + "\n")
            if self.profile.needs_build:
                ok_build, build_log = self._build(work, out, entry, docker)
                if not ok_build:
                    msg = build_log[:4000] if build_log else "Build failed"
                    return [
                        CaseResult(idx=i, status="load_error", exc_type="BuildError",
                                   exc_msg=msg, build_log=build_log)
                        for i in range(n)
                    ]
            base = "/work/" if docker else str(work) + os.sep
            start = 0
            while start < n:
                cfg = {"entry": entry, "timeout": timeout, "cov": opts.cov, "digest": opts.digest,
                       "rand_seed": self.s.rand_seed, "start": start,
                       "perturb_idx": opts.hashseed,
                       "props_path": (base + "props.py") if opts.props_path else None}
                (work / "cfg.json").write_text(json.dumps(cfg))
                out_file = out / "out.jsonl"
                out_file.write_text("")
                proc, name = self._spawn(work, out, opts.hashseed, n, timeout)
                try:
                    _, stalled = self._watch(proc, out_file, results, timeout, name)
                finally:
                    try:
                        proc.wait(timeout=5)
                    except Exception:
                        self._kill(proc, name)
                bad = next((i for i in range(start, n) if results[i] is None), None)
                if bad is None:
                    break
                if results[0] is not None and results[0].status == "load_error":
                    for i in range(n):                    # broken code: no point retrying every case
                        if results[i] is None:
                            results[i] = results[0].model_copy(update={"idx": i})
                    break
                err = ""
                ef = out / "stderr.txt"
                if ef.exists():
                    err = ef.read_text(errors="replace")[-300:]
                results[bad] = CaseResult(idx=bad, status="timeout" if stalled else "crash", exc_msg=err)
                start = bad + 1
        return results  # type: ignore[return-value]

    # ---------- internals ----------
    def _build(self, work: Path, out: Path, entry: str, docker: bool) -> tuple[bool, str]:
        """Run optional pre-execution build step (for compiled languages or JS bundling)."""
        if self.profile.build_hook is not None:
            return self.profile.build_hook(work, out, entry, self.s, docker)
        if self.profile.build_cmd is None:
            return True, ""
        cmd = self.profile.build_cmd(work, out, docker)
        timeout = getattr(self.s, "compile_timeout_s", 30.0)
        if docker:
            name = f"optagent-build-{uuid.uuid4().hex[:12]}"
            dcmd = ["docker", "run", "--rm", "--name", name, "--network", "none",
                    "--memory", self.s.docker_mem, "--memory-swap", self.s.docker_mem,
                    "--cpus", self.s.docker_cpus, "--pids-limit", "128", "--read-only",
                    "--tmpfs", "/tmp:rw,size=256m", "--cap-drop", "ALL",
                    "--security-opt", "no-new-privileges",
                    "-v", f"{work}:/work:ro", "-v", f"{out}:/out:rw",
                    "-v", f"{PKG_ROOT}:/opt/optagent:ro", "-w", "/tmp",
                    self._image] + cmd
            try:
                proc = subprocess.run(dcmd, capture_output=True, text=True, timeout=timeout)
                log = (proc.stdout + "\n" + proc.stderr).strip()[:16000]
                return proc.returncode == 0, log
            except subprocess.TimeoutExpired:
                subprocess.run(["docker", "kill", name], capture_output=True, timeout=10)
                return False, f"Build timed out after {timeout}s"
        try:
            proc = subprocess.run(cmd, cwd=out, capture_output=True, text=True, timeout=timeout)
            log = (proc.stdout + "\n" + proc.stderr).strip()[:16000]
            return proc.returncode == 0, log
        except subprocess.TimeoutExpired:
            return False, f"Build timed out after {timeout}s"
        except FileNotFoundError as e:
            return False, f"Build tool not found: {e}"

    def _spawn(self, work: Path, out: Path, hashseed: int, n: int, timeout: float):
        errf = open(out / "stderr.txt", "wb")
        profile_env = self.profile.env(hashseed) if self.profile.env else _python_env(hashseed)
        if self.backend == "docker":
            name = f"optagent-{uuid.uuid4().hex[:12]}"
            cmd = ["docker", "run", "--rm", "--name", name, "--network", "none",
                   "--memory", self.s.docker_mem, "--memory-swap", self.s.docker_mem,
                   "--cpus", self.s.docker_cpus, "--pids-limit", "128", "--read-only",
                   "--tmpfs", "/tmp:rw,size=128m", "--cap-drop", "ALL",
                   "--security-opt", "no-new-privileges"]
            for ek, ev in profile_env.items():
                cmd += ["-e", f"{ek}={ev}"]
            cmd += ["-v", f"{work}:/work:ro", "-v", f"{out}:/out:rw",
                    "-v", f"{PKG_ROOT}:/opt/optagent:ro", "-w", "/tmp"]
            if os.name == "posix":
                cmd += ["--user", f"{os.getuid()}:{os.getgid()}"]
            if self.profile.run_cmd is not None:
                run_args = self.profile.run_cmd(work, out, True)
            else:
                run_args = ["python", "/opt/optagent/optagent/runtime/batch_harness.py",
                            "/opt/optagent", f"/work/{self.profile.target_name}",
                            "/work/cases.jsonl", "/out/out.jsonl", "/work/cfg.json"]
            cmd += [self._image] + run_args
            return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=errf), name
        env = {"PATH": os.environ.get("PATH", "")}
        env.update(profile_env)
        for k in ("SYSTEMROOT", "TEMP", "TMP", "HOME", "VIRTUAL_ENV", "LD_LIBRARY_PATH"):
            if k in os.environ:
                env[k] = os.environ[k]
        if self.profile.run_cmd is not None:
            cmd = self.profile.run_cmd(work, out, False)
        else:
            cmd = [sys.executable, str(HARNESS), str(PKG_ROOT), str(work / self.profile.target_name),
                   str(work / "cases.jsonl"), str(out / "out.jsonl"), str(work / "cfg.json")]
        kw = {}
        if os.name == "posix":
            kw = dict(start_new_session=True,
                      preexec_fn=_limiter(self.s.exec_mem_mb, int(timeout * n + 120)))
        return subprocess.Popen(cmd, cwd=out, env=env, stdout=subprocess.DEVNULL, stderr=errf, **kw), None

    def _watch(self, proc, out_file: Path, results, timeout: float, name):
        """Tail the result file. Kill if no progress within the stall limit."""
        pos, buf, seen, finished = 0, b"", 0, False
        last = time.time()
        grace = 25.0 if self.backend == "docker" else 8.0
        while True:
            rc = proc.poll()
            try:
                with open(out_file, "rb") as f:
                    f.seek(pos)
                    chunk = f.read()
            except FileNotFoundError:
                chunk = b""
            if chunk:
                pos += len(chunk)
                buf += chunk
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    if not line:
                        continue
                    try:
                        d = json.loads(line.decode("utf-8", "replace"))
                    except Exception:
                        continue
                    if d.get("done"):
                        finished = True
                    elif "idx" in d:
                        results[d["idx"]] = CaseResult(**d)
                        seen += 1
                        last = time.time()
            if finished:
                return True, False
            if rc is not None and not chunk:
                return False, False
            if time.time() - last > (timeout + 3.0 if seen else grace + timeout):
                self._kill(proc, name)
                return False, True
            time.sleep(0.02)

    def _kill(self, proc, name):
        try:
            if self.backend == "docker" and name:
                subprocess.run(["docker", "kill", name], capture_output=True, timeout=10)
            elif os.name == "posix":
                os.killpg(proc.pid, signal.SIGKILL)
        except Exception:
            pass
        try:
            proc.kill()
        except Exception:
            pass