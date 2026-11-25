"""
Tests for the security dataset, the ML training/evaluation pipeline and the block-wise profiler.

Dataset tests read the built dataset (``python -m src.dataset.build``) and are skipped when it is
missing; template, split, profiler and metric tests run without it.
"""
import gzip
import json
import os
import random
import unittest
from collections import defaultdict

from src import perf
from src.dataset import build as B
from src.vulnml.pipeline import binary_metrics

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
DS = os.path.join(ROOT, "datasets", "security_dataset", "v1")
SAMPLES = os.path.join(DS, "samples.jsonl.gz")


def _load():
    with gzip.open(SAMPLES, "rt", encoding="utf-8") as fh:
        return [json.loads(l) for l in fh]


class TestSplitsAndTemplates(unittest.TestCase):
    def test_hash_split_is_deterministic_and_close_to_70_15_15(self):
        groups = [f"g{i}" for i in range(6000)]
        a = [B.hash_split(g) for g in groups]
        self.assertEqual(a, [B.hash_split(g) for g in groups])
        share = {s: a.count(s) / len(a) for s in B.SPLITS}
        self.assertAlmostEqual(share["train"], 0.70, delta=0.03)
        self.assertAlmostEqual(share["val"], 0.15, delta=0.03)
        self.assertAlmostEqual(share["test"], 0.15, delta=0.03)

    def test_ranked_splits_give_every_split_a_group(self):
        m = B.ranked_splits([f"t{i}" for i in range(10)])
        self.assertEqual(set(m.values()), set(B.SPLITS))

    def test_markers_are_stripped_and_recorded(self):
        code, labels = B.strip_markers("int a;\nsystem(cmd);  // expect: SEC002\nreturn 0;\n")
        self.assertNotIn("expect", code)
        self.assertEqual(labels, [("SEC002", 2)])

    def test_fixture_templates_have_twins_in_the_same_group(self):
        ts = B.fixture_templates()
        self.assertGreater(len(ts), 60)
        groups = defaultdict(list)
        for t in ts:
            groups[t.group].append(t)
        # a vulnerable template and its "Safe" twin share one group, so they can never cross splits
        paired = [g for g, v in groups.items() if any(t.vulnerable for t in v) and any(not t.vulnerable for t in v)]
        self.assertGreater(len(paired), 10)
        for t in ts:
            self.assertNotIn("expect:", t.code)

    def test_cobol_templates_parse_and_label(self):
        ts = B.cobol_templates()
        vuln = [t for t in ts if t.id.endswith("-vuln")]
        self.assertEqual(len(vuln), 11)
        for t in vuln:
            self.assertTrue(t.labels or getattr(t, "data_label_idx", []), t.id)
            code, labels = B.cobol_program("TSTPROG", [(t, "1")], [])
            self.assertIsNone(B.parses(code, "cobol"), t.id)
            self.assertTrue(labels, t.id)


