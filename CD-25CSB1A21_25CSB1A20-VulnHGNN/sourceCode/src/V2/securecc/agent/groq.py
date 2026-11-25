from __future__ import annotations

import json
import re
from typing import Any

from .prompts import SYSTEM_PROMPT


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            return json.loads(match.group(0))
        raise


def plan_next_step(
    *,
    user_message: str,
    source_path: str,
    history: list[dict[str, Any]],
    model_name: str | None = None,
) -> dict[str, Any]:
    from src.V2.securecc.groq_config import groq_api_key
    from src.V2.securecc.llm_completion import complete_chat, ollama_available

    if not groq_api_key() and not ollama_available():
        raise RuntimeError(
            "No LLM backend. Set GROQ_API_KEY or start Ollama (see README)."
        )

    context = {
        "source_file": source_path,
        "user_message": user_message,
        "prior_steps": history[-6:],
    }

    prompt = (
        "Given the context JSON below, choose the next action.\n"
        f"{json.dumps(context, indent=2)}"
    )

    raw, _backend = complete_chat(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        json_mode=True,
        temperature=0.2,
        model=model_name,
    )
    return _extract_json(raw)
