"""Unit tests for AgenticWorkflowService orchestration and service boundaries."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from backend.agentic.repository import InMemorySessionRepository
from backend.agentic.schemas import (
    PlanPreviewRequest,
    PlanPreviewResponse,
    SchemaValidationError,
    WorkflowRunRequest,
    WorkflowRunResponse,
)
from backend.agentic.service import AgenticWorkflowService
from backend.agentic.session import SessionManager


class TestAgenticWorkflowService(unittest.TestCase):
    """Test suite for AgenticWorkflowService business logic and boundaries."""

    def setUp(self):
        self.session_repo = InMemorySessionRepository()
        self.session_manager = SessionManager(repository=self.session_repo)
        self.service = AgenticWorkflowService(session_manager=self.session_manager)
        self.sample_code = "def add(x, y):\n    return x + y\n"

    def test_preview_plan_deterministic(self):
        req = PlanPreviewRequest(task="Check code for SQL injection vulnerabilities", intent="security_scan")
        preview = self.service.preview_plan(req)

        self.assertIsInstance(preview, PlanPreviewResponse)
        self.assertEqual(preview.intent, "security_scan")
        self.assertTrue(preview.read_only)
        self.assertIn("red_team", preview.allowed_agents)
        self.assertTrue(len(preview.plan) >= 1)

    def test_start_workflow_sync(self):
        req = WorkflowRunRequest(
            code=self.sample_code,
            task="Audit code structure",
            async_run=False,
            execution_mode="deterministic",
        )
        response, token, status_code = self.service.start_workflow(req)

        self.assertEqual(status_code, 200)
        self.assertIsInstance(response, WorkflowRunResponse)
        self.assertEqual(response.status, response.result["status"])
        self.assertIsNotNone(token)
        self.assertIsNotNone(response.result)

    def test_start_workflow_reports_failed_result_status(self):
        req = WorkflowRunRequest(
            code=self.sample_code,
            task="Audit code structure",
            async_run=False,
            execution_mode="deterministic",
        )
        with patch.object(
            self.service.runtime,
            "execute_session",
            return_value={"status": "failed", "error": "execution failed"},
        ):
            response, _, status_code = self.service.start_workflow(req)

        self.assertEqual(status_code, 200)
        self.assertEqual(response.status, "failed")

    def test_start_workflow_async(self):
        req = WorkflowRunRequest(
            code=self.sample_code,
            task="Audit code structure",
            async_run=True,
            execution_mode="deterministic",
        )
        response, token, status_code = self.service.start_workflow(req)

        self.assertEqual(status_code, 202)
        self.assertIsInstance(response, WorkflowRunResponse)
        self.assertEqual(response.status, "accepted")
        self.assertIn(f"/agentic/stream/{response.session_id}", response.stream_url)

    def test_explicit_model_mode_is_recorded_as_required(self):
        self.service.runtime.set_model_client(MagicMock())
        req = WorkflowRunRequest(
            code=self.sample_code,
            task="Explain this module",
            async_run=True,
            execution_mode="model",
            require_model=True,
        )
        with patch.object(self.service, "is_model_ready", return_value=True):
            with patch.object(self.service.executor, "submit") as submit:
                response, _, status_code = self.service.start_workflow(req)

        self.assertEqual(status_code, 202)
        session = self.session_manager.get_session(response.session_id)
        self.assertTrue(session.metadata["require_model"])
        submit.assert_called_once()

    def test_start_workflow_invalid_dag_rejected(self):
        invalid_plan = [
            {"task_id": "step_1", "agent_key": "forge", "dependencies": ["non_existent_step"]}
        ]
        req = WorkflowRunRequest(
            code=self.sample_code,
            task="Invalid DAG task",
            plan=invalid_plan,
        )
        with self.assertRaises(SchemaValidationError) as ctx:
            self.service.start_workflow(req)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("Invalid custom plan", str(ctx.exception))

    def test_cancel_session_and_tickets(self):
        req = WorkflowRunRequest(
            code=self.sample_code,
            task="Scan code for security vulnerabilities",
            intent="security_scan",
            async_run=True,
            execution_mode="deterministic",
        )
        with patch.object(self.service.runtime, "execute_session"):
            resp, token, _ = self.service.start_workflow(req)
            session = self.session_manager.get_session(resp.session_id)
            self.assertIsNotNone(session)

            # Generate ticket
            ticket_resp = self.service.create_sse_ticket(session)
            self.assertTrue(ticket_resp.ticket.startswith("sse_"))

            # Cancel
            cancel_res, code = self.service.cancel_session(resp.session_id)
            self.assertIn(code, (202, 200))
            self.assertEqual(cancel_res["status"], "cancellation_requested")


if __name__ == "__main__":
    unittest.main()
