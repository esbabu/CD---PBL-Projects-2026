"""
scripts/generate_large/generate_all.py
--------------------------------------
Master orchestration script to generate the entire large program corpus (92 files):
- Group 1: 40 Benign files (10 C++, 10 C, 10 Python, 10 Java)
- Group 2: 20 Hard Negative files (5 C++, 5 C, 5 Python, 5 Java)
- Group 3: 32 Broken files (8 C++, 8 C, 8 Python, 8 Java)
"""

from __future__ import annotations

import time
from pathlib import Path

from .generate_benign import generate_all_benign
from .generate_hard_negative import generate_all_hard_negatives
from .generate_broken import generate_all_broken
from .utils import load_manifest

ROOT = Path(__file__).resolve().parent.parent.parent


def run_all() -> None:
    t0 = time.time()
    data_dir = ROOT / "data" / "large"
    data_dir.mkdir(parents=True, exist_ok=True)

    manifest_benign = data_dir / "manifest_benign.jsonl"
    manifest_broken = data_dir / "manifest_broken.jsonl"

    if manifest_benign.exists():
        manifest_benign.unlink()
    if manifest_broken.exists():
        manifest_broken.unlink()

    print("==================================================")
    print("STEP 1: Generating Benign Corpus (40 files)")
    print("==================================================")
    benign_recs = generate_all_benign(manifest_benign)

    print("\n==================================================")
    print("STEP 2: Generating Hard Negative Corpus (20 files)")
    print("==================================================")
    hn_recs = generate_all_hard_negatives(manifest_benign)

    print("\n==================================================")
    print("STEP 3: Generating Broken Corpus (32 files)")
    print("==================================================")
    broken_recs = generate_all_broken(manifest_broken)

    elapsed = time.time() - t0
    total_files = len(benign_recs) + len(hn_recs) + len(broken_recs)

    print("\n==================================================")
    print(f"COMPLETE: Successfully generated and verified {total_files} files in {elapsed:.1f}s.")
    print(f"Manifest benign: {manifest_benign} ({len(benign_recs) + len(hn_recs)} records)")
    print(f"Manifest broken: {manifest_broken} ({len(broken_recs)} records)")
    print("==================================================")


if __name__ == "__main__":
    run_all()
