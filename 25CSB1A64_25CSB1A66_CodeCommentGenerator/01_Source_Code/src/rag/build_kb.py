"""
Build the security knowledge base
==================================
    python -m src.rag.build_kb            # needs .benchmarks/mitre and .benchmarks/juliet (benchmarks/fetch.py)

Sources (all read locally, every entry keeps its attribution):

* MITRE CWE 5.0 (``cwec_v5.0.xml``) — every weakness that is not deprecated:
  description, extended description, likelihood of exploit, consequences,
  applicable languages, detection methods, mitigations, demonstrative examples
  (vulnerable and fixed code where MITRE marks them Bad / Good), observed CVE
  examples (linked to NVD / cve.org), related weaknesses and attack patterns,
  taxonomy mappings (OWASP Top Ten, CERT, …) and references.
* MITRE CAPEC 3.9 (``capec_latest.xml``) — every attack pattern that is not
  deprecated or obsolete: description, likelihood, typical severity,
  prerequisites, execution flow, mitigations, example instances, related CWEs.
* NIST SARD Juliet Test Suite 1.3 (Java, C/C++, C#) — for each CWE it covers, a
  vulnerable (``bad``) and a fixed (``good``) function from the first test case,
  added to that CWE's examples.

Each CWE entry also records whether this project *detects* it (``detection``:
the rules and languages from ``security.coverage``), so documented and
implemented coverage stay distinguishable.

Output: ``src/rag/data/security_kb.json.gz``.
"""
from __future__ import annotations

import glob
import gzip
import json
import os
import re
import sys
import textwrap
import xml.etree.ElementTree as ET
import zipfile
from collections import defaultdict
from typing import Dict, List, Optional

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA = os.path.join(ROOT, ".benchmarks")
OUT = os.path.join(os.path.dirname(__file__), "data", "security_kb.json.gz")
MAX_CODE = 3500


def _kids(el) -> list:
    return list(el) if el is not None else []


def _txt(el) -> str:
    if el is None:
        return ""
    return re.sub(r"[ \t]+", " ", re.sub(r"\n\s*\n+", "\n", "".join(el.itertext()))).strip()


def _code(el) -> str:
    """Example code as written (XHTML <div style="margin-left"> blocks become indentation)."""
    lines: List[str] = []

    def walk(e, depth):
        tag = e.tag.split("}")[-1]
        indent = depth + (1 if tag == "div" and "margin-left" in (e.get("style") or "") else 0)
        if e.text and e.text.strip():
            lines.append("    " * indent + e.text.strip())
        for c in e:
            walk(c, indent)
            if c.tail and c.tail.strip():
                lines.append("    " * indent + c.tail.strip())
    walk(el, 0)
    return "\n".join(lines)[:MAX_CODE]


