"""
Security dataset builder
=========================
    python -m src.dataset.build [--version v1] [--juliet-per-cwe 100] [--variants 3]

Builds ``datasets/security_dataset/<version>/`` for Python, Java, C#, C, C++, Rust and COBOL.

Sources
-------
public
  * NIST SARD Juliet Test Suite 1.3 (Java, C, C++, C#): ``bad`` functions (vulnerable, labelled with
    the test case's CWE; flaw lines taken from Juliet's own ``FLAW`` comments) and ``good*`` functions
    (safe). Read from ``.benchmarks/juliet``.
  * OWASP BenchmarkPython: the request handler of every test case, labelled real / false with its CWE.
custom (hand-labelled; the expected rule and line are written next to the code, never taken from
the analyzer)
  * function templates cut from the language fixtures (``tests/multilang_fixtures``), each with its
    ``expect:`` markers, and their safe twins;
  * Python vulnerable / safe snippet pairs (``tests/large_corpus/snippets.py``);
  * COBOL paragraph templates (``src/dataset/cobol_templates.py``);
  * one-vulnerability programs per (language, rule) from ``tests/test_multilang_coverage.py``;
  * **long programs** of 1,000-2,000 lines per language, composed from the templates of one split
    plus ordinary code (``src/dataset/fillers.py``), with every planted vulnerability's line recorded.

Splits (70 / 15 / 15) are assigned per *group*, never per sample: a Juliet functional variant, an
OWASP template family, or a custom template together with its safe twin and all its renamed
variants. Long programs of a split use only that split's templates. So no sample in test shares a
template, source/sink pair or derived variant with a training sample.

Validation of custom samples: every file must parse without syntax errors, every vulnerable sample
must carry at least one location label, and every safe sample none. Failures are excluded and listed
in the manifest.
"""
from __future__ import annotations

import argparse
import ast
import gzip
import hashlib
import json
import os
import random
import re
import sys
import textwrap
import time
import zipfile
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional, Tuple

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_ROOT = os.path.join(ROOT, "datasets", "security_dataset")
EXT = {"java": ".java", "csharp": ".cs", "c": ".c", "cpp": ".cpp", "rust": ".rs", "cobol": ".cbl", "python": ".py"}
LANGS = ("python", "java", "csharp", "c", "cpp", "rust", "cobol")
SPLITS = ("train", "val", "test")
_MARK = re.compile(r"\s*(?://|/\*|#|\*>)?\s*expect:\s*((?:SEC\d+[ ,]*)+)\s*(?:\*/)?\s*$")
_BANG = re.compile(r"\s*#!\s*$")


# ---------------------------------------------------------------------------
# split assignment
# ---------------------------------------------------------------------------

def _h(text: str, seed: str) -> float:
    return int(hashlib.sha1(f"{seed}:{text}".encode(), usedforsecurity=False).hexdigest()[:8], 16) / 0xFFFFFFFF


def hash_split(group: str, seed: str = "v1") -> str:
    x = _h(group, seed)
    return "train" if x < 0.70 else ("val" if x < 0.85 else "test")


def ranked_splits(groups: List[str], seed: str = "v1") -> Dict[str, str]:
    """Deterministic 70/15/15 by rank (small group sets: every split gets at least one group when n >= 3)."""
    order = sorted(set(groups), key=lambda g: _h(g, seed))
    n = len(order)
    n_test = max(1, round(n * 0.15)) if n >= 3 else 0
    n_val = max(1, round(n * 0.15)) if n >= 3 else 0
    out = {}
    for i, g in enumerate(order):
        out[g] = "test" if i < n_test else ("val" if i < n_test + n_val else "train")
    return out


# ---------------------------------------------------------------------------
# custom templates
# ---------------------------------------------------------------------------

@dataclass
class Template:
    id: str
    language: str
    group: str
    code: str
    labels: List[Tuple[str, int]]          # (rule, 1-based line within code)
    name: str                              # function / paragraph name to rename per instance
    origin: str
    data_items: List[str] = field(default_factory=list)      # COBOL only
    linkage_items: List[str] = field(default_factory=list)   # COBOL only

    @property
    def vulnerable(self) -> bool:
        return bool(self.labels)


def strip_markers(code: str) -> Tuple[str, List[Tuple[str, int]]]:
    out, labels = [], []
    for i, line in enumerate(code.splitlines(), 1):
        m = _MARK.search(line)
        if m:
            labels += [(r, i) for r in re.findall(r"SEC\d+", m.group(1))]
            line = line[:m.start()].rstrip()
        elif _BANG.search(line):
            labels.append(("?", i))
            line = _BANG.sub("", line)
        out.append(line)
    return "\n".join(out) + "\n", labels


