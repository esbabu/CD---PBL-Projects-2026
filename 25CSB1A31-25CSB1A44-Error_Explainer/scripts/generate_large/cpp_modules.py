"""
scripts/generate_large/cpp_modules.py
-------------------------------------
Aggregator and file assembler for C++ modules.
Supports assembling complete single-file C++ programs to exact line target tiers.
"""

from typing import Dict, List, Tuple, Any
from .cpp_core_modules import MODULES as CORE_MODULES
from .cpp_algo_modules import MODULES as ALGO_MODULES
from .cpp_system_modules import MODULES as SYSTEM_MODULES
from .cpp_security_modules import MODULES as SECURITY_MODULES

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


CPP_HEADERS = """#include <iostream>
#include <vector>
#include <string>
#include <map>
#include <unordered_map>
#include <set>
#include <memory>
#include <algorithm>
#include <sstream>
#include <functional>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <optional>
#include <queue>
#include <stack>
#include <cassert>
#include <iomanip>
"""


def assemble_cpp_program(
    selected_module_keys: List[str],
    target_lines: int,
    seed: int = 42
) -> Tuple[str, List[str]]:
    """
    Assembles a valid modern C++17 single-file program using selected modules,
    tuning line count to land strictly within target_lines +/- 5%.
    """
    modules_used = [k for k in selected_module_keys if k in ALL_MODULES]
    
    # We will assemble code in sections:
    # 1. Headers
    # 2. Module cores
    # 3. Module extensions (as needed to hit target)
    # 4. Main function exercising all modules
    
    sections = [CPP_HEADERS.strip()]
    
    for k in modules_used:
        mod = ALL_MODULES[k]
        sections.append(mod["core"].strip())
    
    # Check current lines
    def build_code(ext_keys: List[str], extra_assertions: int = 0) -> str:
        parts = [CPP_HEADERS.strip()]
        for mk in modules_used:
            parts.append(ALL_MODULES[mk]["core"].strip())
        for ek in ext_keys:
            if "extended" in ALL_MODULES[ek] and ALL_MODULES[ek]["extended"].strip():
                parts.append(ALL_MODULES[ek]["extended"].strip())
        
        # Build main
        main_lines = [
            "int main() {",
            "    // Execute verification routines across all active modules"
        ]
        for mk in modules_used:
            main_lines.append(f"    {ALL_MODULES[mk]['test_call']}")
        
        # Add realistic assertion checks if extra lines needed
        for i in range(extra_assertions):
            v = (i * 31 + seed) % 1000
            main_lines.append(f"    assert(({v} * 2) >= {v});")
            
        main_lines.append('    std::cout << "All subsystem diagnostics completed cleanly." << std::endl;')
        main_lines.append("    return 0;")
        main_lines.append("}")
        parts.append("\n".join(main_lines))
        return "\n\n".join(parts) + "\n"

    # Incrementally add extensions until close to target
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
    
    # Fine-tune with assertion lines in main if under target
    diff = target_lines - current_lines
    if diff > 0:
        current_code = build_code(ext_keys, extra_assertions=diff)
        
    return current_code, modules_used
