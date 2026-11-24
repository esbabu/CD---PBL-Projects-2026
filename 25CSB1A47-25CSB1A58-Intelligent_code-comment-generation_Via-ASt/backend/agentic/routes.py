"""Flask routes and streaming endpoints for the Agentic AI Layer."""

from __future__ import annotations

import logging
import secrets
from typing import Any, Optional

from flask import Blueprint, Response, current_app, jsonify, request

from backend.config import AppConfig
from backend.agentic.events import default_broadcaster
from backend.agentic.intent import (
    classify_intent,
)
from backend.agentic.schemas import (
    PlanPreviewRequest,
    SchemaValidationError,
    UserActionRequest,
    WorkflowRunRequest,
)
from backend.agentic.service import (
    default_workflow_service,
)
from backend.agentic.session import (
    AgentSession,
    default_session_manager,
    default_sse_ticket_store,
    is_valid_session_id,
)
from backend.model_provider import (
    create_model_client,
    provider_display_name,
    provider_ready,
)
from backend.request_utils import request_data as _parse_request_data

logger = logging.getLogger(__name__)

agentic_routes = Blueprint("agentic", __name__)

# Shared runtime and service instances hooked to broadcaster
_runtime = default_workflow_service.runtime
_tool_registry = default_workflow_service.runtime.tools
_agent_executor = default_workflow_service.executor


def _verify_session_access(session: AgentSession) -> Optional[tuple[Response, int]]:
    """Enforce session ownership or admin authorization on all routes.

    A valid owner credential is required in ALL environments (dev, test, prod).
    Bare session UUIDs NEVER authorize access.
    """
    expected_api_key = (current_app.config.get("API_KEY") or "").strip()
    auth_header = request.headers.get("Authorization", "")
    bearer_token = ""
    if auth_header.lower().startswith("bearer "):
        bearer_token = auth_header.split(None, 1)[1].strip()

    provided_api_key = request.headers.get("X-API-Key", "").strip() or bearer_token

    # 1. Admin API key check
    is_admin = bool(
        expected_api_key
        and provided_api_key
        and secrets.compare_digest(provided_api_key, expected_api_key)
    )
    if is_admin:
        return None

    session_token = getattr(session, "owner_token", "")
    if not session_token:
        return jsonify({"error": "Session state invalid: missing owner token."}), 500

    # Reject durable tokens in query parameters across all routes
    if request.args.get("token") or request.args.get("owner_token"):
        return jsonify({
            "error": "Forbidden: durable tokens in query parameters are disallowed. Use headers, session cookies, or single-use SSE tickets.",
            "status": "query_token_disallowed",
        }), 403

    # 2. Check X-Session-Token or Bearer matching session_token
    header_token = request.headers.get("X-Session-Token", "").strip()
    if not header_token and bearer_token:
        header_token = bearer_token

    # 3. Check Cookie (preferred for browser same-origin sessions)
    cookie_token = (
        request.cookies.get(f"ast_session_{session.session_id}", "").strip()
        or request.cookies.get("ast_session_token", "").strip()
    )

    # 4. Check JSON body token (for POST /agentic/action)
    body_token = ""
    if request.is_json:
        body = request.get_json(silent=True) or {}
        if isinstance(body, dict):
            body_token = str(body.get("token") or body.get("owner_token") or "").strip()

    provided_token = header_token or cookie_token or body_token

    if not provided_token:
        return jsonify({
            "error": "Authentication required: missing session owner credential.",
            "status": "unauthorized",
        }), 401

    if secrets.compare_digest(provided_token, session_token):
        return None

    return jsonify({
        "error": "Forbidden: invalid session token.",
        "status": "forbidden",
    }), 403


def refresh_agentic_model_client() -> None:
    """Keep the shared agent runtime aligned with provider settings changes."""
    _runtime.set_model_client(create_model_client())


def agentic_model_ready() -> bool:
    """Report whether a real, configured model provider is ready for agent runs."""
    return bool(
        AppConfig.AI_PROVIDER != "ast"
        and getattr(_runtime.model_client, "chat", None)
        and provider_ready(_runtime.model_client)
    )


def run_agentic_workflow_sync(
    source_code: str,
    task: str,
    *,
    auto_approve: bool = False,
    max_review_cycles: int = 5,
    execution_mode: Optional[str] = None,
) -> dict[str, Any]:
    """Execute the shared supervisor workflow synchronously for compatibility routes."""
    session = _runtime.start_session(
        source_code=source_code,
        task=task,
        auto_approve=auto_approve,
        max_review_cycles=max_review_cycles,
        execution_mode=execution_mode,
        require_model=execution_mode == "model",
    )
    return _runtime.execute_session(session.session_id)


def _request_data():
    return _parse_request_data(request)


