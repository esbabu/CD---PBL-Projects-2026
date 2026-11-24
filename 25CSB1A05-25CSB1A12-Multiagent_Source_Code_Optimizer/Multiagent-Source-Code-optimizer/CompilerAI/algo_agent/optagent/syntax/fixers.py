"""Deterministic syntax error detectors and heuristic fixers."""
from __future__ import annotations

import difflib
import re
from typing import Any, Dict, List, Optional, Tuple

from .report import SyntaxEdit


def check_syntax(source: str, language: str = "python") -> Optional[Dict[str, Any]]:
    """
    Check code syntax.
    Returns None if valid, or a dict {line, column, message, error_type}.
    """
    lang = language.lower().strip()
    if lang in ("python", "py"):
        try:
            compile(source, "<string>", "exec")
            return None
        except (SyntaxError, IndentationError, TabError) as e:
            return {
                "line": e.lineno or 1,
                "column": e.offset or 1,
                "message": e.msg or str(e),
                "error_type": type(e).__name__,
            }

    elif lang in ("javascript", "js"):
        try:
            import tree_sitter_javascript
            from tree_sitter import Language, Parser
            parser = Parser(Language(tree_sitter_javascript.language()))
            tree = parser.parse(source.encode("utf-8"))
            if tree.root_node.has_error:
                # Find the first error node
                def find_error(node):
                    if node.is_error or node.is_missing:
                        return node
                    for child in node.children:
                        res = find_error(child)
                        if res is not None:
                            return res
                    return None
                err = find_error(tree.root_node)
                if err:
                    return {
                        "line": err.start_point.row + 1,
                        "column": err.start_point.column + 1,
                        "message": f"Syntax error near '{source.encode('utf-8')[err.start_byte:err.end_byte].decode('utf-8', 'ignore')}'",
                        "error_type": "TreeSitterSyntaxError",
                    }
            return None
        except Exception:
            return None

    elif lang in ("c", "cpp", "c++"):
        try:
            import tree_sitter_c, tree_sitter_cpp
            from tree_sitter import Language, Parser
            lang_mod = tree_sitter_cpp if lang in ("cpp", "c++") else tree_sitter_c
            parser = Parser(Language(lang_mod.language()))
            tree = parser.parse(source.encode("utf-8"))
            if tree.root_node.has_error:
                def find_error(node):
                    if node.is_error or node.is_missing:
                        return node
                    for child in node.children:
                        res = find_error(child)
                        if res is not None:
                            return res
                    return None
                err = find_error(tree.root_node)
                if err:
                    return {
                        "line": err.start_point.row + 1,
                        "column": err.start_point.column + 1,
                        "message": f"Syntax error near '{source.encode('utf-8')[err.start_byte:err.end_byte].decode('utf-8', 'ignore')}'",
                        "error_type": "TreeSitterSyntaxError",
                    }
            return None
        except Exception:
            return None

    return None


