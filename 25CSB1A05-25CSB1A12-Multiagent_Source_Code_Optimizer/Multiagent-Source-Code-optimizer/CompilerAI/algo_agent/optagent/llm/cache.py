"""SQLite response cache for the Ollama LLM gateway (`runs/.llm_cache.db`)."""
from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any


class LLMCache:
    """Thread-safe SQLite cache keyed by (model, options, system, user, schema_hash)."""

    def __init__(self, db_path: str | Path = "runs/.llm_cache.db", enabled: bool = True) -> None:
        self.db_path = Path(db_path)
        self.enabled = enabled
        self._lock = threading.Lock()
        if self.enabled:
            self._init_db()

    def _init_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS llm_cache (
                    cache_key TEXT PRIMARY KEY,
                    model TEXT NOT NULL,
                    response_json TEXT NOT NULL,
                    prompt_tokens INTEGER DEFAULT 0,
                    completion_tokens INTEGER DEFAULT 0,
                    created_at REAL NOT NULL
                )
                """
            )
            conn.commit()

    @staticmethod
    def make_key(
        model: str,
        options: dict[str, Any],
        system: str,
        user: str,
        schema_hash: str,
    ) -> str:
        payload = json.dumps(
            {
                "model": model,
                "options": options,
                "system": system,
                "user": user,
                "schema_hash": schema_hash,
            },
            sort_keys=True,
            ensure_ascii=False,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def get(self, key: str) -> dict[str, Any] | None:
        if not self.enabled:
            return None
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    row = conn.execute(
                        "SELECT response_json, prompt_tokens, completion_tokens FROM llm_cache WHERE cache_key = ?",
                        (key,),
                    ).fetchone()
                if not row:
                    return None
                return {
                    "response": json.loads(row[0]),
                    "prompt_tokens": int(row[1] or 0),
                    "completion_tokens": int(row[2] or 0),
                }
            except Exception:
                return None

    def put(
        self,
        key: str,
        model: str,
        response: dict[str, Any],
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
    ) -> None:
        if not self.enabled:
            return
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO llm_cache
                        (cache_key, model, response_json, prompt_tokens, completion_tokens, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (key, model, json.dumps(response), prompt_tokens, completion_tokens, time.time()),
                    )
                    conn.commit()
            except Exception:
                pass
