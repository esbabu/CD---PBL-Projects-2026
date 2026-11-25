"""
tests/test_large_corpus.py
--------------------------
Pytest test suite for large realistic program corpus (2,000 to 5,000 lines).
Verifies:
  - Manifest files exist and are valid JSONL
  - All 92 files exist on disk
  - SHA-256 digests match manifest records
  - Line counts are strictly within [1900, 5300] range and match manifest
  - Clean programs (benign and hard negative) compile cleanly (marked @pytest.mark.slow)
  - Broken programs fail compilation with real errors (marked @pytest.mark.slow)
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from scripts.generate_large.utils import compute_sha256, count_lines, check_compilation

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_BENIGN = ROOT / "data" / "large" / "manifest_benign.jsonl"
MANIFEST_BROKEN = ROOT / "data" / "large" / "manifest_broken.jsonl"


def load_jsonl(path: Path):
    assert path.exists(), f"Manifest missing: {path}"
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


# ==================== FAST TESTS (Runs in milliseconds) ====================

def test_manifests_exist_and_count():
    benign_recs = load_jsonl(MANIFEST_BENIGN)
    broken_recs = load_jsonl(MANIFEST_BROKEN)

    assert len(benign_recs) == 60, f"Expected 60 records in manifest_benign, got {len(benign_recs)}"
    assert len(broken_recs) == 32, f"Expected 32 records in manifest_broken, got {len(broken_recs)}"

    benign_only = [r for r in benign_recs if r["group"] == "benign"]
    hard_neg = [r for r in benign_recs if r["group"] == "hard_negative"]

    assert len(benign_only) == 40, f"Expected 40 benign files, got {len(benign_only)}"
    assert len(hard_neg) == 20, f"Expected 20 hard negative files, got {len(hard_neg)}"


def test_manifest_schemas():
    for rec in load_jsonl(MANIFEST_BENIGN):
        for req in ["id", "path", "language", "group", "lines", "sha256", "seed", "modules"]:
            assert req in rec, f"Missing {req} in benign record {rec}"
        assert rec["group"] in ("benign", "hard_negative")
        assert len(rec["modules"]) > 0

    for rec in load_jsonl(MANIFEST_BROKEN):
        for req in ["id", "path", "language", "group", "lines", "sha256", "seed", "modules", "errors"]:
            assert req in rec, f"Missing {req} in broken record {rec}"
        assert rec["group"] == "broken"
        assert len(rec["errors"]) >= 1, f"No errors recorded for {rec['id']}"


def test_all_files_exist_and_hashes():
    all_recs = load_jsonl(MANIFEST_BENIGN) + load_jsonl(MANIFEST_BROKEN)
    for rec in all_recs:
        file_path = ROOT / rec["path"]
        assert file_path.exists(), f"File does not exist: {file_path}"
        actual_sha = compute_sha256(file_path)
        assert actual_sha == rec["sha256"], f"SHA256 mismatch for {rec['path']}: {actual_sha} vs {rec['sha256']}"


def test_line_counts_in_range():
    all_recs = load_jsonl(MANIFEST_BENIGN) + load_jsonl(MANIFEST_BROKEN)
    for rec in all_recs:
        file_path = ROOT / rec["path"]
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        lines = count_lines(content)
        assert lines == rec["lines"], f"Line count mismatch for {rec['path']}: {lines} vs {rec['lines']}"
        assert 1900 <= lines <= 5300, f"Line count {lines} out of [1900, 5300] range in {rec['path']}"


# ==================== SLOW COMPILATION TESTS ====================

@pytest.mark.slow
def test_benign_and_hard_negative_compilation():
    """Verify that all benign and hard negative programs compile cleanly with real compilers."""
    benign_recs = load_jsonl(MANIFEST_BENIGN)
    for rec in benign_recs:
        file_path = ROOT / rec["path"]
        ok, msg = check_compilation(str(file_path), rec["language"])
        assert ok, f"Clean compilation failed for {rec['path']}:\n{msg}"


@pytest.mark.slow
def test_broken_files_fail_compilation():
    """Verify that every broken file fails compilation on the real compiler."""
    broken_recs = load_jsonl(MANIFEST_BROKEN)
    for rec in broken_recs:
        file_path = ROOT / rec["path"]
        ok, msg = check_compilation(str(file_path), rec["language"])
        assert not ok, f"Expected broken file {rec['path']} to fail compilation, but it succeeded!"
