"""Multi-language compiler back end and security analysis.

* Fixtures (tests/multilang_fixtures): realistic programs in Java, C#, C, C++, Rust and COBOL.
  Expected findings are written by hand as ``expect: SECxxx`` markers on the line the rule must
  report; the analyzer must report exactly those (rule, line) pairs — every vulnerability found,
  nothing reported on the safe twins.
* IR / CFG / data-flow structure per language, comment styles for C#, Rust and COBOL.
"""
import glob
import os
import re

import pytest

from src.analysis.cfg_builder import build_cfg
from src.analysis.dfa_engine import run_dfa
from src.logger import PipelineLogger
from src.main import run_pipeline
from src.multilang.analyzer import CAPABILITIES, analyze_file, analyze_source
from src.multilang.cobol import lower_cobol
from src.multilang.lower import lower_source

HERE = os.path.dirname(__file__)
FIXTURES = sorted(glob.glob(os.path.join(HERE, "multilang_fixtures", "*", "*.*")))


def _expected(path):
    lines = open(path, encoding="utf-8").read().splitlines()
    return {(r, i + 1) for i, l in enumerate(lines) for grp in re.findall(r"expect:\s*((?:SEC\d+[ ,]*)+)", l)
            for r in re.findall(r"SEC\d+", grp)}


def test_fixture_set_covers_six_languages():
    exts = {os.path.splitext(f)[1] for f in FIXTURES}
    assert {".java", ".cs", ".c", ".cpp", ".rs", ".cbl"} <= exts
    assert sum(len(_expected(f)) for f in FIXTURES) >= 80


@pytest.mark.parametrize("path", FIXTURES, ids=[os.path.basename(f) for f in FIXTURES])
def test_fixture_findings_match_markers_exactly(path):
    rep = analyze_file(path)
    assert rep.parse_error is None
    got = {(f.rule_id, f.line) for f in rep.active()}
    exp = _expected(path)
    assert exp - got == set(), "missed"
    assert got - exp == set(), "reported outside the marked lines"


@pytest.mark.parametrize("path", FIXTURES, ids=[os.path.basename(f) for f in FIXTURES])
def test_every_taint_finding_has_a_source_to_sink_trace(path):
    for f in analyze_file(path).active():
        if f.analysis == "taint":
            kinds = [s["kind"] for s in f.trace]
            assert kinds[0] == "source" and kinds[-1] == "sink", (f.rule_id, f.line, kinds)
            assert f.cwe and f.remediation


def test_sanitizer_and_bounds_check_remove_the_flow():
    java = '''class A { void f(HttpServletRequest r) throws Exception {
        String id = r.getParameter("id");
        int n = Integer.parseInt(id);
        st.executeQuery("SELECT * FROM t WHERE id = " + n); } }'''
    assert not [f for f in analyze_source(java, "A.java", "java").active() if f.rule_id == "SEC005"]
    c = '''void f(int s){ char h[8]; char b[64]; recv(s, h, 8, 0); int n = atoi(h);
        if (n < 0 || n > 64) return; memcpy(b, h, n); }'''
    assert not [f for f in analyze_source(c, "a.c", "c").active() if f.rule_id == "SEC053"]


def test_interprocedural_flow_through_a_helper():
    java = '''class A {
      String build(String v) { return "SELECT * FROM t WHERE n = '" + v + "'"; }
      void f(HttpServletRequest r, Statement st) throws Exception {
        st.executeQuery(build(r.getParameter("n"))); } }'''
    hits = [f for f in analyze_source(java, "A.java", "java").active() if f.rule_id == "SEC005"]
    assert hits and any(s["kind"] == "call" for s in hits[0].trace)


def test_nosec_with_reason_suppresses():
    c = 'void f(void){ char b[8]; gets(b); /* nosec SEC051: test harness only */ }'
    rep = analyze_source(c, "a.c", "c")
    f = next(x for x in rep.findings if x.rule_id == "SEC051")
    assert f.status == "suppressed" and "harness" in f.suppression_reason


# ── IR / CFG / data flow ────────────────────────────────────────────────────

