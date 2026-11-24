"""Service layer orchestrating workflow execution, plan formulation, and actions.

Keeps Flask routes thin:
Request Validation -> Service Call -> Response Mapping
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Tuple

from backend.agentic.events import EventBroadcaster, default_broadcaster
from backend.agentic.intent import (
    POLICY_TABLE,
    build_deterministic_plan,
    classify_intent,
    validate_dag,
)
from backend.agentic.provider_adapter import (
    ProviderAdapter,
    default_provider_adapter,
)
from backend.agentic.runtime import AgentRuntime
from backend.agentic.schemas import (
    PlanPreviewRequest,
    PlanPreviewResponse,
    SSETicketResponse,
    SchemaValidationError,
    UserActionRequest,
    WorkflowRunRequest,
    WorkflowRunResponse,
)
from backend.agentic.session import (
    AgentSession,
    SessionManager,
    default_session_manager,
    default_sse_ticket_store,
)
from backend.agentic.tools import create_standard_tool_registry
from backend.config import AppConfig
from backend.security_queue import BoundedExecutor, QueueFullError

logger = logging.getLogger(__name__)


class AgenticWorkflowService:
    """Orchestration authority managing runtime lifecycle, task planning, and user approvals."""

    def __init__(
        self,
        runtime: Optional[AgentRuntime] = None,
        session_manager: Optional[SessionManager] = None,
        broadcaster: Optional[EventBroadcaster] = None,
        executor: Optional[BoundedExecutor] = None,
        provider_adapter: Optional[ProviderAdapter] = None,
    ) -> None:
        self.session_manager = session_manager or default_session_manager
        self.broadcaster = broadcaster or default_broadcaster
        self.executor = executor or BoundedExecutor(max_workers=5, max_queue_size=20, name_prefix="agentic-worker")
        self.provider_adapter = provider_adapter or default_provider_adapter

        if runtime is not None:
            self.runtime = runtime
        else:
            tool_registry = create_standard_tool_registry()
            self.runtime = AgentRuntime(
                tools=tool_registry,
                session_manager=self.session_manager,
                model_client=self.provider_adapter.create_client(),
                event_callback=self.broadcaster.emit,
                provider_adapter=self.provider_adapter,
            )

    def is_model_ready(self) -> bool:
        """Report whether configured provider is ready for model-assisted workflows."""
        return self.provider_adapter.is_model_execution_ready(self.runtime.model_client)

    def preview_plan(self, req: PlanPreviewRequest) -> PlanPreviewResponse:
        """Formulate and preview an execution plan before workflow dispatch."""
        try:
            intent = classify_intent(req.task, explicit_intent=req.intent)
        except ValueError as exc:
            raise SchemaValidationError(str(exc), status_code=400, details={"status": "invalid_intent"}) from exc

        profile = POLICY_TABLE[intent]
        plan = build_deterministic_plan(intent, req.task)

        return PlanPreviewResponse(
            intent=intent.value,
            profile_name=profile.name,
            description=profile.description,
            read_only=profile.read_only,
            requires_approval=profile.requires_approval,
            verification_required=profile.verification_required,
            allowed_agents=profile.allowed_agents,
            plan=plan,
            why_agents=profile.agent_reasons,
            workspace_id=req.workspace_id,
            active_file=req.active_file,
            context_files=list(req.context_files),
        )

    def start_workflow(
        self,
        req: WorkflowRunRequest,
        is_secure: bool = False,
        is_model_ready: Optional[bool] = None,
    ) -> Tuple[WorkflowRunResponse, str, int]:
        """Validate configuration, initialize session, and dispatch synchronous or asynchronous execution."""
        if req.auto_approve:
            raise SchemaValidationError(
                "Automatic approval is disabled; source changes require explicit operator approval.",
                status_code=400,
            )

        # 1. Resolve execution mode
        model_ready = self.is_model_ready() if is_model_ready is None else is_model_ready
        if req.execution_mode == "model":
            execution_mode = "model"
            require_model = True
        elif req.execution_mode == "deterministic":
            execution_mode = "deterministic"
            require_model = False
        elif req.require_model is True:
            execution_mode = "model"
            require_model = True
        elif req.require_model is False:
            execution_mode = "deterministic"
            require_model = False
        else:
            execution_mode = "model" if model_ready else "deterministic"
            require_model = False

        if (require_model or execution_mode == "model") and not model_ready:
            raise SchemaValidationError(
                "A ready AI model provider is required for this workflow. Configure and test a provider in Settings, then retry.",
                status_code=503,
                details={
                    "configuration_required": True,
                    "provider": AppConfig.AI_PROVIDER,
                    "provider_ready": False,
                },
            )

        # 2. Validate custom DAG if provided
        if req.plan:
            try:
                validate_dag(req.plan)
            except ValueError as exc:
                raise SchemaValidationError(f"Invalid custom plan: {exc}", status_code=400) from exc

        # 3. Start Session
        try:
            session = self.runtime.start_session(
                source_code=req.code,
                task=req.task,
                auto_approve=False,
                max_review_cycles=req.max_review_cycles,
                execution_mode=execution_mode,
                intent=req.intent,
                custom_plan=req.plan,
                workspace_id=req.workspace_id,
                active_file=req.active_file,
                project_context=req.project_context,
                require_model=require_model,
            )
        except ValueError as exc:
            raise SchemaValidationError(str(exc), status_code=400, details={"syntax_error": True}) from exc
        except PermissionError as exc:
            raise SchemaValidationError(str(exc), status_code=422, details={"security_blocked": True}) from exc
        except Exception as exc:
            logger.exception("Failed to initialize agent session")
            raise SchemaValidationError(f"Failed to initialize session: {exc}", status_code=500) from exc

        # 4. Dispatch Execution
        stream_endpoint = f"/agentic/stream/{session.session_id}"
        owner_token = session.owner_token

        if req.async_run:
            try:
                self.executor.submit(self.runtime.execute_session, session.session_id)
            except QueueFullError as exc:
                raise SchemaValidationError(str(exc), status_code=503, details={"status": "rejected"}) from exc

            response = WorkflowRunResponse(
                status="accepted",
                session_id=session.session_id,
                owner_token=owner_token,
                stream_url=stream_endpoint,
                task=session.task,
                execution_mode=session.metadata.get("execution_mode", "deterministic"),
                max_review_cycles=session.metadata.get("max_review_cycles", 5),
            )
            return response, owner_token, 202

        # Synchronous execution
        result = self.runtime.execute_session(session.session_id)
        response = WorkflowRunResponse(
            status=result.get("status", "completed"),
            session_id=session.session_id,
            owner_token=owner_token,
            stream_url=stream_endpoint,
            task=session.task,
            execution_mode=session.metadata.get("execution_mode", "deterministic"),
            max_review_cycles=session.metadata.get("max_review_cycles", 5),
            result=result,
        )
        return response, owner_token, 200

    def handle_user_action(self, req: UserActionRequest, session: AgentSession) -> Tuple[Dict[str, Any], int]:
        """Process operator approval or rejection for a pending mutation."""
        result = self.runtime.handle_user_action(
            req.session_id,
            req.action,
            req.feedback,
            approver=req.approver,
            candidate_digest=req.candidate_digest,
        )
        if result.get("status") == "error":
            return result, 400

        if session.status == "running":
            try:
                self.executor.submit(self.runtime.execute_session, req.session_id)
            except QueueFullError as exc:
                return {"error": str(exc), "status": "rejected"}, 503

        return result, 200

    def cancel_session(self, session_id: str) -> Tuple[Dict[str, Any], int]:
        """Request graceful cancellation of an active workflow."""
        try:
            result = self.runtime.cancel_session(session_id)
        except KeyError as exc:
            return {"error": str(exc)}, 404

        status_code = 202 if result["status"] in {"cancellation_requested", "cancelled"} else 409
        return result, status_code

    def create_sse_ticket(self, session: AgentSession) -> SSETicketResponse:
        """Issue a single-use, 60s ticket bound to a session."""
        ticket = default_sse_ticket_store.create_ticket(
            session_id=session.session_id,
            owner_token=session.owner_token,
            ttl_seconds=60.0,
        )
        return SSETicketResponse(
            status="success",
            ticket=ticket,
            session_id=session.session_id,
            expires_in=60,
        )


default_workflow_service = AgenticWorkflowService()
