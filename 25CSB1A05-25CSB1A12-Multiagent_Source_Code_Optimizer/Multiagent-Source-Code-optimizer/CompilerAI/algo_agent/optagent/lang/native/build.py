"""Native C11/C++17 build manager with content-addressed caching and sanitizer/coverage configs."""
from __future__ import annotations

import hashlib
import shutil
import subprocess
from pathlib import Path
from typing import Any

from ...config import Settings
from ...runtime.sandbox import PKG_ROOT
from ..base import BuildResult
from .clang_facts import analyze_native_source
from .codegen import generate_driver
from .marshal import build_signature

NATIVE_DIR = Path(__file__).resolve().parent
VENDOR_DIR = NATIVE_DIR / "vendor"
RUNTIME_NATIVE_DIR = PKG_ROOT / "optagent" / "runtime" / "native"


def build_cache_key(source: str, entry: str, language: str, flags: list[str], mode: str = "opt") -> str:
    payload = "\0".join([language, entry, mode, " ".join(flags), source])
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def resolve_compile_flags(
    language: str,
    s: Settings,
    hints: dict[str, Any] | None = None,
    mode: str = "opt",
    allow_native_ext: bool = False,
) -> list[str]:
    """Compute identical compiler flags for original and candidate.

    Modes:
    - `opt`: standard `-O2`
    - `O0`: `-O0` (for UB/optimization-sensitivity differential check)
    - `san`: `-O1 -fsanitize=address,undefined -fno-sanitize-recover=all`
    - `sancov`: `-O1 -fsanitize-coverage=inline-8bit-counters`
    - `cov`: `-O0 -fprofile-instr-generate -fcoverage-mapping`
    - `libcxx`: C++ `-stdlib=libc++` (cross-stdlib check)
    """
    hints = hints or {}
    ch = hints.get("compile") or {}
    base = list(s.cpp_flags if language == "cpp" else s.c_flags)
    if ch.get("std"):
        base = [f for f in base if not f.startswith("-std=")]
        base.insert(0, f"-std={ch['std']}")
    if ch.get("flags"):
        base = list(ch["flags"])
    for d in ch.get("defines") or []:
        base.append(f"-D{d}")

    if mode == "O0":
        base = [f for f in base if not f.startswith("-O")] + ["-O0"]
    elif mode == "san":
        base = [f for f in base if not f.startswith("-O")] + [
            "-O1", "-fsanitize=address,undefined", "-fno-sanitize-recover=all",
        ]
    elif mode == "sancov":
        base = [f for f in base if not f.startswith("-O")] + [
            "-O1", "-fsanitize-coverage=inline-8bit-counters",
        ]
    elif mode == "cov":
        base = [f for f in base if not f.startswith("-O")] + [
            "-O0", "-fprofile-instr-generate", "-fcoverage-mapping",
        ]
    elif mode == "libcxx" and language == "cpp":
        base.append("-stdlib=libc++")

    if allow_native_ext:
        base.append("-march=native")
    return base


def prepare_build_dir(
    source: str,
    entry: str,
    language: str,
    hints: dict[str, Any] | None,
    workdir: Path,
) -> tuple[Path, Path]:
    """Generate driver + copy target, harness_common.h, and vendored JSON files into workdir."""
    workdir.mkdir(parents=True, exist_ok=True)
    is_cpp = language == "cpp"
    target_name = "target.cpp" if is_cpp else "target.c"
    driver_name = "driver.cpp" if is_cpp else "driver.c"

    target_path = workdir / target_name
    target_path.write_text(source, encoding="utf-8")

    # Extra header files from hints
    for fname, content in ((hints or {}).get("extra_files") or {}).items():
        ep = workdir / fname
        ep.parent.mkdir(parents=True, exist_ok=True)
        ep.write_text(content, encoding="utf-8")

    shutil.copy(RUNTIME_NATIVE_DIR / "harness_common.h", workdir / "harness_common.h")
    if is_cpp:
        shutil.copy(VENDOR_DIR / "json.hpp", workdir / "json.hpp")
    else:
        shutil.copy(VENDOR_DIR / "cJSON.h", workdir / "cJSON.h")
        shutil.copy(VENDOR_DIR / "cJSON.c", workdir / "cJSON.c")

    mod = analyze_native_source(source, language, hints)
    if entry not in mod.functions:
        raise ValueError(f"Entry function '{entry}' not found in {language} source")
    sig = build_signature(mod.functions[entry], language, hints)
    driver_src = generate_driver(sig, target_filename=target_name, hints=hints)
    driver_path = workdir / driver_name
    driver_path.write_text(driver_src, encoding="utf-8")
    return driver_path, target_path