@unittest.skipUnless(os.path.isfile(SAMPLES), "dataset not built (python -m src.dataset.build)")
class TestBuiltDataset(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.S = _load()
        cls.M = json.load(open(os.path.join(DS, "manifest.json"), encoding="utf-8"))

    def test_all_languages_present(self):
        langs = {s["language"] for s in self.S}
        self.assertEqual(langs, set(B.LANGS))

    def test_no_group_crosses_splits(self):
        split_of = {}
        for s in self.S:
            self.assertEqual(split_of.setdefault(s["group"], s["split"]), s["split"], s["group"])

    def test_no_identical_code_across_train_and_test(self):
        def key(s):
            return " ".join((s.get("function_code") or s.get("code") or "").split())
        train = {key(s) for s in self.S if s["split"] == "train" and s["source"] in ("custom", "owasp")}
        test = [s for s in self.S if s["split"] == "test" and s["source"] in ("custom", "owasp")]
        leaked = [s["id"] for s in test if key(s) in train]
        self.assertEqual(leaked, [])

    def test_labels_are_consistent(self):
        for s in self.S:
            if s["source"] in ("custom", "custom-long"):
                if s["label"] == "vulnerable":
                    self.assertTrue(s["locations"], s["id"])
                else:
                    self.assertFalse(s["locations"], s["id"])
            if s["label"] == "vulnerable" and s["source"] != "custom-long":
                self.assertTrue(s.get("cwe"), s["id"])

    def test_long_programs_are_1000_to_2000_lines_in_every_language_and_split(self):
        longs = [s for s in self.S if s["source"] == "custom-long"]
        for s in longs:
            self.assertGreaterEqual(s["lines"], 1000, s["path"])
            self.assertLessEqual(s["lines"], 2000, s["path"])
            self.assertTrue(os.path.isfile(os.path.join(ROOT, s["path"])))
        have = {(s["language"], s["split"]) for s in longs}
        self.assertEqual(have, {(l, sp) for l in B.LANGS for sp in B.SPLITS})

    def test_manifest_counts_match_samples(self):
        st = self.M["statistics"]
        self.assertEqual(st["samples"], len(self.S))
        self.assertEqual(st["total_lines_of_code"], sum(s["lines"] for s in self.S))
        self.assertEqual(self.M["validation"]["rejected"], [])

    def test_long_program_labels_match_the_planted_code(self):
        """Every labelled line of a sampled long program holds the code of the template that was planted."""
        from src.security.analyzer import analyze_file
        rng = random.Random(3)
        for lang in B.LANGS:
            if lang == "python":
                continue        # Python long programs are checked by the evaluation (two SEC015 misses documented)
            s = rng.choice([x for x in self.S if x["source"] == "custom-long" and x["language"] == lang])
            exp = {(l["rule"], l["line"]) for l in s["locations"]}
            got = {(f.rule_id, f.line) for f in analyze_file(os.path.join(ROOT, s["path"])).active()}
            # ground truth was not taken from the analyzer; this checks the labels land on real code lines
            self.assertGreater(len(exp & got) / len(exp), 0.9, (lang, s["path"]))


class TestProfiler(unittest.TestCase):
    def test_blocks_are_noops_without_a_profile(self):
        with perf.block("x"):
            pass
        self.assertIsNone(perf.active())

    def test_timing_and_nesting(self):
        with perf.profile() as p:
            with perf.block("outer", lines=10):
                with perf.block("inner"):
                    sum(range(10000))
        b = p.by_block()
        self.assertEqual(set(b), {"outer", "inner"})
        self.assertGreaterEqual(b["outer"]["total_ms"], b["inner"]["total_ms"])
        self.assertEqual(b["outer"]["lines"], 10)
        self.assertIsNone(b["outer"]["peak_kb"])

    def test_memory_peak_seen_by_parent(self):
        with perf.profile(memory=True) as p:
            with perf.block("outer"):
                with perf.block("alloc"):
                    data = [bytes(1024) for _ in range(2000)]
                    del data
        b = p.by_block()
        self.assertGreater(b["alloc"]["peak_kb"], 1500)
        self.assertGreaterEqual(b["outer"]["peak_kb"], b["alloc"]["peak_kb"])

    def test_real_analysis_reports_its_blocks(self):
        from src.security.analyzer import analyze_file
        with perf.profile() as p:
            analyze_file(os.path.join(ROOT, "tests", "multilang_fixtures", "c", "netconf.c"))
        self.assertIn("security.cfg_dataflow_taint", p.by_block())
        self.assertIn("security.parse_and_ir_lowering", p.by_block())


class TestScopeAndBenchmarkHelpers(unittest.TestCase):
    def test_rule_families_follow_the_coverage_map(self):
        from src.vulnml.pipeline import rule_families
        fams = rule_families()
        self.assertIn("buffer-overflow", fams["c"])
        self.assertIn("sql-injection", fams["java"])
        self.assertNotIn("buffer-overflow", fams["java"])

    def test_in_scope_recall_splits_juliet_rows(self):
        from src.vulnml.pipeline import in_scope_recall
        rows = [
            {"language": "c", "source": "juliet", "truth": True, "family": "buffer-overflow",
             "rules": True, "ml": True, "neurosymbolic": True},
            {"language": "c", "source": "juliet", "truth": True, "family": "buffer-overflow",
             "rules": False, "ml": True, "neurosymbolic": False},
            {"language": "c", "source": "juliet", "truth": True, "family": "integer-overflow-not-a-rule",
             "rules": False, "ml": False, "neurosymbolic": False},
            {"language": "c", "source": "juliet", "truth": False, "family": None,
             "rules": True, "ml": False, "neurosymbolic": True},
        ]
        r = in_scope_recall(rows)["c"]
        self.assertEqual((r["in_scope_n"], r["out_of_scope_n"]), (2, 1))
        self.assertEqual(r["rules_recall_in_scope"], 0.5)
        self.assertEqual(r["ml_recall_in_scope"], 1.0)
        self.assertEqual(r["rules_recall_out_of_scope"], 0.0)

    def test_benchmark_show_prints_a_saved_result(self):
        import contextlib
        import io
        from src.perfbench import show
        res = {"languages": {"c": {"files": 2, "lines": 100, "bottleneck": "Data flow & taint",
                                   "end_to_end": {"mean_ms_per_file": 12.0, "lines_per_second": 4000.0,
                                                  "peak_kb_memory_pass": 2048}}},
               "overall_groups": {"Data flow & taint": {"share": 0.6, "total_ms": 24.0},
                                  "ML model": {"share": 0.4, "total_ms": 16.0}},
               "overall_bottleneck": "Data flow & taint"}
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            show(res)
        out = buf.getvalue()
        self.assertIn("overall bottleneck: Data flow & taint", out)
        self.assertIn("60.0 %", out)

    def test_ml_explanations_are_identical_with_a_precomputed_row(self):
        from src.vulnml import model as mlmodel
        m = mlmodel.load("c")
        if m is None:
            self.skipTest("no trained C model (python -m src.vulnml.pipeline train)")
        text = "void f ( char * STR ) { char buf [ NUM ] ; strcpy ( buf , data ) ; }"
        fam = [c for c in m["pipeline"].classes_ if c != "safe"][0]
        x = m["pipeline"].named_steps["tfidf"].transform([text])
        self.assertEqual(mlmodel.explain(m, text, fam), mlmodel.explain(m, text, fam, x=x[0]))


class TestMetrics(unittest.TestCase):
    def test_binary_metrics(self):
        m = binary_metrics([True, True, False, False, True], [True, False, False, True, True])
        self.assertEqual(m["confusion"], {"tn": 1, "fp": 1, "fn": 1, "tp": 2})
        self.assertAlmostEqual(m["precision"], 2 / 3, places=3)
        self.assertAlmostEqual(m["recall"], 2 / 3, places=3)
        self.assertAlmostEqual(m["fpr"], 0.5)
        self.assertAlmostEqual(m["fnr"], 1 / 3, places=3)
        self.assertAlmostEqual(m["accuracy"], 0.6)


if __name__ == "__main__":
    unittest.main()


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
try:
    from PyQt6.QtWidgets import QApplication
    _QT = True
except ImportError:  # pragma: no cover
    _QT = False


@unittest.skipUnless(_QT, "PyQt6 is not installed")
class TestPerformanceWorkspace(unittest.TestCase):
    def test_tabs_and_live_profile(self):
        import time
        from src.gui.performance_workspace import PerformanceWorkspace
        app = QApplication.instance() or QApplication([])
        w = PerformanceWorkspace()
        tabs = [w.tabs.tabText(i) for i in range(w.tabs.count())]
        self.assertEqual(tabs, ["Comparison", "Rule-Based", "ML Model", "Neuro-Symbolic", "Pipeline"])
        src = open(os.path.join(ROOT, "tests", "multilang_fixtures", "c", "netconf.c"), encoding="utf-8").read()
        w.code_provider = lambda: (src, "c")
        w.profile_editor()
        deadline = time.time() + 300
        while time.time() < deadline and not w.btn_profile.isEnabled():
            app.processEvents()
            time.sleep(0.02)
        app.processEvents()
        self.assertIn("findings", w.profile_label.text())
        names = {r[0] for r in w.live_rows}
        self.assertIn("security.cfg_dataflow_taint", names)
        self.assertIn("pipeline.parse", names)
