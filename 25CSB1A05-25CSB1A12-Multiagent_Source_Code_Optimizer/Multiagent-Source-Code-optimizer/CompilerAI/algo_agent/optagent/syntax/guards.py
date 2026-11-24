"""Syntax patch guards enforcing strict minimal-patch invariants."""
from __future__ import annotations

import re
from typing import Tuple, List, Optional


def tolerant_tokenize(text: str, language: str = "python") -> list[tuple[str, str]]:
    """
    Tokenize text into (kind, value) pairs.
    Kinds: IDENT, NUMBER, STRING, PUNCT, KEYWORD, WS.
    """
    token_spec = [
        ("NUMBER", r"0[xX][0-9a-fA-F]+|\d+(?:\.\d+)?(?:[eE][+-]?\d+)?"),
        ("STRING", r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|"[^"\\]*(?:\\.[^"\\]*)*"|\'[^\'\\]*(?:\\.[^\'\\]*)*\''),
        ("PUNCT", r"[:;,\(\)\[\]\{\}\.\+\-\*\/\=\<\>\!\&\|\^\~\%\\\@]"),
        ("IDENT", r"[a-zA-Z_][a-zA-Z0-9_]*"),
        ("WS", r"\s+"),
    ]
    tok_regex = "|".join(f"(?P<{pair[0]}>{pair[1]})" for pair in token_spec)
    tokens: list[tuple[str, str]] = []

    pos = 0
    while pos < len(text):
        m = re.compile(tok_regex).match(text, pos)
        if m:
            kind = m.lastgroup
            val = m.group(kind)
            tokens.append((kind, val))
            pos = m.end()
        else:
            tokens.append(("PUNCT", text[pos]))
            pos += 1
    return tokens


ALLOWED_PUNCT_CHARS = set(r":;,\()[]{}'\"`.-")
ALLOWED_ADDED_KEYWORDS = {"pass", "else", "end"}


def token_preservation_guard(
    orig_text: str,
    patched_text: str,
    language: str = "python",
) -> Tuple[bool, Optional[str]]:
    """
    Ensure the token stream diff consists ONLY of punctuation/delimiters, whitespace,
    and allowed keywords ('pass', 'else').
    Any deletion, replacement, or reordering of identifiers, numbers, or string content rejects the patch.
    """
    orig_toks = tolerant_tokenize(orig_text, language)
    patched_toks = tolerant_tokenize(patched_text, language)

    # Filter out pure whitespace
    orig_semantic = [t for t in orig_toks if t[0] != "WS"]
    patched_semantic = [t for t in patched_toks if t[0] != "WS"]

    # Extract non-punctuation tokens (IDENT, NUMBER, STRING)
    orig_content = [t for t in orig_semantic if t[0] in ("IDENT", "NUMBER", "STRING")]
    patched_content = [t for t in patched_semantic if t[0] in ("IDENT", "NUMBER", "STRING")]

    # Check if any content token was changed or reordered
    # Allow trivial case where content is identical
    if orig_content != patched_content:
        # Check for allowed keyword insertion like 'pass'
        # Filter allowed keywords from patched_content
        filtered_patched = [t for t in patched_content if not (t[0] == "IDENT" and t[1] in ALLOWED_ADDED_KEYWORDS)]
        if orig_content != filtered_patched:
            # Find first difference for reporting
            for i in range(max(len(orig_content), len(filtered_patched))):
                o = orig_content[i] if i < len(orig_content) else "<EOF>"
                p = filtered_patched[i] if i < len(filtered_patched) else "<EOF>"
                if o != p:
                    return False, f"Token preservation violated at token #{i}: original={o}, patched={p}"
            return False, "Token preservation violated: identifier, number, or string content changed."

    # Verify that added punctuation tokens are strictly in allowed set
    orig_punct = [t[1] for t in orig_semantic if t[0] == "PUNCT"]
    patched_punct = [t[1] for t in patched_semantic if t[0] == "PUNCT"]
    # Punctuation can be inserted/replaced, but no weird symbols
    for p in patched_punct:
        if p not in ALLOWED_PUNCT_CHARS and p not in orig_punct:
            return False, f"Unauthorized punctuation inserted: {p!r}"

    return True, None


def budget_guard(
    orig_tokens_count: int,
    changed_tokens_count: int,
    changed_lines_count: int,
    total_tokens_changed_so_far: int = 0,
) -> Tuple[bool, Optional[str]]:
    """
    Guard: At most max(3, 1% of tokens) changed tokens per round and at most 20 per file;
    at most 5 changed lines per round.
    """
    max_round_tokens = max(3, int(0.01 * orig_tokens_count))
    if changed_tokens_count > max_round_tokens:
        return False, f"Budget exceeded: {changed_tokens_count} tokens changed in round (max allowed: {max_round_tokens})"
    if total_tokens_changed_so_far + changed_tokens_count > 20:
        return False, f"File budget exceeded: {total_tokens_changed_so_far + changed_tokens_count} tokens changed total (max: 20)"
    if changed_lines_count > 5:
        return False, f"Line budget exceeded: {changed_lines_count} lines changed in round (max allowed: 5)"
    return True, None


def progress_guard(
    initial_error_loc: Tuple[int, int],
    new_error_loc: Optional[Tuple[int, int]],
) -> Tuple[bool, Optional[str]]:
    """
    Guard: The first error must disappear (new_error_loc is None) or move later in the file.
    """
    if new_error_loc is None:
        return True, None  # All errors resolved

    init_line, init_col = initial_error_loc
    new_line, new_col = new_error_loc

    if new_line > init_line or (new_line == init_line and new_col > init_col):
        return True, None

    return False, f"No progress made: error remained at line {new_line}, col {new_col} (was {init_line}, {init_col})"
