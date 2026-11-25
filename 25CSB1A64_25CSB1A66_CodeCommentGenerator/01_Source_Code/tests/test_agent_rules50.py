"""Fix strategies for the newer rules: the agent must fix each vulnerable snippet,
the verifier must accept the patch, and the rule must be gone afterwards."""
import textwrap

import pytest

from src.agent.fixer import FIXED, fix_source
from src.security.analyzer import analyze_source
from tests.test_security_rules50 import CASES

FIXABLE = {"SEC024": "regex-escape", "SEC029": "debug-off", "SEC030": "tls-verify-on",
           "SEC042": "tar-data-filter", "SEC043": "jinja-autoescape", "SEC044": "cookie-secure"}


@pytest.mark.parametrize("rule", sorted(FIXABLE))
def test_agent_fixes_and_verifies(rule):
    source = textwrap.dedent(CASES[rule][0])
    result = fix_source(source, "case.py")
    outcome = next(o for o in result.outcomes if o.rule_id == rule)
    assert outcome.status == FIXED, outcome.reason
    assert outcome.strategy == FIXABLE[rule]
    after = {f.rule_id for f in analyze_source(result.patched, "case.py").active()}
    assert rule not in after
    compile(result.patched, "case.py", "exec")


def test_cookie_fix_sets_both_flags():
    source = textwrap.dedent(CASES["SEC044"][0])
    patched = fix_source(source, "case.py").patched
    assert "secure=True" in patched and "httponly=True" in patched
