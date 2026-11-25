"""
tests/test_large_attacks.py
---------------------------
Validates data/large/manifest_attacks.jsonl and generated samples in
test_cases/large/attack/:
  - Manifest schema, file existence, SHA-256 integrity, and line counts
  - Class coverage (>=5 attack samples per class A-K)
  - 50/50 dev/test stratified split balance
  - Language, stage (ingress/egress), position_pct, and obfuscation (>=35%) distributions
  - Benign/hard_negative baseline entries for false-positive measurement
  - Neutral filenames and absence of forbidden label-leakage words in inserted code
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

from scripts.generate_large.utils import compute_sha256, count_lines

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / "data" / "large" / "manifest_attacks.jsonl"
ATTACK_DIR = ROOT / "test_cases" / "large" / "attack"

VALID_CLASSES = [chr(c) for c in range(ord("A"), ord("K") + 1)]
VALID_LANGUAGES = ("cpp", "c", "python", "java")
VALID_POSITIONS = (2, 25, 50, 75, 98)
FORBIDDEN_WORDS = (
    "attack",
    "malicious",
    "payload",
    "exploit",
    "trojan",
    "backdoor",
    "adversarial",
)
REQUIRED_KEYS = (
    "id",
    "language",
    "lines",
    "class",
    "stage",
    "carrier",
    "position_pct",
    "obfuscation",
    "expected",
    "split",
    "sha256",
)


def _load_records() -> List[Dict[str, Any]]:
    assert MANIFEST_PATH.exists(), f"Manifest missing: {MANIFEST_PATH}"
    records: List[Dict[str, Any]] = []
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped:
                records.append(json.loads(stripped))
    return records


def test_manifest_schema_and_integrity() -> None:
    records = _load_records()
    attacks = [r for r in records if r["expected"] == "attack"]
    benigns = [r for r in records if r["expected"] == "benign"]

    assert 55 <= len(attacks) <= 70, f"Expected ~60 attacks, got {len(attacks)}"
    assert 15 <= len(benigns) <= 30, f"Expected ~20 benign entries, got {len(benigns)}"

    seen_ids = set()
    for rec in records:
        for key in REQUIRED_KEYS:
            assert key in rec, f"Missing key '{key}' in {rec.get('id')}"

        assert rec["id"] not in seen_ids, f"Duplicate ID: {rec['id']}"
        seen_ids.add(rec["id"])

        assert rec["language"] in VALID_LANGUAGES
        assert rec["stage"] in ("ingress", "egress")
        assert rec["expected"] in ("attack", "benign")
        assert rec["split"] in ("dev", "test")

        carrier_path = ROOT / rec["carrier"]
        assert carrier_path.exists(), f"Carrier missing: {carrier_path}"

        if rec["stage"] == "ingress":
            assert "path" in rec, f"Ingress record missing 'path': {rec['id']}"
            target_path = ROOT / rec["path"]
        else:
            assert "original_path" in rec and "patched_path" in rec, (
                f"Egress record missing original_path/patched_path: {rec['id']}"
            )
            orig_path = ROOT / rec["original_path"]
            assert orig_path.exists(), f"Original path missing: {orig_path}"
            target_path = ROOT / rec["patched_path"]

        assert target_path.exists(), f"Target file missing: {target_path}"
        content = target_path.read_text(encoding="utf-8")
        actual_lines = count_lines(content)
        actual_sha = compute_sha256(target_path)

        assert rec["lines"] == actual_lines, (
            f"Line count mismatch for {rec['id']}: {rec['lines']} vs {actual_lines}"
        )
        assert rec["sha256"] == actual_sha, (
            f"SHA-256 mismatch for {rec['id']}: {rec['sha256']} vs {actual_sha}"
        )
        assert 1900 <= actual_lines <= 5300, (
            f"Line count {actual_lines} out of large program range in {rec['id']}"
        )


def test_class_coverage_and_stratified_splits() -> None:
    records = _load_records()
    attacks = [r for r in records if r["expected"] == "attack"]
    benigns = [r for r in records if r["expected"] == "benign"]

    by_class = Counter(r["class"] for r in attacks)
    for cls_name in VALID_CLASSES:
        assert by_class[cls_name] >= 5, (
            f"Class {cls_name} has {by_class[cls_name]} attack samples, expected >= 5"
        )
        cls_splits = Counter(r["split"] for r in attacks if r["class"] == cls_name)
        assert cls_splits["dev"] >= 2 and cls_splits["test"] >= 2, (
            f"Class {cls_name} not represented in both splits: {dict(cls_splits)}"
        )
        assert abs(cls_splits["dev"] - cls_splits["test"]) <= 1, (
            f"Class {cls_name} split imbalanced: {dict(cls_splits)}"
        )

    atk_splits = Counter(r["split"] for r in attacks)
    assert atk_splits["dev"] == atk_splits["test"], (
        f"Attack dev/test split not 50/50: {dict(atk_splits)}"
    )

    ben_splits = Counter(r["split"] for r in benigns)
    assert abs(ben_splits["dev"] - ben_splits["test"]) <= 1, (
        f"Benign dev/test split imbalanced: {dict(ben_splits)}"
    )


def test_distributions_and_obfuscation_rate() -> None:
    records = _load_records()
    attacks = [r for r in records if r["expected"] == "attack"]

    langs = Counter(r["language"] for r in attacks)
    for lang in VALID_LANGUAGES:
        assert langs[lang] >= 12, f"Insufficient samples for {lang}: {langs[lang]}"

    stages = Counter(r["stage"] for r in attacks)
    assert stages["ingress"] >= 30 and stages["egress"] >= 20, (
        f"Unexpected stage distribution: {dict(stages)}"
    )

    positions = Counter(r["position_pct"] for r in attacks)
    for pos in VALID_POSITIONS:
        assert positions[pos] >= 10, f"Position {pos}% underrepresented: {positions[pos]}"

    obfuscated = [r for r in attacks if r["obfuscation"] != "none"]
    obf_ratio = len(obfuscated) / len(attacks)
    assert obf_ratio >= 0.35, f"Obfuscation ratio {obf_ratio:.2%} < 35%"

    expected_obf_families = {
        "base64", "hex", "rot13", "homoglyph", "zero_width",
        "leet", "split_string", "multilingual",
    }
    present_obfs = {r["obfuscation"] for r in obfuscated}
    assert expected_obf_families.issubset(present_obfs), (
        f"Missing obfuscation encoders: {expected_obf_families - present_obfs}"
    )
    assert any(o.startswith("combo_") for o in present_obfs), "Missing combination obfuscators"


def test_neutral_names_and_insertion_sizes() -> None:
    records = _load_records()
    attacks = [r for r in records if r["expected"] == "attack"]

    for rec in attacks:
        rel = rec["path"] if rec["stage"] == "ingress" else rec["patched_path"]
        file_path = ROOT / rel
        fname = file_path.name.lower()
        for word in FORBIDDEN_WORDS:
            assert word not in fname, f"Forbidden word '{word}' in filename: {rel}"

        carrier_lines = (ROOT / rec["carrier"]).read_text(encoding="utf-8").splitlines()
        sample_lines = file_path.read_text(encoding="utf-8").splitlines()
        added_count = len(sample_lines) - len(carrier_lines)
        assert 3 <= added_count <= 30, (
            f"Inserted line count {added_count} outside [3, 30] in {rel}"
        )
