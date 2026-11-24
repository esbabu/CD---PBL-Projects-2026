import ast
import re
import unittest
from unittest.mock import patch
from backend.app import app
from backend.security_attack_agent import simulate_attacks


class FrontendAssetIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_index_html_loads_successfully(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        content = response.data.decode("utf-8")
        self.assertIn("<title>AST Studio", content)
        self.assertIn("id=\"code-editor\"", content)
        self.assertIn("id=\"btn-multi-agent-team\"", content)
        self.assertIn("id=\"confusion-matrix-container\"", content)
        self.assertIn("id=\"btn-simulate-custom-attack\"", content)
        self.assertIn("AST Insights", content)
        self.assertIn("id=\"explanations-content\"", content)
        self.assertIn("id=\"btn-open-file\"", content)
        self.assertIn("id=\"btn-sandbox-open-file\"", content)
        self.assertIn("id=\"sandbox-source-status\"", content)
        self.assertIn("id=\"btn-sec-simulate-code\"", content)
        self.assertIn("id=\"btn-banner-simulate\"", content)
        self.assertIn("id=\"btn-banner-remediate-generate\"", content)
        self.assertIn("id=\"sec-active-code-section\"", content)
        self.assertNotIn("data-tab=\"tab-explanations\"", content)
        self.assertNotIn("data-tab=\"tab-agentic\"", content)
        self.assertIn("AI Agent Workforce", content)
        self.assertIn("Autonomous AI Engineering Workforce", content)
        self.assertIn("NEXUS", content)
        self.assertIn("Reviewer Agent", content)
        self.assertIn("Engineering Agent", content)
        self.assertIn("id=\"btn-run-agentic\"", content)
        self.assertIn("id=\"btn-agentic-cancel\"", content)
        self.assertIn("id=\"agentic-stream-console\"", content)
        self.assertIn("id=\"agentic-agent-telemetry\"", content)
        self.assertIn("id=\"agentic-result-box\"", content)
        self.assertNotIn("GitHub Copilot AI + AST", content)
        self.assertNotIn(">Attack Guard Active", content)
        self.assertNotIn(">Multi-Agent Ready", content)

    def test_project_workspace_controls_use_the_existing_textarea(self):
        index = self.client.get("/").data.decode("utf-8")
        script = self.client.get("/script.js").data.decode("utf-8")

        for element_id in (
            "project-archive-input",
            "btn-upload-project",
            "project-workspace-panel",
            "project-file-tree",
            "project-active-file",
            "btn-save-project-file",
        ):
            self.assertIn(f'id="{element_id}"', index)
        self.assertIn("Single-file context — related project files are not loaded.", script)
        self.assertIn("sessionStorage.setItem(PROJECT_CONTEXT_STORAGE_KEY", script)
        self.assertIn("button.setAttribute('aria-selected'", script)

        self.assertIn("formData.append('archive', archive)", script)
        self.assertIn("`/api/project/${encodeURIComponent(currentWorkspaceId)}/tree`", script)
        self.assertIn("encodeURIComponent(path)", script)
        self.assertIn("JSON.stringify({ path, content })", script)
        self.assertIn("fileButton.textContent = node.name", script)
        self.assertIn("This project file has unsaved changes. Discard them?", script)
        self.assertIn("openProjectWorkspacePanel();", script)
        self.assertNotIn("if (fileInput) fileInput.click();", script)

    def test_provider_readiness_is_distinguished_from_live_connectivity(self):
        index = self.client.get("/").data.decode("utf-8")
        script = self.client.get("/script.js").data.decode("utf-8")
        self.assertIn('id="provider-connectivity-status"', index)
        self.assertIn("provider_status_detail", script)
        self.assertIn("The live provider request succeeded.", script)
        self.assertIn("CONFIGURED / NOT TESTED", script)
        self.assertIn("data.provider_status", script)

    def test_nexus_composer_routes_questions_reviews_changes_and_tests(self):
        script = self.client.get("/script.js").data.decode("utf-8")
        index = self.client.get("/").data.decode("utf-8")
        for route in (
            "case 'code_change':",
            "case 'security_review':",
            "case 'architecture_review':",
            "case 'test':",
            "await submitNexusChat('debug')",
            "await submitNexusChat('explain')",
            "await proposeProjectChangesFromComposer()",
            "await previewNexusPlan(prompt, workflowIntent)",
            "auto_approve: false",
        ):
            self.assertIn(route, script)
        self.assertIn("workspace_id: currentWorkspaceId, active_file: currentFilePath", script)
        self.assertIn("The project file changed after this plan was previewed.", script)
        self.assertIn("/assistant/propose-changes", script)
        self.assertNotIn("auto_approve: true", script)
        self.assertIn("Generate Reviewable Proposal", index)
        self.assertIn("Review Remediation Proposal", script)

    def test_agentic_candidate_is_staged_for_project_approval(self):
        script = self.client.get("/script.js").data.decode("utf-8")
        self.assertIn("/changes/propose-agentic-candidate", script)
        self.assertIn("lastAgenticCandidateSourceCode", script)
        self.assertIn("Stage in Project for Review", script)
        self.assertIn("Candidate copied into the editor buffer only", script)

    def test_agent_workforce_uses_new_identities_and_hides_empty_agent_cards(self):
        index = self.client.get("/").data.decode("utf-8")
        script = self.client.get("/script.js").data.decode("utf-8")
        visible = re.sub(r"<!--.*?-->", "", index, flags=re.DOTALL)
        visible = re.sub(r"<[^>]+>", " ", visible)

        for retired_label in (
            "Red Team",
            "Blue Team",
            "Professor-Student",
            "Pedagogical QA Loop",
            "Red Team Simulator",
            "Blue Team Patcher",
            "Quality Auditor",
        ):
            self.assertNotIn(retired_label, visible)

        for identity in ("ATLAS", "FORGE", "SENTINEL", "REMEDY", "SCRIBE", "VERITY"):
            self.assertIn(f"name: '{identity}'", script)
        self.assertIn("id=\"agentic-workflow-graph\"", index)
        self.assertIn("id=\"agentic-communications\"", index)
        self.assertIn("id=\"agentic-agent-inspector\"", index)
        self.assertRegex(
            index,
            r'id="agentic-agent-telemetry"[^>]*hidden',
        )
        self.assertIn("Reviewer-Verified Candidate Diff", index)
        self.assertIn("Maximum Review Cycles", index)

    def test_examples_one_through_eight_are_undocumented_source_inputs(self):
        content = self.client.get("/").data.decode("utf-8")
        for example_id in range(1, 9):
            match = re.search(
                rf'<script type="application/json" id="example-{example_id}">(.*?)</script>',
                content,
                re.DOTALL,
            )
            self.assertIsNotNone(match, f"Example {example_id} was not found")
            source = match.group(1).strip()
            self.assertNotIn('"""', source, f"Example {example_id} has a docstring")
            self.assertNotIn("'''", source, f"Example {example_id} has a docstring")
            ast.parse(source)

    def test_every_selectable_example_has_parseable_source(self):
        content = self.client.get("/").data.decode("utf-8")
        selector = re.search(r'<select id="example-select".*?</select>', content, re.DOTALL)
        self.assertIsNotNone(selector)
        option_ids = set(re.findall(r'<option value="(\d+)">', selector.group(0)))
        examples = dict(
            re.findall(
                r'<script type="application/json" id="example-(\d+)">(.*?)</script>',
                content,
                re.DOTALL,
            )
        )

        self.assertEqual(option_ids, {str(example_id) for example_id in range(1, 15)})
        self.assertEqual(option_ids, set(examples))
        for example_id, source in examples.items():
            ast.parse(source.strip(), filename=f"<example-{example_id}>")

    def test_unsafe_formatter_is_disabled_without_changing_nested_python(self):
        index = self.client.get("/").data.decode("utf-8")
        script = self.client.get("/script.js").data.decode("utf-8")
        self.assertRegex(
            index,
            r'<button[^>]*id="btn-format"[^>]*disabled[^>]*>',
        )
        self.assertIn(
            "Formatting is unavailable because automatic re-indentation can change Python code behavior.",
            index,
        )
        self.assertNotIn("function formatCode()", script)
        self.assertNotIn("btn-format').addEventListener", script)

        source = (
            "def f(flag):\n"
            "    if flag:\n"
            "        return 1\n"
            "    return 0\n"
        )
        namespace = {}
        exec(compile(source, "<nested-branch-regression>", "exec"), namespace)
        self.assertEqual(namespace["f"](False), 0)
        self.assertEqual(namespace["f"](True), 1)

    def test_styles_css_loads_successfully(self):
        response = self.client.get("/styles.css")
        self.assertEqual(response.status_code, 200)
        content = response.data.decode("utf-8")
        self.assertIn("--bg-canvas: #ffffff", content)
        self.assertIn("--accent-cyan: #0284c7", content)
        self.assertIn("color-scheme: light", content)
        self.assertIn(".matrix-container", content)

    def test_professor_student_panel_uses_readable_light_theme(self):
        index = self.client.get("/").data.decode("utf-8")
        styles = self.client.get("/styles.css").data.decode("utf-8")
        self.assertIn('id="professor-student-panel"', index)
        self.assertIn('class="professor-student-title"', index)
        self.assertIn(".professor-student-panel", styles)
        self.assertIn("color: var(--text-primary);", styles)
        self.assertRegex(
            styles,
            r"(?s)\.professor-student-panel\s*\{[^}]*background:\s*#ffffff;",
        )
        self.assertNotIn("background: rgba(15, 23, 42, 0.7)", index)
        self.assertNotIn('style="font-size:1.05rem; color:#f8fafc;"', index)

    def test_settings_modal_uses_fixed_centered_overlay_and_dialog_card(self):
        index = self.client.get("/").data.decode("utf-8")
        styles = self.client.get("/styles.css").data.decode("utf-8")
        script = self.client.get("/script.js").data.decode("utf-8")
        self.assertRegex(
            index,
            r'<div id="settings-modal" class="settings-modal-overlay"',
        )
        self.assertRegex(
            styles,
            r"(?s)\.settings-modal-overlay\s*\{[^}]*"
            r"position:\s*fixed;[^}]*inset:\s*0;[^}]*"
            r"align-items:\s*center;[^}]*justify-content:\s*center;",
        )
        self.assertRegex(
            styles,
            r"(?s)\.settings-modal-card\s*\{[^}]*"
            r"max-height:\s*88vh;[^}]*display:\s*flex;[^}]*"
            r"flex-direction:\s*column;",
        )
        self.assertIn("'No API key required'", script)

    def test_editor_overlay_supports_horizontal_overflow_sync(self):
        styles = self.client.get("/styles.css").data.decode("utf-8")
        script = self.client.get("/script.js").data.decode("utf-8")
        self.assertRegex(
            styles,
            r"(?s)\.editor-highlight\s*\{[^}]*overflow:\s*hidden",
        )
        self.assertRegex(
            styles,
            r"(?s)\.editor-highlight\s+code\s*\{[^}]*"
            r"width:\s*max-content;[^}]*min-width:\s*100%;",
        )
        self.assertIn("white-space: pre;", styles)
        self.assertIn("editorHighlight.scrollLeft = editor.scrollLeft;", script)

    def test_script_js_loads_successfully(self):
        response_wb = self.client.get("/workbench.js")
        self.assertEqual(response_wb.status_code, 200)
        response = self.client.get("/script.js")
        self.assertEqual(response.status_code, 200)
        content = response.data.decode("utf-8")
        self.assertIn("runMultiAgentTeam", content)
        self.assertIn("return runAgenticSwarm(", content)
        self.assertIn("Perform a full end-to-end multi-agent optimization", content)
        self.assertIn("require_model: requireModel", content)
        self.assertIn("restoreLatestAgenticSession", content)
        self.assertNotIn("/agent/multi-agent-workflow", content)
        self.assertIn("simulateCustomAttack", content)
        self.assertIn("filterBenchmarkTable", content)
        self.assertIn("runSecurityLabCodeSimulation", content)
        self.assertIn("High Static Quality", content)
        self.assertNotIn("Production Ready ✓", content)
        self.assertNotIn("ai-mode-badge", content)
        for event_name in (
            "task_assigned",
            "agent_started",
            "tool_started",
            "tool_completed",
            "trajectory_step",
            "model_call_started",
            "cancellation_requested",
            "workflow_cancelled",
            "finding_published",
            "agent_message",
            "checkpoint_created",
            "approval_required",
            "verification_completed",
            "candidate_validated",
            "agent_failed",
            "session_failed",
            "workflow_completed",
        ):
            self.assertIn(f"registerEvent('{event_name}'", content)
        self.assertIn("payload.session_id !== sessionId", content)
        self.assertIn("payload.replay_through_event_id", content)
        self.assertIn("lastEventSequence", content)
        self.assertIn("syncAgentTelemetry(sessData)", content)
        for field in (
            "Current task and input context",
            "Recorded findings and deliverables",
            "Execution activity",
            "Structured model output",
            "Tool calls and observed results",
            "Communication history",
        ):
            self.assertIn(field, content)
        self.assertIn("Argument names:", content)
        self.assertIn("trajectory.length", content)
        self.assertIn("goal-specific plan", content)

    def test_analyze_returns_ast_explanations(self):
        response = self.client.post(
            "/analyze",
            json={"code": "def choose(value):\n    if value:\n        return 1\n    return 0\n"},
        )
        self.assertEqual(response.status_code, 200)
        explanations = response.get_json()["smart_explanations"]
        self.assertTrue(any(item["kind"] == "function" for item in explanations))
        self.assertTrue(any(item["kind"] == "branch" for item in explanations))

    def test_custom_attack_simulation_sqli(self):
        payload = {
            "payload": "' OR '1'='1' --",
            "attack_type": "sqli",
            "code": "def get_user(uid):\n    query = f'SELECT * FROM users WHERE id = {uid}'\n    cursor.execute(query)\n"
        }
        response = self.client.post("/security/simulate-custom-attack", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "success")
        self.assertTrue(data["detected"])
        self.assertIn("SQL", data["cwe"])
        self.assertGreaterEqual(data["risk_score"], 80)
        self.assertEqual(len(data["ast_trace_steps"]), 4)
        self.assertEqual(
            data["ast_trace_steps"][1]["name"], "AST Node & Sink Resolution"
        )
        matched_node = data["ast_trace_steps"][1]["details"]["resolved_nodes"][0]
        self.assertIn("ast.JoinedStr", matched_node["ast_node_type"])
        self.assertEqual(matched_node["ast_sink_symbol"], "cursor.execute")
        self.assertTrue(
            matched_node["ast_security_comment"].startswith("# [AST-SEC CWE-89]")
        )
        static_analysis = data["ast_trace_steps"][2]["details"]
        self.assertEqual(
            static_analysis["static_match_status"],
            "attack_type_ast_pattern_matched",
        )
        self.assertFalse(static_analysis["code_execution"])
        self.assertIn("Static AST simulation only", static_analysis["execution_notice"])
        defense = data["ast_trace_steps"][3]["details"]
        self.assertTrue(defense["comment_specification"].startswith("# [AST-DEFENSE]"))
        self.assertIn("parameterized", defense["recommended_code_fix"])

    def test_simulated_subprocess_finding_identifies_exact_ast_sink(self):
        result = simulate_attacks(
            "import subprocess\n"
            "def run(command):\n"
            "    return subprocess.run(command, shell=True)\n"
        )

        scenario = next(
            item
            for item in result["attack_scenarios"]
            if item["cwe"].startswith("CWE-78")
        )
        self.assertEqual(
            scenario["ast_node_type"],
            "ast.Call -> subprocess.run(shell=True)",
        )
        self.assertEqual(scenario["ast_sink_symbol"], "subprocess.run")
        self.assertTrue(scenario["ast_security_comment"].startswith("# [AST-SEC CWE-78]"))

    def test_custom_attack_simulation_command_injection(self):
        payload = {
            "payload": "; cat /etc/passwd #",
            "attack_type": "cmdi",
            "code": "import os\ndef ping(host):\n    os.system(f'ping -c 1 {host}')\n"
        }
        response = self.client.post("/security/simulate-custom-attack", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "success")
        self.assertTrue(data["detected"])
        self.assertIn("Command", data["cwe"])

    def test_custom_attack_simulation_benign(self):
        payload = {
            "payload": "user123",
            "attack_type": "custom",
            "code": "def add(a, b):\n    return a + b\n"
        }
        response = self.client.post("/security/simulate-custom-attack", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "success")
        self.assertFalse(data["exploit_successful"])


    def test_threat_remediation_modal_elements_present(self):
        index = self.client.get("/").data.decode("utf-8")
        styles = self.client.get("/styles.css").data.decode("utf-8")
        script = self.client.get("/script.js").data.decode("utf-8")
        self.assertIn('id="security-threat-modal"', index)
        self.assertIn('id="btn-threat-modal-autofix"', index)
        self.assertIn('id="btn-threat-modal-dismiss"', index)
        self.assertIn('.threat-modal-overlay', styles)
        self.assertIn('showThreatRemediationModal', script)
        self.assertIn('applyAutoFixFromModal', script)

    def test_security_lab_offers_remediation_after_reviewing_attack_risks(self):
        script = self.client.get("/script.js").data.decode("utf-8")
        self.assertIn('id="btn-sec-proceed-remediation"', script)
        self.assertIn("<strong>Pattern:</strong>", script)
        self.assertIn("Risk indicator:", script)
        self.assertIn("not a calibrated probability", script)
        self.assertIn("Would you like to apply an automatic fix or keep the code unchanged?", script)
        simulation_flow = script.split("async function runSecurityLabCodeSimulation()", 1)[1].split(
            "\nasync function evaluateSecurity(", 1
        )[0]
        self.assertLess(
            simulation_flow.index("proceedRemediationBtn.addEventListener"),
            simulation_flow.index("showThreatRemediationModal({"),
        )

    def test_security_overview_does_not_claim_results_before_a_scan(self):
        index = self.client.get("/").data.decode("utf-8")
        script = self.client.get("/script.js").data.decode("utf-8")
        self.assertIn('id="sec-resilience-value">--<', index)
        self.assertIn('id="sec-total-checks">--<', index)
        self.assertIn('id="sec-vulns-detected">--<', index)
        self.assertIn('id="sec-last-scan-badge">Not analyzed<', index)
        self.assertIn("14 static AST checks", index)
        self.assertIn("Static security analysis returned incomplete or invalid metrics.", script)
        self.assertIn("Static security analysis returned contradictory finding metrics.", script)
        self.assertIn("vulnerabilityCount !== scenarios.length", script)
        self.assertIn("Source-to-sink:", script)
        self.assertIn("Results for earlier code", script)
        self.assertIn("Editor source changed during analysis. The pending scan result will be discarded.", script)
        self.assertIn("activeSecurityScan.source !== editor.value", script)
        self.assertIn("if (!activeSecurityScan || activeSecurityScan.id !== scanId)", script)
        self.assertIn(
            "No security scan was completed for this source; findings have not been assessed.",
            script,
        )
        self.assertIn("const scanId = ++securityScanSequence;", script)
        self.assertIn("lastBlueTeamRemediation.source_snapshot !== editor.value", script)
        self.assertIn("remediatedCount = verifiedResolved;", script)
        self.assertNotIn("remediatedCount += verifiedResolved;", script)
        self.assertIn("securityScanStatus = 'failed';", script)
        self.assertNotIn(
            "data.resilience_score !== undefined ? data.resilience_score : 100",
            script,
        )

    @patch("backend.app.simulate_attacks", side_effect=RuntimeError("analysis fault"))
    def test_custom_simulation_surfaces_static_analysis_failure(self, _simulate_attacks):
        response = self.client.post(
            "/security/simulate-custom-attack",
            json={
                "payload": "synthetic input",
                "attack_type": "custom",
                "code": "def add(a, b):\n    return a + b\n",
            },
        )

        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertEqual(data["status"], "failed")
        self.assertEqual(data["error_type"], "RuntimeError")
        self.assertIn("could not be completed", data["error"])

    def test_tabs_bar_vertical_clipping_fix_present(self):
        styles = self.client.get("/styles.css").data.decode("utf-8")
        self.assertIn('flex: 0 0 48px !important;', styles)
        self.assertIn('min-height: 48px;', styles)

    def test_ghost_text_alignment_and_font_style_normal(self):
        styles = self.client.get("/styles.css").data.decode("utf-8")
        script = self.client.get("/script.js").data.decode("utf-8")
        self.assertIn('font-style: normal;', styles)
        self.assertIn('clearGhostText', script)


    def test_assistant_prompt_auto_fix_and_keydown_wired(self):
        script = self.client.get("/script.js").data.decode("utf-8")
        self.assertIn("assistantPrompt.addEventListener('keydown'", script)
        self.assertIn("btn-revert-agent-run", script)
        self.assertIn("btn-revert-quality-candidate", script)
        self.assertIn("data-preset", script)

    def test_agent_run_extract_and_synthesize_candidate(self):
        from backend.agent import extract_or_synthesize_candidate, extract_python_code
        reply = "Here is the fix:\n```python\ndef safe(x):\n    return x\n```\nDone."
        code = extract_python_code(reply)
        self.assertEqual(code, "def safe(x):\n    return x")

        vulnerable = "def run(cmd):\n    import os\n    os.system(cmd)\n"
        candidate = extract_or_synthesize_candidate(vulnerable, "fix security vulnerabilities")
        self.assertIsNotNone(candidate)
        self.assertNotEqual(candidate, vulnerable)

    def test_offline_readiness_and_no_remote_resource_urls(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")

        # Verify CSP contains no external origin hosts
        csp = response.headers.get("Content-Security-Policy", "")
        self.assertIn("default-src 'self'", csp)
        self.assertIn("font-src 'self' data:", csp)
        for host in ("googleapis.com", "gstatic.com", "cdnjs.cloudflare.com", "jsdelivr.net"):
            self.assertNotIn(host, csp)

        # Parse and verify resource links and scripts have no remote URLs
        resource_matches = re.findall(
            r'<(?:link|script|img|iframe)\b[^>]*(?:src|href)=["\']([^"\']+)["\']',
            html,
            re.IGNORECASE,
        )
        self.assertTrue(len(resource_matches) > 0)
        for url in resource_matches:
            self.assertFalse(
                url.startswith("http://") or url.startswith("https://") or url.startswith("//"),
                f"Remote resource URL found in index.html: {url}",
            )

        # Verify vendored assets are reachable locally via static routing
        for asset_path in (
            "/vendor/fonts/fonts.css",
            "/vendor/fonts/jetbrains-mono.woff2",
            "/vendor/fonts/manrope.woff2",
            "/vendor/highlight/github.min.css",
            "/vendor/highlight/highlight.min.js",
            "/vendor/highlight/python.min.js",
        ):
            res = self.client.get(asset_path)
            self.assertEqual(res.status_code, 200, f"Vendored asset not found: {asset_path}")
            self.assertGreater(len(res.data), 0)



if __name__ == "__main__":
    unittest.main()
