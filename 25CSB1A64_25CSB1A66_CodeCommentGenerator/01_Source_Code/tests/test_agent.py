"""
Tests for the fix-and-verify agent (src/agent).

Every patched result is re-checked here with the analyzer itself and ast.parse,
independently of the agent's own verification.
"""
import ast
import glob
import os
import shutil

import pytest

from src.agent import FIXED, MANUAL, fix_file, fix_source
from src.agent import llm_strategy
from src.agent.source import allowed_lines
from src.agent.strategies import STRATEGIES, Patch, Strategy
from src.agent.verify import changed_outside, verify_patch
from src.security.analyzer import analyze_source

HERE = os.path.dirname(__file__)
AGENT_FIXTURES = os.path.join(HERE, "security_fixtures", "agent")
FIXTURES = os.path.join(HERE, "security_fixtures")


def _read(name):
    with open(os.path.join(AGENT_FIXTURES, name), encoding="utf-8") as fh:
        return fh.read()


def _rules(source):
    return [(f.rule_id, f.function) for f in analyze_source(source).active()]


# ── one fixture per strategy: patched, verified clean, still parsable ─────────

@pytest.mark.parametrize("fixture, rule, strategy, expected_text", [
    ("sqli_concat.py", "SEC005", "sql-param-qmark", 'WHERE name = ?", (name,))'),
    ("sqli_django.py", "SEC005", "sql-param-format", 'WHERE id = %s", (book_id,))'),
    ("cmdi_system.py", "SEC002", "cmd-argv-list", 'subprocess.run(["ping", "-c", "1", host], shell=False, check=True)'),
    ("cmdi_pipe.py", "SEC002", "cmd-shlex-quote", "shlex.quote(str(name))"),
    ("yaml_load.py", "SEC010", "yaml-safe-load", "yaml.safe_load(request.data)"),
    ("hash_md5.py", "SEC004", "hash-sha256", "hashlib.sha256(password.encode())"),
    ("eval_input.py", "SEC001", "eval-literal-eval", 'ast.literal_eval(request.args["expr"])'),
])
def test_each_strategy_fixes_and_verifies(fixture, rule, strategy, expected_text):
    source = _read(fixture)
    assert any(r == rule for r, _ in _rules(source)), "fixture must start vulnerable"
    result = fix_source(source, fixture)
    ast.parse(result.patched)
    assert expected_text in result.patched
    assert not any(r == rule for r, _ in _rules(result.patched)), "analyzer must report it fixed"
    assert [o.status for o in result.outcomes] == [FIXED]
    assert result.outcomes[0].strategy == strategy


def test_imports_are_added_when_a_fix_needs_them():
    assert "import subprocess" in fix_source(_read("cmdi_system.py")).patched
    assert "import shlex" in fix_source(_read("cmdi_pipe.py")).patched
    assert "import ast" in fix_source(_read("eval_input.py")).patched


def test_usedforsecurity_false_is_left_alone():
    patched = fix_source(_read("hash_md5.py")).patched
    assert "hashlib.md5(data, usedforsecurity=False)" in patched


def test_variable_built_query_is_parameterised_at_its_assignment():
    src = ('import sqlite3\nfrom flask import request\n\n\ndef f():\n'
           '    uid = request.form["id"]\n    query = "DELETE FROM t WHERE id = " + uid\n'
           '    final = query\n    sqlite3.connect("a.db").execute(final)\n')
    r = fix_source(src)
    assert 'query = "DELETE FROM t WHERE id = ?"' in r.patched
    assert "execute(final, (uid,))" in r.patched
    assert not _rules(r.patched)


# ── retries ───────────────────────────────────────────────────────────────────

def test_first_strategy_not_applicable_then_second_succeeds():
    result = fix_source(_read("sqli_django.py"))
    attempts = [(a.strategy, a.result) for a in result.outcomes[0].attempts]
    assert attempts == [("sql-param-qmark", "not applicable"), ("sql-param-format", "accepted")]


