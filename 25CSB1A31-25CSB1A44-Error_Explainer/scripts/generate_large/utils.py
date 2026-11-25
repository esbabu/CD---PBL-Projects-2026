"""
scripts/generate_large/utils.py
-------------------------------
Utilities for large realistic program corpus generation and validation:
- wc -l semantics line counting
- Configurable line range validation [1900, 5300]
- Real toolchain validation (g++ -std=c++17, gcc -std=c11, python -m py_compile, javac)
- SHA-256 calculation
- Manifest JSONL helpers
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def count_lines(text: str) -> int:
    """
    Count lines with wc -l semantics (number of newline characters).
    Ensures trailing newline is present so line count matches splitlines().
    """
    if not text:
        return 0
    if not text.endswith("\n"):
        text += "\n"
    return text.count("\n")


def compute_sha256(file_path: Path | str) -> str:
    """Compute hex SHA-256 digest of a file."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def check_compilation(file_path: str, lang: str, timeout: int = 25) -> Tuple[bool, str]:
    """
    Runs the appropriate compiler or interpreter on file_path in a temp dir.
    Returns (success: bool, stderr_or_msg: str).
    """
    file_path = os.path.abspath(file_path)
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_bin = os.path.join(tmp_dir, "test_bin.exe" if os.name == "nt" else "test_bin")
        try:
            if lang == "cpp":
                cmd = ["g++", "-std=c++17", "-O0", file_path, "-o", out_bin]
                res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)
                return (res.returncode == 0, res.stderr)
            elif lang == "c":
                cmd = ["gcc", "-std=c11", "-O0", file_path, "-o", out_bin]
                res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)
                return (res.returncode == 0, res.stderr)
            elif lang == "python":
                cmd = ["python", "-m", "py_compile", file_path]
                res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)
                return (res.returncode == 0, res.stderr)
            elif lang == "java":
                cmd = ["javac", "-d", tmp_dir, file_path]
                res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)
                return (res.returncode == 0, res.stderr)
            else:
                return False, f"Unsupported language: {lang}"
        except subprocess.TimeoutExpired:
            return False, f"Compilation timed out after {timeout} seconds"
        except Exception as e:
            return False, str(e)


def validate_and_write(
    path: Path,
    code: str,
    expect_compile: bool = True,
    lang: str = "cpp",
    min_lines: int = 1900,
    max_lines: int = 5300,
) -> Tuple[bool, int, str]:
    """
    Validates code constraints and writes to file:
      1. Ensures single trailing newline.
      2. Line count must be within [min_lines, max_lines].
      3. If expect_compile is True, verifies compilation succeeds with 0 errors.
      4. If expect_compile is False, verifies compilation fails with >=1 error.
    Returns: (success: bool, line_count: int, message: str)
    """
    if not code.endswith("\n"):
        code += "\n"

    line_count = count_lines(code)
    if line_count < min_lines or line_count > max_lines:
        return False, line_count, f"Line count {line_count} outside allowed [{min_lines}, {max_lines}] range."

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

    compile_ok, msg = check_compilation(str(path), lang)
    if expect_compile and not compile_ok:
        return False, line_count, f"Compilation failed unexpectedly: {msg.strip()}"
    if not expect_compile and compile_ok:
        return False, line_count, "Expected compilation to fail, but it compiled cleanly."

    return True, line_count, "OK"


def append_manifest_record(manifest_path: Path, record: Dict[str, Any]) -> None:
    """Append a JSON record to manifest file."""
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_manifest(manifest_path: Path) -> List[Dict[str, Any]]:
    """Load JSONL manifest."""
    records = []
    if not manifest_path.exists():
        return records
    with open(manifest_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records
