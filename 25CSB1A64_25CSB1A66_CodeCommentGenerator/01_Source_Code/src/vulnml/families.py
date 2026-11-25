"""
Vulnerability families
=======================
The ML detector predicts a *family* (a group of closely related CWEs), not one
of ~110 individual Juliet CWEs: families have enough examples each to learn
from, and each maps to the project's rules and dashboard classes.
"""
from __future__ import annotations

from typing import Dict, Optional, Tuple

# family → (label, CWE numbers, rules that detect it, representative CWE)
FAMILIES: Dict[str, Tuple[str, Tuple[int, ...], Tuple[str, ...], str]] = {
    "command-injection": ("OS command injection", (77, 78, 88), ("SEC002",), "CWE-78"),
    "sql-injection": ("SQL injection", (89, 564), ("SEC005",), "CWE-89"),
    "code-injection": ("Code / expression injection", (94, 95, 917, 1336), ("SEC001", "SEC015"), "CWE-94"),
    "ldap-injection": ("LDAP injection", (90,), ("SEC019",), "CWE-90"),
    "xpath-injection": ("XPath injection", (643,), ("SEC020",), "CWE-643"),
    "xss": ("Cross-site scripting", (79, 80, 81, 83), ("SEC014", "SEC043"), "CWE-79"),
    "path-traversal": ("Path traversal", (22, 23, 36), ("SEC013", "SEC042"), "CWE-22"),
    "deserialization": ("Insecure deserialization", (502,), ("SEC009", "SEC010"), "CWE-502"),
    "xxe": ("XML external entities", (611, 776), ("SEC018",), "CWE-611"),
    "weak-crypto": ("Weak cryptography", (325, 326, 327, 328, 329, 759, 760, 780, 916), ("SEC004", "SEC033", "SEC034",
                                                                                         "SEC035", "SEC036"), "CWE-327"),
    "weak-randomness": ("Weak randomness", (330, 335, 336, 338), ("SEC011",), "CWE-338"),
    "hardcoded-credentials": ("Hard-coded credentials", (259, 321, 798), ("SEC003",), "CWE-798"),
    "cleartext": ("Cleartext transmission / storage", (311, 312, 313, 314, 315, 319, 523, 549), ("SEC040", "SEC041"),
                  "CWE-319"),
    "buffer-overflow": ("Buffer overflow / out-of-bounds access", (119, 120, 121, 122, 123, 124, 126, 127, 131, 170,
                                                                   242, 464, 787, 788, 805, 806), ("SEC051", "SEC052",
                                                                                                   "SEC053"), "CWE-787"),
    "index-validation": ("Improper array index validation", (129,), ("SEC054",), "CWE-129"),
    "integer-overflow": ("Integer overflow / numeric errors", (190, 191, 194, 195, 196, 197, 369, 680, 681),
                         ("SEC055",), "CWE-190"),
    "memory-management": ("Memory management (use after free, double free, bad free, leaks)",
                          (401, 404, 415, 416, 590, 761, 762, 763, 772, 775), ("SEC056", "SEC057"), "CWE-416"),
    "null-dereference": ("NULL pointer dereference", (476, 690), ("SEC058",), "CWE-476"),
    "format-string": ("Format string", (134,), ("SEC026",), "CWE-134"),
    "race-condition": ("Race condition / TOCTOU", (362, 364, 366, 367, 479, 567, 609, 663, 765, 832, 833),
                       ("SEC059", "SEC063"), "CWE-367"),
    "resource-exhaustion": ("Uncontrolled resource consumption", (400, 674, 770, 789, 834, 835), (), "CWE-400"),
    "header-injection": ("HTTP header / response splitting", (113, 644), ("SEC023",), "CWE-113"),
    "log-injection": ("Log injection", (117,), ("SEC022",), "CWE-117"),
    "open-redirect": ("Open redirect", (601,), ("SEC017",), "CWE-601"),
    "ssrf": ("Server-side request forgery", (918,), ("SEC016",), "CWE-918"),
    "authorization": ("Missing / incorrect authorization or authentication", (284, 285, 306, 307, 352, 425, 566, 620,
                                                                              639, 862, 863), ("SEC045", "SEC061"),
                      "CWE-862"),
    "information-exposure": ("Information exposure", (200, 209, 214, 215, 226, 244, 497, 526, 532, 534, 535, 539,
                                                      598, 615), ("SEC050",), "CWE-200"),
    "error-handling": ("Error handling", (248, 252, 253, 390, 391, 396, 397, 459, 460, 600, 617, 703),
                       ("SEC006", "SEC049"), "CWE-703"),
    "trust-boundary": ("Trust boundary / mass assignment / reflection", (470, 501, 915), ("SEC025", "SEC027", "SEC028"),
                       "CWE-501"),
    "input-validation": ("Improper input validation", (15, 20, 114, 426, 427, 606, 1284), ("SEC062",), "CWE-20"),
}
SAFE = "safe"
_BY_CWE: Dict[int, str] = {c: fam for fam, (_, cwes, _, _) in FAMILIES.items() for c in cwes}
_BY_RULE: Dict[str, str] = {r: fam for fam, (_, _, rules, _) in FAMILIES.items() for r in rules}


def family_of_cwe(cwe) -> Optional[str]:
    try:
        n = int(str(cwe).replace("CWE-", "").replace("CWE", ""))
    except ValueError:
        return None
    return _BY_CWE.get(n)


def family_of_rule(rule_id: str) -> Optional[str]:
    return _BY_RULE.get(rule_id)


def family_label(fam: str) -> str:
    return FAMILIES[fam][0] if fam in FAMILIES else fam


def family_cwe(fam: str) -> Optional[str]:
    return FAMILIES[fam][3] if fam in FAMILIES else None
