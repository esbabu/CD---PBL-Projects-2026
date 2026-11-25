"""Groq advisory review of source text (not verified by SecureCC engine)."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def ai_source_review(source: Path, *, language: str = "c") -> dict[str, Any]:
    from src.V2.securecc.groq_config import groq_api_key
    from src.V2.securecc.llm_completion import complete_chat, ollama_available

    text = source.read_text(encoding="utf-8", errors="replace")
    if not groq_api_key() and not ollama_available():
        return {
            "tool": "ai_source_review",
            "status": "SKIPPED",
            "message": "No LLM backend (Groq or Ollama)",
            "issues": [],
            "issue_count": 0,
        }

    system = (
        'Return ONLY JSON: {"issues": ['
        '{"severity":"low|medium|high","cwe_id":"CWE-XXX or null","line":number or null,'
        '"title":"short","message":"why it matters"}]}. '
        f"Language: {language}. Review for security bugs, undefined behavior, and common CWE patterns. "
        "Do not claim code is verified or safe. Max 8 issues. No markdown."
    )
    user = json.dumps(
        {
            "filename": source.name,
            "source": text[:16000],
        },
        indent=0,
    )

    try:
        raw, backend = complete_chat(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            json_mode=True,
            temperature=0.2,
        )
    except Exception as exc:
        return {
            "tool": "ai_source_review",
            "status": "ERROR",
            "message": str(exc)[:300],
            "issues": [],
            "issue_count": 0,
        }
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", raw)
        if not match:
            return {
                "tool": "ai_source_review",
                "status": "ERROR",
                "message": "AI returned non-JSON",
                "issues": [],
                "issue_count": 0,
            }
        data = json.loads(match.group(0))

    issues = data.get("issues") or []
    if not isinstance(issues, list):
        issues = []
    cleaned: list[dict[str, Any]] = []
    for item in issues[:8]:
        if not isinstance(item, dict):
            continue
        cleaned.append(
            {
                "severity": str(item.get("severity") or "medium"),
                "cwe_id": item.get("cwe_id"),
                "line": item.get("line"),
                "title": str(item.get("title") or "Issue")[:120],
                "message": str(item.get("message") or "")[:500],
            }
        )

    return {
        "tool": "ai_source_review",
        "status": "OK",
        "message": f"{len(cleaned)} advisory issue(s)",
        "issues": cleaned,
        "issue_count": len(cleaned),
    }
