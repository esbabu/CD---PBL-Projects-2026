"""SQLite-backed memory store for verified positive and negative algorithm rewrites."""
from __future__ import annotations

import json
import re
import sqlite3
import time
from pathlib import Path

from ..config import Settings
from .schemas import MemoryEntry


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"\w+", text.lower()))


class MemoryStore:
    """Persistent storage and retrieval of verified algorithm rewrites."""

    def __init__(self, db_path: str | Path | None = None):
        if db_path is None:
            db_path = Settings().memory_db_path
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS rewrites (
                    id TEXT PRIMARY KEY,
                    pattern_key TEXT,
                    conditions TEXT,
                    original_snippet TEXT,
                    rewrite_snippet TEXT,
                    transform_ids TEXT,
                    speedup REAL,
                    mem_ratio REAL,
                    evidence_tier TEXT,
                    is_positive INTEGER,
                    failure_reason TEXT,
                    timestamp TEXT
                );
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_pattern_key ON rewrites(pattern_key);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_is_positive ON rewrites(is_positive);")
            conn.commit()

    def store(self, entry: MemoryEntry) -> None:
        """Store or update a memory entry."""
        ts = entry.timestamp or time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        with self._get_conn() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO rewrites (
                    id, pattern_key, conditions, original_snippet, rewrite_snippet,
                    transform_ids, speedup, mem_ratio, evidence_tier, is_positive,
                    failure_reason, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    entry.id,
                    entry.pattern_key,
                    json.dumps(entry.conditions),
                    entry.original_snippet,
                    entry.rewrite_snippet,
                    json.dumps(entry.transform_ids),
                    entry.speedup,
                    entry.mem_ratio,
                    entry.evidence_tier,
                    1 if entry.is_positive else 0,
                    entry.failure_reason,
                    ts,
                ),
            )
            conn.commit()

    def store_positive(self, entry: MemoryEntry) -> None:
        entry.is_positive = True
        self.store(entry)

    def store_negative(self, entry: MemoryEntry) -> None:
        entry.is_positive = False
        self.store(entry)

    def retrieve(self, pattern_key: str | None = None, is_positive: bool = True,
                 top_k: int = 5) -> list[MemoryEntry]:
        """Retrieve stored rewrites matching a pattern key."""
        with self._get_conn() as conn:
            if pattern_key:
                cur = conn.execute(
                    """
                    SELECT * FROM rewrites
                    WHERE pattern_key = ? AND is_positive = ?
                    ORDER BY speedup DESC
                    LIMIT ?;
                    """,
                    (pattern_key, 1 if is_positive else 0, top_k),
                )
            else:
                cur = conn.execute(
                    """
                    SELECT * FROM rewrites
                    WHERE is_positive = ?
                    ORDER BY speedup DESC
                    LIMIT ?;
                    """,
                    (1 if is_positive else 0, top_k),
                )
            rows = cur.fetchall()

        return [self._row_to_entry(r) for r in rows]

    def retrieve_similar(self, source: str, is_positive: bool = True,
                         top_k: int = 5) -> list[MemoryEntry]:
        """Rank stored rewrites by token similarity to the input source code."""
        all_entries = self.retrieve(is_positive=is_positive, top_k=100)
        if not all_entries:
            return []

        src_tokens = _tokenize(source)
        scored: list[tuple[float, MemoryEntry]] = []

        for e in all_entries:
            orig_tokens = _tokenize(e.original_snippet)
            if not orig_tokens:
                continue
            # Jaccard overlap
            overlap = len(src_tokens & orig_tokens)
            union = len(src_tokens | orig_tokens)
            sim = overlap / union if union else 0.0
            scored.append((sim, e))

        scored.sort(key=lambda t: t[0], reverse=True)
        return [e for sim, e in scored[:top_k] if sim > 0.1]

    def list_all(self) -> list[MemoryEntry]:
        """List all entries in the store."""
        with self._get_conn() as conn:
            cur = conn.execute("SELECT * FROM rewrites ORDER BY timestamp DESC;")
            rows = cur.fetchall()
        return [self._row_to_entry(r) for r in rows]

    def _row_to_entry(self, r: sqlite3.Row) -> MemoryEntry:
        return MemoryEntry(
            id=r["id"],
            pattern_key=r["pattern_key"],
            conditions=json.loads(r["conditions"]),
            original_snippet=r["original_snippet"],
            rewrite_snippet=r["rewrite_snippet"],
            transform_ids=json.loads(r["transform_ids"]),
            speedup=r["speedup"],
            mem_ratio=r["mem_ratio"],
            evidence_tier=r["evidence_tier"],
            is_positive=bool(r["is_positive"]),
            failure_reason=r["failure_reason"] or "",
            timestamp=r["timestamp"] or "",
        )