def parse_cwe(path: str) -> Dict[str, dict]:
    root = ET.parse(path).getroot()
    ns = root.tag.split("}")[0] + "}"
    version = root.get("Version", "")
    refs = {}
    for r in _kids(root.find(ns + "External_References")):
        title = _txt(r.find(ns + "Title"))
        url = _txt(r.find(ns + "URL"))
        refs[r.get("Reference_ID")] = {"title": title, "url": url}
    out: Dict[str, dict] = {}
    for w in root.find(ns + "Weaknesses"):
        if w.get("Status") in ("Deprecated", "Obsolete"):
            continue
        wid = f"CWE-{w.get('ID')}"
        desc = _txt(w.find(ns + "Description"))
        if len(desc) < 30:
            continue
        e = {"id": wid, "kind": "weakness", "name": w.get("Name"), "abstraction": w.get("Abstraction"),
             "status": w.get("Status"), "source": f"MITRE CWE {version}",
             "url": f"https://cwe.mitre.org/data/definitions/{w.get('ID')}.html",
             "description": desc, "extended_description": _txt(w.find(ns + "Extended_Description"))[:2500],
             "likelihood_of_exploit": _txt(w.find(ns + "Likelihood_Of_Exploit")) or None}
        e["languages"] = []
        ap = w.find(ns + "Applicable_Platforms")
        for lang in (ap.findall(ns + "Language") if ap is not None else []):
            e["languages"].append(lang.get("Name") or lang.get("Class"))
        e["consequences"] = [{"scope": [_txt(s) for s in c.findall(ns + "Scope")],
                              "impact": [_txt(i) for i in c.findall(ns + "Impact")]}
                             for c in _kids(w.find(ns + "Common_Consequences"))]
        e["detection_methods"] = [{"method": _txt(d.find(ns + "Method")),
                                   "description": _txt(d.find(ns + "Description"))[:800],
                                   "effectiveness": _txt(d.find(ns + "Effectiveness")) or None}
                                  for d in _kids(w.find(ns + "Detection_Methods"))]
        e["mitigations"] = [{"phase": [_txt(p) for p in m.findall(ns + "Phase")],
                             "strategy": _txt(m.find(ns + "Strategy")) or None,
                             "description": _txt(m.find(ns + "Description"))[:1200]}
                            for m in _kids(w.find(ns + "Potential_Mitigations"))]
        exs = []
        for d in _kids(w.find(ns + "Demonstrative_Examples")):
            intro = _txt(d.find(ns + "Intro_Text"))[:600]
            for code in d.findall(ns + "Example_Code"):
                nature = (code.get("Nature") or "").lower()
                if nature not in ("bad", "good"):
                    continue
                body = _code(code)
                if len(body) < 10:
                    continue
                exs.append({"nature": nature, "language": code.get("Language") or "", "code": body,
                            "intro": intro, "source": f"MITRE CWE {version} demonstrative example"})
        e["examples"] = exs[:8]
        e["observed_examples"] = [{"cve": _txt(o.find(ns + "Reference")), "description": _txt(o.find(ns + "Description"))[:300],
                                   "link": _txt(o.find(ns + "Link"))}
                                  for o in _kids(w.find(ns + "Observed_Examples"))][:8]
        e["related_weaknesses"] = sorted({f"CWE-{r.get('CWE_ID')}" for r in _kids(w.find(ns + "Related_Weaknesses"))})
        e["related_attack_patterns"] = [f"CAPEC-{r.get('CAPEC_ID')}" for r in _kids(w.find(ns + "Related_Attack_Patterns"))]
        e["taxonomy"] = [{"name": t.get("Taxonomy_Name"), "entry_id": _txt(t.find(ns + "Entry_ID")) or None,
                          "entry_name": _txt(t.find(ns + "Entry_Name")) or None}
                         for t in _kids(w.find(ns + "Taxonomy_Mappings"))]
        e["references"] = [refs.get(r.get("External_Reference_ID"), {"title": r.get("External_Reference_ID"), "url": ""})
                           for r in _kids(w.find(ns + "References"))][:8]
        out[wid] = e
    return out


def parse_capec(path: str) -> Dict[str, dict]:
    root = ET.parse(path).getroot()
    ns = root.tag.split("}")[0] + "}"
    version = root.get("Version", "")
    out: Dict[str, dict] = {}
    for a in root.find(ns + "Attack_Patterns"):
        if a.get("Status") in ("Deprecated", "Obsolete"):
            continue
        aid = f"CAPEC-{a.get('ID')}"
        desc = _txt(a.find(ns + "Description"))
        if len(desc) < 30:
            continue
        flow = []
        ef = a.find(ns + "Execution_Flow")
        for st in (ef if ef is not None else []):
            flow.append(f"{_txt(st.find(ns + 'Phase'))}: {_txt(st.find(ns + 'Description'))}"[:400])
        out[aid] = {
            "id": aid, "kind": "attack-pattern", "name": a.get("Name"), "abstraction": a.get("Abstraction"),
            "status": a.get("Status"), "source": f"MITRE CAPEC {version}",
            "url": f"https://capec.mitre.org/data/definitions/{a.get('ID')}.html",
            "description": desc, "likelihood_of_attack": _txt(a.find(ns + "Likelihood_Of_Attack")) or None,
            "severity": (_txt(a.find(ns + "Typical_Severity")) or None),
            "severity_source": "CAPEC Typical_Severity" if _txt(a.find(ns + "Typical_Severity")) else None,
            "prerequisites": [_txt(p)[:400] for p in _kids(a.find(ns + "Prerequisites"))],
            "execution_flow": flow[:10],
            "mitigations": [{"description": _txt(m)[:800]} for m in _kids(a.find(ns + "Mitigations"))],
            "examples": [{"nature": "instance", "language": "", "code": "", "intro": _txt(x)[:700],
                          "source": f"MITRE CAPEC {version} example instance"} for x in _kids(a.find(ns + "Example_Instances"))][:4],
            "related_weaknesses": [f"CWE-{r.get('CWE_ID')}" for r in _kids(a.find(ns + "Related_Weaknesses"))],
            "languages": [],
        }
    return out


# ---------------------------------------------------------------------------
# Juliet examples
# ---------------------------------------------------------------------------
JULIET = {
    "java": ("juliet_java_v1_3.zip", "NIST SARD Juliet Test Suite for Java v1.3", (".java",), "Java"),
    "c": ("juliet_c_cpp_v1_3.zip", "NIST SARD Juliet Test Suite for C/C++ v1.3", (".c",), "C"),
    "cpp": ("juliet_c_cpp_v1_3.zip", "NIST SARD Juliet Test Suite for C/C++ v1.3", (".cpp",), "C++"),
    "csharp": ("juliet_csharp_v1_3.zip", "NIST SARD Juliet Test Suite for C# v1.3", (".cs",), "C#"),
}


