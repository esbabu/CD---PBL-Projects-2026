"""Thread-safe session state and context persistence for Agentic AI Layer."""

from __future__ import annotations

import hashlib
import json
import os
import re
import secrets
import sqlite3
import threading
import time
import uuid
from contextlib import closing
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from backend.agentic.repository import (
    AbstractSessionRepository,
    InMemorySessionRepository,
    SQLiteSessionRepository,
)
from backend.agentic.verification_contract import migrate_legacy_audit

SESSION_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_\-]{8,64}$")


def is_valid_session_id(session_id: str) -> bool:
    """Validate that a session_id matches safe alphanumeric token format."""
    return bool(session_id and isinstance(session_id, str) and SESSION_ID_PATTERN.match(session_id))


@dataclass
class Checkpoint:
    """Snapshot of source code and audit metrics at a specific step."""

    id: str
    step: int
    label: str
    code: str
    code_digest: str
    created_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TrajectoryStep:
    """Audit record of a single agent deliberation or tool execution turn."""

    step: int
    agent: str
    thought: str
    action: str
    tool: Optional[str] = None
    tool_arguments: Optional[Dict[str, Any]] = None
    observation: Optional[Dict[str, Any]] = None
    model_output: Optional[Dict[str, Any]] = None
    duration_ms: float = 0.0
    timestamp: float = field(default_factory=time.time)