def test_first_patch_rejected_by_verification_then_second_accepted():
    def useless(ctx):        # produces valid code that still has the vulnerability
        return Patch(ctx.source.replace("def find_user", "def find_user", 1) + "\n# touched\n", "no-op")

    real = next(s for s in STRATEGIES if s.name == "sql-param-qmark")
    strategies = [Strategy("bogus", "SEC005", "leaves the bug in place", useless), real]
    result = fix_source(_read("sqli_concat.py"), strategies=strategies)
    o = result.outcomes[0]
    assert [(a.strategy, a.result) for a in o.attempts] == [("bogus", "rejected"), ("sql-param-qmark", "accepted")]
    assert o.status == FIXED and o.rejected == 1
    failed = {c["name"] for c in o.attempts[0].checks if not c["ok"]}
    assert "finding gone" in failed
    assert any(s.phase == "decide" and "Reject bogus" in s.message for s in result.steps)


def test_max_attempts_limits_the_strategies_tried():
    result = fix_source(_read("sqli_django.py"), max_attempts=1)
    o = result.outcomes[0]
    assert len(o.attempts) == 1 and o.status == MANUAL


# ── giving up ─────────────────────────────────────────────────────────────────

def test_nothing_works_marks_needs_manual_fix_and_leaves_code():
    source = _read("sqli_order_by.py")
    result = fix_source(source)
    assert [o.status for o in result.outcomes] == [MANUAL]
    assert "allow-list" in result.outcomes[0].reason
    assert result.patched == source and result.findings_after == result.findings_before


def test_rule_without_strategy_is_manual_with_remediation():
    src = "import pickle\nfrom flask import request\n\n\ndef load():\n    return pickle.loads(request.data)\n"
    result = fix_source(src)
    assert result.outcomes[0].status == MANUAL
    assert result.outcomes[0].attempts == []
    assert "no automatic fix for SEC009" in result.outcomes[0].reason


# ── scope ─────────────────────────────────────────────────────────────────────

def test_verification_rejects_a_patch_outside_the_function():
    source = _read("sqli_concat.py")
    report = analyze_source(source)
    finding = report.active()[0]
    good = fix_source(source).patched
    bad = good.replace('return "SELECT 1"', 'return "SELECT 2"')
    check = verify_patch(source, bad, finding, report)
    assert not check.ok
    assert not next(c for c in check.checks if c.name == "only the reported function changed").ok


def test_changed_outside_allows_only_new_imports():
    original = "import os\n\n\ndef f():\n    return 1\n\n\ndef g():\n    return 2\n"
    allowed = allowed_lines(ast.parse(original), "f", len(original.splitlines()))
    assert changed_outside(original, original.replace("return 1", "return 3"), allowed) == []
    assert changed_outside(original, "import ast\n" + original, allowed) == []
    assert changed_outside(original, original.replace("return 2", "return 3"), allowed) == [9]
    assert changed_outside(original, original + "x = 1\n", allowed) != []


@pytest.mark.parametrize("name", ["sqli_vulnerable.py", "cmdi_vulnerable.py",
                                  "code_deser_vulnerable.py", "patterns_mixed.py"])
def test_agent_never_changes_code_outside_reported_functions(name):
    path = os.path.join(FIXTURES, name)
    result = fix_file(path)
    original_tree = ast.parse(result.original)
    n = len(result.original.splitlines())
    allowed = set()
    for o in result.outcomes:
        if o.status == FIXED:
            allowed |= allowed_lines(original_tree, o.function, n)
    assert changed_outside(result.original, result.patched, allowed) == []
    ast.parse(result.patched)
    assert result.findings_after < result.findings_before


# ── no-ops ────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("path", sorted(glob.glob(os.path.join(FIXTURES, "*_safe.py"))))
def test_safe_file_is_left_unchanged(path):
    result = fix_file(path)
    assert result.outcomes == []
    assert result.patched == result.original and not result.changed and result.diff() == ""


