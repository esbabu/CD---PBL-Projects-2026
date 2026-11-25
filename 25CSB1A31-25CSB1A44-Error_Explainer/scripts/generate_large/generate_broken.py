"""
scripts/generate_large/generate_broken.py
-----------------------------------------
Generates GROUP 3: Broken programs (32 files = 8 per language).
Each program is a clean large program (2000-5000 lines) with 1 to 5 injected compile errors
at varied depths (~2%, 40%, 75%, 98%).
Every file MUST FAIL real compilation.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Dict, Any, Tuple

from .utils import validate_and_write, compute_sha256, append_manifest_record, count_lines
from .cpp_modules import assemble_cpp_program, BENIGN_MODULES as CPP_BENIGN
from .c_modules import assemble_c_program, BENIGN_MODULES as C_BENIGN
from .python_modules import assemble_python_program, BENIGN_MODULES as PY_BENIGN
from .java_modules import assemble_java_program, BENIGN_MODULES as JAVA_BENIGN

ROOT = Path(__file__).resolve().parent.parent.parent

BROKEN_BASE_NAMES = [
    "service_node_01",
    "compute_worker_02",
    "gateway_proxy_03",
    "storage_replica_04",
    "pipeline_stage_05",
    "analytics_engine_06",
    "transaction_host_07",
    "platform_kernel_08"
]

BROKEN_JAVA_CLASS_NAMES = [
    "ServiceNode01",
    "ComputeWorker02",
    "GatewayProxy03",
    "StorageReplica04",
    "PipelineStage05",
    "AnalyticsEngine06",
    "TransactionHost07",
    "PlatformKernel08"
]

# Tiers distribution for 8 files: 2x 2000, 2x 3000, 2x 4000, 2x 5000
BROKEN_TIER_TARGETS = [
    2000, 2000,
    3000, 3000,
    4000, 4000,
    5000, 5000
]


def inject_errors_cpp_c(lines: List[str], error_plan: List[Tuple[float, str]]) -> Tuple[List[str], List[Dict[str, Any]]]:
    """Inject errors at specified depths in C/C++ source lines."""
    injected_records = []
    modified_lines = list(lines)
    total_lines = len(modified_lines)

    for depth, err_type in error_plan:
        target_idx = int(depth * total_lines)
        target_idx = max(20, min(total_lines - 10, target_idx))

        if err_type == "missing_semicolon":
            # Search nearby for line ending with semicolon
            found = False
            for offset in range(0, 50):
                idx = target_idx + offset
                if idx < total_lines and modified_lines[idx].rstrip().endswith(";"):
                    line_content = modified_lines[idx].rstrip()
                    modified_lines[idx] = line_content[:-1]  # strip semicolon
                    injected_records.append({"line": idx + 1, "type": "missing_semicolon"})
                    found = True
                    break
            if not found:
                modified_lines.insert(target_idx, "int broken_missing_semi = 42")
                injected_records.append({"line": target_idx + 1, "type": "missing_semicolon"})

        elif err_type == "undeclared_variable":
            modified_lines.insert(target_idx, "UNDECLARED_SYMBOL_XYZ_NOT_FOUND = 12345;")
            injected_records.append({"line": target_idx + 1, "type": "undeclared_variable"})

        elif err_type == "type_mismatch":
            modified_lines.insert(target_idx, 'int invalid_type_assign_mismatch = "cannot_assign_string_literal";')
            injected_records.append({"line": target_idx + 1, "type": "type_mismatch"})

        elif err_type == "missing_brace":
            # Find a line with '}' and remove it
            found = False
            for offset in range(0, 50):
                idx = target_idx + offset
                if idx < total_lines and "}" in modified_lines[idx]:
                    modified_lines[idx] = modified_lines[idx].replace("}", "/* missing brace */")
                    injected_records.append({"line": idx + 1, "type": "missing_brace"})
                    found = True
                    break
            if not found:
                modified_lines.insert(target_idx, "{ /* unclosed opening brace */")
                injected_records.append({"line": target_idx + 1, "type": "missing_brace"})

        elif err_type == "wrong_return_type":
            modified_lines.insert(target_idx, 'return "illegal_return_string_in_int_context";')
            injected_records.append({"line": target_idx + 1, "type": "wrong_return_type"})

    return modified_lines, injected_records


def inject_errors_python(lines: List[str], error_plan: List[Tuple[float, str]]) -> Tuple[List[str], List[Dict[str, Any]]]:
    """Inject syntax and compile errors in Python source lines."""
    injected_records = []
    modified_lines = list(lines)
    total_lines = len(modified_lines)

    for depth, err_type in error_plan:
        target_idx = int(depth * total_lines)
        target_idx = max(10, min(total_lines - 10, target_idx))

        if err_type == "bad_indentation":
            modified_lines.insert(target_idx, "         print('unexpected indentation level')")
            injected_records.append({"line": target_idx + 1, "type": "bad_indentation"})

        elif err_type == "syntax_error":
            # Invalid syntax like missing colon or broken statement
            modified_lines.insert(target_idx, "def broken_syntax_function_declaration(a b)")
            injected_records.append({"line": target_idx + 1, "type": "syntax_error"})

        elif err_type == "undeclared_variable":
            modified_lines.insert(target_idx, "def invalid_syntax_keyword_as_var(): pass = 42")
            injected_records.append({"line": target_idx + 1, "type": "syntax_error"})

        elif err_type == "missing_colon":
            modified_lines.insert(target_idx, "if True")
            injected_records.append({"line": target_idx + 1, "type": "missing_colon"})

    return modified_lines, injected_records


def inject_errors_java(lines: List[str], error_plan: List[Tuple[float, str]]) -> Tuple[List[str], List[Dict[str, Any]]]:
    """Inject errors at specified depths in Java source lines."""
    injected_records = []
    modified_lines = list(lines)
    total_lines = len(modified_lines)

    for depth, err_type in error_plan:
        target_idx = int(depth * total_lines)
        target_idx = max(20, min(total_lines - 10, target_idx))

        if err_type == "missing_semicolon":
            found = False
            for offset in range(0, 50):
                idx = target_idx + offset
                if idx < total_lines and modified_lines[idx].rstrip().endswith(";"):
                    modified_lines[idx] = modified_lines[idx].rstrip()[:-1]
                    injected_records.append({"line": idx + 1, "type": "missing_semicolon"})
                    found = True
                    break
            if not found:
                modified_lines.insert(target_idx, "        int brokenMissingSemi = 42")
                injected_records.append({"line": target_idx + 1, "type": "missing_semicolon"})

        elif err_type == "missing_symbol":
            modified_lines.insert(target_idx, "        NonExistentJavaClassType objRef = new NonExistentJavaClassType();")
            injected_records.append({"line": target_idx + 1, "type": "missing_symbol"})

        elif err_type == "type_mismatch":
            modified_lines.insert(target_idx, '        int typeMismatchVal = "incompatible_string_literal";')
            injected_records.append({"line": target_idx + 1, "type": "type_mismatch"})

        elif err_type == "missing_brace":
            found = False
            for offset in range(0, 50):
                idx = target_idx + offset
                if idx < total_lines and "}" in modified_lines[idx]:
                    modified_lines[idx] = modified_lines[idx].replace("}", "/* missing closing brace */")
                    injected_records.append({"line": idx + 1, "type": "missing_brace"})
                    found = True
                    break
            if not found:
                modified_lines.insert(target_idx, "    { /* unclosed brace */")
                injected_records.append({"line": target_idx + 1, "type": "missing_brace"})

    return modified_lines, injected_records


# Error injection plans for the 8 files (varied count 1 to 5, varied depths)
ERROR_PLANS_C_CPP = [
    # 0 (tier 2000): 1 error at depth 40%
    [(0.40, "undeclared_variable")],
    # 1 (tier 2000): 2 errors at depths 2%, 75%
    [(0.02, "missing_semicolon"), (0.75, "type_mismatch")],
    # 2 (tier 3000): 3 errors at depths 2%, 40%, 98%
    [(0.02, "missing_semicolon"), (0.40, "missing_brace"), (0.98, "wrong_return_type")],
    # 3 (tier 3000): 2 errors at depths 40%, 75%
    [(0.40, "undeclared_variable"), (0.75, "type_mismatch")],
    # 4 (tier 4000): 4 errors at depths 2%, 40%, 75%, 98%
    [(0.02, "missing_semicolon"), (0.40, "missing_brace"), (0.75, "undeclared_variable"), (0.98, "type_mismatch")],
    # 5 (tier 4000): 3 errors at depths 2%, 75%, 98%
    [(0.02, "missing_semicolon"), (0.75, "undeclared_variable"), (0.98, "wrong_return_type")],
    # 6 (tier 5000): 5 errors at depths 2%, 25%, 50%, 75%, 98%
    [(0.02, "missing_semicolon"), (0.25, "missing_brace"), (0.50, "undeclared_variable"), (0.75, "type_mismatch"), (0.98, "wrong_return_type")],
    # 7 (tier 5000): 4 errors at depths 2%, 40%, 75%, 98%
    [(0.02, "missing_semicolon"), (0.40, "undeclared_variable"), (0.75, "missing_brace"), (0.98, "type_mismatch")]
]

ERROR_PLANS_PY = [
    [(0.40, "syntax_error")],
    [(0.02, "bad_indentation"), (0.75, "syntax_error")],
    [(0.02, "bad_indentation"), (0.40, "missing_colon"), (0.98, "syntax_error")],
    [(0.40, "undeclared_variable"), (0.75, "bad_indentation")],
    [(0.02, "bad_indentation"), (0.40, "syntax_error"), (0.75, "missing_colon"), (0.98, "bad_indentation")],
    [(0.02, "syntax_error"), (0.75, "bad_indentation"), (0.98, "syntax_error")],
    [(0.02, "bad_indentation"), (0.25, "missing_colon"), (0.50, "syntax_error"), (0.75, "undeclared_variable"), (0.98, "bad_indentation")],
    [(0.02, "syntax_error"), (0.40, "bad_indentation"), (0.75, "missing_colon"), (0.98, "syntax_error")]
]

ERROR_PLANS_JAVA = [
    [(0.40, "missing_symbol")],
    [(0.02, "missing_semicolon"), (0.75, "type_mismatch")],
    [(0.02, "missing_semicolon"), (0.40, "missing_brace"), (0.98, "type_mismatch")],
    [(0.40, "missing_symbol"), (0.75, "type_mismatch")],
    [(0.02, "missing_semicolon"), (0.40, "missing_brace"), (0.75, "missing_symbol"), (0.98, "type_mismatch")],
    [(0.02, "missing_semicolon"), (0.75, "missing_symbol"), (0.98, "type_mismatch")],
    [(0.02, "missing_semicolon"), (0.25, "missing_brace"), (0.50, "missing_symbol"), (0.75, "type_mismatch"), (0.98, "missing_semicolon")],
    [(0.02, "missing_semicolon"), (0.40, "missing_symbol"), (0.75, "missing_brace"), (0.98, "type_mismatch")]
]


def generate_all_broken(manifest_path: Path) -> List[Dict[str, Any]]:
    records = []
    langs = ["cpp", "c", "python", "java"]

    for lang in langs:
        print(f"Generating broken corpus for {lang}...")
        for i in range(8):
            target_lines = BROKEN_TIER_TARGETS[i]
            base_name = BROKEN_BASE_NAMES[i]
            seed = 8000 + i * 31
            file_id = f"large_broken_{lang}_{i+1:02d}"

            # Assemble valid base program
            if lang == "cpp":
                rel_path = f"test_cases/large/broken/cpp/{base_name}.cpp"
                mod_keys = list(CPP_BENIGN.keys())
                selected_keys = mod_keys[(i + 1) % 4:] + mod_keys[:(i + 1) % 4]
                clean_code, used_mods = assemble_cpp_program(selected_keys, target_lines, seed=seed)
                lines = clean_code.splitlines()
                broken_lines, err_records = inject_errors_cpp_c(lines, ERROR_PLANS_C_CPP[i])

            elif lang == "c":
                rel_path = f"test_cases/large/broken/c/{base_name}.c"
                mod_keys = list(C_BENIGN.keys())
                selected_keys = mod_keys[(i + 1) % 3:] + mod_keys[:(i + 1) % 3]
                clean_code, used_mods = assemble_c_program(selected_keys, target_lines, seed=seed)
                lines = clean_code.splitlines()
                broken_lines, err_records = inject_errors_cpp_c(lines, ERROR_PLANS_C_CPP[i])

            elif lang == "python":
                rel_path = f"test_cases/large/broken/python/{base_name}.py"
                mod_keys = list(PY_BENIGN.keys())
                selected_keys = mod_keys[(i + 1) % 3:] + mod_keys[:(i + 1) % 3]
                clean_code, used_mods = assemble_python_program(selected_keys, target_lines, seed=seed)
                lines = clean_code.splitlines()
                broken_lines, err_records = inject_errors_python(lines, ERROR_PLANS_PY[i])

            elif lang == "java":
                java_class = BROKEN_JAVA_CLASS_NAMES[i]
                rel_path = f"test_cases/large/broken/java/{java_class}.java"
                mod_keys = list(JAVA_BENIGN.keys())
                selected_keys = mod_keys[(i + 1) % 3:] + mod_keys[:(i + 1) % 3]
                clean_code, used_mods = assemble_java_program(selected_keys, target_lines, class_name=java_class, seed=seed)
                lines = clean_code.splitlines()
                broken_lines, err_records = inject_errors_java(lines, ERROR_PLANS_JAVA[i])

            broken_code = "\n".join(broken_lines) + "\n"
            full_path = ROOT / rel_path

            # Expect compilation to FAIL (expect_compile=False)
            ok, actual_lines, msg = validate_and_write(full_path, broken_code, expect_compile=False, lang=lang)
            if not ok:
                raise RuntimeError(f"Failed to generate broken file {rel_path}: {msg}")

            sha = compute_sha256(full_path)
            rec = {
                "id": file_id,
                "path": rel_path.replace("\\\\", "/"),
                "language": lang,
                "group": "broken",
                "lines": actual_lines,
                "sha256": sha,
                "seed": seed,
                "modules": used_mods,
                "errors": err_records
            }
            append_manifest_record(manifest_path, rec)
            records.append(rec)
            print(f"  [OK-BROKEN] {rel_path} ({actual_lines} lines, {len(err_records)} errors injected, sha256={sha[:8]}...)")

    return records


if __name__ == "__main__":
    manifest = ROOT / "data" / "large" / "manifest_broken.jsonl"
    if manifest.exists():
        manifest.unlink()
    recs = generate_all_broken(manifest)
    print(f"Broken generation complete: {len(recs)} files written.")
