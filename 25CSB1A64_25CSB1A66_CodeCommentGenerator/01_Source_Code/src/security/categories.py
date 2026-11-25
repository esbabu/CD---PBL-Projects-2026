"""
Vulnerability classes for the dashboard (9 classes)
=====================================================
The eight original classes are the OWASP BenchmarkPython categories the analyzer
was first evaluated on; every other rule falls into a ninth class, **Others**.
Each finding keeps its detailed rule id, title, family (``RuleMeta.category``)
and CWE — the class is only the top-level grouping used by charts and tables.
"""
from __future__ import annotations

from collections import OrderedDict
from typing import Dict, Iterable

# key → (label, rule ids)
CLASSES: "OrderedDict[str, tuple]" = OrderedDict([
    ("cmdi", ("Command Injection", ("SEC002",))),
    ("codeinj", ("Code Injection", ("SEC001", "SEC015"))),
    ("deserialization", ("Insecure Deserialization", ("SEC009", "SEC010"))),
    ("hash", ("Weak Hashing", ("SEC004",))),
    ("pathtraver", ("Path Traversal", ("SEC013", "SEC042"))),
    ("sqli", ("SQL Injection", ("SEC005",))),
    ("weakrand", ("Weak Randomness", ("SEC011",))),
    ("xss", ("Cross-Site Scripting", ("SEC014", "SEC043"))),
    ("others", ("Others", ())),
])
ORIGINAL_EIGHT = tuple(k for k in CLASSES if k != "others")
_RULE_CLASS: Dict[str, str] = {r: k for k, (_, rules) in CLASSES.items() for r in rules}


def class_of(rule_id: str) -> str:
    """Dashboard class key of a rule (``"others"`` for everything outside the original eight)."""
    return _RULE_CLASS.get(rule_id, "others")


def class_label(key: str) -> str:
    return CLASSES[key][0]


def count_by_class(rule_ids: Iterable[str]) -> "OrderedDict[str, int]":
    """Counts for all nine classes, in display order (zeros included)."""
    out = OrderedDict((k, 0) for k in CLASSES)
    for r in rule_ids:
        out[class_of(r)] += 1
    return out