def _group_name(lang: str, name: str) -> str:
    return f"{lang}:" + re.sub(r"(?i)[-_]?safe$", "", name).lower()


def fixture_templates() -> List[Template]:
    from ..multilang.lower import lower_source
    out = []
    files = {"java": ["java/AccountServlet.java", "java/OrderController.java"],
             "csharp": ["csharp/ReportsController.cs"], "c": ["c/netconf.c"], "cpp": ["cpp/inventory_server.cpp"],
             "rust": ["rust/handlers.rs"]}
    for lang, rels in files.items():
        for rel in rels:
            path = os.path.join(ROOT, "tests", "multilang_fixtures", rel)
            src = open(path, encoding="utf-8").read()
            lines = src.splitlines()
            mod = lower_source(src, lang, path)
            for info in mod.functions.values():
                fn, node = info.fn, info.node
                if node.type in ("constructor_declaration",) or fn.name in ("main", fn.class_name):
                    continue
                start = node.start_point[0] + 1
                prev = node.prev_named_sibling
                while prev is not None and prev.type in ("attribute_item",) and prev.end_point[0] + 1 >= start - 1:
                    start = prev.start_point[0] + 1
                    prev = prev.prev_named_sibling
                code = textwrap.dedent("\n".join(lines[start - 1:fn.end_lineno]))
                clean, labels = strip_markers(code)
                out.append(Template(f"{lang}-{fn.name}", lang, _group_name(lang, fn.name), clean, labels, fn.name,
                                    f"tests/multilang_fixtures/{rel}"))
    return out


def python_templates() -> List[Template]:
    sys.path.insert(0, ROOT)
    from tests.large_corpus.snippets import SAFE, VULN
    out = []
    for rule in sorted(VULN):
        for kind, src in (("vuln", VULN[rule]), ("safe", SAFE[rule])):
            src = src.replace("__M__", str(20 + sum(map(ord, rule)) % 200))     # IP octet, as generate.py does
            code, labels = strip_markers(src.strip("\n"))
            labels = [(rule, ln) for _, ln in labels]
            m = re.search(r"def (\w+)", code)
            out.append(Template(f"python-{rule}-{kind}", "python", f"python:{rule}", code, labels,
                                m.group(1).replace("__N__", "") if m else "f", "tests/large_corpus/snippets.py"))
    return out


def cobol_templates() -> List[Template]:
    from .cobol_templates import TEMPLATES
    out = []
    for tid, rule, vuln, safe, items, linkage in TEMPLATES:
        for kind, para in (("vuln", vuln), ("safe", safe)):
            clean, labels = strip_markers(para.rstrip("\n"))
            labels = [(rule, ln) for _, ln in labels]
            data = list(items)
            data_labels = []
            if kind == "vuln":
                for k, it in enumerate(data):            # a marker on a data item (hard-coded VALUE)
                    if _BANG.search(it):
                        data_labels.append(k)
                        data[k] = _BANG.sub("", it)
            else:
                data = [_BANG.sub("", it) for it in data]
            name = clean.strip().split(".")[0].strip()
            t = Template(f"{tid}-{kind}", "cobol", f"cobol:{tid}", clean, labels, name.replace("__N__", ""),
                         "src/dataset/cobol_templates.py", data, list(linkage))
            t.data_label_rule = rule if data_labels else None          # type: ignore[attr-defined]
            t.data_label_idx = data_labels                              # type: ignore[attr-defined]
            out.append(t)
    return out


def snippet_samples() -> List[dict]:
    sys.path.insert(0, ROOT)
    from tests.test_multilang_coverage import SNIPPETS
    out = []
    for (lang, rule), code in sorted(SNIPPETS.items()):
        out.append({"language": lang, "rule": rule, "code": code + ("\n" if not code.endswith("\n") else ""),
                    "group": f"snippet:{'c-cpp' if lang in ('c', 'cpp') else lang}:{rule}"})
    return out


# ---------------------------------------------------------------------------
# wrappers: turn function templates into compilable files
# ---------------------------------------------------------------------------

def _fixture_imports(lang: str) -> List[str]:
    pats = {"java": r"^import .*;$", "csharp": r"^using .*;$", "c": r"^#include .*$", "cpp": r"^#include .*$",
            "rust": r"^use .*;$"}
    seen = []
    for f in sorted(os.listdir(os.path.join(ROOT, "tests", "multilang_fixtures", {"csharp": "csharp"}.get(lang, lang)))):
        for line in open(os.path.join(ROOT, "tests", "multilang_fixtures", lang, f), encoding="utf-8"):
            line = line.rstrip()
            if re.match(pats[lang], line) and line not in seen:
                seen.append(line)
    return seen


