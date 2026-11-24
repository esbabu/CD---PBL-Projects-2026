"""SQLite database migrations and schema versioning for AST Studio.

Provides robust, versioned schema management for the agent session store
and audit log repository, ensuring WAL mode, indices, and ACID consistency.
"""

from __future__ import annotations

import logging
import sqlite3
import time
from contextlib import closing
from pathlib import Path
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)

MIGRATIONS: List[Tuple[int, str, List[str]]] = [
    (
        1,
        "Initial agent sessions schema",
        [
            """
            CREATE TABLE IF NOT EXISTS agent_sessions (
                session_id TEXT PRIMARY KEY,
                updated_at REAL NOT NULL,
                payload TEXT NOT NULL
            );
            """
        ],
    ),
    (
        2,
        "Performance optimization: session indices and WAL pragma",
        [
            """
            CREATE INDEX IF NOT EXISTS idx_agent_sessions_updated_at
            ON agent_sessions (updated_at);
            """
        ],
    ),
    (
        3,
        "Enterprise session audit and security log table",
        [
            """
            CREATE TABLE IF NOT EXISTS session_audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                actor TEXT NOT NULL,
                details TEXT NOT NULL,
                timestamp REAL NOT NULL
            );
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_audit_session_id
            ON session_audit_logs (session_id);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_audit_timestamp
            ON session_audit_logs (timestamp);
            """,
        ],
    ),
]


def _init_migration_table(connection: sqlite3.Connection) -> None:
    """Create the schema_migrations tracking table if absent."""
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            description TEXT NOT NULL,
            applied_at REAL NOT NULL
        );
        """
    )


def get_current_version(db_path: str | Path) -> int:
    """Return the current schema version of the SQLite database."""
    path = Path(db_path)
    if not path.exists():
        return 0
    with closing(sqlite3.connect(path)) as conn:
        _init_migration_table(conn)
        cursor = conn.execute("SELECT MAX(version) FROM schema_migrations")
        row = cursor.fetchone()
        return int(row[0]) if row and row[0] is not None else 0


def run_migrations(db_path: str | Path) -> Dict[str, Any]:
    """Execute all unapplied migrations in chronological order.

    Returns summary of executed migrations and resulting schema version.
    """
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    applied_now: List[int] = []

    with closing(sqlite3.connect(path)) as conn:
        # Enable WAL mode and busy timeout for concurrent safety
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA busy_timeout = 5000;")
        conn.execute("PRAGMA foreign_keys = ON;")

        _init_migration_table(conn)
        cursor = conn.execute("SELECT version FROM schema_migrations")
        applied_versions = {row[0] for row in cursor.fetchall()}

        for version, description, statements in MIGRATIONS:
            if version not in applied_versions:
                logger.info("Applying database migration %d: %s", version, description)
                with conn:
                    for stmt in statements:
                        conn.execute(stmt)
                    conn.execute(
                        """
                        INSERT INTO schema_migrations (version, description, applied_at)
                        VALUES (?, ?, ?)
                        """,
                        (version, description, time.time()),
                    )
                applied_now.append(version)

        cursor = conn.execute("SELECT MAX(version) FROM schema_migrations")
        current_v = cursor.fetchone()[0] or 0

    return {
        "status": "success",
        "current_version": current_v,
        "migrations_applied": applied_now,
        "total_migrations": len(MIGRATIONS),
    }


def record_audit_event(
    db_path: str | Path,
    session_id: str,
    event_type: str,
    actor: str,
    details: str,
) -> None:
    """Record an audit trail event into the session_audit_logs table."""
    path = Path(db_path)
    if not path.exists():
        return
    try:
        with closing(sqlite3.connect(path)) as conn:
            conn.execute("PRAGMA busy_timeout = 5000;")
            with conn:
                conn.execute(
                    """
                    INSERT INTO session_audit_logs (session_id, event_type, actor, details, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (session_id, event_type, actor, details, time.time()),
                )
    except Exception as exc:
        logger.warning("Failed to record audit log: %s", exc)
