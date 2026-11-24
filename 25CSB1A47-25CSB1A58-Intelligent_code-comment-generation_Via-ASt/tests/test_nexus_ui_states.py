"""Browser-based E2E Test Suite for NEXUS Workspace UI States.

Tests explicit lifecycle states at desktop (1280px) and mobile (375px/390px) viewports:
- IDLE: Welcome composer, concise examples, no empty activity card or deliverables
- PLANNING: Interpreted task, proposed agents, scope, permissions, Edit plan / Start buttons
- RUNNING: Progress indicator, selective specialists rendering, telemetry drawer collapsed
- AWAITING APPROVAL: Proposed action, reason, consequences, diff, Approve/Reject controls
- COMPLETED: Summary, verification level, deliverables shown only when deliverables exist
- FAILED / CANCELLED: What failed, last successful stage, candidate status, safe retry
- Include Code switch: strictly controls request payload and explains exclusions
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

SAMPLE_CODE = """def calculate_metrics(items):
    total = 0
    for item in items:
        total += item
    return total
"""


@pytest.fixture(scope="module")
def live_server():
    """Start an ephemeral background Flask server for UI state testing."""
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
def browser_instance():
    """Launch headless Chrome once for the test module."""
    launch_kwargs = {
        "headless": True,
        "args": ["--no-sandbox", "--disable-dev-shm-usage"],
    }
    if CHROME_PATH:
        launch_kwargs["executable_path"] = CHROME_PATH
    with sync_playwright() as p:
        browser = p.chromium.launch(**launch_kwargs)
        yield browser
        browser.close()


class TestNexusWorkspaceUIStates:
    """Test suite covering all NEXUS progressive workspace UI states."""

    @pytest.mark.parametrize("viewport_width,viewport_height", [
        (1280, 800),  # Desktop
        (390, 844),   # Modern Mobile (iPhone 12/13/14)
        (375, 667),   # Compact Mobile (iPhone SE)
    ])
    def test_idle_state_on_first_load(self, live_server: str, browser_instance, viewport_width, viewport_height):
        """IDLE: Welcome composer, examples, no empty activity card and no empty deliverables tabs."""
        context = browser_instance.new_context(viewport={"width": viewport_width, "height": viewport_height})
        page = context.new_page()
        page.goto(live_server)

        # Navigate to AI Agent Workforce
        page.locator('button[data-tab="tab-assistant"]').click()
        page.wait_for_timeout(200)

        # 1. Welcome frame is visible
        assert page.locator("#nexus-welcome-frame").is_visible()
        assert page.locator("#nexus-conversation-title").is_visible()

        # 2. Empty activity card and deliverables center MUST BE HIDDEN
        assert not page.locator("#nexus-compact-activity-card").is_visible()
        assert not page.locator("#agentic-results-center").is_visible()
        assert not page.locator("#nexus-planning-card").is_visible()
        assert not page.locator("#nexus-status-notice-card").is_visible()
        assert not page.locator("#nexus-progress-timeline").is_visible()

        # 3. Primary action button is the one-call assistant; specialists remain optional.
        primary_btn = page.locator("#btn-run-agentic")
        assert primary_btn.is_visible()
        assert "Ask NEXUS" in primary_btn.text_content()

        # 4. Abort button is disabled
        cancel_btn = page.locator("#btn-agentic-cancel")
        assert cancel_btn.is_visible()
        assert cancel_btn.is_disabled()

        # 5. Suggestion cards are clickable and touch target >= 40px
        cards = page.locator(".welcome-suggestions-grid .suggestion-card")
        assert cards.count() == 4
        for i in range(4):
            box = cards.nth(i).bounding_box()
            assert box is not None
            assert box["height"] >= 40

        context.close()

    def test_new_conversation_resets_to_idle(self, live_server: str, browser_instance):
        """New conversation returns workspace to clean IDLE state."""
        context = browser_instance.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        page.goto(live_server)

        page.locator('button[data-tab="tab-assistant"]').click()
        page.wait_for_timeout(200)

        # Trigger planning state by clicking a suggestion card
        page.locator('.suggestion-card[data-intent="architecture_analysis"]').click()
        page.wait_for_timeout(500)
        assert page.locator("#nexus-planning-card").is_visible()

        # Click New Conversation
        page.locator("#btn-nexus-new-chat").click()
        page.wait_for_timeout(250)

        # Assert returned to clean IDLE state
        assert page.locator("#nexus-welcome-frame").is_visible()
        assert not page.locator("#nexus-planning-card").is_visible()
        assert not page.locator("#nexus-compact-activity-card").is_visible()
        assert not page.locator("#agentic-results-center").is_visible()
        assert not page.locator("#nexus-progress-timeline").is_visible()
        assert page.locator("#agentic-task-input").input_value() == ""

        context.close()

    @pytest.mark.parametrize("viewport_width,viewport_height", [
        (1280, 800),
        (390, 844),
    ])
    def test_planning_state_shows_selected_agents_and_controls(self, live_server: str, browser_instance, viewport_width, viewport_height):
        """PLANNING: Show interpreted task, proposed agents, files/scope, permissions, Edit plan / Start buttons."""
        context = browser_instance.new_context(viewport={"width": viewport_width, "height": viewport_height})
        page = context.new_page()
        page.goto(live_server)

        # Fill code editor
        page.locator("#code-editor").fill(SAMPLE_CODE)

        # Navigate to AI Agent Workforce
        page.locator('button[data-tab="tab-assistant"]').click()
        page.wait_for_timeout(200)

        # Click Security Scan card
        page.locator('.suggestion-card[data-intent="security_scan"]').click()
        page.wait_for_timeout(600)

        # 1. Welcome frame is hidden, Planning card is visible
        assert not page.locator("#nexus-welcome-frame").is_visible()
        planning_card = page.locator("#nexus-planning-card")
        assert planning_card.is_visible()

        # 2. Timeline is visible with Step 1 (Plan) active
        timeline = page.locator("#nexus-progress-timeline")
        assert timeline.is_visible()
        assert "active" in page.locator("#timeline-step-plan").get_attribute("class")

        # 3. Displays profile title, permission badge (Read-Only)
        profile_title = page.locator("#planning-profile-title").text_content()
        assert "Security" in profile_title and ("Scan" in profile_title or "Vulnerability" in profile_title)
        assert "Read-Only" in page.locator("#planning-permission-badge").text_content()

        # 4. Scope and permissions text
        assert "Editor Code" in page.locator("#planning-scope-text").text_content()
        assert "Analysis only" in page.locator("#planning-permissions-text").text_content()

        # 5. Proposed specialists: only SENTINEL selected with rationale
        specialist_rows = page.locator("#planning-specialists-list .planning-specialist-row")
        assert specialist_rows.count() >= 1
        row_text = specialist_rows.first.text_content()
        assert "SENTINEL" in row_text or "Security" in row_text

        # 6. Action buttons: Start Analysis and Edit Prompt
        start_btn = page.locator("#btn-plan-start")
        edit_btn = page.locator("#btn-plan-edit")
        assert start_btn.is_visible()
        assert edit_btn.is_visible()
        assert "Start Analysis" in start_btn.text_content()

        # 7. Primary composer remains the one-call assistant while the plan card owns workflow start.
        primary_btn = page.locator("#btn-run-agentic")
        assert "Ask NEXUS" in primary_btn.text_content()

        context.close()

    def test_running_state_shows_only_selected_specialists(self, live_server: str, browser_instance):
        """RUNNING: Overall progress indicator, show ONLY selected specialists, telemetry drawer collapsed."""
        context = browser_instance.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        page.goto(live_server)

        # Enter code
        page.locator("#code-editor").fill(SAMPLE_CODE)

        # Switch to workforce tab
        page.locator('button[data-tab="tab-assistant"]').click()
        page.wait_for_timeout(200)

        # Click Security Scan card
        page.locator('.suggestion-card[data-intent="security_scan"]').click()
        page.wait_for_timeout(500)

        # Start Analysis
        page.locator("#btn-plan-start").click()
        page.wait_for_timeout(600)

        # 1. Activity card is now visible
        activity_card = page.locator("#nexus-compact-activity-card")
        assert activity_card.is_visible()

        # 2. Progress timeline has Step 2 (Analyze) active
        assert "active" in page.locator("#timeline-step-analyze").get_attribute("class")

        # 3. Only SENTINEL (red_team) is visible! Other agents are hidden in compact card!
        sentinel_chip = page.locator("#chip-agent-red_team")
        assert sentinel_chip.is_visible()

        # ATLAS, FORGE, REMEDY, SCRIBE, VERITY chips must be hidden
        assert not page.locator("#chip-agent-architect").is_visible()
        assert not page.locator("#chip-agent-optimizer").is_visible()
        assert not page.locator("#chip-agent-blue_team").is_visible()
        assert not page.locator("#chip-agent-docstring").is_visible()
        assert not page.locator("#chip-agent-audit").is_visible()

        # 4. Counter shows 1 Active
        counter_text = page.locator("#nexus-activity-counter").text_content()
        assert "1" in counter_text

        # 5. Telemetry drawer is collapsed by default
        drawer = page.locator("#nexus-deep-drawer")
        assert not drawer.is_visible() or "open" not in (drawer.get_attribute("class") or "")

        context.close()

    def test_awaiting_approval_state(self, live_server: str, browser_instance):
        """AWAITING APPROVAL: Proposed action, consequences, diff preview, Approve/Reject controls."""
        context = browser_instance.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        page.goto(live_server)

        page.locator('button[data-tab="tab-assistant"]').click()
        page.wait_for_timeout(200)

        # Simulate AWAITING_APPROVAL state via client state controller
        page.evaluate("""
            setNexusWorkspaceState('AWAITING_APPROVAL', {
                agent: 'blue_team',
                agent_key: 'blue_team',
                tool: 'apply_defensive_patch',
                reason: 'Remediating detected CWE-20 input validation issue',
                consequences: 'Modifies AST nodes in active file; requires non-regression audit.',
                candidate_code: 'def calculate_metrics(items):\\n    if not isinstance(items, (list, tuple)):\\n        raise TypeError("Expected sequence")\\n    return sum(items)\\n'
            });
            renderApprovalCenter({
                status: 'awaiting_approval',
                session_id: 'test-session-approval-1',
                current_code: 'def calculate_metrics(items):\\n    return sum(items)\\n',
                pending_approval: {
                    agent: 'blue_team',
                    tool: 'apply_defensive_patch',
                    reason: 'Remediating detected CWE-20 input validation issue',
                    consequences: 'Modifies AST nodes in active file; requires non-regression audit.',
                    candidate_code: 'def calculate_metrics(items):\\n    if not isinstance(items, (list, tuple)):\\n        raise TypeError("Expected sequence")\\n    return sum(items)\\n'
                }
            });
        """)
        page.wait_for_timeout(300)

        # 1. Approval center is visible
        approval_center = page.locator("#agentic-approval-center")
        assert approval_center.is_visible()

        # 2. Approval elements present
        assert page.locator("#btn-approve-action").is_visible()
        assert page.locator("#btn-reject-action").is_visible()
        assert page.locator("#approval-consequences-box").is_visible()

        # 3. Timeline candidate step marked warning
        timeline_candidate = page.locator("#timeline-step-candidate")
        assert "warning" in (timeline_candidate.get_attribute("class") or "")

        context.close()

    def test_completed_state_renders_summary_and_deliverables(self, live_server: str, browser_instance):
        """COMPLETED: Result summary, verification level, and deliverables tabs when deliverables exist."""
        context = browser_instance.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        page.goto(live_server)

        page.locator('button[data-tab="tab-assistant"]').click()
        page.wait_for_timeout(200)

        # Simulate COMPLETED state with deliverables
        page.evaluate("""
            setNexusWorkspaceState('COMPLETED', {
                status: 'completed',
                code_changed: true,
                final_code: 'def calculate_metrics(items):\\n    return sum(items)\\n',
                original_code: 'def calculate_metrics(items):\\n    total = 0\\n    for i in items: total += i\\n    return total\\n',
                final_audit: {
                    schema_version: 1,
                    status: 'passed',
                    verification_level: 'full',
                    checks: {
                        syntax: { status: 'passed' },
                        definitions: { status: 'passed' },
                        security: { status: 'passed' },
                        types: { status: 'passed' },
                        behavior: { status: 'passed' },
                        approval: { status: 'passed' }
                    },
                    summary: 'All checks passed',
                    failures: [],
                    warnings: []
                }
            });
        """)
        page.wait_for_timeout(300)

        # 1. Timeline step Result is completed
        assert "completed" in (page.locator("#timeline-step-result").get_attribute("class") or "")

        # 2. Results center is visible because deliverables exist
        assert page.locator("#agentic-results-center").is_visible()

        # 3. Primary assistant action remains available after specialist completion.
        assert "Ask NEXUS" in page.locator("#btn-run-agentic").text_content()

        context.close()

    def test_failed_and_cancelled_state(self, live_server: str, browser_instance):
        """FAILED/CANCELLED: Shows what failed, last successful stage, candidate status, and safe retry."""
        context = browser_instance.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        page.goto(live_server)

        page.locator('button[data-tab="tab-assistant"]').click()
        page.wait_for_timeout(200)

        # Simulate FAILED state
        page.evaluate("""
            setNexusWorkspaceState('FAILED', {
                error: 'Model provider timeout during AST analysis stage.',
                last_stage: 'Vulnerability Scan',
                last_agent: 'red_team',
                code_modified: false
            });
        """)
        page.wait_for_timeout(300)

        # 1. Notice card is visible
        notice = page.locator("#nexus-status-notice-card")
        assert notice.is_visible()

        # 2. Displays failure title, message, last stage
        assert "Failed" in page.locator("#notice-status-title").text_content()
        assert "timeout" in page.locator("#notice-status-message").text_content().lower()
        assert "Vulnerability Scan" in page.locator("#notice-last-stage").text_content()
        assert "No candidate" in page.locator("#notice-candidate-status").text_content()

        # 3. Safe retry button is visible
        retry_btn = page.locator("#btn-nexus-retry-safe")
        assert retry_btn.is_visible()

        # Click Dismiss hides notice
        page.locator("#btn-notice-dismiss").click()
        page.wait_for_timeout(200)
        assert not page.locator("#nexus-status-notice-card").is_visible()

        context.close()

    def test_include_code_switch_controls_payload_and_explains_exclusion(self, live_server: str, browser_instance):
        """Include Code switch controls payload and displays calm explanation when code is required."""
        context = browser_instance.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        page.goto(live_server)

        # Put code in editor
        page.locator("#code-editor").fill(SAMPLE_CODE)

        # Navigate to assistant
        page.locator('button[data-tab="tab-assistant"]').click()
        page.wait_for_timeout(200)

        # 1. Context pill is initially visible with lines count
        pill = page.locator("#context-file-pill")
        assert pill.is_visible()
        assert "lines" in pill.text_content().lower()

        # 2. Click toggle button to exclude code
        toggle_btn = page.locator("#btn-toggle-include-code")
        toggle_btn.click()
        page.wait_for_timeout(200)

        # 3. Pill updates to Excluded and button icon becomes '+'
        assert "Excluded" in pill.text_content()
        assert "+" in toggle_btn.text_content()

        # 4. Try running AST analysis with excluded code: displays calm explanation
        page.locator("#agentic-task-input").fill("Analyze AST topology")
        page.locator("#btn-run-agentic").click()
        page.wait_for_timeout(400)
        start_btn = page.locator("#btn-plan-start")
        if start_btn.is_visible():
            start_btn.click()
            page.wait_for_timeout(300)

        # Toast / notice informs user that active code is excluded and required
        toast = page.locator("#toast-container")
        assert "excluded" in toast.text_content().lower() or "required" in toast.text_content().lower()

        # 5. Click toggle button again to re-include code
        toggle_btn.click()
        page.wait_for_timeout(200)
        assert "lines" in pill.text_content().lower()
        assert "✕" in toggle_btn.text_content()

        context.close()
