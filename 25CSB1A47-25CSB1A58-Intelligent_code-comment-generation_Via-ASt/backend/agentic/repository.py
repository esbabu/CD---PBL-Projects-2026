"""Persistence repository interface and schema migrations for Agentic AI sessions."""

from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import closing
import json
import logging
from pathlib import Path
import sqlite3
import threading
import time
from typing import Any, Dict, List, Optional

from backend.agentic.verification_contract import migrate_legacy_audit

logger = logging.getLogger(__name__)

CURRENT_SCHEMA_VERSION = 2


class AbstractSessionRepository(ABC):
    """Abstract interface defining persistence operations for agent workflow sessions."""

    @abstractmethod
    def save(self, session: Any) -> None:
        """Persist or update an AgentSession."""

    @abstractmethod
    def get(self, session_id: str) -> Optional[Any]:
        """Retrieve an AgentSession by its identifier."""

    @abstractmethod
    def delete(self, session_id: str) -> bool:
        """Remove a session from storage."""

    @abstractmethod
    def list_all(self) -> List[Any]:
        """Return all stored sessions."""

    @abstractmethod
    def cleanup_expired(self, ttl_seconds: float) -> int:
        """Prune inactive sessions past their expiration TTL."""

    @abstractmethod
    def runtime_statistics(self) -> Dict[str, int]:
        """Return aggregate statistics across sessions without exposing source code."""

    @abstractmethod
    def migrate(self) -> None:
        """Apply schema migrations up to CURRENT_SCHEMA_VERSION."""


class InMemorySessionRepository(AbstractSessionRepository):
    """Thread-safe in-memory session repository for testing and diskless execution."""

    def __init__(self, max_sessions: int = 100) -> None:
        self._sessions: Dict[str, Any] = {}
        self._lock = threading.RLock()
        self.max_sessions = max_sessions

    def save(self, session: Any) -> None:
        with self._lock:
            self._sessions[session.session_id] = session

    def get(self, session_id: str) -> Optional[Any]:
        with self._lock:
            return self._sessions.get(session_id)

    def delete(self, session_id: str) -> bool:
        with self._lock:
            return bool(self._sessions.pop(session_id, None))

    def list_all(self) -> List[Any]:
        with self._lock:
            return list(self._sessions.values())

    def cleanup_expired(self, ttl_seconds: float) -> int:
        now = time.time()
        to_delete = []
        with self._lock:
            for sid, sess in self._sessions.items():
                if now - sess.updated_at > ttl_seconds:
                    to_delete.append(sid)
            for sid in to_delete:
                del self._sessions[sid]
        return len(to_delete)

    def runtime_statistics(self) -> Dict[str, int]:
        with self._lock:
            sessions = list(self._sessions.values())
        active = sum(1 for s in sessions if getattr(s, "status", "") in {"created", "planning", "running", "awaiting_approval"})
        completed = sum(sum(1 for t in getattr(s, "tasks", {}).values() if t.get("status") == "completed") for s in sessions)
        failed = sum(sum(1 for t in getattr(s, "tasks", {}).values() if t.get("status") == "failed") for s in sessions)
        return {
            "active_executions": active,
            "completed_tasks": completed,
            "failed_tasks": failed,
        }

    def migrate(self) -> None:
        pass


class SQLiteSessionRepository(AbstractSessionRepository):
    """SQLite implementation of AbstractSessionRepository with schema migrations.

    Ensures durable persistence across server restarts, atomic updates, and
    schema versioning.
    """

    def __init__(self, storage_path: Path, max_sessions: int = 100) -> None:
        self.storage_path = Path(storage_path)
        self.max_sessions = max_sessions
        self._lock = threading.RLock()
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.migrate()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.storage_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn

    def migrate(self) -> None:
        """Run database migrations via centralized db_migrations runner."""
        try:
            from backend.db_migrations import run_migrations
            run_migrations(self.storage_path)
        except Exception as exc:
            logger.warning("Could not run centralized migrations: %s. Falling back to local DDL.", exc)
            with self._lock, closing(self._get_connection()) as conn:
                with conn:
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS agent_sessions (
                            session_id TEXT PRIMARY KEY,
                            updated_at REAL NOT NULL,
                            payload TEXT NOT NULL
                        )
                    """)
                    conn.execute("""
                        CREATE INDEX IF NOT EXISTS idx_agent_sessions_updated_at
                        ON agent_sessions (updated_at)
                    """)

    def save(self, session: Any) -> None:
        """Persist or update an AgentSession atomically."""
        from backend.agentic.session import AgentSession

        if not isinstance(session, AgentSession):
            raise TypeError("Session must be an AgentSession instance.")

        payload = json.dumps(session.to_dict(include_owner_token=True), ensure_ascii=True, default=str)

        with self._lock, closing(self._get_connection()) as conn:
            with conn:
                conn.execute(
                    """
                    INSERT INTO agent_sessions (session_id, updated_at, payload)
                    VALUES (?, ?, ?)
                    ON CONFLICT(session_id) DO UPDATE SET
                        updated_at = excluded.updated_at,
                        payload = excluded.payload
                    """,
                    (session.session_id, session.updated_at, payload),
                )

    def get(self, session_id: str) -> Optional[Any]:
        """Fetch session by ID and deserialize safely."""
        with self._lock, closing(self._get_connection()) as conn:
            row = conn.execute(
                "SELECT payload FROM agent_sessions WHERE session_id = ?",
                (session_id,),
            ).fetchone()
            if not row:
                return None
            data = json.loads(row["payload"])
            return self._deserialize_session(data)

    def delete(self, session_id: str) -> bool:
        """Delete session by ID."""
        with self._lock, closing(self._get_connection()) as conn:
            with conn:
                cur = conn.execute(
                    "DELETE FROM agent_sessions WHERE session_id = ?",
                    (session_id,),
                )
                return cur.rowcount > 0

    def list_all(self) -> List[Any]:
        """Return all deserialized sessions."""
        with self._lock, closing(self._get_connection()) as conn:
            rows = conn.execute("SELECT payload FROM agent_sessions ORDER BY updated_at DESC").fetchall()
            return [self._deserialize_session(json.loads(r["payload"])) for r in rows]

    def cleanup_expired(self, ttl_seconds: float) -> int:
        """Prune sessions older than TTL."""
        cutoff = time.time() - ttl_seconds
        with self._lock, closing(self._get_connection()) as conn:
            with conn:
                cur = conn.execute("DELETE FROM agent_sessions WHERE updated_at < ?", (cutoff,))
                return cur.rowcount

    def runtime_statistics(self) -> Dict[str, int]:
        """Aggregate stats across all sessions efficiently."""
        sessions = self.list_all()
        active = 0
        completed = 0
        failed = 0
        for s in sessions:
            if getattr(s, "status", "") in {"created", "planning", "running", "awaiting_approval"}:
                active += 1
            for task in getattr(s, "tasks", {}).values():
                if task.get("status") == "completed":
                    completed += 1
                elif task.get("status") == "failed":
                    failed += 1
        return {
            "active_executions": active,
            "completed_tasks": completed,
            "failed_tasks": failed,
        }

    def _deserialize_session(self, data: Dict[str, Any]) -> Any:
        from backend.agentic.session import AgentSession, Checkpoint, TrajectoryStep
        import secrets

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
