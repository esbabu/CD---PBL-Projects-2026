"""Agent Runtime managing state machine lifecycles and supervisor execution."""

from __future__ import annotations

import hashlib
import logging
import time
import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any, Callable, Dict, List, Optional

from backend.agentic.intent import validate_dag
from backend.agentic.provider_adapter import (
    ProviderAdapter,
    default_provider_adapter,
)
from backend.agentic.session import AgentSession, SessionManager, default_session_manager
from backend.agentic.supervisor import SupervisorAgent
from backend.agentic.tools import create_standard_tool_registry
from backend.agentic.tools.registry import ToolRegistry
from backend.attack_guard import detect_attack
from backend import model_provider
from backend.validator import validate_code

logger = logging.getLogger(__name__)


class _SessionModelClient:
    """Count provider calls per session while preserving the chat-completions API."""

    def __init__(self, client: Any, session: AgentSession) -> None:
        self._client = client
        self._session = session
        self.chat = SimpleNamespace(
            completions=SimpleNamespace(create=self._create_completion)
        )

    def _create_completion(self, **kwargs: Any) -> Any:
        self._session.record_model_call()
        return self._client.chat.completions.create(**kwargs)


class AgentRuntime:
    """Core runtime engine for stateful agentic workflows."""

    def __init__(
        self,
        tools: Optional[ToolRegistry] = None,
        session_manager: Optional[SessionManager] = None,
        model_client: Any = None,
        event_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None,
        provider_adapter: Optional[ProviderAdapter] = None,
    ) -> None:
        self.tools = tools or create_standard_tool_registry()
        self.session_manager = session_manager or default_session_manager
        self.provider_adapter = provider_adapter or default_provider_adapter
        self.model_client = self._adapt_model_client(model_client)
        self.event_callback = event_callback or (lambda event, payload: None)
        self.supervisor = SupervisorAgent(
            tools=self.tools,
            model_client=self.model_client,
            event_callback=self.event_callback,
        )

    def _adapt_model_client(self, model_client: Any) -> Any:
        if model_client is None or getattr(
            model_client, "_provider_adapter_wrapped", False
        ) is True:
            return model_client
        return self.provider_adapter.as_chat_client(model_client)

    def set_model_client(self, model_client: Any, model_name: Optional[str] = None) -> None:
        """Refresh model configuration for the runtime and all existing agents."""
        adapted_client = self._adapt_model_client(model_client)
        self.model_client = adapted_client
        self.supervisor.model_client = adapted_client
        self.supervisor.model_name = model_name or model_provider.MODEL_NAME
        for agent in self.supervisor.swarm.values():
            agent.model_client = adapted_client
            agent.model_name = self.supervisor.model_name

    def start_session(
        self,
        source_code: str,
        task: str = "",
        session_id: Optional[str] = None,
        auto_approve: bool = False,
        max_review_cycles: int = 5,
        execution_mode: Optional[str] = None,
        intent: Optional[str] = None,
        custom_plan: Optional[List[Dict[str, Any]]] = None,
        workspace_id: Optional[str] = None,
        active_file: Optional[str] = None,
        project_context: Optional[Dict[str, str]] = None,
        require_model: bool = False,
    ) -> AgentSession:
        """Initialize a new session with preflight syntax and attack checks."""
        if auto_approve:
            raise ValueError(
                "Automatic approval is disabled; source changes require explicit operator approval."
            )

        # 1. Syntax Validation
        valid = validate_code(source_code)
        if valid is not True:
            raise ValueError(f"Initial source code fails Python syntax validation: {valid}")

        # 2. Attack Guardrail Pre-scan:
        # Scan prompt task for adversarial prompt injection / policy bypass
        if task:
            prompt_detection = detect_attack(task, content_type="prompt")
            if prompt_detection["detected"]:
                raise PermissionError(
                    f"Agent session blocked by security layer: {', '.join(prompt_detection.get('categories', []))}"
                )

        # Scan source code for embedded prompt injection or credential/data exfiltration
        source_prompt_scan = detect_attack(source_code, content_type="prompt")
        source_code_scan = detect_attack(source_code, content_type="code")
        adversarial_categories = {
            "policy_bypass",
            "safety_control_bypass",
            "credential_exfiltration",
            "private_data_exfiltration",
            "jailbreak_attempt",
            "sensitive_data_transfer",
        }
        detected_categories = [
            cat
            for cat in (source_prompt_scan.get("categories", []) + source_code_scan.get("categories", []))
            if cat in adversarial_categories
        ]
        if detected_categories:
            unique_cats = list(dict.fromkeys(detected_categories))
            raise PermissionError(
                f"Agent session blocked by security layer: {', '.join(unique_cats)}"
            )

        resolved_mode = str(execution_mode).strip().lower() if execution_mode else None
        if resolved_mode not in {"model", "deterministic"}:
            resolved_mode = "model" if getattr(self.model_client, "chat", None) else "deterministic"
        if require_model and (
            resolved_mode != "model"
            or not getattr(self.model_client, "chat", None)
        ):
            raise ValueError("A required AI model client is not available.")

        # 3. Create or reuse Session
        if session_id:
            existing = self.session_manager.get_session(session_id)
            if existing:
                existing.event_callback = self.event_callback
                if resolved_mode == "deterministic":
                    existing.model_client = None
                    existing.metadata["execution_mode"] = "deterministic"
                else:
                    existing.model_client = (
                        _SessionModelClient(self.model_client, existing)
                        if self.model_client is not None
                        else None
                    )
                    existing.metadata["execution_mode"] = (
                        "model" if getattr(existing.model_client, "chat", None) else "deterministic"
                    )
                existing.metadata["max_review_cycles"] = int(max_review_cycles)
                existing.metadata["require_model"] = bool(
                    require_model and resolved_mode == "model"
                )
                existing.task = task or existing.task
                existing.update_code(source_code)
                existing.project_context = dict(project_context or {})
                if workspace_id and active_file:
                    existing.metadata["project_workspace_id"] = workspace_id
                    existing.metadata["active_file"] = active_file
                return existing

        session = self.session_manager.create_session(code=source_code, task=task)
        session.event_callback = self.event_callback
        if resolved_mode == "deterministic":
            session.model_client = None
            session.metadata["execution_mode"] = "deterministic"
        else:
            session.model_client = (
                _SessionModelClient(self.model_client, session)
                if self.model_client is not None
                else None
            )
            session.metadata["execution_mode"] = (
                "model" if getattr(session.model_client, "chat", None) else "deterministic"
            )

        session.is_approved = False
        session.approval_status = "not_required"
        session.metadata["max_review_cycles"] = int(max_review_cycles)
        session.metadata["require_model"] = bool(
            require_model and resolved_mode == "model"
        )
        session.project_context = dict(project_context or {})
        if workspace_id and active_file:
            session.metadata["project_workspace_id"] = workspace_id
            session.metadata["active_file"] = active_file
        if intent:
            session.metadata["intent"] = str(intent).strip().lower()
        if custom_plan:
            validate_dag(custom_plan)
            session.plan = custom_plan
        session.emit_event(
            "session_created",
            agent="SupervisorAgent",
            status="created",
            task=session.task,
            execution_mode=session.metadata["execution_mode"],
            max_review_cycles=session.metadata["max_review_cycles"],
        )
        return session

    def execute_session(self, session_id: str) -> Dict[str, Any]:
        """Run the supervisor workflow for a given session."""
        session = self.session_manager.get_session(session_id)
        if not session:
            raise KeyError(f"Session '{session_id}' not found.")

        try:
            return self.supervisor.run(session)
        except Exception as exc:
            logger.exception("Agent runtime execution failed for session %s", session_id)
            session.set_status("failed")
            from backend.agentic.verification_contract import create_failed_audit
            failed_audit = create_failed_audit(str(exc), session=session)
            session.final_audit = failed_audit
            error_payload = {
                "status": "failed",
                "session_id": session_id,
                "error": str(exc),
                "error_type": type(exc).__name__,
                "final_audit": failed_audit,
                "audit_passed": False,
                "audit_status": "failed",
                "verification_level": "static_only",
            }
            session.emit_event(
                "session_failed",
                agent="SupervisorAgent",
                status="failed",
                error=str(exc),
                error_type=type(exc).__name__,
                final_audit=failed_audit,
                audit_passed=False,
                audit_status="failed",
            )
            return error_payload

    def cancel_session(self, session_id: str) -> Dict[str, Any]:
        """Request cooperative cancellation between active task/tool turns."""
        session = self.session_manager.get_session(session_id)
        if not session:
            raise KeyError(f"Session '{session_id}' not found.")
        with session._lock:
            if session.status in {"completed", "failed", "cancelled"}:
                return {
                    "status": "ignored",
                    "session_id": session_id,
                    "error": f"Session is already {session.status}.",
                }
            session.cancel_requested = True
            session.updated_at = time.time()
            awaiting_approval = session.status == "awaiting_approval"
            if awaiting_approval:
                session.status = "cancelled"
        if awaiting_approval:
            from backend.agentic.verification_contract import create_not_run_audit
            cancelled_audit = create_not_run_audit("Session cancelled by operator", session=session)
            session.final_audit = cancelled_audit
            session.emit_event(
                "workflow_cancelled",
                agent="SupervisorAgent",
                status="cancelled",
                original_code=session.original_code,
                final_code=session.current_code,
                code_changed=session.current_code.strip()
                != session.original_code.strip(),
                plan=session.plan,
                tasks=session.tasks,
                model_call_count=int(session.metadata.get("model_call_count", 0)),
                final_audit=cancelled_audit,
                audit_passed=False,
                audit_status="not_run",
            )
            return {
                "status": "cancelled",
                "session_id": session_id,
                "final_audit": cancelled_audit,
                "audit_status": "not_run",
            }
        session.emit_event(
            "cancellation_requested",
            agent="HumanSupervisor",
            status="cancellation_requested",
        )
        return {"status": "cancellation_requested", "session_id": session_id}

    def handle_user_action(
        self,
        session_id: str,
        action: str,
        feedback: Optional[str] = None,
        approver: Optional[str] = None,
        candidate_digest: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Process Human-in-the-Loop decision on pending approval with tamper-evident audit binding."""
        session = self.session_manager.get_session(session_id)
        if not session:
            raise KeyError(f"Session '{session_id}' not found.")

        if session.pending_approval is None:
            return {
                "status": "ignored",
                "session_id": session_id,
                "error": "No action is currently awaiting approval.",
            }

        pending = dict(session.pending_approval)
        pending_digest = pending.get("candidate_digest")
        is_candidate_approval = pending.get("tool") == "apply_candidate"

        # Tamper-evident check: if candidate_digest was provided, verify it matches pending digest
        if candidate_digest and pending_digest and candidate_digest != pending_digest:
            return {
                "status": "error",
                "session_id": session_id,
                "error": "Candidate digest mismatch: the code being approved does not match the pending proposal.",
            }
        if is_candidate_approval and action.lower() == "approve":
            candidate = pending.get("candidate_code")
            before_digest = pending.get("before_digest")
            actual_before_digest = hashlib.sha256(
                session.current_code.encode("utf-8")
            ).hexdigest()
            actual_candidate_digest = (
                hashlib.sha256(candidate.encode("utf-8")).hexdigest()
                if isinstance(candidate, str)
                else None
            )
            if (
                not candidate_digest
                or not isinstance(candidate, str)
                or not before_digest
                or actual_before_digest != before_digest
                or actual_candidate_digest != pending_digest
            ):
                return {
                    "status": "error",
                    "session_id": session_id,
                    "error": "The staged candidate changed or its review digest is missing; no source was modified.",
                }

        effective_digest = (
            candidate_digest
            or pending_digest
            or hashlib.sha256(session.current_code.encode("utf-8")).hexdigest()
        )
        approver_identity = approver or "operator"
        timestamp = datetime.now(timezone.utc).isoformat()

        approval_record = {
            "id": uuid.uuid4().hex[:12],
            "action": action.lower(),
            "approver": approver_identity,
            "timestamp": timestamp,
            "task_id": pending.get("task_id"),
            "tool": pending.get("tool"),
            "candidate_digest": effective_digest,
            "feedback": feedback,
            "permissions_granted": (
                ["generate_candidate", "apply_candidate"]
                if action.lower() == "approve"
                else []
            ),
        }
        session.approval_history.append(approval_record)

        if action.lower() == "approve":
            session.is_approved = not is_candidate_approval
            session.approval_status = "approved"
            task_id = pending.get("task_id")
            if is_candidate_approval:
                session.update_code(pending["candidate_code"])
                session.record_modification(
                    {
                        "agent": pending.get("agent"),
                        "task_id": task_id,
                        "status": "accepted",
                        "changed": True,
                        "checkpoint_id": pending.get("checkpoint_id"),
                        "before_digest": pending.get("before_digest"),
                        "candidate_digest": pending_digest,
                        "after_digest": pending_digest,
                        "candidate_validation": pending.get("candidate_validation", {}),
                    }
                )
                if task_id and task_id in session.tasks:
                    session.update_task(
                        task_id,
                        status="completed",
                        candidate_status="accepted",
                        candidate_digest=pending_digest,
                        code_modified=True,
                    )
                outcomes = session.metadata.get("candidate_outcomes", [])
                if isinstance(outcomes, list):
                    for outcome in reversed(outcomes):
                        if isinstance(outcome, dict) and outcome.get("candidate_digest") == pending_digest:
                            outcome.update(
                                status="accepted",
                                changed=True,
                                after_digest=pending_digest,
                            )
                            break
                session.is_approved = False
                session.pending_approval = None
            elif task_id and task_id in session.tasks:
                session.update_task(task_id, status="pending")
                session.pending_approval = None
            else:
                session.pending_approval = None

            proposal_id = pending.get("proposal_id") or (
                pending.get("arguments", {}).get("proposal_id")
                if isinstance(pending.get("arguments"), dict)
                else None
            )
            workspace_id = session.metadata.get("project_workspace_id")
            if proposal_id and workspace_id:
                from backend.project.routes import _get_workspace
                from backend.project.change_management import ProjectChangeManager

                try:
                    ws = _get_workspace(workspace_id)
                    cm = ProjectChangeManager(ws)
                    commit_info = cm.approve_and_commit_changes(proposal_id)
                    approval_record["commit_result"] = commit_info
                    session.record_modification({
                        "agent": pending.get("agent"),
                        "task_id": task_id,
                        "status": "accepted",
                        "changed": True,
                        "proposal_id": proposal_id,
                        "commit_result": commit_info,
                    })
                except Exception as exc:
                    logger.warning("Could not commit workspace proposal %s: %s", proposal_id, exc)
            session.record_step(
                agent="HumanSupervisor",
                thought="User approved pending action.",
                action="human_approval",
                observation={
                    "decision": "approved",
                    "feedback": feedback,
                    "approval_record": approval_record,
                },
            )
            session.emit_event(
                "action_approved",
                agent="HumanSupervisor",
                status="approved",
                feedback=feedback,
                approval_record=approval_record,
            )
            if session.plan:
                session.set_status("running")
            return {
                "status": "resumed",
                "session_id": session_id,
                "decision": "approved",
                "approval_record": approval_record,
            }

        if action.lower() == "reject":
            session.is_approved = False
            session.approval_status = "rejected"
            task_id = pending.get("task_id")
            if is_candidate_approval:
                if task_id and task_id in session.tasks:
                    session.update_task(
                        task_id,
                        status="completed",
                        candidate_status="rejected",
                        candidate_rejection_feedback=feedback,
                        code_modified=False,
                    )
                outcomes = session.metadata.get("candidate_outcomes", [])
                if isinstance(outcomes, list):
                    for outcome in reversed(outcomes):
                        if isinstance(outcome, dict) and outcome.get("candidate_digest") == pending_digest:
                            outcome.update(status="rejected", changed=False)
                            break
            elif task_id and task_id in session.tasks:
                session.update_task(
                    task_id,
                    status="failed",
                    error="Pending action rejected by user.",
                )
            elif session.checkpoints:
                latest_chk = session.checkpoints[-1]
                session.rollback_to(latest_chk.id)

            proposal_id = pending.get("proposal_id") or (
                pending.get("arguments", {}).get("proposal_id")
                if isinstance(pending.get("arguments"), dict)
                else None
            )
            workspace_id = session.metadata.get("project_workspace_id")
            if proposal_id and workspace_id:
                from backend.project.routes import _get_workspace
                from backend.project.change_management import ProjectChangeManager

                try:
                    ws = _get_workspace(workspace_id)
                    cm = ProjectChangeManager(ws)
                    reject_info = cm.reject_proposal(proposal_id)
                    approval_record["reject_result"] = reject_info
                except Exception as exc:
                    logger.warning("Could not reject workspace proposal %s: %s", proposal_id, exc)
            session.pending_approval = None
            session.record_step(
                agent="HumanSupervisor",
                thought="User rejected pending action; restored previous checkpoint.",
                action="human_rejection",
                observation={
                    "decision": "rejected",
                    "feedback": feedback,
                    "approval_record": approval_record,
                },
            )
            session.emit_event(
                "action_rejected",
                agent="HumanSupervisor",
                status="rejected",
                feedback=feedback,
                approval_record=approval_record,
            )
            if session.plan:
                session.set_status("running")
            return {
                "status": "rolled_back",
                "session_id": session_id,
                "decision": "rejected",
                "approval_record": approval_record,
            }

        return {"status": "ignored", "session_id": session_id, "error": f"Unknown action '{action}'"}
