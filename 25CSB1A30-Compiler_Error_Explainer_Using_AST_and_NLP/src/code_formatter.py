"""C++ source code formatter with clang-format integration and pure-Python fallback.

Provides:
- is_clang_format_available() -> bool
- format_cpp_code(source, style="LLVM", fallback_on_error=True) -> str
- format_cpp_with_engine(source, style="LLVM", fallback_on_error=True) -> tuple[str, str]
- fallback_beautify_cpp(source) -> str
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from typing import Tuple


def is_clang_format_available() -> bool:
    """Return True if clang-format is installed and callable via PATH."""
    return shutil.which("clang-format") is not None


def fallback_beautify_cpp(source: str, indent_size: int = 4) -> str:
    """Beautify C++ source code using pure Python without requiring clang-format.

    Safely handles:
    - Preprocessor directives (#include, #define, #ifdef, etc.)
    - Single-line (//) and multi-line (/* */) comments
    - String literals ("...", '...')
    - Block scopes with '{' and '}'
    - Semicolon spacing and trailing whitespace
    """
    if not source or not source.strip():
        return ""

    indent_unit = " " * indent_size
    lines = source.splitlines()

    result_lines = []
    current_indent = 0
    in_block_comment = False

    for line in lines:
        stripped = line.strip()

        # Handle empty lines
        if not stripped:
            # Avoid multiple consecutive blank lines
            if result_lines and result_lines[-1] != "":
                result_lines.append("")
            continue

        # If inside multi-line comment /* ... */
        if in_block_comment:
            result_lines.append(indent_unit * current_indent + stripped)
            if "*/" in stripped:
                in_block_comment = False
            continue

        # Check for start of multi-line comment
        if stripped.startswith("/*"):
            if "*/" not in stripped:
                in_block_comment = True
            result_lines.append(indent_unit * current_indent + stripped)
            continue

        # Preprocessor directives: always column 0
        if stripped.startswith("#"):
            result_lines.append(stripped)
            continue

        # Analyze braces outside of strings and comments to determine indentation
        code_without_strings = _mask_strings_and_comments(stripped)

        # Count net open and close braces in this line
        opens = code_without_strings.count("{")
        closes = code_without_strings.count("}")

        # Check if line starts with closing brace (e.g., '}', '} else {', '};')
        first_significant_char = ""
        for ch in code_without_strings:
            if not ch.isspace():
                first_significant_char = ch
                break

        # If line starts with '}', adjust current indent before printing
        line_indent = current_indent
        if first_significant_char == "}":
            line_indent = max(0, current_indent - 1)
        elif stripped.startswith(("public:", "private:", "protected:", "case ", "default:")):
            line_indent = max(0, current_indent - 1)

        # Append formatted line
        result_lines.append(indent_unit * line_indent + stripped)

        # Update indent level for next lines
        current_indent = max(0, current_indent + (opens - closes))

    return "\n".join(result_lines) + "\n"


def _mask_strings_and_comments(line: str) -> str:
    """Mask string literals and line comments so braces inside them are not counted."""
    comment_idx = -1
    in_quote = None
    escaped = False

    for i, ch in enumerate(line):
        if escaped:
            escaped = False
            continue
        if ch == "\\":
            escaped = True
            continue
        if in_quote:
            if ch == in_quote:
                in_quote = None
        else:
            if ch in ('"', "'"):
                in_quote = ch
            elif ch == "/" and i + 1 < len(line) and line[i + 1] == "/":
                comment_idx = i
                break

    if comment_idx >= 0:
        line = line[:comment_idx]

    # Remove strings
    line = re.sub(r'"(?:\\.|[^"\\])*"', '""', line)
    line = re.sub(r"'(?:\\.|[^'\\])*'", "''", line)
    return line


def format_cpp_with_engine(
    source: str,
    style: str = "LLVM",
    fallback_on_error: bool = True,
    timeout_sec: float = 5.0,
) -> Tuple[str, str]:
    """Format C++ code, returning (formatted_source, engine_name).

    engine_name is either 'clang-format' or 'fallback'.
    """
    if not source or not source.strip():
        return ("", "fallback")

    if is_clang_format_available():
        try:
            cmd = ["clang-format", f"-style={style}"]
            proc = subprocess.run(
                cmd,
                input=source,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                encoding="utf-8",
                errors="replace",
            )
            if proc.returncode == 0 and proc.stdout:
                return (proc.stdout, "clang-format")
        except (subprocess.SubprocessError, OSError, ValueError):
            pass

    if fallback_on_error:
        return (fallback_beautify_cpp(source), "fallback")

    return (source, "none")


def format_cpp_code(
    source: str,
    style: str = "LLVM",
    fallback_on_error: bool = True,
    timeout_sec: float = 5.0,
) -> str:
    """Format C++ code and return the formatted code string."""
    formatted, _ = format_cpp_with_engine(
        source, style=style, fallback_on_error=fallback_on_error, timeout_sec=timeout_sec
    )
    return formatted