def _load_project_context(workspace_id: str, active_file: str) -> dict[str, str]:
    """Load redacted, bounded project files from the server-owned workspace."""
    from backend.project.assistant_service import (
        ProjectAssistantError,
        build_project_context,
    )
    from backend.project.routes import _get_workspace

    try:
        workspace = _get_workspace(workspace_id)
        context, _ = build_project_context(workspace, active_file)
    except KeyError as exc:
        raise SchemaValidationError(
            "The requested project workspace was not found.",
            status_code=404,
        ) from exc
    except ProjectAssistantError as exc:
        raise SchemaValidationError(str(exc), status_code=exc.status_code) from exc
    return context


@agentic_routes.route("/agentic/status", methods=["GET"])
def get_agentic_runtime_status_route():
    """Return provider, workforce, and retained workflow counters for the control center."""
    provider = AppConfig.AI_PROVIDER
    configured_provider_ready = provider_ready(_runtime.model_client)
    model_execution_ready = agentic_model_ready()
    return jsonify({
        "orchestrator": {
            "name": "NEXUS",
            "role": "Autonomous AI Orchestrator",
            "status": "ready",
        },
        "provider": {
            "id": provider,
            "name": provider_display_name(provider),
            "model": _runtime.supervisor.model_name,
            "ready": configured_provider_ready,
            "model_execution_ready": model_execution_ready,
            "execution_mode": (
                "model-assisted" if model_execution_ready else "deterministic"
            ),
        },
        "registered_agent_count": len(_runtime.supervisor.swarm),
        "agents": [
            {
                "key": key,
                "name": agent.name,
                "responsibility": agent.role_description,
                "model": agent.model_name,
            }
            for key, agent in _runtime.supervisor.swarm.items()
        ],
        "statistics": default_session_manager.runtime_statistics(),
    })


@agentic_routes.route("/agentic/tools", methods=["GET"])
def list_agentic_tools_route():
    """Return allowlisted tools and their standard schemas."""
    return jsonify({
        "status": "success",
        "count": len(_tool_registry.list_tools()),
        "tools": [
            {
                "name": t.name,
                "description": t.description,
                "is_read_only": t.is_read_only,
                "requires_approval": t.requires_approval,
                "schema": t.parameters_schema,
            }
            for t in _tool_registry.list_tools()
        ],
    })


@agentic_routes.route("/agentic/plan/preview", methods=["POST"])
def preview_agentic_plan_route():
    """Preview the task DAG and agent assignments before starting execution."""
    try:
        req = PlanPreviewRequest.from_dict(_request_data())
        if req.workspace_id and req.active_file:
            context = _load_project_context(req.workspace_id, req.active_file)
            req.context_files = sorted(context)
        resp = default_workflow_service.preview_plan(req)
        return jsonify(resp.to_dict()), 200
    except SchemaValidationError as exc:
        return jsonify({"error": exc.message, **exc.details}), exc.status_code


@agentic_routes.route("/agentic/run", methods=["POST"])
def run_agentic_workflow_route():
    """Start an autonomous agentic workflow with optional background streaming."""
    try:
        req = WorkflowRunRequest.from_dict(
            _request_data(),
            max_source_length=current_app.config.get("MAX_SOURCE_LENGTH", 50000),
        )
        if req.workspace_id:
            try:
                req.intent = classify_intent(req.task, explicit_intent=req.intent).value
            except ValueError as exc:
                raise SchemaValidationError(str(exc), status_code=400) from exc
            if req.active_file:
                req.project_context = _load_project_context(
                    req.workspace_id,
                    req.active_file,
                )
                req.code = req.project_context.get(req.active_file, req.code or "")
            elif not req.code:
                from backend.project.routes import _get_workspace
                try:
                    ws = _get_workspace(req.workspace_id)
                    py_files = ws.list_python_files()
                    if py_files:
                        req.active_file = py_files[0]
                        req.project_context = _load_project_context(
                            req.workspace_id,
                            req.active_file,
                        )
                        req.code = req.project_context.get(req.active_file, "")
                except Exception:
                    pass
        response_schema, owner_token, status_code = default_workflow_service.start_workflow(
            req,
            is_secure=request.is_secure,
            is_model_ready=agentic_model_ready(),
        )
    except SchemaValidationError as exc:
        return jsonify({"error": exc.message, **exc.details}), exc.status_code

    resp = jsonify(response_schema.to_dict())
    resp.status_code = status_code
    if owner_token:
        resp.set_cookie(
            f"ast_session_{response_schema.session_id}",
            owner_token,
            httponly=True,
            samesite="Lax",
            secure=request.is_secure,
            path="/",
        )
    return resp


