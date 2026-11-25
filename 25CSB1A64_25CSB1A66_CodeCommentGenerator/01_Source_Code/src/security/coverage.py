"""
Detection coverage: which rule is implemented for which language
=================================================================
Separates *documented* weaknesses (the knowledge base describes 950+ CWEs)
from *implemented* detection (a rule that runs on code of that language).

Every (rule, language) pair listed here is exercised by a test in
``tests/test_multilang_coverage.py`` or the language fixtures — nothing is
listed only because it is described somewhere.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Set

from .rules import RULES

LANGUAGES = ("python", "java", "csharp", "c", "cpp", "rust", "cobol")

# rules implemented by syntax / flow checks (src/multilang/patterns.py, memory.py, cobol.py)
_PATTERN_RULES: Dict[str, Set[str]] = {
    "java": {"SEC003", "SEC004", "SEC009", "SEC011", "SEC018", "SEC032", "SEC033", "SEC034", "SEC035", "SEC036",
             "SEC044", "SEC045", "SEC046", "SEC047", "SEC049", "SEC050", "SEC059", "SEC061", "SEC063"},
    "csharp": {"SEC003", "SEC004", "SEC009", "SEC011", "SEC018", "SEC029", "SEC031", "SEC032", "SEC033", "SEC034",
               "SEC035", "SEC036", "SEC044", "SEC045", "SEC046", "SEC047", "SEC049", "SEC050", "SEC059", "SEC060",
               "SEC061", "SEC063"},
    "c": {"SEC003", "SEC004", "SEC011", "SEC018", "SEC026", "SEC030", "SEC031", "SEC032", "SEC033", "SEC034",
          "SEC035", "SEC037", "SEC050", "SEC051", "SEC052", "SEC056", "SEC057", "SEC058", "SEC059"},
    "cpp": {"SEC003", "SEC004", "SEC011", "SEC018", "SEC026", "SEC030", "SEC031", "SEC032", "SEC033", "SEC034",
            "SEC035", "SEC037", "SEC049", "SEC050", "SEC051", "SEC052", "SEC056", "SEC057", "SEC058", "SEC059"},
    "rust": {"SEC003", "SEC004", "SEC030", "SEC033", "SEC034", "SEC035", "SEC046", "SEC047", "SEC050", "SEC059",
             "SEC060", "SEC063"},
    "cobol": {"SEC003", "SEC050"},
}


def rule_languages() -> Dict[str, List[str]]:
    """rule id → languages it is implemented for."""
    from ..multilang.specs import SPECS
    out: Dict[str, Set[str]] = defaultdict(set)
    for rid, r in RULES.items():
        if int(rid[3:]) <= 50:
            out[rid].add("python")
    for lang, spec in SPECS.items():
        for sink in spec.sinks:
            out[sink.rule_id].add(lang)
        if spec.sources and lang in ("c", "cpp"):
            out["SEC054"].add(lang)          # array index sink is built into the C/C++ taint transfer
    for lang, rules in _PATTERN_RULES.items():
        for rid in rules:
            out[rid].add(lang)
    return {rid: [l for l in LANGUAGES if l in langs] for rid, langs in sorted(out.items())}


def cwe_coverage() -> Dict[str, Dict[str, List[str]]]:
    """CWE id → {"rules": [...], "languages": [...]} for every CWE some rule detects."""
    langs = rule_languages()
    out: Dict[str, Dict[str, Set[str]]] = defaultdict(lambda: {"rules": set(), "languages": set()})
    for rid, r in RULES.items():
        if r.cwe:
            out[r.cwe]["rules"].add(rid)
            out[r.cwe]["languages"].update(langs.get(rid, []))
    return {cwe: {"rules": sorted(v["rules"]), "languages": [l for l in LANGUAGES if l in v["languages"]]}
            for cwe, v in sorted(out.items())}


def matrix() -> List[dict]:
    """One row per rule: id, title, CWE, 9-class bucket and a yes/no per language (for docs and the GUI)."""
    from .categories import class_label, class_of
    langs = rule_languages()
    rows = []
    for rid, r in sorted(RULES.items()):
        rows.append({"rule": rid, "title": r.title, "cwe": r.cwe or "", "class": class_label(class_of(rid)),
                     **{l: l in langs.get(rid, []) for l in LANGUAGES}})
    return rows
