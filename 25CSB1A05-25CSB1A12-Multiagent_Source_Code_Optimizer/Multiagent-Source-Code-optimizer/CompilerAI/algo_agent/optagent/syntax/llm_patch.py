"""LLM-assisted syntax patcher with windowed prompts and strict guardrails."""
from __future__ import annotations

import json
from typing import Any, Callable, Dict, List, Optional, Tuple

from .guards import budget_guard, progress_guard, token_preservation_guard
from .report import SyntaxEdit, SyntaxRound


class LLMSyntaxPatcher:
    """Attempts minimal guarded syntax patches via LLM for errors resisting heuristic fixers."""

    def __init__(self, gateway_or_callable: Any = None):
        self.gateway = gateway_or_callable

    def _call_llm(self, prompt: str) -> Optional[dict]:
        """Call LLM gateway or injected fake/mock."""
        if not self.gateway:
            return None

        # Check if gateway has generate() or similar method
        if hasattr(self.gateway, "generate_json"):
            return self.gateway.generate_json(prompt, role="syntax_fixer")
        elif hasattr(self.gateway, "call"):
            res = self.gateway.call(prompt, role="syntax_fixer", format="json")
            if isinstance(res, dict):
                return res
            elif isinstance(res, str):
                try:
                    return json.loads(res)
                except Exception:
                    return None
        elif callable(self.gateway):
            res = self.gateway(prompt)
            if isinstance(res, str):
                try:
                    return json.loads(res)
                except Exception:
                    return None
            return res
        return None

    def attempt_patch(
        self,
        source: str,
        error: dict[str, Any],
        language: str = "python",
        total_tokens_changed: int = 0,
    ) -> Tuple[Optional[str], Optional[SyntaxRound]]:
        """
        Request and validate a minimal windowed LLM syntax patch.
        Returns (repaired_source, round_info) on success, or (None, round_info) on rejection.
        """
        err_line = error.get("line", 1)
        err_col = error.get("column", 1)
        err_msg = error.get("message", "Syntax error")

        lines = source.splitlines()
        start_line = max(1, err_line - 15)
        end_line = min(len(lines), err_line + 15)

        window_numbered = [f"{i}: {lines[i - 1]}" for i in range(start_line, end_line + 1)]
        window_text = "\n".join(window_numbered)

        prompt = (
            f"You are a specialized syntax repair tool for {language}.\n"
            f"Parser error: {err_msg} at line {err_line}, column {err_col}.\n\n"
            f"CODE WINDOW (lines {start_line} to {end_line}):\n"
            f"{window_text}\n\n"
            f"INSTRUCTION (MUST FOLLOW VERBATIM):\n"
            f"Fix SYNTAX errors only. Do not rename anything, do not reformat, do not refactor, "
            f"do not change logic, do not add or remove statements except what is strictly required "
            f"for the file to parse. Return a minimal patch.\n\n"
            f"Respond ONLY with a JSON object in this schema:\n"
            f"{{\n"
            f'  "edits": [\n'
            f'    {{"line": {err_line}, "old": "<exact line text before patch>", "new": "<fixed line text>", "reason": "<brief justification>"}}\n'
            f'  ]\n'
            f"}}\n"
        )

        response = self._call_llm(prompt)
        if not response or not isinstance(response, dict) or "edits" not in response:
            return None, SyntaxRound(
                error=error,
                method="llm",
                edits=[],
                accepted=False,
                reject_reason="LLM response missing or invalid JSON schema",
            )

        edits_data = response.get("edits", [])
        if not edits_data or not isinstance(edits_data, list):
            return None, SyntaxRound(
                error=error,
                method="llm",
                edits=[],
                accepted=False,
                reject_reason="LLM returned no edits",
            )

        syntax_edits: list[SyntaxEdit] = []
        new_lines = list(lines)

        for e in edits_data:
            if not isinstance(e, dict):
                continue
            line_no = e.get("line")
            old_val = e.get("old")
            new_val = e.get("new")
            reason_txt = e.get("reason", "LLM syntax patch")

            if not line_no or not (1 <= line_no <= len(lines)):
                return None, SyntaxRound(
                    error=error,
                    method="llm",
                    edits=[],
                    accepted=False,
                    reject_reason=f"Edit line {line_no} out of bounds",
                )

            current_line = lines[line_no - 1]
            if old_val is not None and old_val.strip() != current_line.strip():
                return None, SyntaxRound(
                    error=error,
                    method="llm",
                    edits=[],
                    accepted=False,
                    reject_reason=f"Line {line_no} mismatch: expected {current_line!r}, got {old_val!r}",
                )

            new_lines[line_no - 1] = new_val
            syntax_edits.append(
                SyntaxEdit(
                    line=line_no,
                    old=current_line,
                    new=new_val,
                    method="llm",
                    fixer="llm_patch",
                    reason=reason_txt,
                )
            )

        candidate_source = "\n".join(new_lines)

        # ----------------------------------------------------------------------
        # ENFORCE GUARDS
        # ----------------------------------------------------------------------
        # 1. Token preservation guard
        tok_ok, tok_reason = token_preservation_guard(source, candidate_source, language)
        if not tok_ok:
            return None, SyntaxRound(
                error=error,
                method="llm",
                edits=syntax_edits,
                accepted=False,
                reject_reason=f"Token preservation guard failed: {tok_reason}",
            )

        # 2. Budget guard
        from .guards import tolerant_tokenize
        orig_tokens = len(tolerant_tokenize(source, language))
        patch_tokens = len(tolerant_tokenize(candidate_source, language))
        tok_diff = abs(patch_tokens - orig_tokens) + len(syntax_edits)
        changed_lines = len(syntax_edits)

        bud_ok, bud_reason = budget_guard(orig_tokens, tok_diff, changed_lines, total_tokens_changed)
        if not bud_ok:
            return None, SyntaxRound(
                error=error,
                method="llm",
                edits=syntax_edits,
                accepted=False,
                reject_reason=f"Budget guard failed: {bud_reason}",
            )

        return candidate_source, SyntaxRound(
            error=error,
            method="llm",
            edits=syntax_edits,
            accepted=True,
            reject_reason=None,
        )
