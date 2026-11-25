"""
Large-file corpus: 50 generated files of ~1,800-2,400 lines (about 101,000 lines).

Each file plants 10 vulnerabilities (every rule SEC001-SEC050 is planted in 10
files) and 10 safe twins among ordinary application code. The expected
(rule, line) pairs come from the ``#!`` markers in tests/large_corpus/snippets.py,
written by hand; they are not derived from the analyzer.

Per file the analyzer must report exactly the planted pairs: every planted
vulnerability found, and nothing else (no finding on a safe twin or on the
ordinary code). A second set of tests runs the full comment-generation pipeline
on a sample of the files.
"""
import ast
import json
import os

import pytest

from src.logger import PipelineLogger
from src.main import run_pipeline
from src.security.analyzer import analyze_file
from tests.large_corpus.generate import CASES_DIR, MANIFEST, build_case

with open(MANIFEST, encoding="utf-8") as _fh:
    CORPUS = json.load(_fh)["cases"]
IDS = [c["file"][:-3] for c in CORPUS]


def test_corpus_shape():
    assert len(CORPUS) == 50
    assert all(c["lines"] >= 1500 for c in CORPUS)
    planted = [e["rule"] for c in CORPUS for e in c["expected"]]
    assert len(planted) == 500
    assert {r: planted.count(r) for r in set(planted)} == {f"SEC{n:03d}": 10 for n in range(1, 51)}


@pytest.mark.parametrize("index", range(1, 51), ids=IDS)
def test_files_match_the_generator(index):
    """The checked-in files and manifest are exactly what generate.py produces."""
    fname, source, expected, twins = build_case(index)
    case = CORPUS[index - 1]
    assert case["file"] == fname and case["expected"] == expected and case["safe_twins"] == twins
    with open(os.path.join(CASES_DIR, fname), encoding="utf-8", newline="") as fh:
        assert fh.read() == source


@pytest.mark.parametrize("case", CORPUS, ids=IDS)
def test_planted_vulnerabilities_found_and_nothing_else(case):
    report = analyze_file(os.path.join(CASES_DIR, case["file"]))
    assert report.parse_error is None
    got = {(f.rule_id, f.line) for f in report.active()}
    expected = {(e["rule"], e["line"]) for e in case["expected"]}
    assert expected - got == set(), "missed planted vulnerabilities"
    assert got - expected == set(), "findings outside the planted lines"


@pytest.mark.parametrize("case", CORPUS[::10], ids=IDS[::10])
def test_comment_pipeline_documents_every_definition(case):
    path = os.path.join(CASES_DIR, case["file"])
    result = run_pipeline(path, PipelineLogger(input_file=path))
    tree = ast.parse(result.annotated_source)
    defs = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
    assert len(defs) > 50
    assert all(ast.get_docstring(n) for n in defs)
    assert {(i.pattern_id, i.lineno) for i in result.security_report.issues} >= \
        {(e["rule"], e["line"]) for e in case["expected"]}
