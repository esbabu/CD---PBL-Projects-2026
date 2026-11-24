"""Tests for Stage S0: Syntax Gate and guards."""
import pytest
from optagent.syntax.gate import SyntaxGate
from optagent.syntax.guards import token_preservation_guard, budget_guard, progress_guard


def test_syntax_gate_valid_code_zero_edits():
    valid_py = "def add(a: int, b: int) -> int:\n    return a + b\n"
    gate = SyntaxGate(mode="auto")
    repaired, report = gate.process(valid_py, "python")
    assert report.ok is True
    assert report.llm_calls == 0
    assert report.tokens_changed == 0
    assert repaired == valid_py
    assert report.diff == ""


def test_syntax_gate_missing_colon_heuristic():
    broken_py = "def solve(n)\n    return n * 2\n"
    expected_py = "def solve(n):\n    return n * 2\n"
    gate = SyntaxGate(mode="auto")
    repaired, report = gate.process(broken_py, "python")
    assert report.ok is True
    assert report.llm_calls == 0
    assert repaired == expected_py
    assert len(report.rounds) >= 1
    assert any("colon" in r.method for r in report.rounds)


def test_syntax_gate_smart_quotes_and_markdown_fence():
    broken_py = "```python\ndef get_greeting():\n    return “hello world”\n```"
    expected_py = 'def get_greeting():\n    return "hello world"'
    gate = SyntaxGate(mode="auto")
    repaired, report = gate.process(broken_py, "python")
    assert report.ok is True
    assert report.llm_calls == 0
    assert repaired == expected_py


def test_syntax_gate_unbalanced_parenthesis():
    broken_py = 'print("hello world"'
    expected_py = 'print("hello world")'
    gate = SyntaxGate(mode="auto")
    repaired, report = gate.process(broken_py, "python")
    assert report.ok is True
    assert report.llm_calls == 0
    assert repaired == expected_py


def test_syntax_gate_python2_print():
    broken_py = 'print "hello world"'
    expected_py = 'print("hello world")'
    gate = SyntaxGate(mode="auto")
    repaired, report = gate.process(broken_py, "python")
    assert report.ok is True
    assert report.llm_calls == 0
    assert repaired == expected_py


def test_syntax_gate_tab_spaces_mix():
    broken_py = "def count():\n\tval = 1\n    return val\n"
    expected_py = "def count():\n    val = 1\n    return val\n"
    gate = SyntaxGate(mode="auto")
    repaired, report = gate.process(broken_py, "python")
    assert report.ok is True
    assert report.llm_calls == 0
    assert repaired == expected_py


def test_syntax_gate_two_errors_sequential_repair():
    # Error 1: missing colon on def
    # Error 2: missing closing paren on hashlib.md5
    broken_py = "def check(pw)\n    val = hashlib.md5(pw.encode()\n"
    # Colon fixer fixes line 1, paren fixer fixes line 2
    gate = SyntaxGate(mode="auto")
    repaired, report = gate.process(broken_py, "python")
    assert report.ok is True
    assert report.llm_calls == 0
    assert repaired == "def check(pw):\n    val = hashlib.md5(pw.encode())\n"


def test_guard_rejects_cheating_patch_renaming_variable():
    orig = "def compute(x):\n    return x + 1"
    # Cheating: renamed x to y
    cheated = "def compute(y):\n    return y + 1"
    ok, reason = token_preservation_guard(orig, cheated, "python")
    assert ok is False
    assert "Token preservation violated" in reason


def test_guard_rejects_cheating_patch_changing_operator():
    orig = "def compute(x):\n    return x + 1"
    # Cheating: changed + to *
    cheated = "def compute(x):\n    return x * 1"
    ok, reason = token_preservation_guard(orig, cheated, "python")
    assert ok is False


def test_guard_rejects_cheating_patch_deleting_statement():
    orig = "def compute(x):\n    y = x * 2\n    return y"
    # Cheating: deleted statement
    cheated = "def compute(x):\n    return x"
    ok, reason = token_preservation_guard(orig, cheated, "python")
    assert ok is False


def test_llm_syntax_patcher_with_fake_llm_accepts_valid_patch():
    broken_py = "def calculate(a, b\n    return a + b\n"
    fake_response = {
        "edits": [
            {
                "line": 1,
                "old": "def calculate(a, b",
                "new": "def calculate(a, b):",
                "reason": "Add missing closing delimiter and colon",
            }
        ]
    }
    gate = SyntaxGate(mode="auto", llm_gateway=lambda p: fake_response)
    repaired, report = gate.process(broken_py, "python")
    assert report.ok is True
    assert "def calculate(a, b):" in repaired


def test_llm_syntax_patcher_rejects_malicious_rewrite():
    broken_py = "def calculate(a, b\n    return a + b\n"
    # Fake LLM attempts to replace logic with pass
    malicious_response = {
        "edits": [
            {
                "line": 2,
                "old": "    return a + b",
                "new": "    pass",
                "reason": "Wipe logic",
            }
        ]
    }
    gate = SyntaxGate(mode="auto", llm_gateway=lambda p: malicious_response)
    repaired, report = gate.process(broken_py, "python")
    # Must reject the malicious patch!
    assert any("guard failed" in (r.reject_reason or "") for r in report.rounds if r.method == "llm")
