"""Automated verification test for the clean submission archive.

Ensures that:
1. `scripts/build_clean_submission.py` packages strictly git-tracked files.
2. The produced ZIP archive contains zero forbidden files or directories (.env, .venv,
   instance, backups, dist, .coverage, __pycache__, .pytest_cache, .ruff_cache, *.db, *.pyc).
3. All members in the ZIP archive are traceable to `git ls-files`.
"""

from __future__ import annotations

import zipfile
from pathlib import Path


from scripts.build_clean_submission import (
    FORBIDDEN_DIR_PARTS,
    FORBIDDEN_EXACT_NAMES,
    FORBIDDEN_EXTENSIONS,
    build_clean_submission,
    get_git_tracked_files,
    is_forbidden,
)


def test_build_clean_submission_produces_clean_archive(tmp_path: Path):
    project_root = Path(__file__).resolve().parent.parent
    output_zip = tmp_path / "test_submission.zip"

    # Build the submission archive into the tmp_path location
    result_path = build_clean_submission(output_zip=output_zip)
    assert result_path.is_file(), f"Expected submission archive at {result_path}"
    assert result_path.stat().st_size > 0

    tracked = set(get_git_tracked_files(project_root))
    # Normalize slashes for cross-platform comparison
    norm_tracked = {p.replace("\\", "/") for p in tracked}

    with zipfile.ZipFile(result_path, "r") as zf:
        members = zf.namelist()
        assert len(members) > 0, "Submission ZIP is empty"

        for member in members:
            # 1. Must be a tracked git file
            assert member in norm_tracked, f"Untracked file found in submission archive: {member}"

            # 2. Must not be forbidden by path helper
            assert not is_forbidden(member), f"Forbidden file found in archive: {member}"

            # 3. Check exact forbidden criteria
            p = Path(member)
            if p.name != ".env.example":
                assert p.name not in FORBIDDEN_EXACT_NAMES, f"Forbidden exact name: {p.name}"
                assert not p.name.startswith(".env"), f"Forbidden .env variation: {p.name}"

            assert not p.name.startswith(".coverage"), f"Forbidden coverage artifact: {p.name}"
            assert p.suffix.lower() not in FORBIDDEN_EXTENSIONS, f"Forbidden extension: {p.suffix}"

            for part in p.parts[:-1]:
                assert part not in FORBIDDEN_DIR_PARTS, f"Forbidden directory part '{part}' in '{member}'"
                assert not part.startswith(".venv"), f"Forbidden venv path in '{member}'"
                assert part != "instance", f"Forbidden instance path in '{member}'"
                assert part != "backups", f"Forbidden backups path in '{member}'"
                assert part != "dist", f"Forbidden dist path in '{member}'"
