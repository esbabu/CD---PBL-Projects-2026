"""Language-neutral harness conformance suite (`tests/conformance/`).

Tests each language's Sandbox harness directly against `spec.json` to isolate
protocol bugs (ret, exc_type, mut, stdout, timeout, crash, special values).
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path
import pytest

from optagent.config import Settings
from optagent.lang.registry import get_adapter
from optagent.oracle.schemas import Case
from optagent.runtime.sandbox import RunOpts, Sandbox

CONF_DIR = Path(__file__).resolve().parent
SPEC = json.loads((CONF_DIR / "spec.json").read_text(encoding="utf-8"))

HAS_NODE = bool(shutil.which("node")) or (Path.home() / ".nodejs" / "node-v20.18.0-win-x64" / "node.exe").exists()
HAS_GCC = bool(shutil.which("gcc") or shutil.which("clang"))
HAS_GXX = bool(shutil.which("g++") or shutil.which("clang++"))


def _run_behavior(lang: str, src_path: Path, name: str, args: list, timeout: float = 1.5):
    s = Settings(sandbox_backend="local", case_timeout_s=timeout, allow_local_native=True)
    ad = get_adapter(lang)
    sb = Sandbox(s, profile=ad.sandbox_profile({}))
    res = sb.run(src_path, name, [Case.make(args, {}, origin="conformance")], RunOpts(hashseed=0, timeout=timeout))[0]
    return ad.normalize_result(res)


@pytest.mark.parametrize("beh", SPEC["behaviors"], ids=[b["name"] for b in SPEC["behaviors"]])
def test_python_harness_conformance(beh):
    r = _run_behavior("python", CONF_DIR / "impl.py", beh["name"], beh["args"])
    assert r.status == beh["expected_status"], f"{beh['name']}: got {r}"
    if "expected_ret" in beh:
        assert r.ret == beh["expected_ret"]
    if beh.get("expect_mutation"):
        assert r.mut, f"Expected argument mutation to be recorded: {r}"
    if "expected_stdout_contains" in beh:
        assert beh["expected_stdout_contains"] in (r.stdout or "")
    if beh["expected_status"] == "exception":
        assert r.exc_type == "ValueError"
    if beh.get("special_check"):
        assert isinstance(r.ret, list) and len(r.ret) == 4


@pytest.mark.skipif(not HAS_NODE, reason="Node.js not available on host")
@pytest.mark.parametrize("beh", SPEC["behaviors"], ids=[b["name"] for b in SPEC["behaviors"]])
def test_js_harness_conformance(beh):
    r = _run_behavior("javascript", CONF_DIR / "impl.js", beh["name"], beh["args"])
    if beh["name"] == "crashes_hard":
        # Inside vm context process may be blocked or exit -> crash or exception
        assert r.status in ("crash", "exception"), f"got {r}"
        return
    assert r.status == beh["expected_status"], f"{beh['name']}: got {r}"
    if "expected_ret" in beh:
        assert r.ret == beh["expected_ret"]
    if beh.get("expect_mutation"):
        assert r.mut, f"Expected argument mutation to be recorded: {r}"
    if "expected_stdout_contains" in beh:
        assert beh["expected_stdout_contains"] in (r.stdout or "")
    if beh["expected_status"] == "exception":
        assert r.exc_type is not None
    if beh.get("special_check"):
        assert isinstance(r.ret, list) and len(r.ret) == 4


@pytest.mark.skipif(not HAS_GCC, reason="C compiler not available on host")
def test_c_harness_conformance_smoke():
    r = _run_behavior("c", CONF_DIR / "impl.c", "add", [3, 4])
    assert r.status == "ok" and r.ret == 7


@pytest.mark.skipif(not HAS_GXX, reason="C++ compiler not available on host")
def test_cpp_harness_conformance_smoke():
    r = _run_behavior("cpp", CONF_DIR / "impl.cpp", "add", [3, 4])
    assert r.status == "ok" and r.ret == 7
