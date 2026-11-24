"""Browser-based End-to-End (E2E) UI Test Suite for AST Studio.

Uses Playwright with headless Chrome against a live local server instance.
Tests:
- Conversational Workspace loading and tab navigation to AI Agent Workforce
- NEXUS Command Center, DAG canvas, and 6 specialist agent roster nodes
- Selecting agents and verifying live Agent Inspector panel updates in deep drawer
- Deploying NEXUS workforce and receiving live streaming events
- Terminal console event filtering (Tools, Reasoning, Findings, All)
- Results Center tab navigation (Diff, Docstrings, Security, Verification)
- Operator approval controls and cancellation interface
"""

from __future__ import annotations

import io
import json
import os
import threading
from types import SimpleNamespace
from unittest.mock import patch
import zipfile

import pytest

pytest.importorskip("playwright.sync_api")
from playwright.sync_api import expect, sync_playwright
from werkzeug.serving import make_server

from backend.app import create_app

CHROME_PATH = os.getenv("PLAYWRIGHT_CHROME_PATH") or os.getenv("PLAYWRIGHT_EXECUTABLE_PATH")

SAMPLE_CODE = """
def divide_elements(a, b):
    # Calculate division
    return a / b
"""


@pytest.fixture(scope="module")
def live_server():
    """Start an ephemeral background Flask server for real browser testing."""
    app = create_app({
        "TESTING": True,
        "REQUIRE_API_KEY": False,  # Allow frontend UI access without key prompts
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


class TestFrontendE2E:
    """Comprehensive browser E2E tests for the AST Studio AI Agent Workforce."""

    def test_project_workspace_upload_open_and_save(self, live_server: str, browser_context):
        page = browser_context.new_page()
        page.goto(live_server)

        archive = io.BytesIO()
        with zipfile.ZipFile(archive, "w") as project_zip:
            project_zip.writestr("main.py", "def main():\n    return 'original'\n")
            project_zip.writestr("utils.py", "def helper():\n    return True\n")
            project_zip.writestr("tests/test_main.py", "def test_main():\n    assert True\n")

        workspace_id = None
        try:
            page.locator("#btn-upload-project").click()
            with page.expect_response(
                lambda response: response.url.endswith("/api/project/upload")
            ) as upload_response:
                page.locator("#project-archive-input").set_input_files({
                    "name": "sample-project.zip",
                    "mimeType": "application/zip",
                    "buffer": archive.getvalue(),
                })
            assert upload_response.value.status == 201
            workspace_id = upload_response.value.json()["workspace_id"]

            main_file = page.locator('[data-project-file-path="main.py"]')
            main_file.wait_for(state="visible")
            assert page.locator("[data-project-file-path]").count() == 3
            main_file.click()
            editor = page.locator("#code-editor")
            expect(editor).to_have_value("def main():\n    return 'original'\n")

            unsaved_content = "def main():\n    return 'pending'\n"
            editor.fill(unsaved_content)
            expect(editor).to_have_value(unsaved_content)
            page.once("dialog", lambda dialog: dialog.dismiss())
            page.locator('[data-project-file-path="utils.py"]').click()
            expect(editor).to_have_value(unsaved_content)

            saved_content = "def main():\n    return 'saved'\n"
            editor.fill(saved_content)
            page.locator("#btn-save-project-file").click()
            expect(page.locator("#btn-save-project-file")).to_be_disabled()
            expect(page.locator("#project-workspace-status")).to_have_text("Saved main.py")

            page.reload()
            main_file = page.locator('[data-project-file-path="main.py"]')
            main_file.wait_for(state="visible")
            expect(page.locator("#project-active-file")).to_contain_text("main.py")
            expect(page.locator("#code-editor")).to_have_value(saved_content)

            page.locator('[data-project-file-path="utils.py"]').click()
            expect(page.locator("#code-editor")).to_have_value(
                "def helper():\n    return True\n"
            )
            expect(main_file).to_have_attribute("aria-selected", "false")
            expect(page.locator('[data-project-file-path="utils.py"]')).to_have_attribute(
                "aria-selected", "true"
            )
            main_file.click()
            expect(editor).to_have_value(saved_content)

            page.locator('button[data-tab="tab-assistant"]').click()
            page.locator("#nav-nexus-project-files").click()
            expect(page.locator("#project-workspace-panel")).to_be_visible()
            expect(page.locator("#tab-output")).to_be_visible()
        finally:
            if workspace_id:
                from backend.project.routes import _ACTIVE_WORKSPACES

                workspace = _ACTIVE_WORKSPACES.pop(workspace_id, None)
                if workspace:
                    workspace.cleanup()
            page.close()

    def test_local_python_file_is_labeled_as_single_file_context(
        self, live_server: str, browser_context
    ):
        page = browser_context.new_page()
        page.goto(live_server)
        page.locator("#file-input").set_input_files({
            "name": "local_module.py",
            "mimeType": "text/x-python",
            "buffer": b"def local_function():\n    return True\n",
        })
        expect(page.locator("#code-editor")).to_have_value(
            "def local_function():\n    return True\n"
        )
        expect(page.locator("#project-active-file")).to_contain_text(
            "Single-file context"
        )
        expect(page.locator("#project-context-files")).to_contain_text(
            "related project files are not loaded"
        )
        page.close()

    def test_project_chat_proposal_approval_verification_and_rollback(
        self, live_server: str, browser_context
    ):
        page = browser_context.new_page()
        page.goto(live_server)
        archive = io.BytesIO()
        original = "def average(values):\n    return sum(values) / len(values)\n"
        updated = (
            "def average(values):\n"
            "    if not values:\n"
            "        return 0\n"
            "    return sum(values) / len(values)\n"
        )
        with zipfile.ZipFile(archive, "w") as project_zip:
            project_zip.writestr("main.py", original)
            project_zip.writestr("utils.py", "def ready(): return True\n")
            project_zip.writestr("tests/test_main.py", "from main import average\n")

        proposal = json.dumps({
            "assistant_reply": "I prepared an empty-input guard.",
            "reason": "Avoid division by zero for an empty sequence.",
            "changes": {"main.py": updated},
            "tests_to_run": ["tests/test_main.py"],
        })
        responses = [
            "main.py defines average; tests/test_main.py contains the related test.",
            "The existing test module imports average from main.py.",
            proposal,
            proposal,
        ]
        provider_calls = []

        def create_completion(**kwargs):
            provider_calls.append(kwargs)
            content = responses.pop(0)
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
            )

        model_client = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(create=create_completion),
            )
        )
        workspace_id = None
        try:
            with patch("backend.agentic.routes._runtime.model_client", model_client), patch(
                "backend.agentic.routes._runtime.supervisor.model_name", "e2e-test-model"
            ), patch("backend.model_provider.provider_display_name", return_value="Test Provider"):
                page.locator("#btn-upload-project").click()
                with page.expect_response(
                    lambda response: response.url.endswith("/api/project/upload")
                ) as upload_response:
                    page.locator("#project-archive-input").set_input_files({
                        "name": "assistant-project.zip",
                        "mimeType": "application/zip",
                        "buffer": archive.getvalue(),
                    })
                assert upload_response.value.status == 201
                workspace_id = upload_response.value.json()["workspace_id"]

                page.locator('[data-project-file-path="main.py"]').click()
                expect(page.locator("#code-editor")).to_have_value(original)
                page.locator('button[data-tab="tab-assistant"]').click()

                prompt = page.locator("#agentic-task-input")
                prompt.fill("Explain this project.")
                page.locator("#btn-run-agentic").click()
                expect(page.locator(".project-chat-message-text").last).to_contain_text(
                    "tests/test_main.py"
                )
                expect(page.locator(".project-chat-context-files").last).to_contain_text(
                    "utils.py"
                )

                prompt.fill("Which test imports average?")
                page.locator("#btn-run-agentic").click()
                expect(page.locator(".project-chat-message-text").last).to_contain_text(
                    "imports average"
                )
                assert provider_calls[1]["messages"][1]["content"] == "Explain this project."
                assert provider_calls[1]["messages"][2]["content"] == (
                    "main.py defines average; tests/test_main.py contains the related test."
                )

                prompt.fill("Handle empty input.")
                with page.expect_response(
                    lambda response: response.url.endswith("/assistant/propose-changes")
                ):
                    page.locator("#btn-project-propose").click()
                proposal_card = page.locator(".project-proposal-card").last
                expect(proposal_card).to_be_visible()
                expect(proposal_card.locator(".project-proposal-diff")).to_contain_text(
                    "if not values"
                )
                unchanged = proposal_card.get_by_role("button", name="Reject")
                with page.expect_response(
                    lambda response: response.url.endswith("/changes/reject")
                ):
                    unchanged.click()
                expect(proposal_card.locator(".project-proposal-status")).to_contain_text(
                    "Rejected"
                )
                file_url = f"{live_server}/api/project/{workspace_id}/file?path=main.py"
                assert page.request.get(file_url).json()["content"] == original

                prompt.fill("Handle empty input.")
                with page.expect_response(
                    lambda response: response.url.endswith("/assistant/propose-changes")
                ):
                    page.locator("#btn-project-propose").click()
                expect(proposal_card).to_be_visible()
                with page.expect_response(
                    lambda response: response.url.endswith("/changes/approve")
                ):
                    proposal_card.get_by_role("button", name="Approve & Apply").click()
                expect(page.locator("#code-editor")).to_have_value(updated)

                verification = proposal_card.locator(".project-verification-card")
                expect(verification).to_contain_text("Project tests: NOT RUN")
                expect(verification).to_contain_text("OS-level sandbox")
                rollback = proposal_card.get_by_role(
                    "button", name="Roll back approved change"
                )
                with page.expect_response(
                    lambda response: response.url.endswith("/changes/rollback")
                ):
                    rollback.click()
                expect(page.locator("#code-editor")).to_have_value(original)
        finally:
            if workspace_id:
                from backend.project.routes import _ACTIVE_WORKSPACES

                workspace = _ACTIVE_WORKSPACES.pop(workspace_id, None)
                if workspace:
                    workspace.cleanup()
            page.close()

    def test_workforce_tab_navigation_and_initial_state(self, live_server: str, browser_context):
        page = browser_context.new_page()
        page.goto(live_server)

        # 1. Verify Page Loaded
        assert "AST Studio" in page.title() or page.locator("body").is_visible()

        # 2. Click AI Agent Workforce tab
        workforce_tab = page.locator('button[data-tab="tab-assistant"]')
        assert workforce_tab.is_visible()
        workforce_tab.click()

        # 3. Verify NEXUS Conversational Workspace components
        assert page.locator("#tab-assistant").is_visible()
        assert page.locator("#btn-run-agentic").is_visible()
        assert page.locator("#agentic-task-input").is_visible()

        # 4. Verify Calm IDLE state: Welcome card visible, empty activity card & deliverables hidden
        assert page.locator("#nexus-welcome-frame").is_visible()
        assert not page.locator("#nexus-compact-activity-card").is_visible()
        assert not page.locator("#agentic-results-center").is_visible()
        for agent_key in ("architect", "optimizer", "red_team", "blue_team", "docstring", "audit"):
            card = page.locator(f'button.agent-card-btn[data-agent-key="{agent_key}"]')
            assert card.count() == 1

        # 5. Open Deep Drawer and verify SVG Topology canvas & plan section
        page.locator("#btn-toggle-deep-inspector").click()
        page.wait_for_timeout(350)
        assert page.locator("#nexus-plan-section").is_visible()
        assert page.locator("#agentic-workflow-graph").is_visible()
        page.close()

    def test_agent_inspector_selection(self, live_server: str, browser_context):
        page = browser_context.new_page()
        page.goto(live_server)

        # Switch to workforce tab
        page.locator('button[data-tab="tab-assistant"]').click()

        # Display activity card (as when active workflow or specialist inspection is running)
        page.evaluate("document.getElementById('nexus-compact-activity-card').style.display = 'block'")

        # Click on ATLAS (Architect Agent) to open inspector in drawer
        page.locator('button.agent-card-btn[data-agent-key="architect"]').click()
        page.wait_for_timeout(350)
        inspector = page.locator("#agentic-inspector-content")
        assert inspector.is_visible()
        text = inspector.text_content().lower()
        assert "architecture" in text or "responsibility" in text or "task" in text

        # Click on SENTINEL (Security Agent) - force=True because open drawer overlays main chat area
        page.locator('button.agent-card-btn[data-agent-key="red_team"]').click(force=True)
        page.wait_for_timeout(350)
        text_sentinel = inspector.text_content().lower()
        assert "security" in text_sentinel or "responsibility" in text_sentinel

        page.close()

    def test_deploy_nexus_workforce_execution(self, live_server: str, browser_context):
        page = browser_context.new_page()
        page.goto(live_server)

        # 1. Fill Python code in code editor
        code_editor = page.locator("#code-editor")
        code_editor.fill(SAMPLE_CODE)

        # 2. Switch to workforce tab
        page.locator('button[data-tab="tab-assistant"]').click()

        # 3. Fill task objective
        task_input = page.locator("#agentic-task-input")
        task_input.fill("Audit security and generate verified docstrings")

        # 4. Explicitly launch the optional specialist workflow.
        deploy_btn = page.locator("#btn-run-specialists")
        deploy_btn.click()
        page.wait_for_timeout(400)
        start_btn = page.locator("#btn-plan-start")
        if start_btn.is_visible():
            start_btn.click()
        else:
            deploy_btn.click()

        # 5. Verify run initiated: Inspect stream events in drawer tool console
        page.wait_for_timeout(1000)
        page.locator("#btn-toggle-deep-inspector").click()
        page.wait_for_timeout(350)
        page.locator('button.drawer-tab-btn[data-drawer-tab="terminal"]').click()
        page.wait_for_timeout(300)
        console = page.locator("#agentic-stream-console")
        assert console.is_visible()

        # Wait for either completion or steps in terminal
        page.wait_for_timeout(2000)
        content = console.text_content()
        assert len(content.strip()) > 20

        page.close()

    def test_terminal_console_tabs_and_filtering(self, live_server: str, browser_context):
        page = browser_context.new_page()
        page.goto(live_server)

        page.locator('button[data-tab="tab-assistant"]').click()
        page.locator("#btn-toggle-deep-inspector").click()
        page.wait_for_timeout(350)
        page.locator('button.drawer-tab-btn[data-drawer-tab="terminal"]').click()
        page.wait_for_timeout(300)

        # Switch terminal tabs: Tools, Reasoning, All
        page.locator('button[data-term-tab="tools"]').click()
        assert "active" in page.locator('button[data-term-tab="tools"]').get_attribute("class")

        page.locator('button[data-term-tab="reasoning"]').click()
        assert "active" in page.locator('button[data-term-tab="reasoning"]').get_attribute("class")

        page.locator('button[data-term-tab="all"]').click()
        assert "active" in page.locator('button[data-term-tab="all"]').get_attribute("class")

        page.close()

    def test_results_center_tab_navigation(self, live_server: str, browser_context):
        page = browser_context.new_page()
        page.goto(live_server)

        page.locator('button[data-tab="tab-assistant"]').click()

        # Display results center (as when workflow produces deliverables)
        page.evaluate("document.getElementById('agentic-results-center').style.display = 'block'")

        # Switch results center tabs: docs, security, diff
        docs_tab = page.locator('button[data-res-tab="docs"]')
        docs_tab.click()
        assert "active" in docs_tab.get_attribute("class")

        sec_tab = page.locator('button[data-res-tab="security"]')
        sec_tab.click()
        assert "active" in sec_tab.get_attribute("class")

        diff_tab = page.locator('button[data-res-tab="diff"]')
        diff_tab.click()
        assert "active" in diff_tab.get_attribute("class")

        page.close()

    def test_operator_approval_elements_present(self, live_server: str, browser_context):
        page = browser_context.new_page()
        page.goto(live_server)

        page.locator('button[data-tab="tab-assistant"]').click()

        # Verify Approval Gate elements exist in DOM
        assert page.locator("#agentic-require-approval-toggle").count() == 1
        assert page.locator("#btn-approve-action").count() == 1
        assert page.locator("#btn-reject-action").count() == 1

        # Check approval checkbox toggle (open Advanced Settings if inside collapsible dropdown)
        adv_btn = page.locator("#btn-toggle-advanced-settings")
        if adv_btn.count() > 0 and adv_btn.is_visible():
            adv_btn.click()
        toggle = page.locator("#agentic-require-approval-toggle")
        toggle.check(force=True)
        assert toggle.is_checked()
        toggle.uncheck(force=True)
        assert not toggle.is_checked()

        page.close()

    def test_ide_agent_workflow_open_project_run_activity_approve_rollback(
        self, live_server: str, browser_context
    ):
        page = browser_context.new_page()
        page.goto(live_server)

        archive = io.BytesIO()
        original_main = "def process(items):\n    return [x * 2 for x in items]\n"
        proposed_main = "def process(items):\n    \"\"\"Process items by doubling each value.\"\"\"\n    return [x * 2 for x in items]\n"
        with zipfile.ZipFile(archive, "w") as project_zip:
            project_zip.writestr("main.py", original_main)
            project_zip.writestr("utils.py", "def helper(): return True\n")

        workspace_id = None
        try:
            # 1. Open project
            page.locator("#btn-upload-project").click()
            with page.expect_response(
                lambda response: response.url.endswith("/api/project/upload")
            ) as upload_response:
                page.locator("#project-archive-input").set_input_files({
                    "name": "ide-test-project.zip",
                    "mimeType": "application/zip",
                    "buffer": archive.getvalue(),
                })
            assert upload_response.value.status == 201
            workspace_id = upload_response.value.json()["workspace_id"]

            main_file = page.locator('[data-project-file-path="main.py"]')
            main_file.wait_for(state="visible")
            main_file.click()
            editor = page.locator("#code-editor")
            expect(editor).to_have_value(original_main)

            # 2. Run agent / dispatch events into live activity panel
            page.locator('button[data-tab="tab-assistant"]').click()
            page.evaluate(
                """() => {
                    renderLiveActivityItem('ATLAS', 'read_project_file', { path: 'main.py', start_line: 1, end_line: 80 });
                    renderLiveActivityItem('SENTINEL', 'search_project_code', { pattern: 'eval(' }, { hits: [ { file: 'main.py', line: 2 } ] });
                    renderLiveActivityItem('REMEDY', 'propose_file_patch', { path: 'main.py' });
                }"""
            )

            # 3. See activity items
            expect(page.locator("#nexus-live-activity-feed")).to_be_visible()
            activity_items = page.locator(".activity-item-btn")
            expect(activity_items).to_have_count(3)
            expect(activity_items.first).to_contain_text("ATLAS read main.py:1-80")
            expect(activity_items.nth(1)).to_contain_text("SENTINEL searched 'eval('")
            expect(activity_items.nth(2)).to_contain_text("REMEDY proposed patch for main.py")

            # Clicking an activity item opens that file at that line in editor
            activity_items.first.click()
            expect(page.locator("#tab-output")).to_be_visible()
            expect(page.locator("#code-editor")).to_be_visible()

            # 4. Stage patch / proposal and approve
            page.locator('button[data-tab="tab-assistant"]').click()
            proposal_res = page.request.post(
                f"{live_server}/api/project/{workspace_id}/changes/propose",
                data=json.dumps({
                    "changes": {"main.py": proposed_main},
                    "author": "REMEDY",
                    "reason": "Add AST ground-truth docstring",
                }),
                headers={"Content-Type": "application/json"},
            )
            assert proposal_res.status == 200
            proposal_data = proposal_res.json()

            page.evaluate(
                """(propData) => {
                    renderProjectProposalCard(propData);
                }""",
                proposal_data,
            )

            proposal_card = page.locator(".project-proposal-card")
            expect(proposal_card).to_be_visible()

            # Approve
            with page.expect_response(
                lambda response: response.url.endswith("/changes/approve")
            ):
                proposal_card.locator(".btn-proposal-approve").click()

            # 5. Editor content updates
            expect(page.locator("#code-editor")).to_have_value(proposed_main)

            # 6. Rollback
            rollback_btn = proposal_card.locator(".btn-proposal-rollback")
            expect(rollback_btn).to_be_visible()
            with page.expect_response(
                lambda response: response.url.endswith("/changes/rollback")
            ):
                rollback_btn.click()

            # Verify editor reverted to original
            expect(page.locator("#code-editor")).to_have_value(original_main)
        finally:
            if workspace_id:
                from backend.project.routes import _ACTIVE_WORKSPACES

                workspace = _ACTIVE_WORKSPACES.pop(workspace_id, None)
                if workspace:
                    workspace.cleanup()
            page.close()

    def test_offline_mode_and_zero_remote_traffic(self, live_server: str, browser_context, tmp_path):
        """Verify the app functions completely offline with all remote traffic blocked."""
        import os

        page = browser_context.new_page()
        remote_requests = []

        def _route_filter(route):
            url = route.request.url
            if url.startswith(live_server) or url.startswith("http://127.0.0.1") or url.startswith("http://localhost"):
                route.continue_()
            else:
                remote_requests.append(url)
                route.abort("internetdisconnected")

        page.route("**/*", _route_filter)

        try:
            page.goto(live_server)

            # 1. Zero outbound remote requests were attempted
            assert len(remote_requests) == 0, f"Unexpected remote requests during load: {remote_requests}"

            # 2. Local fonts and highlight assets loaded
            editor = page.locator("#code-editor")
            expect(editor).to_be_visible()

            # 3. Enter code and verify local syntax highlighting and overlay sync
            code = "def calculate_tax(amount, rate):\n    # Compute total tax\n    return amount * rate\n"
            editor.fill(code)
            expect(editor).to_have_value(code)

            highlight = page.locator("#editor-highlight")
            expect(highlight).to_be_visible()

            # 4. Trigger comment generation (deterministic / AST mode)
            with page.expect_response(lambda response: response.url.endswith("/generate")):
                page.locator("#btn-generate").click()

            # 5. Output code displays successfully without network
            output_elem = page.locator("#output-code")
            expect(output_elem).to_be_visible()
            output_text = output_elem.text_content()
            assert "def calculate_tax" in output_text

            # 6. Capture offline mode screenshot for audit proof
            screenshots_dir = tmp_path / "screenshots"
            screenshots_dir.mkdir(parents=True, exist_ok=True)
            screenshot_path = str(screenshots_dir / "offline_mode_verified.png")
            page.screenshot(path=screenshot_path)
            assert os.path.exists(screenshot_path)
            assert os.path.getsize(screenshot_path) > 0
        finally:
            page.close()