def juliet_functions(code: str, lang: str):
    """(name, text) of every function / method in a Juliet file."""
    from ..multilang.lower import lower_source, text
    mod = lower_source(code, lang)
    src = code.encode("utf-8")
    for info in mod.functions.values():
        yield info.fn.name, text(info.node, src)


def juliet_examples(lang: str) -> Dict[str, List[dict]]:
    zname, label, exts, display = JULIET[lang]
    path = os.path.join(DATA, "juliet", zname)
    if not os.path.isfile(path):
        return {}
    zf = zipfile.ZipFile(path)
    first: Dict[str, str] = {}
    for n in sorted(zf.namelist()):
        m = re.search(r"testcases/CWE(\d+)_[^/]+/(?:s\d+/)?(CWE\d+_[^/]+_01)\w*\.(\w+)$", n)
        if m and n.endswith(exts) and f"CWE-{m.group(1)}" not in first:
            first[f"CWE-{m.group(1)}"] = n
    out: Dict[str, List[dict]] = {}
    for cwe, n in first.items():
        code = zf.read(n).decode("utf-8", errors="replace")
        bad = good = None
        for name, body in juliet_functions(code, lang):
            low = name.lower()
            if bad is None and (low == "bad" or low.endswith("_bad")):
                bad = body
            elif good is None and (low.startswith("goodg2b") or low == "good1" or low.endswith("good1")):
                good = body
        if bad:
            ex = [{"nature": "bad", "language": display, "code": textwrap.dedent(bad)[:MAX_CODE],
                   "intro": f"Juliet test case {os.path.basename(n)} — flawed function.", "source": label}]
            if good:
                ex.append({"nature": "good", "language": display, "code": textwrap.dedent(good)[:MAX_CODE],
                           "intro": f"Juliet test case {os.path.basename(n)} — fixed variant.", "source": label})
            out[cwe] = ex
    return out


def build() -> dict:
    from ..security.coverage import cwe_coverage
    cwe_path = sorted(glob.glob(os.path.join(DATA, "mitre", "cwec_v*.xml")))
    if not cwe_path:
        raise SystemExit("CWE XML missing: download https://cwe.mitre.org/data/xml/cwec_latest.xml.zip "
                         "into .benchmarks/mitre and unzip it")
    cwe = parse_cwe(cwe_path[-1])
    capec = parse_capec(os.path.join(DATA, "mitre", "capec_latest.xml"))
    cov = cwe_coverage()
    juliet_added = defaultdict(int)
    for lang in JULIET:
        for cid, exs in juliet_examples(lang).items():
            if cid in cwe:
                cwe[cid]["examples"].extend(exs)
                juliet_added[lang] += 1
    for cid, e in cwe.items():
        c = cov.get(cid)
        e["detection"] = {"implemented": bool(c), "rules": c["rules"] if c else [],
                          "languages": c["languages"] if c else []}
        if c and not e.get("severity"):
            from ..security.rules import RULES
            sev = sorted({RULES[r].severity for r in c["rules"]})
            e["severity"] = sev[-1] if len(sev) == 1 else "/".join(sev)
            e["severity_source"] = "this project's rule severity"
        e.setdefault("severity", None)
        e.setdefault("severity_source", None)
    entries = list(cwe.values()) + list(capec.values())
    # integrity: unique ids, no duplicate descriptions
    ids = [e["id"] for e in entries]
    assert len(ids) == len(set(ids)), "duplicate ids"
    meta = {"generated_from": {"cwe": os.path.basename(cwe_path[-1]), "capec": "capec_latest.xml",
                               "juliet": {k: JULIET[k][1] for k in JULIET}},
            "counts": {"weaknesses": len(cwe), "attack_patterns": len(capec), "total": len(entries),
                       "with_code_examples": sum(1 for e in entries if any(x.get("code") for x in e.get("examples", []))),
                       "juliet_examples_added": dict(juliet_added),
                       "detected_by_this_project": sum(1 for e in cwe.values() if e["detection"]["implemented"])},
            "license": "CWE and CAPEC content © MITRE, used under the CWE/CAPEC Terms of Use; Juliet test suites are "
                       "public domain software from NIST SARD."}
    return {"meta": meta, "entries": entries}


def main() -> int:
    kb = build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with gzip.open(OUT, "wt", encoding="utf-8") as fh:
        json.dump(kb, fh, ensure_ascii=False)
    print(json.dumps(kb["meta"]["counts"], indent=1))
    print(f"written {OUT} ({os.path.getsize(OUT) // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
