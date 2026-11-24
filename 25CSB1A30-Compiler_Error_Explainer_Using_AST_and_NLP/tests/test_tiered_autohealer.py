"""
tests/test_tiered_autohealer.py
───────────────────────────────
Unit tests for tiered auto-healer (Safety Tiers S0, S1, S2) and candidate generation.
"""

import os
import sys

_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR = os.path.dirname(_TESTS_DIR)
_SRC_DIR = os.path.join(_ROOT_DIR, "src")
for _p in (_ROOT_DIR, _SRC_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pytest
from auto_healer import (
    SafetyTier,
    get_safety_tier,
    get_tier_info,
    attempt_fix_tiered,
    generate_candidate_repairs,
    attempt_fix,
)


def test_safety_tier_metadata():
    assert SafetyTier.TIER_1_COMPILER == 1
    assert SafetyTier.TIER_2_AST == 2
    assert SafetyTier.TIER_3_HEURISTIC == 3

    info1 = get_tier_info("missing_include")
    assert info1["tier"] in (1, 2, 3)
    assert "tier_name" in info1

    info2 = get_tier_info("buffer_overflow")
    assert info2["tier"] == 3


def test_attempt_fix_tiered_semicolon():
    source = "int main() {\n    int a = 5\n    return 0;\n}"
    err = {
        "line": 3,
        "column": 5,
        "category": "syntax_error",
        "message": "expected ';' before 'return'",
    }

    cand = attempt_fix_tiered(source, err)
    assert cand is not None
    assert "patched_source" in cand
    assert ";" in cand["patched_source"]
    assert cand.get("safety_level") in ("S0", "S1", "S2")
    assert "tier_name" in cand


def test_attempt_fix_tiered_missing_include():
    source = "int main() {\n    std::cout << 42 << std::endl;\n    return 0;\n}"
    err = {
        "line": 2,
        "column": 5,
        "category": "missing_include",
        "message": "'cout' is not a member of 'std'",
    }

    cand = attempt_fix_tiered(source, err)
    assert cand is not None
    assert "#include <iostream>" in cand["patched_source"]
    assert cand.get("safety_level") == "S0"


def test_attempt_fix_tiered_security_memory_leak():
    source = "int main() {\n    int* p = (int*)malloc(sizeof(int));\n    return 0;\n}"
    err = {
        "line": 2,
        "column": 5,
        "category": "memory_leak",
        "message": "potential memory leak: malloc without free",
    }

    cand = attempt_fix_tiered(source, err)
    assert cand is not None
    assert "free(p)" in cand["patched_source"] or "delete" in cand["patched_source"]
    assert cand.get("safety_level") == "S2"


def test_generate_candidate_repairs():
    source = "int main() {\n    int x = 10\n    return 0;\n}"
    err = {
        "line": 3,
        "column": 5,
        "category": "syntax_error",
        "message": "expected ';'",
    }

    cands = generate_candidate_repairs(source, err)
    assert isinstance(cands, list)
    assert len(cands) >= 1
    assert all("patched_source" in c and "safety_level" in c for c in cands)
