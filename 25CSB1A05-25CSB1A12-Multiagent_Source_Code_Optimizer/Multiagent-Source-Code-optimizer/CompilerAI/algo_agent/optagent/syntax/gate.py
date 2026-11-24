"""Stage S0: Syntax Gate orchestrator."""
from __future__ import annotations

import difflib
import hashlib
from typing import Any, List, Optional, Tuple

from .fixers import HeuristicFixer, check_syntax
from .guards import progress_guard
from .llm_patch import LLMSyntaxPatcher
from .report import SyntaxEdit, SyntaxReport, SyntaxRound


class SyntaxGate:
    """
    Stage S0: Validates and repairs syntax errors before triage.
    Enforces deterministic fixers first, then guarded LLM patches.
    """

    def __init__(self, mode: str = "auto", llm_gateway: Any = None):
        self.mode = mode.lower().strip()  # off | heuristic | auto
        self.patcher = LLMSyntaxPatcher(llm_gateway) if llm_gateway else None

    def process(self, source: str, language: str = "python") -> tuple[str, SyntaxReport]:
        """
        Run the Syntax Gate.
        Returns (repaired_or_original_source, syntax_report).
        """
        orig_sha = hashlib.sha256(source.encode("utf-8")).hexdigest()[:12]

        if self.mode == "off":
            return source, SyntaxReport(
                ok=True,
                language=language,
                original_sha=orig_sha,
                repaired_sha=orig_sha,
            )

        initial_err = check_syntax(source, language)
        if initial_err is None:
            # Code is already valid: zero changes, zero LLM calls
            return source, SyntaxReport(
                ok=True,
                language=language,
                original_sha=orig_sha,
                repaired_sha=orig_sha,
                diff="",
                tokens_changed=0,
                llm_calls=0,
            )

        current_source = source
        rounds: list[SyntaxRound] = []
        total_tokens_changed = 0
        llm_calls_made = 0

        # ======================================================================
        # 1. Deterministic Heuristic Fixers
        # ======================================================================
        # Step 1a: Global normalization (markdown fences first, then smart quotes, then tab/spaces)
        current_source, fence_edits = HeuristicFixer.strip_stray_markdown_fences(current_source)
        if fence_edits:
            rounds.append(
                SyntaxRound(
                    error=initial_err,
                    method="heuristic:strip_fences",
                    edits=fence_edits,
                    accepted=True,
                )
            )

        current_source, q_edits = HeuristicFixer.fix_smart_quotes(current_source)
        if q_edits:
            rounds.append(
                SyntaxRound(
                    error=initial_err,
                    method="heuristic:smart_quotes",
                    edits=q_edits,
                    accepted=True,
                )
            )

        lang_lower = language.lower().strip()
        if lang_lower in ("python", "py"):
            current_source, tab_edits = HeuristicFixer.fix_tab_spaces_mix_python(current_source)
            if tab_edits:
                rounds.append(
                    SyntaxRound(
                        error=initial_err,
                        method="heuristic:tab_spaces_mix",
                        edits=tab_edits,
                        accepted=True,
                    )
                )

        if lang_lower in ("c", "cpp", "c++"):
            current_source, header_edits = HeuristicFixer.fix_missing_headers_c_cpp(current_source)
            if header_edits:
                rounds.append(
                    SyntaxRound(
                        error=initial_err,
                        method="heuristic:missing_headers",
                        edits=header_edits,
                        accepted=True,
                    )
                )

        # Step 1b: Iterative targeted heuristic fix loop (up to 20 rounds)
        for h_round in range(20):
            err = check_syntax(current_source, language)
            if err is None:
                break  # Successfully repaired by heuristics!

            progress_made = False
            last_err_loc = (err.get("line", 1), err.get("column", 1))

            # Try targeted heuristic fixers based on language and error
            candidate_source = current_source
            candidate_edits: list[SyntaxEdit] = []

            if lang_lower in ("python", "py"):
                # Try colon fixer
                candidate_source, candidate_edits = HeuristicFixer.fix_missing_colons_python(current_source, err)
                if not candidate_edits:
                    # Try unbalanced delimiters
                    candidate_source, candidate_edits = HeuristicFixer.fix_unbalanced_delimiters(current_source, err)
                if not candidate_edits:
                    # Try python2 print
                    candidate_source, candidate_edits = HeuristicFixer.fix_python2_print(current_source, err)

            elif lang_lower in ("c", "cpp", "c++", "javascript", "js"):
                # Try unbalanced delimiters
                candidate_source, candidate_edits = HeuristicFixer.fix_unbalanced_delimiters(current_source, err)
                if not candidate_edits and lang_lower in ("c", "cpp", "c++"):
                    # Try missing semicolon
                    candidate_source, candidate_edits = HeuristicFixer.fix_missing_semicolon_c_cpp(current_source, err)

            if candidate_edits and candidate_source != current_source:
                new_err = check_syntax(candidate_source, language)
                new_err_loc = (new_err.get("line", 1), new_err.get("column", 1)) if new_err else None
                prog_ok, _ = progress_guard(last_err_loc, new_err_loc)

                if prog_ok:
                    current_source = candidate_source
                    rounds.append(
                        SyntaxRound(
                            error=err,
                            method=f"heuristic:{candidate_edits[0].fixer}",
                            edits=candidate_edits,
                            accepted=True,
                        )
                    )
                    progress_made = True

            if not progress_made:
                break  # Heuristics exhausted

        # ======================================================================
        # 2. Guarded LLM Syntax Patch (if heuristics did not fully resolve error)
        # ======================================================================
        curr_err = check_syntax(current_source, language)
        if curr_err is not None and self.mode in ("auto", "llm") and self.patcher:
            # Max 3 rounds of windowed minimal LLM patches
            for llm_round_idx in range(3):
                err = check_syntax(current_source, language)
                if err is None:
                    break

                llm_calls_made += 1
                patched_source, round_info = self.patcher.attempt_patch(
                    current_source,
                    err,
                    language=language,
                    total_tokens_changed=total_tokens_changed,
                )
                if round_info:
                    rounds.append(round_info)

                if patched_source and round_info and round_info.accepted:
                    new_err = check_syntax(patched_source, language)
                    new_err_loc = (new_err.get("line", 1), new_err.get("column", 1)) if new_err else None
                    last_err_loc = (err.get("line", 1), err.get("column", 1))
                    prog_ok, _ = progress_guard(last_err_loc, new_err_loc)

                    if prog_ok:
                        current_source = patched_source
                        total_tokens_changed += len(round_info.edits)
                        if new_err is None:
                            break  # Fully resolved!

        final_err = check_syntax(current_source, language)
        repaired_sha = hashlib.sha256(current_source.encode("utf-8")).hexdigest()[:12] if final_err is None else None

        # Compute diff if changes occurred
        diff_text = ""
        if current_source != source:
            diff_text = "\n".join(
                difflib.unified_diff(
                    source.splitlines(),
                    current_source.splitlines(),
                    fromfile="original",
                    tofile="syntax_repaired",
                    lineterm="",
                )
            )

        return current_source, SyntaxReport(
            ok=(final_err is None),
            language=language,
            rounds=rounds,
            original_sha=orig_sha,
            repaired_sha=repaired_sha,
            diff=diff_text,
            tokens_changed=total_tokens_changed,
            llm_calls=llm_calls_made,
        )