def wrap(lang: str, name: str, bodies: List[str]) -> Tuple[str, int]:
    """(source text, number of header lines before the first body) for a set of function bodies."""
    ind = {"java": "    ", "csharp": "        ", "cpp": "    "}.get(lang, "")
    if lang == "java":
        head = (_fixture_imports(lang) + ["import org.springframework.jdbc.core.JdbcTemplate;", "",
                f"public class {name} extends HttpServlet {{", "",
                "    private Connection conn;", "    private String lastUser;",
                "    private final JdbcTemplate jdbc = null;", "    private final DirContext ldap = null;",
                "    private final XPath xpath = null;",
                "    private static final org.slf4j.Logger log = org.slf4j.LoggerFactory.getLogger(Object.class);", ""])
        tail = ["}"]
    elif lang == "csharp":
        head = (_fixture_imports(lang) + ["", "namespace Dataset.Generated", "{", "    [ApiController]",
                "    [Authorize]", f"    public class {name}Controller : Controller", "    {",
                "        private static int lastReportId;", "        private readonly SqlConnection _conn;",
                "        private readonly HttpClient _http;", "        private readonly ILogger<object> _logger;", ""])
        tail = ["    }", "}"]
    elif lang == "c":
        head = _fixture_imports(lang) + ["", "#define NAME_MAX_LEN 32", "",
                                         "struct record { int id; char name[NAME_MAX_LEN]; };", ""]
        tail = []
    elif lang == "cpp":
        head = (_fixture_imports(lang) + ["", "namespace inventory {", "",
                "class Item {", "public:", "    int id;", "    std::string name;", "};", "",
                f"class {name} {{", "public:"])
        tail = ["};", "", "}  // namespace inventory"]
    elif lang == "rust":
        head = (_fixture_imports(lang) + ["", "static mut REQUEST_COUNT: u64 = 0;", "", "#[derive(Deserialize)]",
                "pub struct Params {", "    pub name: String,", "    pub host: String,", "    pub next: String,",
                "    pub page: String,", "    pub pattern: String,", "}", ""])
        tail = []
    elif lang == "python":
        sys.path.insert(0, ROOT)
        from tests.large_corpus.snippets import HEADER
        head = HEADER.replace("__TITLE__", f"{name} — dataset program.").replace("__CASE__", name).splitlines() + [""]
        tail = []
    else:
        raise ValueError(lang)
    body_lines: List[str] = []
    for b in bodies:
        body_lines += [ind + l if l.strip() else "" for l in b.rstrip("\n").splitlines()] + [""]
    return "\n".join(head + body_lines + tail) + "\n", len(head)


def _rename(text: str, name: str, suffix: str) -> str:
    return re.sub(rf"\b{re.escape(name)}\b", name + suffix, text) if name else text


# ---------------------------------------------------------------------------
# COBOL program composition
# ---------------------------------------------------------------------------

def cobol_program(prog: str, paras: List[Tuple[Template, str]], fillers: List[Tuple[str, List[str]]]) \
        -> Tuple[str, List[Tuple[str, int]]]:
    """Compose a COBOL program; returns (source, [(rule, line)])."""
    data, linkage, files = [], [], []
    for t, sfx in paras:
        data += [d.replace("__N__", sfx) for d in t.data_items]
        linkage += [l.replace("__N__", sfx) for l in t.linkage_items]
        for m in re.findall(r"EXPORT-FILE(\w*)", t.code.replace("__N__", sfx)):
            if m not in files:
                files.append(m)
    for _, items in fillers:
        data += items
    lines = ["       IDENTIFICATION DIVISION.", f"       PROGRAM-ID. {prog}.", "       ENVIRONMENT DIVISION."]
    if files:
        lines += ["       INPUT-OUTPUT SECTION.", "       FILE-CONTROL."]
        for m in files:
            lines += [f"           SELECT EXPORT-FILE{m} ASSIGN TO DYNAMIC WS-EXPORT-PATH{m}",
                      "               ORGANIZATION IS LINE SEQUENTIAL."]
    lines += ["       DATA DIVISION."]
    if files:
        lines += ["       FILE SECTION."]
        for m in files:
            lines += [f"       FD  EXPORT-FILE{m}.", f"       01  EXPORT-LINE{m}         PIC X(80)."]
    lines += ["       WORKING-STORAGE SECTION."]
    labels: List[Tuple[str, int]] = []
    for t, sfx in paras:
        for k, d in enumerate(t.data_items):
            lines.append(d.replace("__N__", sfx))
            if k in getattr(t, "data_label_idx", []):
                labels.append((t.data_label_rule, len(lines)))
    for _, items in fillers:
        lines += items
    if linkage:
        lines += ["       LINKAGE SECTION."] + linkage
        names = [l.split()[1] for l in linkage]
        lines += [f"       PROCEDURE DIVISION USING {' '.join(names)}."]
    else:
        lines += ["       PROCEDURE DIVISION."]
    order = [("t", p) for p in paras] + [("f", f) for f in fillers]
    random.Random(prog).shuffle(order)
    lines += ["       MAIN-PARA.", "           DISPLAY 'START'.", "           GOBACK.", ""]
    for kind, item in order:
        if kind == "t":
            t, sfx = item
            base = len(lines)
            lines += t.code.replace("__N__", sfx).rstrip("\n").splitlines() + [""]
            labels += [(r, base + ln) for r, ln in t.labels]
        else:
            lines += item[0].rstrip("\n").splitlines() + [""]
    return "\n".join(lines) + "\n", labels


