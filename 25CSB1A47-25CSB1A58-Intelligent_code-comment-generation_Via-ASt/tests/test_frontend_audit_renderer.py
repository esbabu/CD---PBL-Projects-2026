"""Frontend browser tests for the Unified Audit Renderer and Contract.

Tests the 7 required frontend render states in headless Chrome via Playwright:
1. all pass: all checks pass -> renders 'PASSED'
2. one failure: one check fails -> renders 'FAILED', never 'VERIFIED'
3. missing audit: final_audit is null/omitted -> renders 'NOT RUN', never 'VERIFIED'
4. no code change: code_changed is false -> renders 'All Checks Verified' only if audit passed
5. static-only audit: verification_level is 'static_only' -> visibly labelled 'STATIC ONLY'
6. behavioral test skipped: behavioral check is 'not_run' -> visibly labelled 'NOT RUN'
7. failed workflow: workflow status is 'failed' -> renders failure, never 'VERIFIED'
"""

from __future__ import annotations

import os
import threading
import pytest

pytest.importorskip("playwright.sync_api")
from playwright.sync_api import sync_playwright
from werkzeug.serving import make_server

from backend.app import create_app

CHROME_PATH = os.getenv("PLAYWRIGHT_CHROME_PATH") or os.getenv("PLAYWRIGHT_EXECUTABLE_PATH")


@pytest.fixture(scope="module")
def live_server():
    """Start an ephemeral background Flask server for real browser testing."""
    app = create_app({
        "TESTING": True,
        "REQUIRE_API_KEY": False,
    })
    server = make_server("127.0.0.1", 0, app)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{port}"
    yield base_url
    server.shutdown()


@pytest.fixture(scope="module")
def browser_context():
    """Launch headless Chrome using Playwright."""
    launch_kwargs = {
        "headless": True,
        "args": ["--no-sandbox", "--disable-dev-shm-usage"],
    }
    if CHROME_PATH:
        launch_kwargs["executable_path"] = CHROME_PATH
    with sync_playwright() as p:
        browser = p.chromium.launch(**launch_kwargs)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        yield context
        browser.close()


