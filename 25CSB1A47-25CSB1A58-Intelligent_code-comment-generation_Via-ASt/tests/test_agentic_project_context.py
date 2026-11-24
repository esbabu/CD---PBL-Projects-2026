import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4
from types import SimpleNamespace

import backend.agentic.routes as agentic_routes_module
from backend.agentic.agents.base_agent import BaseAgent
from backend.agentic.schemas import WorkflowRunRequest, WorkflowRunResponse
from backend.agentic.session import AgentSession
from backend.agentic.tools import create_standard_tool_registry
from backend.app import create_app
from backend.project.routes import _ACTIVE_WORKSPACES
from backend.project.workspace import ProjectWorkspace


class AgenticProjectContextTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace_id = str(uuid4())
        self.workspace = ProjectWorkspace(
            workspace_id=self.workspace_id,
            base_storage_dir=Path(self.temp_dir.name) / "workspaces",
        )
        self.active_source = (
            "from helpers import normalize\n\n"
            "def run(value):\n"
            "    return normalize(value)\n"
        )
        self.related_source = (
            "def normalize(value):\n"
            "    return value.strip()\n"
        )
        self.workspace.write_file("main.py", self.active_source)
        self.workspace.write_file("helpers.py", self.related_source)
        self.workspace.write_file(".env", "API_TOKEN=must-not-be-sent")
        _ACTIVE_WORKSPACES[self.workspace_id] = self.workspace
        self.client = create_app(
            {"TESTING": True, "REQUIRE_API_KEY": False}
        ).test_client()

    def tearDown(self):
        _ACTIVE_WORKSPACES.pop(self.workspace_id, None)
        self.workspace.cleanup()
        self.temp_dir.cleanup()

    def test_plan_preview_reports_server_validated_workspace_context(self):
        response = self.client.post(
            "/agentic/plan/preview",
            json={
                "task": "Review the project architecture.",
                "intent": "architecture_analysis",
                "workspace_id": self.workspace_id,
                "active_file": "main.py",
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["workspace_id"], self.workspace_id)
        self.assertEqual(data["active_file"], "main.py")
        self.assertEqual(data["context_files"], ["helpers.py", "main.py"])
        self.assertNotIn(".env", data["context_files"])

    def test_specialist_run_uses_backend_files_not_submitted_editor_source(self):
        captured = {}

        def capture_request(req, **_kwargs):
            captured["request"] = req
            return (
                WorkflowRunResponse(
                    status="accepted",
                    session_id="session-context-123",
                    owner_token=None,
                    stream_url=None,
                    task=req.task,
                    execution_mode="deterministic",
                    max_review_cycles=5,
                ),
                None,
                202,
            )

        with patch.object(
            agentic_routes_module.default_workflow_service,
            "start_workflow",
            side_effect=capture_request,
        ):
            response = self.client.post(
                "/agentic/run",
                json={
                    "code": "def stale_editor_content():\n    return False\n",
                    "task": "Review the project for security vulnerabilities.",
                    "intent": "security_scan",
                    "workspace_id": self.workspace_id,
                    "active_file": "main.py",
                    "auto_approve": False,
                },
            )

        self.assertEqual(response.status_code, 202)
        req = captured["request"]
        self.assertEqual(req.code.replace("\r\n", "\n"), self.active_source)
        self.assertEqual(req.workspace_id, self.workspace_id)
        self.assertEqual(req.active_file, "main.py")
        self.assertEqual(
            req.project_context["helpers.py"].replace("\r\n", "\n"),
            self.related_source,
        )
        self.assertNotIn(".env", req.project_context)

    def test_project_aware_workflow_allows_edit_intents(self):
        fake_response = WorkflowRunResponse(
            status="running",
            session_id="session-edit-123",
            owner_token="token-abc",
            stream_url="/agentic/stream/session-edit-123",
            task="Remediate security findings.",
            execution_mode="deterministic",
            max_review_cycles=5,
        )
        with patch.object(
            agentic_routes_module.default_workflow_service,
            "start_workflow",
            return_value=(fake_response, "token-abc", 202),
        ) as start_workflow:
            response = self.client.post(
                "/agentic/run",
                json={
                    "code": self.active_source,
                    "task": "Remediate security findings.",
                    "intent": "security_remediation",
                    "workspace_id": self.workspace_id,
                    "active_file": "main.py",
                },
            )

        self.assertEqual(response.status_code, 202)
        start_workflow.assert_called_once()
        req = start_workflow.call_args[0][0]
        self.assertEqual(req.intent, "security_remediation")
        self.assertEqual(req.workspace_id, self.workspace_id)

    def test_workflow_service_attaches_project_context_to_runtime_session(self):
        service = agentic_routes_module.default_workflow_service
        session = SimpleNamespace(
            session_id="session-context-123",
            owner_token="owner-token",
            task="Review project architecture.",
            metadata={
                "execution_mode": "deterministic",
                "max_review_cycles": 5,
            },
        )
        project_files = {"helpers.py": self.related_source}
        request = WorkflowRunRequest(
            code=self.active_source,
            task="Review project architecture.",
            async_run=False,
            execution_mode="deterministic",
            workspace_id=self.workspace_id,
            active_file="main.py",
            project_context=project_files,
        )

        with (
            patch.object(service.runtime, "start_session", return_value=session) as start_session,
            patch.object(service.runtime, "execute_session", return_value={"status": "completed"}),
        ):
            _, _, status_code = service.start_workflow(
                request,
                is_model_ready=False,
            )

        self.assertEqual(status_code, 200)
        self.assertEqual(
            start_session.call_args.kwargs["project_context"],
            project_files,
        )
        self.assertEqual(
            start_session.call_args.kwargs["workspace_id"],
            self.workspace_id,
        )
        self.assertEqual(start_session.call_args.kwargs["active_file"], "main.py")

    def test_specialist_prompt_contains_related_project_files_and_identity(self):
        tools = create_standard_tool_registry()
        agent = BaseAgent(
            name="architect",
            role_description="Review architecture.",
            system_prompt="Use AST tools.",
            tools=tools,
            allowed_tools=["inspect_ast_structure"],
        )
        session = AgentSession(
            session_id="session-context-123",
            original_code=self.active_source,
            original_code_digest=hashlib.sha256(
                self.active_source.encode("utf-8")
            ).hexdigest(),
            current_code=self.active_source,
            task="Review the project architecture.",
            metadata={
                "project_workspace_id": self.workspace_id,
                "active_file": "main.py",
            },
            project_context={"helpers.py": self.related_source},
        )

        system_message, user_message = agent.format_messages(
            session,
            "Inspect project dependencies.",
        )

        self.assertIn("project-aware specialist run is read-only", system_message["content"])
        self.assertIn(f"Project Workspace: {self.workspace_id}", user_message["content"])
        self.assertIn("Active Project File: main.py", user_message["content"])
        self.assertIn("--- helpers.py ---", user_message["content"])
        self.assertIn("return value.strip()", user_message["content"])