def compile_native(
    source: str,
    entry: str,
    language: str,
    s: Settings,
    workdir: Path,
    hints: dict[str, Any] | None = None,
    mode: str = "opt",
    docker: bool = False,
    cache_dir: Path | None = None,
) -> BuildResult:
    """Compile the generated native driver with caching, timeout, and output cap."""
    is_cpp = language == "cpp"
    flags = resolve_compile_flags(language, s, hints, mode=mode)
    key = build_cache_key(source, entry, language, flags, mode=mode)
    bin_path = workdir / "driver_bin"

    if cache_dir is not None:
        cache_dir.mkdir(parents=True, exist_ok=True)
        cached = cache_dir / f"{key}.bin"
        if cached.exists():
            shutil.copy(cached, bin_path)
            return BuildResult(ok=True, artifact_path=bin_path, log="cache hit", flags=flags)

    try:
        driver_path, _ = prepare_build_dir(source, entry, language, hints, workdir)
    except Exception as e:
        return BuildResult(ok=False, log=f"Driver generation failed: {e}", flags=flags)

    compiler = ("clang++" if shutil.which("clang++") else "g++") if is_cpp else ("clang" if shutil.which("clang") else "gcc")
    if docker:
        compiler = "clang++" if is_cpp else "clang"

    sources = [str(driver_path)]
    if not is_cpp:
        sources.append(str(workdir / "cJSON.c"))

    link_flags = ["-lm"] + [f"-l{lib}" for lib in ((hints or {}).get("compile") or {}).get("link") or []]
    cmd = [compiler] + flags + ["-I", str(workdir)] + sources + ["-o", str(bin_path)] + link_flags

    if docker:
        d_sources = ["/work/driver.cpp"] if is_cpp else ["/work/driver.c", "/work/cJSON.c"]
        dcmd = [
            "docker", "run", "--rm", "--network", "none",
            "--memory", s.docker_mem, "--memory-swap", s.docker_mem,
            "--cpus", s.docker_cpus, "--pids-limit", "128", "--read-only",
            "--tmpfs", "/tmp:rw,size=256m", "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges",
            "-v", f"{workdir}:/work:rw", "-w", "/tmp",
            s.native_docker_image,
            compiler, *flags, "-I", "/work", *d_sources, "-o", "/work/driver_bin", *link_flags,
        ]
        cmd = dcmd

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=s.compile_timeout_s)
        log = (proc.stdout + "\n" + proc.stderr).strip()[:16000]
        if proc.returncode != 0:
            return BuildResult(ok=False, log=log or f"Compiler exited with code {proc.returncode}", flags=flags)
        if cache_dir is not None and bin_path.exists():
            shutil.copy(bin_path, cache_dir / f"{key}.bin")
        return BuildResult(ok=True, artifact_path=bin_path, log=log, flags=flags)
    except subprocess.TimeoutExpired:
        return BuildResult(ok=False, log=f"Compilation timed out after {s.compile_timeout_s}s", flags=flags)
    except FileNotFoundError as e:
        return BuildResult(ok=False, log=f"Compiler not found ({compiler}): {e}", flags=flags)
