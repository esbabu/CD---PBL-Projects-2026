"""Typed request and response schemas for the Agentic AI Layer.

Provides validated dataclass models for:
- /agentic/run (WorkflowRunRequest, WorkflowRunResponse)
- /agentic/plan/preview (PlanPreviewRequest, PlanPreviewResponse)
- /agentic/action (UserActionRequest, UserActionResponse)
- /agentic/session/<id>/ticket (SSETicketResponse)
- SSE events (SSEEventEnvelope)
- Session state serialization
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import re
from typing import Any, Dict, List, Optional

from backend.request_utils import extract_code as _extract_code

SESSION_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_\-]{8,64}$")


class SchemaValidationError(ValueError):
    """Raised when an incoming request payload fails schema validation."""

    def __init__(self, message: str, status_code: int = 400, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


def validate_session_id(session_id: Any) -> str:
    """Validate that a session_id is a safe token string."""
    if not session_id or not isinstance(session_id, str) or not SESSION_ID_PATTERN.match(session_id):
        raise SchemaValidationError("Invalid session_id format.", status_code=400)
    return session_id


@dataclass
class WorkflowRunRequest:
    """Validated input schema for POST /agentic/run."""

    code: str
    task: str = ""
    auto_approve: bool = False
    async_run: bool = True
    execution_mode: Optional[str] = None
    require_model: Optional[bool] = None
    intent: Optional[str] = None
    plan: Optional[List[Dict[str, Any]]] = None
    max_review_cycles: int = 5
    workspace_id: Optional[str] = None
    active_file: Optional[str] = None
    project_context: Optional[Dict[str, str]] = field(default=None, repr=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any], max_source_length: int = 50000) -> "WorkflowRunRequest":
        """Parse and strictly validate raw JSON payload."""
        if not isinstance(data, dict):
            raise SchemaValidationError("Request payload must be a JSON object.")

        # 1. Code validation
        code = _extract_code(data)
        if code is None:
            raise SchemaValidationError("Code must be a string", status_code=400)
        if not isinstance(code, str):
            raise SchemaValidationError("Code must be a string", status_code=400)
        if not code.strip():
            raise SchemaValidationError("No code provided", status_code=400)
        if len(code) > max_source_length:
            raise SchemaValidationError("Payload Too Large", status_code=413)

        # 2. Task validation
        task = str(data.get("task", "")).strip()
        if len(task) > 4000:
            raise SchemaValidationError("Task is too long", status_code=413)
        workspace_id = data.get("workspace_id")
        active_file = data.get("active_file")
        if (workspace_id is None) != (active_file is None):
            raise SchemaValidationError(
                "workspace_id and active_file must be provided together."
            )
        if workspace_id is not None and (
            not isinstance(workspace_id, str)
            or not workspace_id
            or len(workspace_id) > 128
            or not isinstance(active_file, str)
            or not active_file
            or len(active_file) > 512
        ):
            raise SchemaValidationError("A valid workspace_id and active_file are required.")

        # 3. Strict JSON boolean validation: reject strings such as "false", "true", "0", "1"
        if "auto_approve" in data:
            raw_auto = data["auto_approve"]
            if not isinstance(raw_auto, bool):
                raise SchemaValidationError("'auto_approve' must be a valid JSON boolean (true or false).")
            if raw_auto:
                raise SchemaValidationError(
                    "Automatic approval is disabled; source changes require explicit operator approval."
                )
            auto_approve = False
        else:
            auto_approve = False

        if "async" in data:
            raw_async = data["async"]
            if not isinstance(raw_async, bool):
                raise SchemaValidationError("'async' must be a valid JSON boolean (true or false).")
            async_run = raw_async
        else:
            async_run = True

        # 4. require_model boolean validation
        require_model = data.get("require_model")
        if require_model is not None and not isinstance(require_model, bool):
            raise SchemaValidationError("require_model must be a boolean.")

        # 5. execution_mode validation
        raw_mode = str(data.get("execution_mode", "")).strip().lower()
        if raw_mode in {"deterministic", "offline"}:
            execution_mode = "deterministic"
            require_model = False
        elif raw_mode in {"model", "ai", "online"}:
            execution_mode = "model"
            require_model = True
        elif raw_mode:
            execution_mode = raw_mode
        else:
            execution_mode = None

        # 6. max_review_cycles validation
        raw_cycles = data.get("max_review_cycles", 5)
        try:
            max_review_cycles = int(raw_cycles)
            if max_review_cycles < 1 or max_review_cycles > 10:
                raise SchemaValidationError("max_review_cycles must be between 1 and 10.")
        except (ValueError, TypeError) as exc:
            if isinstance(exc, SchemaValidationError):
                raise
            raise SchemaValidationError("max_review_cycles must be a valid integer.") from exc

        # 7. plan validation (if provided)
        custom_plan = data.get("plan")
        if custom_plan is not None:
            if not isinstance(custom_plan, list):
                raise SchemaValidationError("Custom plan must be a list of task objects.")

        return cls(
            code=code,
            task=task,
            auto_approve=auto_approve,
            async_run=async_run,
            execution_mode=execution_mode,
            require_model=require_model,
            intent=data.get("intent"),
            plan=custom_plan,
            max_review_cycles=max_review_cycles,
            workspace_id=workspace_id,
            active_file=active_file,
        )


@dataclass
class WorkflowRunResponse:
    """Output schema for POST /agentic/run."""

    status: str
    session_id: str
    owner_token: Optional[str]
    stream_url: Optional[str]
    task: str
    execution_mode: str
    max_review_cycles: int
    result: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        if self.result:
            merged = dict(self.result)
            if self.owner_token:
                merged["owner_token"] = self.owner_token
            return merged
        data = {
            "status": self.status,
            "session_id": self.session_id,
            "task": self.task,
            "execution_mode": self.execution_mode,
            "max_review_cycles": self.max_review_cycles,
        }
        if self.owner_token:
            data["owner_token"] = self.owner_token
        if self.stream_url:
            data["stream_url"] = self.stream_url
        return data


@dataclass
class PlanPreviewRequest:
    """Input schema for POST /agentic/plan/preview."""

    task: str
    intent: Optional[str] = None
    code: Optional[str] = None
    workspace_id: Optional[str] = None
    active_file: Optional[str] = None
    context_files: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlanPreviewRequest":
        if not isinstance(data, dict):
            raise SchemaValidationError("Request payload must be a JSON object.")
        task = str(data.get("task", "")).strip()
        intent = data.get("intent")
        if intent is not None and not isinstance(intent, str):
            raise SchemaValidationError("Intent must be a string identifier.")
        code = data.get("code")
        if code is not None and not isinstance(code, str):
            raise SchemaValidationError("Code must be a string.")
        workspace_id = data.get("workspace_id")
        active_file = data.get("active_file")
        if (workspace_id is None) != (active_file is None):
            raise SchemaValidationError(
                "workspace_id and active_file must be provided together."
            )
        if workspace_id is not None and (
            not isinstance(workspace_id, str)
            or not workspace_id
            or len(workspace_id) > 128
            or not isinstance(active_file, str)
            or not active_file
            or len(active_file) > 512
        ):
            raise SchemaValidationError("A valid workspace_id and active_file are required.")
        return cls(
            task=task,
            intent=intent,
            code=code,
            workspace_id=workspace_id,
            active_file=active_file,
        )


@dataclass
class PlanPreviewResponse:
    """Output schema for POST /agentic/plan/preview."""

    intent: str
    profile_name: str
    description: str
    read_only: bool
    requires_approval: bool
    verification_required: bool
    allowed_agents: List[str]
    plan: List[Dict[str, Any]]
    why_agents: Dict[str, str]
    workspace_id: Optional[str] = None
    active_file: Optional[str] = None
    context_files: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class UserActionRequest:
    """Input schema for POST /agentic/action."""

    session_id: str
    action: str
    feedback: Optional[str] = None
    candidate_digest: Optional[str] = None
    approver: str = "operator"

    @classmethod
    def from_dict(cls, data: Dict[str, Any], approver: str = "operator") -> "UserActionRequest":
        if not isinstance(data, dict):
            raise SchemaValidationError("Request payload must be a JSON object.")
        session_id = data.get("session_id")
        if not session_id or not isinstance(session_id, str) or not SESSION_ID_PATTERN.match(session_id):
            raise SchemaValidationError("Missing valid session_id.", status_code=400)
        action = str(data.get("action", "")).strip().lower()
        if action not in ("approve", "reject"):
            raise SchemaValidationError("Action must be 'approve' or 'reject'.", status_code=400)
        feedback = data.get("feedback")
        if feedback is not None and not isinstance(feedback, str):
            feedback = str(feedback)
        candidate_digest = data.get("candidate_digest")
        if candidate_digest is not None and not isinstance(candidate_digest, str):
            candidate_digest = str(candidate_digest)

        return cls(
            session_id=session_id,
            action=action,
            feedback=feedback,
            candidate_digest=candidate_digest,
            approver=approver,
        )


@dataclass
class UserActionResponse:
    """Output schema for POST /agentic/action."""

    status: str
    session_id: str
    approval_status: str
    action: str
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "session_id": self.session_id,
            "approval_status": self.approval_status,
            "action": self.action,
            **self.details,
        }


@dataclass
class SSETicketResponse:
    """Output schema for POST /agentic/session/<id>/ticket."""

    status: str
    ticket: str
    session_id: str
    expires_in: int = 60

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SSEEventEnvelope:
    """Normalized Server-Sent Event payload schema."""

    event: str
    session_id: str
    agent: str = "SupervisorAgent"
    status: str = "running"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    event_id: Optional[int] = None
    data: Dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> Dict[str, Any]:
        """Flatten into wire payload format matching previous event contract."""
        payload = {
            "session_id": self.session_id,
            "agent": self.agent,
            "timestamp": self.timestamp,
            "status": self.status,
            **self.data,
        }
        if self.event_id is not None:
            payload["event_id"] = self.event_id
        return payload