@pytest.mark.parametrize("lang,code", [
    ("java", "class A { int f(int x) { int y = 0; if (x > 1) { y = x; } else { y = 2; } "
             "for (int i = 0; i < x; i++) { y += i; } return y; } }"),
    ("csharp", "class A { int F(int x) { var y = 0; if (x > 1) { y = x; } else { y = 2; } "
               "while (x > 0) { x--; } return y; } }"),
    ("c", "int f(int x) { int y = 0; if (x > 1) { y = x; } else { y = 2; } while (x > 0) { x--; } return y; }"),
    ("cpp", "int f(int x) { int y = 0; if (x > 1) { y = x; } else { y = 2; } for (int i : v) { y += i; } return y; }"),
    ("rust", "fn f(x: i32) -> i32 { let mut y = 0; if x > 1 { y = x; } else { y = 2; } "
             "for i in 0..x { y += i; } y }"),
])
def test_lowering_builds_branches_loops_and_dataflow(lang, code):
    mod = lower_source(code, lang)
    fn = next(iter(mod.functions.values())).fn
    kinds = [b.meta.get("kind") for b in fn.blocks]
    assert "if_true" in kinds and "if_false" in kinds and "join" in kinds
    assert "loop_header" in kinds and "loop_body" in kinds
    header = next(b for b in fn.blocks if b.meta.get("kind") == "loop_header")
    assert len(header.predecessors) >= 2            # entry edge + back edge
    cfg = build_cfg(fn)
    dfa = run_dfa(cfg, fn)
    assert cfg.entry == "entry" and dfa is not None


def test_cobol_lowering():
    src = open(os.path.join(HERE, "multilang_fixtures", "cobol", "CUSTINQ.cbl"), encoding="utf-8").read()
    mod = lower_cobol(src)
    fn = mod.ir.functions[0]
    assert fn.name == "CUSTINQ" and fn.params == ["LK-REQUEST"]
    names = [b.meta.get("name") for b in fn.blocks if b.meta.get("kind") == "paragraph"]
    assert names[1:] == ["MAIN-PARA", "SAFE-QUERY", "RUN-PLUGIN", "LOOKUP", "WRITE-REPORT"]
    assert any(b.meta.get("kind") == "if_true" for b in fn.blocks)
    items = mod.cobol.items
    assert items["WS-ENTRY"].occurs == 10 and items["WS-ENTRY"].parent == "WS-TABLE"
    assert items["WS-DB-PASSWORD"].value == "'Tiger2026!'"
    run_dfa(build_cfg(fn), fn)


def test_cobol_free_format_and_numeric_check():
    src = ("IDENTIFICATION DIVISION.\nPROGRAM-ID. P.\nDATA DIVISION.\nWORKING-STORAGE SECTION.\n"
           "01 I PIC 99.\n01 T.\n   05 E PIC X OCCURS 9 TIMES.\n01 X PIC X.\nPROCEDURE DIVISION.\n"
           "MAIN.\n    ACCEPT I. *> index from the terminal\n    IF I > 0 AND I < 10\n        MOVE E(I) TO X\n"
           "    END-IF.\n    MOVE E(I) TO X.\n    GOBACK.\n")
    rep = analyze_source(src, "p.cbl", "cobol")
    assert [(f.rule_id, f.line) for f in rep.active()] == [("SEC054", 15)]


# ── comments for the new languages ──────────────────────────────────────────

@pytest.mark.parametrize("path,marker", [
    ("csharp/ReportsController.cs", '/// <param name="customer">'),
    ("rust/handlers.rs", "/// # Arguments"),
    ("cobol/CUSTINQ.cbl", "      *> MAIN-PARA:"),
])
def test_comments_for_new_languages(path, marker, tmp_path):
    p = os.path.join(HERE, "multilang_fixtures", path)
    r = run_pipeline(p, PipelineLogger(input_file=p))
    assert marker in r.annotated_source
    assert r.ir_module.functions and r.security_report.total_issues > 0
    # idempotent: documenting the annotated file again adds nothing
    again = tmp_path / os.path.basename(p)
    again.write_text(r.annotated_source, encoding="utf-8")
    assert run_pipeline(str(again), PipelineLogger(input_file=str(again))).comments == []


def test_capability_table_names_every_language():
    assert set(CAPABILITIES) == {"python", "java", "csharp", "c", "cpp", "rust", "cobol"}
    for lang, caps in CAPABILITIES.items():
        assert {"parsing", "taint", "rules", "ml_detector", "neuro_symbolic", "rag"} <= set(caps)
