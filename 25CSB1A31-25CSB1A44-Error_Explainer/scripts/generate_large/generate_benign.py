"""
scripts/generate_large/generate_benign.py
-----------------------------------------
Generates GROUP 1: Benign programs (40 files = 10 per language).
All files compile cleanly with 0 errors and 0 warnings.
Size tiers: 2000, 3000, 4000, 5000 lines (+/- 5%).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Dict, Any

from .utils import validate_and_write, compute_sha256, append_manifest_record, count_lines
from .cpp_modules import assemble_cpp_program, BENIGN_MODULES as CPP_BENIGN
from .c_modules import assemble_c_program, BENIGN_MODULES as C_BENIGN
from .python_modules import assemble_python_program, BENIGN_MODULES as PY_BENIGN
from .java_modules import assemble_java_program, BENIGN_MODULES as JAVA_BENIGN

ROOT = Path(__file__).resolve().parent.parent.parent

# 10 filenames per language
BASE_NAMES = [
    "system_service_01",
    "data_pipeline_02",
    "network_gateway_03",
    "storage_engine_04",
    "compute_cluster_05",
    "telemetry_node_06",
    "workflow_manager_07",
    "transaction_broker_08",
    "analytics_core_09",
    "platform_host_10"
]

JAVA_CLASS_NAMES = [
    "SystemService01",
    "DataPipeline02",
    "NetworkGateway03",
    "StorageEngine04",
    "ComputeCluster05",
    "TelemetryNode06",
    "WorkflowManager07",
    "TransactionBroker08",
    "AnalyticsCore09",
    "PlatformHost10"
]

# Tiers distribution for 10 files: 2x 2000, 3x 3000, 3x 4000, 2x 5000
TIER_TARGETS = [
    2000, 2000,
    3000, 3000, 3000,
    4000, 4000, 4000,
    5000, 5000
]


def generate_all_benign(manifest_path: Path) -> List[Dict[str, Any]]:
    records = []
    langs = ["cpp", "c", "python", "java"]
    
    for lang in langs:
        print(f"Generating benign corpus for {lang}...")
        for i in range(10):
            target_lines = TIER_TARGETS[i]
            base_name = BASE_NAMES[i]
            seed = 1000 + i * 17
            file_id = f"large_benign_{lang}_{i+1:02d}"
            
            if lang == "cpp":
                rel_path = f"test_cases/large/benign/cpp/{base_name}.cpp"
                mod_keys = list(CPP_BENIGN.keys())
                # Rotate module selection for variety
                selected_keys = mod_keys[i % 5:] + mod_keys[:i % 5]
                code, used_mods = assemble_cpp_program(selected_keys, target_lines, seed=seed)
            elif lang == "c":
                rel_path = f"test_cases/large/benign/c/{base_name}.c"
                mod_keys = list(C_BENIGN.keys())
                selected_keys = mod_keys[i % 4:] + mod_keys[:i % 4]
                code, used_mods = assemble_c_program(selected_keys, target_lines, seed=seed)
            elif lang == "python":
                rel_path = f"test_cases/large/benign/python/{base_name}.py"
                mod_keys = list(PY_BENIGN.keys())
                selected_keys = mod_keys[i % 4:] + mod_keys[:i % 4]
                code, used_mods = assemble_python_program(selected_keys, target_lines, seed=seed)
            elif lang == "java":
                java_class = JAVA_CLASS_NAMES[i]
                rel_path = f"test_cases/large/benign/java/{java_class}.java"
                mod_keys = list(JAVA_BENIGN.keys())
                selected_keys = mod_keys[i % 4:] + mod_keys[:i % 4]
                code, used_mods = assemble_java_program(selected_keys, target_lines, class_name=java_class, seed=seed)

            full_path = ROOT / rel_path
            ok, actual_lines, msg = validate_and_write(full_path, code, expect_compile=True, lang=lang)
            if not ok:
                raise RuntimeError(f"Failed to generate {rel_path}: {msg}")

            sha = compute_sha256(full_path)
            rec = {
                "id": file_id,
                "path": rel_path.replace("\\\\", "/"),
                "language": lang,
                "group": "benign",
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
    if manifest.exists():
        manifest.unlink()
    recs = generate_all_benign(manifest)
    print(f"Benign generation complete: {len(recs)} files written.")