# ---------------------------------------------------------------------------
# public data
# ---------------------------------------------------------------------------

def juliet_samples(lang: str, per_cwe: int, files_per_group: int = 2) -> List[dict]:
    from ..multilang.lower import lower_source, text
    from ..vulnml.dataset import JULIET, JULIET_DIR, _group_key, _label_for
    from ..vulnml.families import family_of_cwe
    zname, exts = JULIET[lang]
    path = os.path.join(JULIET_DIR, zname)
    if not os.path.isfile(path):
        print(f"  {lang}: Juliet archive missing at {path}; skipped")
        return []
    zf = zipfile.ZipFile(path)
    groups: Dict[str, Dict[str, List[str]]] = defaultdict(lambda: defaultdict(list))
    for n in zf.namelist():
        m = re.search(r"testcases/CWE(\d+)_", n)
        if m and n.endswith(exts) and "/support" not in n.lower():
            groups[m.group(1)][_group_key(n)].append(n)
    rng = random.Random(f"juliet-{lang}")
    out = []
    for cwe, gs in sorted(groups.items()):
        fam = family_of_cwe(cwe)
        if fam is None:
            continue
        keys = sorted(gs)
        rng.shuffle(keys)
        for g in keys[:per_cwe]:
            group = f"juliet:{lang}:CWE{cwe}:{g}"
            for n in sorted(gs[g])[:files_per_group]:
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
                    if len(body) < 40:
                        continue
                    locs = []
                    if lbl != "safe":
                        blines = body.splitlines()
                        for i, l in enumerate(blines):
                            if re.search(r"/\*\s*(POTENTIAL\s+)?FLAW", l):
                                j = i + 1
                                while j < len(blines) and (not blines[j].strip() or blines[j].strip().startswith(("/*", "*", "//"))):
                                    j += 1
                                if j < len(blines):
                                    locs.append({"line": j + 1, "rule": None, "cwe": f"CWE-{cwe}"})
                    out.append({"language": lang, "source": "juliet", "kind": "function", "group": group,
                                "label": "vulnerable" if lbl != "safe" else "safe", "family": lbl if lbl != "safe" else None,
                                "cwe": f"CWE-{cwe}", "code": body, "locations": locs,
                                "origin": f"NIST SARD Juliet 1.3: {n}#{info.fn.name}"})
    return out


def owasp_samples() -> List[dict]:
    from ..security.benchmarks import OWASP_DIR, owasp_cases, owasp_group_key
    from ..vulnml.dataset import OWASP_CATEGORY_CWE
    from ..vulnml.families import family_of_cwe
    out = []
    try:
        cases = owasp_cases()
    except Exception:
        print("  OWASP BenchmarkPython missing; skipped")
        return out
    for case in cases:
        p = os.path.join(OWASP_DIR, "testcode", f"{case['test']}.py")
        if not os.path.isfile(p):
            continue
        cwe = OWASP_CATEGORY_CWE.get(case["category"])
        fam = family_of_cwe(cwe) if cwe else None
        if cwe == 614:
            fam = "cleartext"
        real = case["real"] in (True, "true")
        out.append({"language": "python", "source": "owasp", "kind": "file", "group": f"owasp:{owasp_group_key(case['test'])}",
                    "label": "vulnerable" if real else "safe", "family": fam if real else None,
                    "cwe": f"CWE-{cwe}" if cwe else None, "path": os.path.relpath(p, ROOT).replace("\\", "/"),
                    "code": open(p, encoding="utf-8").read(), "locations": [],
                    "origin": f"OWASP BenchmarkPython {case['test']} ({case['category']})"})
    return out


