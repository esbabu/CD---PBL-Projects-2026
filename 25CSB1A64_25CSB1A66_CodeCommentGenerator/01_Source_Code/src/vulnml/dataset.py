"""
Labelled training data for the ML detector
============================================
Juliet (NIST SARD Juliet Test Suite 1.3 — Java, C, C++, C#)
    Every test case file holds a flawed function (``bad`` / ``*_bad``) and one or
    more fixed ones (``good*``, ``goodG2B*``, ``goodB2G*``). A function is labelled
    with the family of its test case's CWE (bad) or ``safe`` (good). Helper
    functions (``badSource``, ``goodSink`` …) take the label of their prefix.

    Label leakage is removed before training: comments (Juliet marks flaws with
    ``FLAW`` / ``FIX`` comments), and every identifier that mentions a CWE number,
    ``good`` or ``bad`` (function and class names carry the answer).

    Split: by *functional variant* (the test case name without its trailing flow
    number ``_01`` … ``_84`` and file letter), so the near-identical control-flow
    variants of one source/sink combination never land on both sides.

OWASP BenchmarkPython (Python)
    The request-handling function of every test case, labelled with the case's
    category family when it is a real vulnerability and ``safe`` otherwise. Split
    with the benchmark's own dev / held-out template families.
"""
from __future__ import annotations

import hashlib
import os
import random
import re
import zipfile
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Iterator, List, Optional, Tuple

from .families import SAFE, family_of_cwe

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
JULIET_DIR = os.path.join(ROOT, ".benchmarks", "juliet")
JULIET = {"java": ("juliet_java_v1_3.zip", (".java",)), "c": ("juliet_c_cpp_v1_3.zip", (".c",)),
          "cpp": ("juliet_c_cpp_v1_3.zip", (".cpp",)), "csharp": ("juliet_csharp_v1_3.zip", (".cs",))}
OWASP_CATEGORY_CWE = {"cmdi": 78, "codeinj": 94, "deserialization": 502, "hash": 328, "pathtraver": 22, "sqli": 89,
                      "weakrand": 330, "xss": 79, "redirect": 601, "xxe": 611, "ldapi": 90, "xpathi": 643,
                      "trustbound": 501, "securecookie": 614}


@dataclass
class Sample:
    text: str            # normalised code of one function
    label: str           # family or "safe"
    group: str           # split key
    cwe: Optional[str]
    origin: str          # file / test case


_COMMENT = {
    "java": re.compile(r"/\*.*?\*/|//[^\n]*", re.S), "c": re.compile(r"/\*.*?\*/|//[^\n]*", re.S),
    "cpp": re.compile(r"/\*.*?\*/|//[^\n]*", re.S), "csharp": re.compile(r"/\*.*?\*/|//[^\n]*", re.S),
    "python": re.compile(r"#[^\n]*|\"\"\".*?\"\"\"|'''.*?'''", re.S),
}
_LEAK = re.compile(r"(?i)\w*(cwe\d+|good|bad|g2b|b2g|flaw|fix)\w*")
_MODIFIERS = {"public", "private", "protected", "internal", "static", "final", "sealed", "override", "virtual",
              "readonly", "synchronized", "inline", "extern"}
_WRAPPER = re.compile(r"\{\s*(?:[\w.]+\s*\([^;{}]*\)\s*;\s*)*\}\s*$")
_TOKEN = re.compile(r"\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'|[A-Za-z_][A-Za-z0-9_]*|\d+(?:\.\d+)?|[^\sA-Za-z0-9_\"']{1,3}")


