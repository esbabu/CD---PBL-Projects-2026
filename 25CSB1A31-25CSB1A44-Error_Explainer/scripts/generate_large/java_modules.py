"""
scripts/generate_large/java_modules.py
--------------------------------------
Aggregator and file assembler for Java modules.
"""

from typing import Dict, List, Tuple, Any
from .java_core_modules import MODULES as CORE_MODULES
from .java_algo_modules import MODULES as ALGO_MODULES
from .java_system_modules import MODULES as SYSTEM_MODULES
from .java_security_modules import MODULES as SECURITY_MODULES

BENIGN_MODULES: Dict[str, Dict[str, Any]] = {
    **CORE_MODULES,
    **ALGO_MODULES,
    **SYSTEM_MODULES
}

HARD_NEGATIVE_MODULES: Dict[str, Dict[str, Any]] = SECURITY_MODULES

ALL_MODULES: Dict[str, Dict[str, Any]] = {
    **BENIGN_MODULES,
    **HARD_NEGATIVE_MODULES
}

JAVA_IMPORTS = """import java.util.*;
import java.io.*;
import java.time.*;
import java.math.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
"""


def assemble_java_program(
    selected_module_keys: List[str],
    target_lines: int,
    class_name: str = "EnterpriseApp",
    seed: int = 42
) -> Tuple[str, List[str]]:
    """
    Assembles a valid single-file Java program with public class class_name
    and static nested classes for each module.
    """
    modules_used = [k for k in selected_module_keys if k in ALL_MODULES]

    def build_code(ext_keys: List[str], extra_assertions: int = 0) -> str:
        parts = [JAVA_IMPORTS.strip()]
        class_open = f"public class {class_name} {{"
        parts.append(class_open)

        for mk in modules_used:
            parts.append(ALL_MODULES[mk]["core"].rstrip())
        for ek in ext_keys:
            if "extended" in ALL_MODULES[ek] and ALL_MODULES[ek]["extended"].strip():
                parts.append(ALL_MODULES[ek]["extended"].rstrip())

        main_lines = [
            "    public static void main(String[] args) {",
            "        // Execute verification routines across all active modules"
        ]
        for mk in modules_used:
            main_lines.append(f"        {ALL_MODULES[mk]['test_call']}")

        for i in range(extra_assertions):
            v = (i * 43 + seed) % 1000
            main_lines.append(f"        assert ({v} * 2 >= {v});")

        main_lines.append('        System.out.println("All Java subsystem diagnostics completed cleanly.");')
        main_lines.append("    }")
        main_lines.append("}")
        parts.append("\n".join(main_lines))
        return "\n\n".join(parts) + "\n"

    ext_keys = []
    for k in modules_used:
        candidate = build_code(ext_keys + [k])
        lines = candidate.count("\n")
        if lines <= target_lines:
            ext_keys.append(k)
        if lines >= target_lines:
            break

    current_code = build_code(ext_keys)
    current_lines = current_code.count("\n")

    diff = target_lines - current_lines
    if diff > 0:
        current_code = build_code(ext_keys, extra_assertions=diff)

    return current_code, modules_used
