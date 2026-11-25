"""Security knowledge base, ML detector, neuro-symbolic fusion and the 9 dashboard classes."""
import os
import re

import pytest

from src.rag.knowledge import kb_entry, security_kb
from src.security.categories import CLASSES, ORIGINAL_EIGHT, class_of, count_by_class
from src.security.coverage import cwe_coverage, matrix, rule_languages
from src.security.findings import Finding
from src.security.rules import RULES
from src.vulnml.dataset import Sample, normalise, split
from src.vulnml.families import FAMILIES, family_of_cwe, family_of_rule


# ── knowledge base ──────────────────────────────────────────────────────────

def test_knowledge_base_size_uniqueness_and_attribution():
    kb = security_kb()
    entries = kb["entries"]
    assert len(entries) >= 1000
    ids = [e["id"] for e in entries]
    assert len(ids) == len(set(ids))
    descs = [e["description"] for e in entries]
    assert len(set(descs)) >= 0.98 * len(descs)          # no copy-pasted / superficial entries
    for e in entries:
        assert e["source"].startswith(("MITRE CWE", "MITRE CAPEC")) and e["url"].startswith("https://")
        assert len(e["description"]) >= 30
    counts = kb["meta"]["counts"]
    assert counts["weaknesses"] >= 900 and counts["attack_patterns"] >= 500


def test_entries_carry_the_requested_fields():
    sqli = kb_entry("CWE-89")
    assert sqli["name"].startswith("Improper Neutralization") and sqli["languages"]
    assert sqli["mitigations"] and sqli["detection_methods"] and sqli["observed_examples"]
    assert any(x["nature"] == "bad" for x in sqli["examples"]) and any(x["nature"] == "good" for x in sqli["examples"])
    assert any("Juliet" in x["source"] for x in sqli["examples"])          # NIST SARD examples
    assert sqli["detection"]["implemented"] and "SEC005" in sqli["detection"]["rules"]
    assert {"python", "java", "csharp", "c", "cpp", "rust", "cobol"} <= set(sqli["detection"]["languages"])
    assert sqli["severity"] and sqli["severity_source"]
    capec = kb_entry("CAPEC-66")
    assert capec["kind"] == "attack-pattern" and "CWE-89" in capec["related_weaknesses"]


def test_documented_versus_implemented_is_explicit():
    kb = security_kb()["entries"]
    implemented = {e["id"] for e in kb if e.get("detection", {}).get("implemented")}
    assert implemented == {c for c in cwe_coverage() if c in {e["id"] for e in kb}}
    assert len(implemented) < len([e for e in kb if e["kind"] == "weakness"]) / 5   # most CWEs are documented only


def test_explain_finding_uses_language_specific_examples():
    from src.multilang.analyzer import analyze_file
    from src.rag import explain_finding
    path = os.path.join(os.path.dirname(__file__), "multilang_fixtures", "java", "AccountServlet.java")
    f = next(x for x in analyze_file(path).active() if x.rule_id == "SEC005")
    ex = explain_finding(f, open(path, encoding="utf-8").read(), "java")
    assert ex["evidence"][0]["kind"] == "source" and ex["knowledge"]["id"] == "CWE-89"
    assert ex["knowledge"]["example_vulnerable"]["language"] == "Java"
    assert ex["knowledge"]["mitigations"]


# ── coverage and classes ────────────────────────────────────────────────────

def test_nine_classes_keep_the_original_eight():
    assert list(CLASSES) == ["cmdi", "codeinj", "deserialization", "hash", "pathtraver", "sqli", "weakrand", "xss",
                             "others"]
    assert len(ORIGINAL_EIGHT) == 8
    assert class_of("SEC005") == "sqli" and class_of("SEC002") == "cmdi" and class_of("SEC056") == "others"
    counts = count_by_class(["SEC005", "SEC005", "SEC052", "SEC004"])
    assert list(counts) == list(CLASSES) and counts["sqli"] == 2 and counts["others"] == 1 and counts["xss"] == 0


def test_security_report_counts_classes():
    from src.security_analyzer import run_security_analysis_on_source
    rep = run_security_analysis_on_source(open(os.path.join(os.path.dirname(__file__), "inputs",
                                                            "demo_15_vulns.py"), encoding="utf-8").read(), "d.py")
    d = rep.to_dict()
    assert set(d["by_class"]) == set(CLASSES) and sum(d["by_class"].values()) == rep.total_issues
    assert d["by_class"]["sqli"] >= 1 and d["by_class"]["others"] >= 1
    assert all("class" in i for i in d["issues"])