def normalise(code: str, lang: str) -> str:
    """Code → space-separated tokens: comments dropped, strings STR, numbers NUM, leaking names masked,
    identifiers also split into their camelCase / snake_case parts."""
    code = _COMMENT.get(lang, _COMMENT["c"]).sub(" ", code)
    out: List[str] = []
    for tok in _TOKEN.findall(code):
        if tok[:1] in "\"'":
            low = tok.lower()
            out.append("STR")
            for kw in ("select ", "insert ", "delete ", "update ", "where ", "drop ", " from ", "<script", "http:",
                       "https:", "../", "%s", "%n", "md5", "sha1", "des", "ecb", "password", "file:", "ldap", "//"):
                if kw in low:
                    out.append("STR_" + re.sub(r"\W", "", kw.strip()).upper())
            continue
        if tok[:1].isdigit():
            out.append("NUM")
            continue
        if tok[:1].isalpha() or tok[:1] == "_":
            if tok in _MODIFIERS:
                continue                  # Juliet: bad() is public, good helpers private — a label artefact
            if _LEAK.fullmatch(tok):
                out.append("ID")
                continue
            out.append(tok)
            parts = re.findall(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+|\d+", tok)
            if len(parts) > 1:
                out.extend(p.lower() for p in parts)
            continue
        out.append(tok)
    return " ".join(out)


def _group_key(path: str) -> str:
    base = os.path.splitext(os.path.basename(path))[0]
    base = re.sub(r"_\d+[a-e]?$", "", base)          # drop flow-variant number and file letter
    return base


def _label_for(fname: str, cwe_family: str) -> Optional[str]:
    low = fname.lower()
    if low.startswith("bad") or low.endswith("_bad") or "_bad" in low and "sink" in low or low.startswith("badsink"):
        return cwe_family
    if low.startswith("good") or "_good" in low:
        return SAFE
    return None


def juliet_samples(lang: str, per_cwe: int = 150, seed: int = 7) -> List[Sample]:
    """Labelled functions from Juliet for one language (at most ``per_cwe`` functional variants per CWE)."""
    zname, exts = JULIET[lang]
    path = os.path.join(JULIET_DIR, zname)
    if not os.path.isfile(path):
        raise FileNotFoundError(f"{path} is missing; download the Juliet suite into .benchmarks/juliet")
    from ..multilang.lower import lower_source, text
    zf = zipfile.ZipFile(path)
    by_cwe_group: Dict[str, Dict[str, List[str]]] = defaultdict(lambda: defaultdict(list))
    for n in zf.namelist():
        m = re.search(r"testcases/CWE(\d+)_", n)
        if not m or not n.endswith(exts) or "/support" in n.lower():
            continue
        by_cwe_group[m.group(1)][_group_key(n)].append(n)
    rng = random.Random(seed)
    out: List[Sample] = []
    for cwe, groups in sorted(by_cwe_group.items()):
        fam = family_of_cwe(cwe)
        if fam is None:
            continue
        keys = sorted(groups)
        rng.shuffle(keys)
        for g in keys[:per_cwe]:
            files = sorted(groups[g])[:3]          # a few flow variants of each functional variant
            for n in files:
                code = zf.read(n).decode("utf-8", errors="replace")
                try:
                    mod = lower_source(code, lang)
                except Exception:
                    continue
                src = code.encode("utf-8")
                for info in mod.functions.values():
                    lbl = _label_for(info.fn.name, fam)
                    if lbl is None:
                        continue
                    body = text(info.node, src)
                    brace = body.find("{")
                    if len(body) < 40 or (brace >= 0 and _WRAPPER.match(body[brace:])):
                        continue          # wrapper good() that only calls the good helpers
                    out.append(Sample(normalise(body, lang), lbl, f"CWE{cwe}:{g}", f"CWE-{cwe}", n))
    return out


def owasp_samples() -> List[Tuple[Sample, str]]:
    """(sample, split) for every OWASP BenchmarkPython test case."""
    from ..security.benchmarks import OWASP_DIR, owasp_cases, owasp_group_key, owasp_split
    out = []
    for case in owasp_cases():
        p = os.path.join(OWASP_DIR, "testcode", f"{case['test']}.py")
        if not os.path.isfile(p):
            continue
        src = open(p, encoding="utf-8").read()
        body = src.split("_post():", 1)[-1].split("@app.route", 1)[0]
        body = re.sub(r"BenchmarkTest\d+", "T", body)
        cwe = OWASP_CATEGORY_CWE.get(case["category"])
        fam = family_of_cwe(cwe) if cwe else None
        if cwe == 614:
            fam = "cleartext"           # insecure cookie (missing Secure flag) — cleartext transmission
        label = fam if case["real"] in (True, "true") and fam else SAFE
        out.append((Sample(normalise(body, "python"), label, owasp_group_key(case["test"]), f"CWE-{cwe}" if cwe else None,
                           case["test"]), owasp_split(case["test"])))
    return out


def split(samples: List[Sample], test_fraction: float = 0.2, seed: int = 11) -> Tuple[List[Sample], List[Sample]]:
    """Group-wise split: every functional variant goes wholly to train or to test."""
    train, test = [], []
    for s in samples:
        h = int(hashlib.sha1(f"{seed}:{s.group}".encode(), usedforsecurity=False).hexdigest()[:8], 16)
        (test if (h % 1000) / 1000 < test_fraction else train).append(s)
    return train, test