class TestFrontendAuditRenderer:
    """Browser DOM tests for the unified verification contract and renderer."""

    def test_case_1_all_pass_renders_passed(self, live_server: str, browser_context):
        """All checks pass -> table renders 'PASSED' badges and executive summary shows 'PASSED'."""
        page = browser_context.new_page()
        page.goto(live_server)

        session_payload = {
            "status": "completed",
            "task": "Full multi-agent review",
            "original_code": "def f(): return 1\n",
            "current_code": "def f():\n    '''Return 1.'''\n    return 1\n",
            "final_code": "def f():\n    '''Return 1.'''\n    return 1\n",
            "code_changed": True,
            "final_audit": {
                "schema_version": 1,
                "status": "passed",
                "verification_level": "full",
                "checks": {
                    "syntax": {"status": "passed", "evidence": "AST valid", "details": "ok"},
                    "definitions": {"status": "passed", "evidence": "Preserved", "details": "ok"},
                    "security": {"status": "passed", "evidence": "Clean", "details": "ok"},
                    "types": {"status": "passed", "evidence": "Clean", "details": "ok"},
                    "behavior": {"status": "passed", "evidence": "Assertions passed", "details": "ok"},
                    "approval": {"status": "passed", "evidence": "Approved", "details": "ok"},
                },
                "summary": "Independent verification: PASSED.",
                "failures": [],
                "warnings": [],
            },
        }

        page.evaluate("(data) => { renderResultsCenter(data); }", session_payload)

        ver_html = page.locator("#results-verification-content").inner_html()
        assert "FULL VERIFICATION" in ver_html
        assert "PASSED" in ver_html
        assert "FAILED" not in ver_html

        rep_html = page.locator("#results-report-content").inner_html()
        assert "PASSED (FULL)" in rep_html
        assert "VERIFIED" not in rep_html or "FULL VERIFICATION" in ver_html
        page.close()

    def test_case_2_one_failure_renders_failed_never_verified(self, live_server: str, browser_context):
        """One check failure (security finding) -> renders 'FAILED', NEVER 'VERIFIED'."""
        page = browser_context.new_page()
        page.goto(live_server)

        session_payload = {
            "status": "completed",
            "task": "Security review",
            "original_code": "eval(x)\n",
            "current_code": "eval(x)\n",
            "code_changed": False,
            "final_audit": {
                "schema_version": 1,
                "status": "failed",
                "verification_level": "static_only",
                "checks": {
                    "syntax": {"status": "passed", "evidence": "AST valid", "details": "ok"},
                    "definitions": {"status": "passed", "evidence": "Preserved", "details": "ok"},
                    "security": {"status": "failed", "evidence": "CWE-95 Eval Injection", "details": "Vulnerable"},
                    "types": {"status": "passed", "evidence": "Clean", "details": "ok"},
                    "behavior": {"status": "not_run", "evidence": "Not run", "details": "Skipped"},
                    "approval": {"status": "passed", "evidence": "No change", "details": "ok"},
                },
                "summary": "Independent verification: FAILED.",
                "failures": ["SECURITY: CWE-95 Eval Injection"],
                "warnings": [],
            },
        }

        page.evaluate("(data) => { renderResultsCenter(data); }", session_payload)

        ver_html = page.locator("#results-verification-content").inner_html()
        assert "FAILED" in ver_html
        assert "CWE-95 Eval Injection" in ver_html

        rep_html = page.locator("#results-report-content").inner_html()
        assert "FAILED" in rep_html
        assert "VERIFIED" not in rep_html
        page.close()

    def test_case_3_missing_audit_renders_not_run_never_verified(self, live_server: str, browser_context):
        """Missing or null audit -> renders 'NOT RUN', NEVER 'VERIFIED'."""
        page = browser_context.new_page()
        page.goto(live_server)

        session_payload = {
            "status": "completed",
            "task": "Quick parse",
            "original_code": "x = 1\n",
            "current_code": "x = 1\n",
            "code_changed": False,
            "final_audit": None,  # Missing audit!
        }

        page.evaluate("(data) => { renderResultsCenter(data); }", session_payload)

        ver_html = page.locator("#results-verification-content").inner_html()
        assert "NOT RUN" in ver_html

        rep_html = page.locator("#results-report-content").inner_html()
        assert "NOT RUN" in rep_html
        assert "VERIFIED" not in rep_html
        page.close()

    def test_case_4_no_code_change_clean_vs_unresolved(self, live_server: str, browser_context):
        """no code change: clean audit shows 'All Checks Verified', failed audit shows 'Verification Unresolved'."""
        page = browser_context.new_page()
        page.goto(live_server)

        # 4a. Clean audit with no code change
        clean_session = {
            "status": "completed",
            "original_code": "def f(): return 1\n",
            "current_code": "def f(): return 1\n",
            "final_code": "def f(): return 1\n",
            "code_changed": False,
            "final_audit": {
                "schema_version": 1,
                "status": "passed",
                "verification_level": "static_only",
                "checks": {
                    "syntax": {"status": "passed", "evidence": "Valid", "details": "ok"},
                    "definitions": {"status": "passed", "evidence": "Preserved", "details": "ok"},
                    "security": {"status": "passed", "evidence": "Clean", "details": "ok"},
                    "types": {"status": "passed", "evidence": "Clean", "details": "ok"},
                    "behavior": {"status": "not_run", "evidence": "Skipped", "details": "ok"},
                    "approval": {"status": "passed", "evidence": "No change", "details": "ok"},
                },
            },
        }
        page.evaluate("(data) => { renderResultsCenter(data); }", clean_session)
        empty_diff_html = page.locator("#results-empty-diff").inner_html()
        assert "All Checks Verified" in empty_diff_html

        # 4b. Failed audit with no code change (e.g. read-only security scan that found vulnerabilities)
        failed_session = {
            "status": "completed",
            "original_code": "eval(x)\n",
            "current_code": "eval(x)\n",
            "final_code": "eval(x)\n",
            "code_changed": False,
            "final_audit": {
                "schema_version": 1,
                "status": "failed",
                "verification_level": "static_only",
                "checks": {
                    "syntax": {"status": "passed", "evidence": "Valid", "details": "ok"},
                    "definitions": {"status": "passed", "evidence": "Preserved", "details": "ok"},
                    "security": {"status": "failed", "evidence": "Injection", "details": "flaw"},
                    "types": {"status": "passed", "evidence": "Clean", "details": "ok"},
                    "behavior": {"status": "not_run", "evidence": "Skipped", "details": "ok"},
                    "approval": {"status": "passed", "evidence": "No change", "details": "ok"},
                },
            },
        }
        page.evaluate("(data) => { renderResultsCenter(data); }", failed_session)
        empty_diff_html = page.locator("#results-empty-diff").inner_html()
        assert "Verification Unresolved" in empty_diff_html
        assert "All Checks Verified" not in empty_diff_html
        page.close()

    def test_case_5_static_only_audit_visibly_labelled(self, live_server: str, browser_context):
        """Static-only checks must be visibly labelled 'STATIC ONLY'."""
        page = browser_context.new_page()
        page.goto(live_server)

        session_payload = {
            "status": "completed",
            "original_code": "def f(): return 1\n",
            "current_code": "def f(): return 1\n",
            "final_audit": {
                "schema_version": 1,
                "status": "passed",
                "verification_level": "static_only",
                "checks": {
                    "syntax": {"status": "passed", "evidence": "AST valid", "details": "ok"},
                    "definitions": {"status": "passed", "evidence": "Preserved", "details": "ok"},
                    "security": {"status": "passed", "evidence": "Clean", "details": "ok"},
                    "types": {"status": "passed", "evidence": "Clean", "details": "ok"},
                    "behavior": {"status": "not_run", "evidence": "Skipped", "details": "STATIC ONLY"},
                    "approval": {"status": "passed", "evidence": "Read-only", "details": "ok"},
                },
            },
        }
        page.evaluate("(data) => { renderResultsCenter(data); }", session_payload)

        ver_html = page.locator("#results-verification-content").inner_html()
        assert "STATIC ONLY" in ver_html

        rep_html = page.locator("#results-report-content").inner_html()
        assert "PASSED (STATIC ONLY)" in rep_html
        page.close()

    def test_case_6_behavioral_test_skipped_shows_not_run(self, live_server: str, browser_context):
        """Behavioral tests that did not run must visibly show 'NOT RUN'."""
        page = browser_context.new_page()
        page.goto(live_server)

        session_payload = {
            "status": "completed",
            "original_code": "x = 1\n",
            "current_code": "x = 1\n",
            "final_audit": {
                "schema_version": 1,
                "status": "passed",
                "verification_level": "static_only",
                "checks": {
                    "syntax": {"status": "passed", "evidence": "Valid", "details": "ok"},
                    "definitions": {"status": "passed", "evidence": "Preserved", "details": "ok"},
                    "security": {"status": "passed", "evidence": "Clean", "details": "ok"},
                    "types": {"status": "passed", "evidence": "Clean", "details": "ok"},
                    "behavior": {"status": "not_run", "evidence": "Behavioral testing skipped (static analysis mode).", "details": "STATIC ONLY"},
                    "approval": {"status": "passed", "evidence": "Read-only", "details": "ok"},
                },
            },
        }
        page.evaluate("(data) => { renderResultsCenter(data); }", session_payload)

        ver_html = page.locator("#results-verification-content").inner_html()
        assert "Behavioral Sandbox Tests" in ver_html
        assert "NOT RUN" in ver_html
        page.close()

    def test_case_7_failed_workflow_renders_failure_never_verified(self, live_server: str, browser_context):
        """Failed workflow -> renders failure state, never 'VERIFIED'."""
        page = browser_context.new_page()
        page.goto(live_server)

        session_payload = {
            "status": "failed",
            "task": "Repair code",
            "error": "Task execution timed out",
            "original_code": "def broken(): pass\n",
            "current_code": "def broken(): pass\n",
            "final_audit": {
                "schema_version": 1,
                "status": "failed",
                "verification_level": "static_only",
                "checks": {
                    "syntax": {"status": "failed", "evidence": "Timeout", "details": "Execution failure"},
                    "definitions": {"status": "not_run", "evidence": "Aborted", "details": "Timeout"},
                    "security": {"status": "not_run", "evidence": "Aborted", "details": "Timeout"},
                    "types": {"status": "not_run", "evidence": "Aborted", "details": "Timeout"},
                    "behavior": {"status": "not_run", "evidence": "Aborted", "details": "Timeout"},
                    "approval": {"status": "not_run", "evidence": "Aborted", "details": "Timeout"},
                },
            },
        }
        page.evaluate("(data) => { renderResultsCenter(data); }", session_payload)

        rep_html = page.locator("#results-report-content").inner_html()
        assert "FAILED" in rep_html
        assert "VERIFIED" not in rep_html
        page.close()

    def test_legacy_mapper_in_browser_avoids_value_not_equal_false_trap(self, live_server: str, browser_context):
        """migrateLegacyAudit executed in browser handles missing keys as 'not_run', never true."""
        page = browser_context.new_page()
        page.goto(live_server)

        migrated = page.evaluate("""() => {
            const legacy = {
                passed: true,
                syntax_valid: true
                // definitions_preserved is omitted!
            };
            return migrateLegacyAudit(legacy);
        }""")

        assert migrated["schema_version"] == 1
        assert migrated["checks"]["syntax"]["status"] == "passed"
        assert migrated["checks"]["definitions"]["status"] == "not_run"
        assert migrated["checks"]["security"]["status"] == "not_run"
        assert migrated["status"] == "not_run"
        assert migrated["passed"] is False
        page.close()