def test_coverage_matrix_rows():
    rows = matrix()
    assert len(rows) == len(RULES)
    row = next(r for r in rows if r["rule"] == "SEC005")
    assert all(row[l] for l in ("python", "java", "csharp", "c", "cpp", "rust", "cobol"))
    assert rule_languages()["SEC056"] == ["c", "cpp"]


# ── ML detector: leakage controls and split ─────────────────────────────────

def test_normalise_removes_label_leaks():
    code = '''public void CWE89_SQL_Injection__getParameter_01_bad() {
        /* FLAW: data concatenated into the query */
        String data = request.getParameter("name");
        goodG2BSink(data);  // FIX
    }'''
    toks = normalise(code, "java").split()
    assert "FLAW" not in toks and "FIX" not in toks and "public" not in toks
    assert not any(re.search(r"(?i)cwe\d|good|bad", t) for t in toks)
    assert "getParameter" in toks and "STR" in toks


def test_split_keeps_functional_variants_together():
    samples = [Sample("a", "safe", f"CWE89:variant{i % 40}", "CWE-89", f"f{i}") for i in range(400)]
    train, test = split(samples)
    assert train and test and not ({s.group for s in train} & {s.group for s in test})


def test_families_map_cwes_and_rules():
    assert family_of_cwe("CWE-121") == "buffer-overflow" and family_of_cwe(416) == "memory-management"
    assert family_of_rule("SEC005") == "sql-injection" and family_of_rule("SEC056") == "memory-management"
    for fam, (_, cwes, rules, rep_cwe) in FAMILIES.items():
        assert all(r in RULES for r in rules)


# ── neuro-symbolic reasoning (logic tests with constructed predictions) ────

def _finding(rule, line, status="potential", reasons=None):
    r = RULES[rule]
    return Finding(rule, r.title, r.category, r.cwe, r.severity, "medium" if status == "potential" else "high",
                   status, "x.java", "A.f", line, 0, "m", r.remediation, "taint",
                   confidence_reasons=list(reasons or []))


def test_fusion_agreement_upgrade_disagreement_and_new_findings():
    from src.vulnml.detector import MLPrediction
    from src.vulnml.fusion import _apply
    f_agree = _finding("SEC005", 3, reasons=["sink 'q.executeQuery' matched by method name; the receiver's type was "
                                              "not resolved"])
    f_disagree = _finding("SEC013", 13, status="confirmed")
    preds = [MLPrediction("A.f", 1, 5, "sql-injection", 0.92, 0.9, [("executeQuery", 0.4)]),
             MLPrediction("A.g", 10, 15, "path-traversal", 0.05, 0.03),
             MLPrediction("A.h", 20, 25, "command-injection", 0.88, 0.85, [("exec", 0.5)]),
             MLPrediction("A.k", 30, 35, "xss", 0.95, 0.9)]
    evidence = {"A.h": "L22: calls Runtime.exec() — a os command injection sink — with non-constant data"}
    out = _apply([f_agree, f_disagree], preds, "x.java", lambda p: evidence.get(p.function))
    assert f_agree.status == "confirmed" and any("agrees" in r for r in f_agree.confidence_reasons)
    assert f_disagree.status == "confirmed" and any("considers the function safe" in r
                                                     for r in f_disagree.confidence_reasons)
    new = [f for f in out if f.rule_id == "SEC064"]
    assert len(new) == 1 and new[0].line == 22 and new[0].status == "potential" and new[0].cwe == "CWE-78"
    assert any(r.startswith("semantic:") for r in new[0].confidence_reasons)
    assert not any(f.function == "A.k" for f in out)        # ML alone, no semantic evidence → not reported


@pytest.mark.skipif(not os.path.isfile(os.path.join(os.path.dirname(__file__), "..", "outputs", "vulnml",
                                                    "java.joblib")), reason="ML models not trained")
def test_trained_detector_predicts_per_function():
    from src.multilang.lower import lower_source
    from src.vulnml.detector import predict_lowered
    code = '''class A { void f(HttpServletRequest r, Statement s) throws Exception {
        s.executeQuery("SELECT * FROM t WHERE n = '" + r.getParameter("n") + "'"); }
        int g(int a) { return a + 1; } }'''
    preds = {p.function: p for p in predict_lowered(lower_source(code, "java"), "java")}
    assert set(preds) == {"A.f", "A.g"}
    assert preds["A.f"].p_vulnerable > preds["A.g"].p_vulnerable