@dataclass
class AgentSession:
    """Persistent working state for an autonomous agent execution workflow."""

    session_id: str
    original_code: str
    original_code_digest: str
    current_code: str
    task: str
    status: str = "idle"
    cancel_requested: bool = False
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    plan: List[Dict[str, Any]] = field(default_factory=list)
    trajectory: List[TrajectoryStep] = field(default_factory=list)
    checkpoints: List[Checkpoint] = field(default_factory=list)
    pending_approval: Optional[Dict[str, Any]] = None
    is_approved: bool = False
    approval_status: str = "not_required"
    approval_history: List[Dict[str, Any]] = field(default_factory=list)
    owner_token: str = field(default_factory=lambda: secrets.token_urlsafe(32))
    metadata: Dict[str, Any] = field(default_factory=dict)
    project_context: Dict[str, str] = field(default_factory=dict, repr=False)
    tasks: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    findings: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    messages: List[Dict[str, Any]] = field(default_factory=list)
    tool_observations: List[Dict[str, Any]] = field(default_factory=list)
    modification_history: List[Dict[str, Any]] = field(default_factory=list)
    final_audit: Optional[Dict[str, Any]] = None
    model_client: Any = field(default=None, repr=False, compare=False)
    event_callback: Optional[Callable[[str, Dict[str, Any]], None]] = field(
        default=None, repr=False, compare=False
    )
    persist_callback: Optional[Callable[["AgentSession"], None]] = field(
        default=None, repr=False, compare=False
    )
    _tool_call_signatures: set[str] = field(default_factory=set, repr=False)
    _lock: threading.RLock = field(default_factory=threading.RLock, repr=False)

    def emit_event(
        self,
        event: str,
        *,
        agent: str = "SupervisorAgent",
        status: Optional[str] = None,
        **details: Any,
    ) -> None:
        """Publish an event with session identity and an observed timestamp."""
        payload = {
            "session_id": self.session_id,
            "agent": agent,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": status or self.status,
            **details,
        }
        if self.persist_callback is not None:
            self.persist_callback(self)
        if self.event_callback is not None:
            self.event_callback(event, payload)

    def record_step(
        self,
        agent: str,
        thought: str,
        action: str,
        tool: Optional[str] = None,
        tool_arguments: Optional[Dict[str, Any]] = None,
        observation: Optional[Dict[str, Any]] = None,
        model_output: Optional[Dict[str, Any]] = None,
        duration_ms: float = 0.0,
        task_id: Optional[str] = None,
    ) -> TrajectoryStep:
        """Append an audited step to episodic trajectory memory."""
        with self._lock:
            step_num = len(self.trajectory) + 1
            step = TrajectoryStep(
                step=step_num,
                agent=agent,
                thought=thought,
                action=action,
                tool=tool,
                tool_arguments=tool_arguments,
                observation=observation,
                model_output=model_output,
                duration_ms=round(duration_ms, 3),
            )
            self.trajectory.append(step)
            self.updated_at = time.time()
        observation_status = (
            observation.get("status")
            if isinstance(observation, dict)
            else None
        )
        model_output_summary = (
            {
                "action": model_output.get("action"),
                "tool": model_output.get("tool"),
                "argument_names": sorted(
                    model_output.get("arguments", {})
                )
                if isinstance(model_output.get("arguments"), dict)
                else [],
            }
            if isinstance(model_output, dict)
            else None
        )
        self.emit_event(
            "trajectory_step",
            agent=agent,
            status="recorded",
            task_id=task_id,
            step=step_num,
            action=action,
            tool=tool,
            argument_names=sorted(tool_arguments) if tool_arguments else [],
            observation_status=observation_status,
            model_output=model_output_summary,
            duration_ms=step.duration_ms,
        )
        return step

    def update_step_duration(self, step: TrajectoryStep, duration_ms: float) -> None:
        """Update measured execution time for a completed trajectory step."""
        with self._lock:
            if step in self.trajectory:
                step.duration_ms = round(duration_ms, 3)
                self.updated_at = time.time()

    def create_checkpoint(self, label: str, metadata: Optional[Dict[str, Any]] = None) -> Checkpoint:
        """Create a safe snapshot of current code before applying modifications."""
        with self._lock:
            chk_id = f"chk_{len(self.checkpoints) + 1}_{uuid.uuid4().hex[:6]}"
            digest = hashlib.sha256(self.current_code.encode("utf-8")).hexdigest()
            checkpoint = Checkpoint(
                id=chk_id,
                step=len(self.trajectory),
                label=label,
                code=self.current_code,
                code_digest=digest,
                metadata=metadata or {},
            )
            self.checkpoints.append(checkpoint)
            self.updated_at = time.time()
        self.emit_event(
            "checkpoint_created",
            status="created",
            checkpoint_id=checkpoint.id,
            label=checkpoint.label,
            code_digest=checkpoint.code_digest,
        )
        return checkpoint

    def rollback_to(self, checkpoint_id: str) -> bool:
        """Restore working code to a previous checkpoint."""
        with self._lock:
            for chk in reversed(self.checkpoints):
                if chk.id == checkpoint_id:
                    self.current_code = chk.code
                    self.updated_at = time.time()
                    return True
            return False

    def update_code(self, new_code: str) -> None:
        """Update working code with thread-safe timestamp tracking."""
        with self._lock:
            self.current_code = new_code
            self.updated_at = time.time()

    def assign_task(self, task: Dict[str, Any]) -> None:
        """Persist a supervisor assignment and its dependency contract."""
        task_id = task.get("task_id")
        if not isinstance(task_id, str) or not task_id:
            raise ValueError("A task assignment requires a non-empty task_id.")
        with self._lock:
            self.tasks[task_id] = {
                **task,
                "status": task.get("status", "pending"),
                "assigned_at": datetime.now(timezone.utc).isoformat(),
            }
            self.updated_at = time.time()
        self.emit_event(
            "task_assigned",
            agent=str(task.get("agent_key", "SupervisorAgent")),
            status="pending",
            task_id=task_id,
            task=task.get("name", ""),
            description=task.get("description", ""),
            dependencies=list(task.get("dependencies", [])),
        )

    def request_cancellation(self) -> None:
        with self._lock:
            self.cancel_requested = True
            self.updated_at = time.time()

    def update_task(self, task_id: str, **updates: Any) -> None:
        with self._lock:
            task = self.tasks.get(task_id)
            if task is None:
                raise KeyError(f"Unknown task assignment '{task_id}'.")
            task.update(updates)
            for plan_task in self.plan:
                if plan_task.get("task_id") == task_id:
                    plan_task.update(updates)
            self.updated_at = time.time()

    def publish_findings(
        self,
        agent: str,
        findings: List[Any],
        *,
        task_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Store structured findings independently of the bounded trajectory."""
        if not isinstance(findings, list):
            raise TypeError("Agent findings must be supplied as a list.")
        published: List[Dict[str, Any]] = []
        with self._lock:
            existing = self.findings.setdefault(agent, [])
            for item in findings:
                if isinstance(item, dict):
                    finding = dict(item)
                else:
                    finding = {"summary": str(item)}
                finding.setdefault("source_agent", agent)
                if task_id:
                    finding.setdefault("task_id", task_id)
                if not finding.get("finding_id"):
                    fingerprint = json.dumps(finding, sort_keys=True, default=str)
                    finding["finding_id"] = hashlib.sha256(
                        fingerprint.encode("utf-8")
                    ).hexdigest()[:16]
                finding.setdefault(
                    "published_at", datetime.now(timezone.utc).isoformat()
                )
                existing.append(finding)
                published.append(finding)
            self.updated_at = time.time()
        for finding in published:
            self.emit_event(
                "finding_published",
                agent=agent,
                status="published",
                task_id=task_id,
                finding=finding,
            )
        return published

    def get_findings(self, agent: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve copies of findings by agent or across the shared workspace."""
        with self._lock:
            if agent is not None:
                return [dict(item) for item in self.findings.get(agent, [])]
            return [
                dict(item)
                for items in self.findings.values()
                for item in items
            ]

    def send_message(
        self,
        sender: str,
        recipient: str,
        message: str,
        *,
        evidence_finding_ids: Optional[List[str]] = None,
        structured_payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not message.strip():
            raise ValueError("Agent messages must contain non-whitespace text.")
        record = {
            "message_id": uuid.uuid4().hex,
            "from": sender,
            "to": recipient,
            "message": message,
            "evidence_finding_ids": list(evidence_finding_ids or []),
            "structured_payload": dict(structured_payload or {}),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        with self._lock:
            self.messages.append(record)
            self.updated_at = time.time()
        self.emit_event(
            "agent_message",
            agent=sender,
            status="sent",
            recipient=recipient,
            message_id=record["message_id"],
            message=message,
            evidence_finding_ids=record["evidence_finding_ids"],
            structured_payload=record["structured_payload"],
        )
        self.emit_event(
            "handoff_dispatched",
            agent=sender,
            status="dispatched",
            sender=sender,
            recipient=recipient,
            message_id=record["message_id"],
            message=message,
            evidence_finding_ids=record["evidence_finding_ids"],
            structured_payload=record["structured_payload"],
        )
        return dict(record)

    def context_for(self, agent: str, task_id: Optional[str] = None) -> Dict[str, Any]:
        """Build explicit shared context from assignments, findings, and messages."""
        with self._lock:
            task = dict(self.tasks.get(task_id, {})) if task_id else {}
            dependencies = set(task.get("dependencies", []))
            dependency_agents = {
                self.tasks[dependency]["agent_key"]
                for dependency in dependencies
                if dependency in self.tasks
            }
            available_findings = [
                dict(item)
                for owner in dependency_agents
                for item in self.findings.get(owner, [])
            ]
            messages = [
                dict(item)
                for item in self.messages
                if item["to"] in {agent, "SupervisorAgent"}
                and item["from"] in dependency_agents | {"SupervisorAgent"}
            ]
            tool_observations = [
                dict(item)
                for item in self.tool_observations
                if item["agent"] == agent or item["agent"] in dependency_agents
            ]
            return {
                "task": task,
                "dependency_findings": available_findings,
                "messages": messages,
                "tool_observations": tool_observations,
                "current_code": self.current_code,
                "original_code": self.original_code,
            }

    def has_successful_tool_observation(
        self, agent: str, task_id: Optional[str] = None
    ) -> bool:
        with self._lock:
            return any(
                item["agent"] == agent
                and (task_id is None or item["task_id"] == task_id)
                and item["result"].get("status") == "success"
                for item in self.tool_observations
            )

    def record_tool_observation(
        self,
        agent: str,
        task_id: Optional[str],
        tool: str,
        arguments: Dict[str, Any],
        result: Dict[str, Any],
        duration_ms: float,
    ) -> None:
        """Persist the result actually returned by the registered tool."""
        observation = {
            "agent": agent,
            "task_id": task_id,
            "tool": tool,
            "arguments": dict(arguments),
            "result": dict(result),
            "duration_ms": round(duration_ms, 3),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        with self._lock:
            self.tool_observations.append(observation)
            self.updated_at = time.time()

    def register_tool_call(self, agent: str, task_id: Optional[str], tool: str, arguments: Dict[str, Any]) -> bool:
        """Return false if the same agent repeats an identical action in a task."""
        signature = self._tool_call_signature(agent, task_id, tool, arguments)
        with self._lock:
            if signature in self._tool_call_signatures:
                return False
            self._tool_call_signatures.add(signature)
            return True

    @staticmethod
    def _tool_call_signature(
        agent: str, task_id: Optional[str], tool: str, arguments: Dict[str, Any]
    ) -> str:
        signature_data = json.dumps(
            [agent, task_id, tool, arguments], sort_keys=True, default=str
        )
        return hashlib.sha256(signature_data.encode("utf-8")).hexdigest()

    def unregister_tool_call(
        self, agent: str, task_id: Optional[str], tool: str, arguments: Dict[str, Any]
    ) -> None:
        """Allow the same tool action again after it was paused for approval."""
        signature = self._tool_call_signature(agent, task_id, tool, arguments)
        with self._lock:
            self._tool_call_signatures.discard(signature)

    def record_modification(self, modification: Dict[str, Any]) -> None:
        with self._lock:
            self.modification_history.append(
                {
                    **modification,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )
            self.updated_at = time.time()

    def set_status(self, status: str) -> None:
        """Update session state machine status."""
        with self._lock:
            self.status = status
            self.updated_at = time.time()
        if self.persist_callback is not None:
            self.persist_callback(self)

    def record_model_call(self) -> int:
        """Record one provider request attempt and publish its telemetry."""
        with self._lock:
            call_number = int(self.metadata.get("model_call_count", 0)) + 1
            self.metadata["model_call_count"] = call_number
            self.updated_at = time.time()
        self.emit_event(
            "model_call_started",
            agent="ModelProvider",
            status="running",
            call_number=call_number,
        )
        return call_number

    def to_dict(self, include_owner_token: bool = False) -> Dict[str, Any]:
        """Serialize session state into a JSON-compatible dictionary."""
        with self._lock:
            migrated_audit = (
                migrate_legacy_audit(self.final_audit)
                if self.final_audit is not None
                else None
            )
            data: Dict[str, Any] = {
                "session_id": self.session_id,
                "status": self.status,
                "cancel_requested": self.cancel_requested,
                "task": self.task,
                "created_at": self.created_at,
                "updated_at": self.updated_at,
                "original_code_digest": self.original_code_digest,
                "original_code": self.original_code,
                "current_code": self.current_code,
                "code_changed": self.current_code.strip() != self.original_code.strip(),
                "plan": self.plan,
                "trajectory": [asdict(t) for t in self.trajectory],
                "checkpoints": [asdict(c) for c in self.checkpoints],
                "pending_approval": self.pending_approval,
                "approval_status": self.approval_status,
                "approval_history": [dict(r) for r in self.approval_history],
                "execution_mode": self.metadata.get("execution_mode", "deterministic"),
                "max_review_cycles": self.metadata.get("max_review_cycles", 5),
                "metadata": self.metadata,
                "tasks": {key: dict(value) for key, value in self.tasks.items()},
                "findings": {
                    key: [dict(item) for item in value]
                    for key, value in self.findings.items()
                },
                "messages": [dict(item) for item in self.messages],
                "tool_observations": [dict(item) for item in self.tool_observations],
                "modification_history": [
                    dict(item) for item in self.modification_history
                ],
                "final_audit": migrated_audit,
                "audit_status": (
                    migrated_audit.get("status", "not_run")
                    if migrated_audit is not None
                    else "not_run"
                ),
                "audit_passed": (
                    migrated_audit.get("passed", False)
                    if migrated_audit is not None
                    else False
                ),
                "verification_level": (
                    migrated_audit.get("verification_level", "static_only")
                    if migrated_audit is not None
                    else "static_only"
                ),
            }
            if include_owner_token:
                data["owner_token"] = self.owner_token
            return data


class SessionManager:
    """Thread-safe manager for concurrent active agent sessions."""

    def __init__(
        self,
        default_ttl_seconds: int = 1800,
        storage_path: Optional[str | Path] = None,
        max_sessions: int = 500,
        repository: Optional[AbstractSessionRepository] = None,
    ) -> None:
        self._sessions: Dict[str, AgentSession] = {}
        self._lock = threading.Lock()
        self._storage_lock = threading.Lock()
        self.default_ttl = default_ttl_seconds
        self.max_sessions = max_sessions
        self._last_reap = time.time()
        self.storage_path = Path(storage_path).expanduser() if storage_path else None

        if repository is not None:
            self.repository: AbstractSessionRepository = repository
        elif self.storage_path is not None:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            self._initialize_storage()
            self.repository = SQLiteSessionRepository(self.storage_path, max_sessions=max_sessions)
        else:
            self.repository = InMemorySessionRepository(max_sessions=max_sessions)

        if self.storage_path is not None or repository is not None:
            self._load_sessions()

    def _initialize_storage(self) -> None:
        if self.storage_path is None:
            return
        try:
            os.chmod(self.storage_path.parent, 0o700)
        except (OSError, PermissionError):
            pass
        try:
            from ..db_migrations import run_migrations
            run_migrations(self.storage_path)
        except Exception:
            with closing(sqlite3.connect(self.storage_path, timeout=5.0)) as connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS agent_sessions (
                        session_id TEXT PRIMARY KEY,
                        updated_at REAL NOT NULL,
                        payload TEXT NOT NULL
                    )
                    """
                )
        try:
            os.chmod(self.storage_path, 0o600)
        except (OSError, PermissionError):
            pass

    def _persist_session(self, session: AgentSession) -> None:
        if self.repository is not None:
            self.repository.save(session)

    def _deserialize_session(self, data: Dict[str, Any]) -> AgentSession:
        """Deserialize raw dict into an AgentSession with schema_version 1 audit."""
        return AgentSession(
            session_id=data["session_id"],
            original_code=data["original_code"],
            original_code_digest=data["original_code_digest"],
            current_code=data["current_code"],
            task=data["task"],
            status=data.get("status", "idle"),
            cancel_requested=bool(data.get("cancel_requested", False)),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time()),
            plan=data.get("plan", []),
            trajectory=[
                TrajectoryStep(**item) for item in data.get("trajectory", [])
            ],
            checkpoints=[
                Checkpoint(**item) for item in data.get("checkpoints", [])
            ],
            pending_approval=data.get("pending_approval"),
            is_approved=data.get("approval_status") == "approved",
            approval_status=data.get("approval_status", "not_required"),
            approval_history=data.get("approval_history", []),
            owner_token=data.get("owner_token") or secrets.token_urlsafe(32),
            metadata=data.get("metadata", {}),
            tasks=data.get("tasks", {}),
            findings=data.get("findings", {}),
            messages=data.get("messages", []),
            tool_observations=data.get("tool_observations", []),
            modification_history=data.get("modification_history", []),
            final_audit=(
                migrate_legacy_audit(data.get("final_audit"))
                if data.get("final_audit") is not None
                else None
            ),
        )

    def _load_sessions(self) -> None:
        if self.repository is None:
            return
        stored = self.repository.list_all()
        for session in stored:
            session.persist_callback = self._persist_session
            if session.status in {"created", "planning", "running"}:
                session.status = "failed"
                session.metadata["interruption_reason"] = (
                    "The server restarted before this workflow completed."
                )
                session.updated_at = time.time()
                self._persist_session(session)
            with self._lock:
                self._sessions[session.session_id] = session

    def _maybe_cleanup(self) -> None:
        """Opportunistically reap expired sessions if interval elapsed or capacity reached."""
        now = time.time()
        if now - self._last_reap >= 60.0 or len(self._sessions) >= self.max_sessions:
            self._last_reap = now
            self.cleanup_expired()
            with self._lock:
                if len(self._sessions) > self.max_sessions:
                    overflow = len(self._sessions) - self.max_sessions
                    sorted_sessions = sorted(
                        [s for s in self._sessions.values() if s.status not in {"running", "planning", "awaiting_approval"}],
                        key=lambda s: s.updated_at
                    )
                    to_prune = [s.session_id for s in sorted_sessions[:overflow]]
                    for sid in to_prune:
                        self._sessions.pop(sid, None)

    def create_session(self, code: str, task: str = "") -> AgentSession:
        """Create and register a new stateful AgentSession."""
        self._maybe_cleanup()
        session_id = str(uuid.uuid4())
        digest = hashlib.sha256(code.encode("utf-8")).hexdigest()
        session = AgentSession(
            session_id=session_id,
            original_code=code,
            original_code_digest=digest,
            current_code=code,
            task=task or "",
        )
        with self._lock:
            self._sessions[session_id] = session
        session.persist_callback = self._persist_session
        self._persist_session(session)
        return session

    def get_session(self, session_id: str) -> Optional[AgentSession]:
        """Fetch session by ID."""
        self._maybe_cleanup()
        with self._lock:
            return self._sessions.get(session_id)

    def runtime_statistics(self) -> Dict[str, int]:
        """Return aggregate workflow counts without exposing stored source code."""
        self._maybe_cleanup()
        with self._lock:
            sessions = list(self._sessions.values())

        active_executions = 0
        completed_tasks = 0
        failed_tasks = 0
        for session in sessions:
            with session._lock:
                active_executions += int(
                    session.status
                    in {"created", "planning", "running", "awaiting_approval"}
                )
                completed_tasks += sum(
                    task.get("status") == "completed"
                    for task in session.tasks.values()
                )
                failed_tasks += sum(
                    task.get("status") == "failed"
                    for task in session.tasks.values()
                )
        return {
            "active_executions": active_executions,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
        }

    def delete_session(self, session_id: str) -> bool:
        """Remove a session from registry."""
        default_sse_ticket_store.cleanup_for_session(session_id)
        with self._lock:
            removed_mem = self._sessions.pop(session_id, None) is not None
            removed_repo = False
            if self.repository is not None:
                removed_repo = self.repository.delete(session_id)
            return removed_mem or removed_repo

    def cleanup_expired(self, ttl_seconds: Optional[int] = None) -> int:
        """Prune inactive sessions past their expiration TTL."""
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        now = time.time()
        to_delete = []
        with self._lock:
            for sid, sess in self._sessions.items():
                if now - sess.updated_at > ttl:
                    to_delete.append(sid)
            for sid in to_delete:
                del self._sessions[sid]
        if self.repository is not None:
            self.repository.cleanup_expired(ttl)
        return len(to_delete)


# Global default session manager
_configured_storage_path = os.environ.get("AGENTIC_SESSION_DB")
if _configured_storage_path:
    _session_storage_path = Path(_configured_storage_path).expanduser()
    if not _session_storage_path.is_absolute():
        _session_storage_path = Path(__file__).resolve().parents[2] / _session_storage_path
else:
    _session_storage_path = (
        Path(__file__).resolve().parents[2]
        / "instance"
        / "agentic_sessions.sqlite3"
    )
default_session_manager = SessionManager(storage_path=_session_storage_path)


class SSETicketStore:
    """Thread-safe store for short-lived, single-use Server-Sent Events tickets.

    Avoids durable owner token exposure in query parameters, access logs, and proxy traces.
    """

    def __init__(self, default_ttl_seconds: float = 60.0) -> None:
        self._tickets: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self.default_ttl = default_ttl_seconds

    def create_ticket(
        self, session_id: str, owner_token: str, ttl_seconds: Optional[float] = None
    ) -> str:
        """Create a cryptographically random, single-use ticket bound to a session."""
        ticket = f"sse_{secrets.token_urlsafe(32)}"
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        expires_at = time.time() + ttl
        with self._lock:
            self._tickets[ticket] = {
                "session_id": session_id,
                "owner_token": owner_token,
                "expires_at": expires_at,
            }
        return ticket

    def consume_ticket(self, session_id: str, ticket: str) -> bool:
        """Atomically validate and consume (burn) a single-use ticket.

        Returns True iff ticket exists, is bound to session_id, and has not expired.
        Burning upon consumption prevents replay attacks.
        """
        if not ticket or not isinstance(ticket, str):
            return False
        with self._lock:
            record = self._tickets.pop(ticket, None)
        if not record:
            return False
        if time.time() > record["expires_at"]:
            return False
        if record["session_id"] != session_id:
            return False
        return True

    def is_ticket_expired(self, ticket: str) -> bool:
        """Check whether a ticket exists but has already expired."""
        with self._lock:
            record = self._tickets.get(ticket)
            if record:
                return time.time() > record["expires_at"]
        return False

    def cleanup_for_session(self, session_id: str) -> None:
        """Remove all active tickets for a deleted session."""
        with self._lock:
            to_remove = [
                t for t, rec in self._tickets.items() if rec["session_id"] == session_id
            ]
            for t in to_remove:
                self._tickets.pop(t, None)

    def cleanup(self) -> int:
        """Prune all expired tickets from the ticket store."""
        now = time.time()
        with self._lock:
            expired = [
                t for t, rec in self._tickets.items() if now > rec["expires_at"]
            ]
            for t in expired:
                self._tickets.pop(t, None)
            return len(expired)


default_sse_ticket_store = SSETicketStore()

