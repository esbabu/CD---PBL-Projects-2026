"""
scripts/generate_large/generate_hard_negative.py
------------------------------------------------
Generates GROUP 2: Hard Negative programs (20 files = 5 per language).
These are BENIGN programs that contain patterns (e.g. security awareness prompts,
safe popen calls with constants, Base64, salted password hashing, getenv, WAF attack regexes)
which naive keyword scanners wrongly flag, but are completely benign and safe.
All files compile cleanly with 0 errors and 0 warnings.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Dict, Any

from .utils import validate_and_write, compute_sha256, append_manifest_record, count_lines
from .cpp_modules import assemble_cpp_program, BENIGN_MODULES as CPP_BENIGN, HARD_NEGATIVE_MODULES as CPP_SEC
from .c_modules import assemble_c_program, BENIGN_MODULES as C_BENIGN, HARD_NEGATIVE_MODULES as C_SEC
from .python_modules import assemble_python_program, BENIGN_MODULES as PY_BENIGN, HARD_NEGATIVE_MODULES as PY_SEC
from .java_modules import assemble_java_program, BENIGN_MODULES as JAVA_BENIGN, HARD_NEGATIVE_MODULES as JAVA_SEC

ROOT = Path(__file__).resolve().parent.parent.parent

# 5 filenames per language
HN_BASE_NAMES = [
    "security_audit_app_01",
    "diagnostic_monitor_02",
    "credential_validator_03",
    "firewall_inspect_04",
    "telemetry_filter_05"
]

HN_JAVA_CLASS_NAMES = [
    "SecurityAuditApp01",
    "DiagnosticMonitor02",
    "CredentialValidator03",
    "FirewallInspect04",
    "TelemetryFilter05"
]

HN_TIER_TARGETS = [
    2000,
    3000,
    4000,
    5000,
    3500
]


def generate_all_hard_negatives(manifest_path: Path) -> List[Dict[str, Any]]:
    records = []
    langs = ["cpp", "c", "python", "java"]

    for lang in langs:
        print(f"Generating hard negative corpus for {lang}...")
        for i in range(5):
            target_lines = HN_TIER_TARGETS[i]
            base_name = HN_BASE_NAMES[i]
            seed = 5000 + i * 23
            file_id = f"large_hard_negative_{lang}_{i+1:02d}"

            if lang == "cpp":
                rel_path = f"test_cases/large/hard_negative/cpp/{base_name}.cpp"
                # Include security modules + core benign modules
                sec_keys = list(CPP_SEC.keys())
                benign_keys = list(CPP_BENIGN.keys())
                combined_keys = sec_keys + benign_keys[i % 4:]
                code, used_mods = assemble_cpp_program(combined_keys, target_lines, seed=seed)
            elif lang == "c":
                rel_path = f"test_cases/large/hard_negative/c/{base_name}.c"
                sec_keys = list(C_SEC.keys())
                benign_keys = list(C_BENIGN.keys())
                combined_keys = sec_keys + benign_keys[i % 3:]
                code, used_mods = assemble_c_program(combined_keys, target_lines, seed=seed)
            elif lang == "python":
                rel_path = f"test_cases/large/hard_negative/python/{base_name}.py"
                sec_keys = list(PY_SEC.keys())
                benign_keys = list(PY_BENIGN.keys())
                combined_keys = sec_keys + benign_keys[i % 3:]
                code, used_mods = assemble_python_program(combined_keys, target_lines, seed=seed)
            elif lang == "java":
                java_class = HN_JAVA_CLASS_NAMES[i]
                rel_path = f"test_cases/large/hard_negative/java/{java_class}.java"
                sec_keys = list(JAVA_SEC.keys())
                benign_keys = list(JAVA_BENIGN.keys())
                combined_keys = sec_keys + benign_keys[i % 3:]
                code, used_mods = assemble_java_program(combined_keys, target_lines, class_name=java_class, seed=seed)

            full_path = ROOT / rel_path
            ok, actual_lines, msg = validate_and_write(full_path, code, expect_compile=True, lang=lang)
            if not ok:
                raise RuntimeError(f"Failed to generate {rel_path}: {msg}")

            sha = compute_sha256(full_path)
            rec = {
                "id": file_id,
                "path": rel_path.replace("\\\\", "/"),
                "language": lang,
                "group": "hard_negative",
                "lines": actual_lines,
                "sha256": sha,
                "seed": seed,
                "modules": used_mods
            }
            append_manifest_record(manifest_path, rec)
            records.append(rec)
            print(f"  [OK] {rel_path} ({actual_lines} lines, sha256={sha[:8]}...)")

    return records


if __name__ == "__main__":
    manifest = ROOT / "data" / "large" / "manifest_benign.jsonl"
    recs = generate_all_hard_negatives(manifest)
    print(f"Hard negative generation complete: {len(recs)} files written.")
