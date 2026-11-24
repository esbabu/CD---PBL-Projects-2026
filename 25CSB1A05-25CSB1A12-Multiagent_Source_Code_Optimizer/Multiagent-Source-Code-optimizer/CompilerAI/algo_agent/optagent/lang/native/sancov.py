"""SanCov edge parsing and llvm-cov line coverage extraction for C/C++."""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


def parse_sancov_edges(edges: list[str]) -> set[str]:
    """Extract normalized SanCov counter edge IDs (`sc:<idx>`)."""
    return {e for e in edges if isinstance(e, str) and e.startswith("sc:")}


def export_llvm_cov_lines(binary_path: Path, profraw_paths: list[Path], target_filename: str) -> set[int]:
    """Merge llvm profraw files and export executed 1-based line numbers for `target_filename`."""
    if not profraw_paths or not shutil.which("llvm-profdata") or not shutil.which("llvm-cov"):
        return set()
    profdata = binary_path.with_suffix(".profdata")
    try:
        m = subprocess.run(
            ["llvm-profdata", "merge", "-sparse", *[str(p) for p in profraw_paths], "-o", str(profdata)],
            capture_output=True, text=True, timeout=15,
        )
        if m.returncode != 0:
            return set()
        exp = subprocess.run(
            ["llvm-cov", "export", str(binary_path), f"-instr-profile={profdata}"],
            capture_output=True, text=True, timeout=15,
        )
        if exp.returncode != 0:
            return set()
        data = json.loads(exp.stdout)
        covered: set[int] = set()
        for datum in data.get("data", []):
            for fobj in datum.get("files", []):
                if not fobj.get("filename", "").endswith(target_filename):
                    continue
                for seg in fobj.get("segments", []):
                    # llvm-cov segment: [line, col, count, hasCount, isRegionEntry, ...]
                    if len(seg) >= 4 and seg[3] and seg[2] > 0:
                        covered.add(int(seg[0]))
        return covered
    except Exception:
        return set()