@agentic_routes.route("/agentic/session/<session_id>/ticket", methods=["POST"])
def create_session_sse_ticket_route(session_id: str):
    """Generate a single-use, short-lived (60s) ticket for EventSource streaming."""
    if not is_valid_session_id(session_id):
        return jsonify({"error": "Invalid session_id format."}), 400
    session = default_session_manager.get_session(session_id)
    if not session:
        return jsonify({"error": f"Session '{session_id}' not found."}), 404
    access_error = _verify_session_access(session)
    if access_error is not None:
        return access_error

    ticket_resp = default_workflow_service.create_sse_ticket(session)
    return jsonify(ticket_resp.to_dict()), 200


@agentic_routes.route("/agentic/stream/<session_id>", methods=["GET"])
def stream_agentic_workflow_route(session_id: str):
    """Server-Sent Events endpoint streaming real-time thoughts and tool execution frames."""
    if not is_valid_session_id(session_id):
        return jsonify({"error": "Invalid session_id format."}), 400
    session = default_session_manager.get_session(session_id)
    if not session:
        return jsonify({"error": f"Session '{session_id}' not found."}), 404

    # 1. Ephemeral, single-use ticket in query string
    ticket = request.args.get("ticket", "").strip()
    if ticket:
        if default_sse_ticket_store.is_ticket_expired(ticket):
            return jsonify({
                "error": "Forbidden: SSE ticket has expired.",
                "status": "expired_ticket",
            }), 403
        if not default_sse_ticket_store.consume_ticket(session_id, ticket):
            return jsonify({
                "error": "Forbidden: invalid or replayed SSE ticket.",
                "status": "invalid_ticket",
            }), 403
    else:
        # 2. Durable tokens in query strings are rejected
        if request.args.get("token") or request.args.get("owner_token"):
            return jsonify({
                "error": "Forbidden: durable tokens in query parameters are disallowed. Use a single-use ticket or session cookie.",
                "status": "query_token_disallowed",
            }), 403

        # 3. Verify via Cookie, Header, or Admin API Key
        access_error = _verify_session_access(session)
        if access_error is not None:
            return access_error

    last_event_id = request.headers.get("Last-Event-ID")
    try:
        after_event_id = int(last_event_id) if last_event_id else None
        if after_event_id is not None and after_event_id < 0:
            after_event_id = None
    except ValueError:
        after_event_id = None
    stream_generator = default_broadcaster.generate_sse_stream(
        session_id, after_event_id=after_event_id
    )
    response = Response(stream_generator, mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache, no-transform"
    response.headers["X-Accel-Buffering"] = "no"
    response.headers["Connection"] = "keep-alive"
    return response


@agentic_routes.route("/agentic/session/<session_id>", methods=["GET"])
def get_agentic_session_route(session_id: str):
    """Fetch current state, trajectory, and diff for a session."""
    if not is_valid_session_id(session_id):
        return jsonify({"error": "Invalid session_id format."}), 400
    session = default_session_manager.get_session(session_id)
    if not session:
        return jsonify({"error": f"Session '{session_id}' not found."}), 404
    access_error = _verify_session_access(session)
    if access_error is not None:
        return access_error
    last_event_id = default_broadcaster.latest_event_id(session_id)
    session_data = session.to_dict()
    session_data["last_event_id"] = last_event_id
    return jsonify(session_data)


@agentic_routes.route("/agentic/cancel/<session_id>", methods=["POST"])
@agentic_routes.route("/agentic/session/<session_id>/cancel", methods=["POST"])
def cancel_agentic_session_route(session_id: str):
    """Request cancellation after the current in-flight agent/tool operation."""
    if not is_valid_session_id(session_id):
        return jsonify({"error": "Invalid session_id format."}), 400
    session = default_session_manager.get_session(session_id)
    if not session:
        return jsonify({"error": f"Session '{session_id}' not found."}), 404
    access_error = _verify_session_access(session)
    if access_error is not None:
        return access_error

    result, status_code = default_workflow_service.cancel_session(session_id)
    return jsonify(result), status_code


@agentic_routes.route("/agentic/action", methods=["POST"])
def user_action_agentic_route():
    """Handle Human-in-the-Loop decision for pending approval."""
    data = _request_data()
    approver = request.headers.get("X-Approver-Id") or "operator"
    try:
        action_req = UserActionRequest.from_dict(data, approver=approver)
    except SchemaValidationError as exc:
        return jsonify({"error": exc.message, **exc.details}), exc.status_code

    session = default_session_manager.get_session(action_req.session_id)
    if not session:
        return jsonify({"error": f"Session '{action_req.session_id}' not found."}), 404
    access_error = _verify_session_access(session)
    if access_error is not None:
        return access_error

    result, status_code = default_workflow_service.handle_user_action(action_req, session)
    return jsonify(result), status_code