def test_input_file_is_never_modified(tmp_path):
    target = tmp_path / "vuln.py"
    shutil.copy(os.path.join(AGENT_FIXTURES, "cmdi_system.py"), target)
    before = target.read_text(encoding="utf-8")
    result = fix_file(str(target))
    assert result.changed
    assert target.read_text(encoding="utf-8") == before


def test_unparsable_source_reports_error_without_patching():
    result = fix_source("def broken(:\n    pass\n")
    assert result.parse_error and result.patched == result.original and not result.outcomes


# ── trace ─────────────────────────────────────────────────────────────────────

def test_trace_records_every_phase_and_streams_to_callback():
    seen = []
    result = fix_source(_read("cmdi_pipe.py"), on_step=seen.append)
    phases = [s.phase for s in result.steps]
    for phase in ("observe", "finding", "plan", "act", "decide", "done"):
        assert phase in phases
    assert seen == result.steps
    d = result.to_dict()
    assert d["summary"]["fixed"] == 1 and d["diff"].startswith("---")


# ── optional LLM strategy (no network: the model is stubbed) ─────────────────

def test_llm_is_skipped_quietly_when_no_model(monkeypatch):
    monkeypatch.setattr(llm_strategy, "find_model", lambda: None)
    result = fix_source(_read("sqli_order_by.py"), use_llm=True)
    assert [a.strategy for a in result.outcomes[0].attempts] == ["sql-param-qmark", "sql-param-format"]


def test_llm_rewrite_goes_through_the_same_checks(monkeypatch):
    monkeypatch.setattr(llm_strategy, "find_model", lambda: "stub-coder")
    good = ('```python\ndef list_users():\n    column = request.args["sort"]\n'
            '    if column not in ("name", "email"):\n        column = "name"\n'
            '    conn = sqlite3.connect("app.db")\n'
            '    return conn.execute("SELECT * FROM users ORDER BY " + column).fetchall()\n```')
    monkeypatch.setattr(llm_strategy, "_ask", lambda model, prompt: good)
    result = fix_source(_read("sqli_order_by.py"), use_llm=True)
    o = result.outcomes[0]
    # tried only after both templates declined, and accepted only because all four checks passed
    assert [a.strategy for a in o.attempts] == ["sql-param-qmark", "sql-param-format", "llm-rewrite"]
    assert o.status == FIXED and all(c["ok"] for c in o.attempts[-1].checks)
    assert 'if column not in ("name", "email"):' in result.patched
    assert not any(r == "SEC005" for r, _ in _rules(result.patched))


def test_llm_reply_that_keeps_the_bug_is_rejected(monkeypatch):
    monkeypatch.setattr(llm_strategy, "find_model", lambda: "stub-coder")
    same = "```python\n" + _read("sqli_order_by.py").split("\n\n\n", 1)[1] + "```"
    monkeypatch.setattr(llm_strategy, "_ask", lambda model, prompt: same)
    result = fix_source(_read("sqli_order_by.py"), use_llm=True)
    o = result.outcomes[0]
    assert (o.attempts[-1].strategy, o.attempts[-1].result) == ("llm-rewrite", "rejected")
    assert o.status == MANUAL and result.patched == result.original


# ── CLIs ──────────────────────────────────────────────────────────────────────

def test_agent_cli_writes_patched_copy(tmp_path, capsys):
    from src.agent.__main__ import main
    out = tmp_path / "patched.py"
    assert main([os.path.join(AGENT_FIXTURES, "yaml_load.py"), "--out", str(out)]) == 0
    text = capsys.readouterr().out
    assert "fixed by yaml-safe-load" in text and "+++" in text
    assert "yaml.safe_load(request.data)" in out.read_text(encoding="utf-8")


def test_security_cli_fix_flag(capsys):
    from src.security.__main__ import main
    assert main([os.path.join(AGENT_FIXTURES, "eval_input.py"), "--fix", "--no-trace"]) == 0
    text = capsys.readouterr().out
    assert "Fix-and-verify agent" in text and "eval-literal-eval" in text