class HeuristicFixer:
    """Collection of deterministic syntax fixers."""

    @staticmethod
    def fix_smart_quotes(source: str) -> tuple[str, list[SyntaxEdit]]:
        """Normalize smart quotes and non-breaking spaces to ASCII."""
        has_trailing_nl = source.endswith("\n")
        replacements = [
            ("“", '"'),
            ("”", '"'),
            ("‘", "'"),
            ("’", "'"),
            ("\u00a0", " "),
            ("\u200b", ""),
        ]
        edits: list[SyntaxEdit] = []
        new_lines: list[str] = []
        lines = source.splitlines()

        for idx, line in enumerate(lines, 1):
            curr = line
            for old_char, new_char in replacements:
                if old_char in curr:
                    curr = curr.replace(old_char, new_char)
            if curr != line:
                edits.append(
                    SyntaxEdit(
                        line=idx,
                        old=line,
                        new=curr,
                        method="heuristic",
                        fixer="smart_quotes",
                        reason="Replaced non-ASCII smart quotes or whitespace with ASCII equivalents",
                    )
                )
            new_lines.append(curr)

        res = "\n".join(new_lines)
        if has_trailing_nl and not res.endswith("\n"):
            res += "\n"
        return res, edits

    @staticmethod
    def strip_stray_markdown_fences(source: str) -> tuple[str, list[SyntaxEdit]]:
        """Remove markdown fences and stray introductory/conclusion prose lines."""
        has_trailing_nl = source.endswith("\n")
        lines = source.splitlines()
        edits: list[SyntaxEdit] = []
        new_lines: list[str] = []

        for idx, line in enumerate(lines, 1):
            stripped = line.strip()
            # Fences like ```python, ```, etc.
            if stripped.startswith("```"):
                edits.append(
                    SyntaxEdit(
                        line=idx,
                        old=line,
                        new="",
                        method="heuristic",
                        fixer="strip_fences",
                        reason="Removed markdown code block delimiter",
                    )
                )
                continue
            # Common stray conversational prose at start
            if idx <= 2 and (
                stripped.lower().startswith("here is the ")
                or stripped.lower().startswith("here's the ")
                or stripped.lower().startswith("here is your ")
            ):
                edits.append(
                    SyntaxEdit(
                        line=idx,
                        old=line,
                        new="",
                        method="heuristic",
                        fixer="strip_prose",
                        reason="Removed conversational prose header",
                    )
                )
                continue
            new_lines.append(line)

        res = "\n".join(new_lines)
        if has_trailing_nl and not res.endswith("\n"):
            res += "\n"
        return res, edits

    @staticmethod
    def fix_missing_colons_python(source: str, error: dict[str, Any]) -> tuple[str, list[SyntaxEdit]]:
        """Insert missing colon at the end of block header statements in Python."""
        err_line = error.get("line")
        if not err_line:
            return source, []

        has_trailing_nl = source.endswith("\n")
        lines = source.splitlines()
        if not (1 <= err_line <= len(lines)):
            return source, []

        line_idx = err_line - 1
        line = lines[line_idx]
        stripped = line.rstrip()

        # Check if line looks like a control header missing a colon
        keywords = ("def ", "class ", "if ", "elif ", "else", "for ", "while ", "try", "except", "finally", "with ")
        clean_code = stripped.split("#")[0].strip()
        needs_colon = any(clean_code == kw.strip() or clean_code.startswith(kw) for kw in keywords)

        if needs_colon and not clean_code.endswith(":"):
            # Insert colon before any inline comment
            if "#" in stripped:
                code_part, comment_part = stripped.split("#", 1)
                new_line = code_part.rstrip() + ": #" + comment_part
            else:
                new_line = stripped + ":"

            lines[line_idx] = new_line
            edit = SyntaxEdit(
                line=err_line,
                old=line,
                new=new_line,
                method="heuristic",
                fixer="missing_colon",
                reason="Appended missing colon to control structure header",
            )
            res = "\n".join(lines)
            if has_trailing_nl and not res.endswith("\n"):
                res += "\n"
            return res, [edit]

        return source, []

    @staticmethod
    def fix_python2_print(source: str, error: dict[str, Any]) -> tuple[str, list[SyntaxEdit]]:
        """Convert Python 2 print statements to Python 3 print() calls."""
        has_trailing_nl = source.endswith("\n")
        lines = source.splitlines()
        err_line = error.get("line", 1)
        if not (1 <= err_line <= len(lines)):
            return source, []

        line = lines[err_line - 1]
        m = re.match(r"^(\s*)print\s+([^(].*)$", line)
        if m:
            indent, expr = m.groups()
            new_line = f"{indent}print({expr.strip()})"
            lines[err_line - 1] = new_line
            edit = SyntaxEdit(
                line=err_line,
                old=line,
                new=new_line,
                method="heuristic",
                fixer="python2_print",
                reason="Wrapped Python 2 print statement arguments in parentheses",
            )
            res = "\n".join(lines)
            if has_trailing_nl and not res.endswith("\n"):
                res += "\n"
            return res, [edit]

        return source, []

    @staticmethod
    def fix_unbalanced_delimiters(source: str, error: dict[str, Any]) -> tuple[str, list[SyntaxEdit]]:
        """Fix missing closing parenthesis, bracket, or brace."""
        has_trailing_nl = source.endswith("\n")
        lines = source.splitlines()
        err_line = error.get("line", len(lines))
        target_idx = min(err_line - 1, len(lines) - 1)
        if target_idx < 0:
            return source, []

        # Count delimiters across file up to error line
        text_up_to = "\n".join(lines[: target_idx + 1])
        parens = text_up_to.count("(") - text_up_to.count(")")
        brackets = text_up_to.count("[") - text_up_to.count("]")
        braces = text_up_to.count("{") - text_up_to.count("}")

        closers = ""
        if parens > 0:
            closers += ")" * parens
        if brackets > 0:
            closers += "]" * brackets
        if braces > 0:
            closers += "}" * braces

        if closers:
            old_line = lines[target_idx]
            stripped = old_line.rstrip()
            if stripped.endswith(":"):
                new_line = stripped[:-1].rstrip() + closers + ":"
            else:
                new_line = stripped + closers
            lines[target_idx] = new_line
            edit = SyntaxEdit(
                line=target_idx + 1,
                old=old_line,
                new=new_line,
                method="heuristic",
                fixer="unbalanced_delimiters",
                reason=f"Appended missing closing delimiter(s) '{closers}'",
            )
            res = "\n".join(lines)
            if has_trailing_nl and not res.endswith("\n"):
                res += "\n"
            return res, [edit]

        return source, []

    @staticmethod
    def fix_tab_spaces_mix_python(source: str) -> tuple[str, list[SyntaxEdit]]:
        """Normalize tabs to 4 spaces in Python files."""
        if "\t" not in source:
            return source, []

        has_trailing_nl = source.endswith("\n")
        lines = source.splitlines()
        edits: list[SyntaxEdit] = []
        new_lines: list[str] = []

        for idx, line in enumerate(lines, 1):
            if "\t" in line:
                # Replace leading tabs with 4 spaces each
                leading = len(line) - len(line.lstrip(" \t"))
                prefix = line[:leading].replace("\t", "    ")
                new_line = prefix + line[leading:]
                edits.append(
                    SyntaxEdit(
                        line=idx,
                        old=line,
                        new=new_line,
                        method="heuristic",
                        fixer="tab_spaces_mix",
                        reason="Replaced mixed tabs in indentation with 4 spaces",
                    )
                )
                new_lines.append(new_line)
            else:
                new_lines.append(line)

        res = "\n".join(new_lines)
        if has_trailing_nl and not res.endswith("\n"):
            res += "\n"
        return res, edits

    @staticmethod
    def fix_missing_semicolon_c_cpp(source: str, error: dict[str, Any]) -> tuple[str, list[SyntaxEdit]]:
        """Insert missing semicolon in C/C++ statement."""
        lines = source.splitlines()
        err_line = error.get("line", 1)
        if not (1 <= err_line <= len(lines)):
            return source, []

        # Check line or previous line
        target_idx = err_line - 1
        line = lines[target_idx]
        stripped = line.strip()

        if stripped and not stripped.endswith(";") and not stripped.endswith("{") and not stripped.endswith("}"):
            new_line = line.rstrip() + ";"
            lines[target_idx] = new_line
            edit = SyntaxEdit(
                line=target_idx + 1,
                old=line,
                new=new_line,
                method="heuristic",
                fixer="missing_semicolon",
                reason="Appended missing semicolon to C/C++ statement",
            )
            return "\n".join(lines), [edit]

        return source, []

    @staticmethod
    def fix_missing_headers_c_cpp(source: str) -> tuple[str, list[SyntaxEdit]]:
        """Auto-add missing standard library headers in C/C++ inferred from identifiers."""
        HEADER_MAP = {
            "printf": "<stdio.h>",
            "sprintf": "<stdio.h>",
            "snprintf": "<stdio.h>",
            "malloc": "<stdlib.h>",
            "free": "<stdlib.h>",
            "strlen": "<string.h>",
            "strcpy": "<string.h>",
            "memcpy": "<string.h>",
            "memset": "<string.h>",
            "std::vector": "<vector>",
            "std::string": "<string>",
            "std::cout": "<iostream>",
            "std::cin": "<iostream>",
            "std::endl": "<iostream>",
            "std::unordered_map": "<unordered_map>",
            "std::map": "<map>",
        }

        needed_headers: set[str] = set()
        for ident, header in HEADER_MAP.items():
            if ident in source and header not in source:
                needed_headers.add(header)

        if not needed_headers:
            return source, []

        header_lines = [f"#include {h}" for h in sorted(needed_headers)]
        new_source = "\n".join(header_lines) + "\n" + source
        edit = SyntaxEdit(
            line=1,
            old="",
            new="\n".join(header_lines),
            method="heuristic",
            fixer="missing_headers",
            reason=f"Added inferred missing standard headers: {', '.join(sorted(needed_headers))}",
        )
        return new_source, [edit]
