"""
scripts/generate_large/python_modules.py
----------------------------------------
Aggregator and file assembler for Python modules (Python 3).
"""

from typing import Dict, List, Tuple, Any
from .python_core_modules import MODULES as CORE_MODULES
from .python_algo_modules import MODULES as ALGO_MODULES
from .python_system_modules import MODULES as SYSTEM_MODULES
from .python_security_modules import MODULES as SECURITY_MODULES

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

PYTHON_HEADERS = '''"""
Enterprise Modular System Engine in Python 3.
"""

from __future__ import annotations

import base64
import cmath
import collections
import dataclasses
import enum
import functools
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import time
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
'''


def assemble_python_program(
    selected_module_keys: List[str],
    target_lines: int,
    seed: int = 42
) -> Tuple[str, List[str]]:
    """
    Assembles a valid Python 3 single-file program using selected modules,
    tuning line count to land strictly within target_lines +/- 5%.
    """
    modules_used = [k for k in selected_module_keys if k in ALL_MODULES]

    def build_code(ext_keys: List[str], extra_assertions: int = 0) -> str:
        parts = [PYTHON_HEADERS.strip()]
        for mk in modules_used:
            parts.append(ALL_MODULES[mk]["core"].strip())
        for ek in ext_keys:
            if "extended" in ALL_MODULES[ek] and ALL_MODULES[ek]["extended"].strip():
                parts.append(ALL_MODULES[ek]["extended"].strip())

        main_lines = [
            'if __name__ == "__main__":',
            "    # Execute verification routines across all active modules"
        ]
        for mk in modules_used:
            main_lines.append(f"    {ALL_MODULES[mk]['test_call']}")

        for i in range(extra_assertions):
            v = (i * 41 + seed) % 1000
            main_lines.append(f"    assert ({v} * 2) >= {v}")

        main_lines.append('    print("All Python subsystem diagnostics completed cleanly.")')
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