# ---------------------------------------------------------------------------
# validation
# ---------------------------------------------------------------------------

def parses(code: str, lang: str) -> Optional[str]:
    """None when the code parses cleanly, else the reason."""
    try:
        if lang == "python":
            ast.parse(code)
            return None
        if lang == "cobol":
            from ..multilang.cobol import lower_cobol
            m = lower_cobol(code)
            return None if len([b for b in m.ir.functions[0].blocks if b.meta.get("kind") == "paragraph"]) > 1 \
                else "no paragraphs parsed"
        from ..multilang.lower import lower_source
        m = lower_source(code, lang)
        return m.syntax_error
    except Exception as exc:
        return f"{type(exc).__name__}: {exc}"


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------

def build(version: str = "v1", juliet_per_cwe: int = 100, variants: int = 3, long_per_split=(8, 2, 3)) -> dict:
    from ..security.rules import RULES
    from ..vulnml.families import family_cwe, family_of_rule
    from .fillers import COBOL as COBOL_FILL, FILLERS
    t0 = time.time()
    out_dir = os.path.join(OUT_ROOT, version)
    prog_dir = os.path.join(out_dir, "programs")
    if os.path.isdir(prog_dir):
        import shutil
        shutil.rmtree(prog_dir)
    os.makedirs(prog_dir, exist_ok=True)
    samples: List[dict] = []
    rejected: List[dict] = []

    def sev(rule):
        return RULES[rule].severity if rule in RULES else None

    def add(rec: dict, split: str) -> None:
        rec["split"] = split
        rec["id"] = f"{rec['language']}-{rec['source']}-{len(samples):06d}"
        rec["lines"] = rec.get("lines") or (rec["code"].count("\n") + 1 if rec.get("code") else 0)
        for loc in rec.get("locations", []):
            if loc.get("rule"):
                loc["cwe"] = loc.get("cwe") or RULES[loc["rule"]].cwe
                loc["severity"] = sev(loc["rule"])
        if rec["label"] == "vulnerable":
            rules = [l["rule"] for l in rec.get("locations", []) if l.get("rule")]
            rec["severity"] = max((sev(r) for r in rules), key=lambda s: ["low", "medium", "high", "critical"].index(s),
                                  default=None) if rules else None
            if rec["severity"] is None and rec.get("family"):
                frules = [r for r in RULES if family_of_rule(r) == rec["family"]]
                if frules:
                    rec["severity"] = max((sev(r) for r in frules),
                                          key=lambda s: ["low", "medium", "high", "critical"].index(s))
                    rec["severity_source"] = "this project's rule severity for the CWE family"
            rec.setdefault("severity_source", "rule severity" if rec.get("severity") else None)
        else:
            rec["severity"] = None
        samples.append(rec)

    def write_file(split: str, lang: str, sub: str, name: str, code: str) -> str:
        d = os.path.join(prog_dir, split, lang, sub)
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, name + EXT[lang])
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(code)
        return os.path.relpath(p, ROOT).replace("\\", "/")

    # ── custom templates ─────────────────────────────────────────────────
    templates = fixture_templates() + python_templates() + cobol_templates()
    # reliability rules without a CWE (SEC007 mutable default argument) are not security labels
    excluded = sorted({t.group for t in templates if any(not RULES[r].cwe for r, _ in t.labels if r in RULES)})
    templates = [t for t in templates if t.group not in excluded]
    by_lang: Dict[str, List[Template]] = defaultdict(list)
    for t in templates:
        by_lang[t.language].append(t)
    split_of: Dict[str, str] = {}
    for lang, ts in by_lang.items():
        split_of.update(ranked_splits([t.group for t in ts], seed=version))

    # small samples: each template (and renamed variants) as its own compilable file
    for lang, ts in by_lang.items():
        for t in ts:
            split = split_of[t.group]
            for k in range(variants):
                sfx = "" if k == 0 else f"V{k}"
                if lang == "cobol":
                    code, labels = cobol_program(f"S{abs(hash(t.id)) % 9999:04d}{k}", [(t, f"{k}")], [])
                else:
                    body = _rename(t.code.replace("__N__", ""), t.name, sfx)
                    code, head = wrap(lang, f"Sample{re.sub(r'[^A-Za-z0-9]', '', t.id.title())}{k}", [body])
                    labels = [(r, head + ln) for r, ln in t.labels]
                    if lang == "python":
                        labels = [(r if r != "?" else r, head + ln) for r, ln in t.labels]
                why = parses(code, lang)
                if why:
                    rejected.append({"template": t.id, "variant": k, "reason": why})
                    continue
                vuln = bool(labels)
                rule = next((r for r, _ in labels), None)
                fam = family_of_rule(rule) if rule else None
                path = write_file(split, lang, "small", f"{t.id.replace('/', '_')}_{k}", code)
                add({"language": lang, "source": "custom", "kind": "file", "group": t.group,
                     "label": "vulnerable" if vuln else "safe", "family": fam,
                     "cwe": RULES[rule].cwe if rule else None, "path": path, "code": code,
                     "function_code": t.code.replace("__N__", str(k) if lang == "cobol" else "") if lang != "cobol" else
                     t.code.replace("__N__", str(k)),
                     "locations": [{"line": ln, "rule": r} for r, ln in labels], "origin": t.origin,
                     "template": t.id, "variant": k}, split)

    # one-vulnerability snippet programs (multi-language coverage tests)
    snips = snippet_samples()
    snip_split = ranked_splits([s["group"] for s in snips], seed=version + "-snip")
    for s in snips:
        why = parses(s["code"], s["language"])
        if why:
            rejected.append({"snippet": f"{s['language']}-{s['rule']}", "reason": why})
            continue
        split = snip_split[s["group"]]
        path = write_file(split, s["language"], "snippets", f"{s['rule']}", s["code"])
        add({"language": s["language"], "source": "custom", "kind": "file", "group": s["group"],
             "label": "vulnerable", "family": family_of_rule(s["rule"]), "cwe": RULES[s["rule"]].cwe,
             "path": path, "code": s["code"], "function_code": s["code"],
             "locations": [{"line": None, "rule": s["rule"]}], "origin": "tests/test_multilang_coverage.py",
             "template": f"snippet-{s['language']}-{s['rule']}", "variant": 0}, split)

    # long programs per split, from that split's templates only
    rng = random.Random(f"long-{version}")
    for lang, ts in by_lang.items():
        for split, count in zip(SPLITS, long_per_split):
            pool = [t for t in ts if split_of[t.group] == split]
            if not pool:
                continue
            for i in range(count):
                target = rng.randint(1080, 1950)
                name = f"{split.title()}{lang.title()}Program{i + 1:02d}"
                n = 0
                if lang == "cobol":
                    paras, fills = [], []
                    est = 0
                    while est < target:
                        n += 1
                        if rng.random() < 0.55:
                            t = rng.choice(pool)
                            paras.append((t, f"{n}"))
                            est += t.code.count("\n") + 2 + len(t.data_items)
                        else:
                            text_, items = rng.choice(COBOL_FILL)
                            fills.append((text_.replace("__N__", f"{n}"), [it.replace("__N__", f"{n}") for it in items]))
                            est += text_.count("\n") + 2 + len(items)
                    code, labels = cobol_program(f"L{split[:2].upper()}{i + 1:02d}", paras, fills)
                    while code.count("\n") < 1000:              # estimate fell short: add ordinary code
                        n += 1
                        text_, items = rng.choice(COBOL_FILL)
                        fills.append((text_.replace("__N__", f"{n}"), [it.replace("__N__", f"{n}") for it in items]))
                        code, labels = cobol_program(f"L{split[:2].upper()}{i + 1:02d}", paras, fills)
                else:
                    bodies, planted = [], []
                    est = 30
                    while est < target:
                        n += 1
                        if rng.random() < 0.5:
                            t = rng.choice(pool)
                            body = _rename(t.code.replace("__N__", ""), t.name, f"N{n}")
                            planted.append((len(bodies), t))
                        else:
                            body = rng.choice(FILLERS.get(lang, FILLERS["c"]) if lang != "python" else _py_fillers()).replace("__N__", f"{n}")
                        bodies.append(body)
                        est += body.count("\n") + 1
                    code, head = wrap(lang, name, bodies)
                    while code.count("\n") < 1000:              # estimate fell short: add ordinary code
                        n += 1
                        bodies.append(rng.choice(FILLERS.get(lang, FILLERS["c"]) if lang != "python" else
                                                 _py_fillers()).replace("__N__", f"{n}"))
                        code, head = wrap(lang, name, bodies)
                    # locate each planted template's labels: bodies are written in order, one blank line apart
                    labels, line = [], head + 1
                    planted_at = {idx: t for idx, t in planted}
                    for idx, b in enumerate(bodies):
                        if idx in planted_at:
                            labels += [(r, line + ln - 1) for r, ln in planted_at[idx].labels]
                        line += b.rstrip("\n").count("\n") + 2
                    if lang == "python":
                        labels = [(r, ln) for r, ln in labels]
                why = parses(code, lang)
                if why:
                    rejected.append({"long_program": name, "reason": why})
                    continue
                path = write_file(split, lang, "long", name, code)
                rules = [r for r, _ in labels]
                add({"language": lang, "source": "custom-long", "kind": "file", "group": f"long:{lang}:{split}:{i}",
                     "label": "vulnerable" if labels else "safe", "family": None, "cwe": None, "path": path,
                     "locations": [{"line": ln, "rule": r} for r, ln in labels], "origin": "src/dataset/build.py",
                     "lines": code.count("\n"), "rules_planted": dict(Counter(rules))}, split)

    # ── public data ──────────────────────────────────────────────────────
    for lang in ("java", "c", "cpp", "csharp"):
        for rec in juliet_samples(lang, juliet_per_cwe):
            add(rec, hash_split(rec["group"], seed=version))
    for rec in owasp_samples():
        add(rec, hash_split(rec["group"], seed=version))

    # python long programs: the hand-labelled snippet pairs carry the rule as their label
    for s in samples:
        if s["language"] == "python" and s["source"] in ("custom", "custom-long"):
            for loc in s["locations"]:
                if loc["rule"] == "?":
                    loc["rule"] = s.get("template", "").split("-")[1] if s.get("template") else None

    # ── write ────────────────────────────────────────────────────────────
    os.makedirs(out_dir, exist_ok=True)
    with gzip.open(os.path.join(out_dir, "samples.jsonl.gz"), "wt", encoding="utf-8") as fh:
        for s in samples:
            fh.write(json.dumps(s, ensure_ascii=False) + "\n")
    stats = statistics(samples)
    manifest = {"name": "Code Comment Generator security dataset", "version": version,
                "created_by": "python -m src.dataset.build", "seconds": round(time.time() - t0, 1),
                "config": {"juliet_per_cwe": juliet_per_cwe, "variants": variants, "long_per_split": list(long_per_split),
                           "split": "70/15/15 by group (Juliet functional variant, OWASP template family, custom template "
                                    "with its safe twin and renamed variants); long programs use only their split's templates"},
                "sources": {"juliet": "NIST SARD Juliet Test Suite 1.3 for Java, C/C++, C# (public domain)",
                            "owasp": "OWASP BenchmarkPython (GPL-3.0, pinned commit in src/security/benchmarks.py)",
                            "custom": "hand-labelled templates in tests/ and src/dataset/ (labels written next to the code)"},
                "excluded_template_groups": {g: "rule has no CWE (code-quality rule, not a security label)"
                                             for g in excluded},
                "validation": {"rejected": rejected, "rule": "custom files must parse without syntax errors; vulnerable "
                                                             "samples carry >= 1 location label, safe samples none"},
                "statistics": stats}
    with open(os.path.join(out_dir, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=1)
    with open(os.path.join(out_dir, "DATASHEET.md"), "w", encoding="utf-8") as fh:
        fh.write(datasheet(manifest))
    return manifest


def _py_fillers() -> List[str]:
    sys.path.insert(0, ROOT)
    from tests.large_corpus.filler import TEMPLATES
    return [t.replace("__E__", "Item").replace("__e__", "item") for t in TEMPLATES]


def statistics(samples: List[dict]) -> dict:
    def count(key, subset=None):
        c = Counter(key(s) for s in (subset or samples))
        return dict(sorted(c.items(), key=lambda kv: str(kv[0])))
    vuln = [s for s in samples if s["label"] == "vulnerable"]
    rule_counts = Counter(l["rule"] for s in samples for l in s.get("locations", []) if l.get("rule"))
    cwe_counts = Counter(s["cwe"] for s in vuln if s.get("cwe"))
    for s in samples:
        if s["source"] == "custom-long":
            for l in s["locations"]:
                if l.get("rule"):
                    from ..security.rules import RULES
                    cwe_counts[RULES[l["rule"]].cwe] += 1
    total_lines = sum(s["lines"] for s in samples)
    return {
        "samples": len(samples), "total_lines_of_code": total_lines,
        "by_language": count(lambda s: s["language"]), "by_source": count(lambda s: s["source"]),
        "by_split": count(lambda s: s["split"]), "by_label": count(lambda s: s["label"]),
        "by_language_and_label": count(lambda s: f"{s['language']}/{s['label']}"),
        "by_language_and_split": count(lambda s: f"{s['language']}/{s['split']}"),
        "lines_by_language": {l: sum(s["lines"] for s in samples if s["language"] == l) for l in LANGS},
        "vulnerable_by_family": count(lambda s: s.get("family") or "(per-location rules)", vuln),
        "location_labels_by_rule": dict(sorted(rule_counts.items())),
        "top_cwes": dict(cwe_counts.most_common(40)), "distinct_cwes": len(cwe_counts),
        "long_programs": {"count": sum(1 for s in samples if s["source"] == "custom-long"),
                          "lines": sum(s["lines"] for s in samples if s["source"] == "custom-long"),
                          "min_lines": min((s["lines"] for s in samples if s["source"] == "custom-long"), default=0),
                          "max_lines": max((s["lines"] for s in samples if s["source"] == "custom-long"), default=0),
                          "planted_vulnerabilities": sum(len(s["locations"]) for s in samples if s["source"] == "custom-long"),
                          "by_language": count(lambda s: s["language"], [s for s in samples if s["source"] == "custom-long"])},
        "multi_vulnerability_files": sum(1 for s in samples if len({l.get("rule") for l in s.get("locations", [])}) > 1),
        "groups": len({s["group"] for s in samples}),
    }


def datasheet(m: dict) -> str:
    st = m["statistics"]
    rows = lambda d: "\n".join(f"| {k} | {v} |" for k, v in d.items())
    return f"""# Security dataset {m['version']}

Built by `python -m src.dataset.build` ({m['seconds']} s). Every number below is computed from
`samples.jsonl.gz` by the builder.

| | |
|---|---|
| Samples | {st['samples']:,} |
| Total lines of code | {st['total_lines_of_code']:,} |
| Groups (split unit) | {st['groups']:,} |
| Distinct CWEs | {st['distinct_cwes']} |
| Long programs (1,000-2,000 lines) | {st['long_programs']['count']} programs, {st['long_programs']['lines']:,} lines, {st['long_programs']['planted_vulnerabilities']} planted vulnerabilities |
| Files with more than one vulnerability class | {st['multi_vulnerability_files']} |

## Splits ({m['config']['split']})

| Split | Samples |
|---|---|
{rows(st['by_split'])}

## Languages

| Language | Samples | Lines of code |
|---|---|---|
""" + "\n".join(f"| {l} | {st['by_language'].get(l, 0):,} | {st['lines_by_language'].get(l, 0):,} |"
               for l in LANGS) + f"""

## Sources

| Source | Samples |
|---|---|
{rows(st['by_source'])}

## Labels per language

| Language / label | Samples |
|---|---|
{rows(st['by_language_and_label'])}

## Vulnerable samples by family

| Family | Samples |
|---|---|
{rows(st['vulnerable_by_family'])}

## Location labels by rule (custom samples and long programs)

| Rule | Locations |
|---|---|
{rows(st['location_labels_by_rule'])}

## Record format (`samples.jsonl.gz`, one JSON object per line)

`id, language, source (juliet | owasp | custom | custom-long), kind (function | file), split, group,
label (vulnerable | safe), family, cwe, severity, severity_source, locations [{{line, rule, cwe, severity}}],
lines, code, path (files), origin, template / variant (custom)`

Juliet locations come from Juliet's own `FLAW` comments; OWASP cases carry a file-level label only
(no line); custom locations are the hand-written markers. Severity comes from the project's rule for
that rule or CWE family (CWE itself has no severity field).

## Validation

{len(m['validation']['rejected'])} custom samples were rejected ({m['validation']['rule']}).

## Licences

{m['sources']['juliet']}; {m['sources']['owasp']}; {m['sources']['custom']}.
"""


def main(argv=None) -> int:
    from ..config import configure_stdio
    configure_stdio()
    ap = argparse.ArgumentParser(prog="python -m src.dataset.build")
    ap.add_argument("--version", default="v1")
    ap.add_argument("--juliet-per-cwe", type=int, default=100)
    ap.add_argument("--variants", type=int, default=3)
    args = ap.parse_args(argv)
    m = build(args.version, args.juliet_per_cwe, args.variants)
    st = m["statistics"]
    print(json.dumps({k: st[k] for k in ("samples", "total_lines_of_code", "by_language", "by_source", "by_split",
                                         "by_label", "long_programs", "distinct_cwes")}, indent=1))
    print(f"rejected: {len(m['validation']['rejected'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
