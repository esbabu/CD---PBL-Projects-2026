"""
tests/test_vscode_bridge.py
───────────────────────────
Integration tests for tools/vscode_bridge.py.
Validates stable JSON communication between VS Code extension and Python engine.
"""

import os
import json
import subprocess
import pytest

_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR = os.path.dirname(_TESTS_DIR)
_BRIDGE_SCRIPT = os.path.join(_ROOT_DIR, "tools", "vscode_bridge.py")


def run_bridge(*args):
    cmd = ["python", _BRIDGE_SCRIPT] + list(args)
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=30,
        cwd=_ROOT_DIR,
    )
    assert proc.returncode == 0, f"Bridge crashed with non-zero exit code: {proc.stderr}"
    data = json.loads(proc.stdout)
    return data


def test_bridge_health():
    res = run_bridge("--health")
    assert res.get("ok") is True
    assert res.get("status") == "healthy"


def test_bridge_nonexistent_file():
    res = run_bridge("non_existent_file_xyz123.cpp")
    assert res.get("ok") is False
    assert "File not found" in res.get("error", "")


def test_bridge_diagnostics_syntax_error():
    sample = os.path.join(_ROOT_DIR, "test_cases", "syntax_error.cpp")
    res = run_bridge(sample)
    assert res.get("ok") is True
    assert "compiler" in res
    diags = res.get("diagnostics", [])
    assert len(diags) > 0

    first = diags[0]
    assert "line" in first
    assert "column" in first
    assert "severity" in first
    assert "category" in first
    assert "what" in first
    assert "why" in first
    assert "how" in first


def test_bridge_autoheal():
    sample = os.path.join(_ROOT_DIR, "test_cases", "syntax_error.cpp")
    res = run_bridge("--autoheal", sample)
    assert res.get("ok") is True
    assert res.get("status") in ("success", "no_fixes")
    assert "patched_source" in res
    assert "diff" in res
    if res["status"] == "success":
        assert res.get("healed_count", 0) >= 1
        assert "diff" in res


def test_bridge_format():
    sample = os.path.join(_ROOT_DIR, "test_cases", "syntax_error.cpp")
    res = run_bridge("--format", sample)
    assert res.get("ok") is True
    assert "formatted_source" in res
    assert res.get("method") in ("clang-format", "fallback")
