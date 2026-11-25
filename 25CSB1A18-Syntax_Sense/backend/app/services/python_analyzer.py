"""PythonAnalyzer implementation for SyntaxSense using ast.parse and tokenize."""

import ast
import io
import re
import tokenize
from typing import Any, Dict, List, Optional, Tuple

from backend.app.services.base_analyzer import BaseAnalyzer

MAX_SOURCE_LENGTH = 200_000
ANALYSIS_VERSION = "python-ast-v1"

HELP_MAP: Dict[str, Tuple[str, str]] = {
    "MISSING_COLON": (
        "A colon ':' is required at the end of compound statement headers (such as 'def', 'if', 'for', 'while', 'class', 'try', 'except', 'with').",
        "Add ':' at the end of the header statement.",
    ),
    "UNEXPECTED_INDENT": (
        "Unexpected indentation found. Statements at this level should not be indented further.",
        "Align this line with previous statements at the same block level.",
    ),
    "UNINDENT_MISMATCH": (
        "Unindent does not match any outer indentation level.",
        "Ensure indentation matches the outer block level (standard is 4 spaces per indent).",
    ),
    "INDENTATION_ERROR": (
        "Indentation error detected in Python code blocks.",
        "Use consistent 4-space indentation throughout the file.",
    ),
    "UNMATCHED_DELIMITER": (
        "A bracket, parenthesis, or brace was opened but never properly closed, or delimiters are mismatched.",
        "Match every opening '(', '[', or '{' with its corresponding closing delimiter.",
    ),
    "UNTERMINATED_STRING": (
        "A string literal was started with a quote but not closed before the end of the line or file.",
        "Add the matching closing quote (\", ', \"\"\", or ''') to terminate the string literal.",
    ),
    "INVALID_ASSIGNMENT": (
        "Cannot assign a value to a literal or expression on the left-hand side of '='.",
        "Place a valid variable or target identifier on the left-hand side of the '=' operator.",
    ),
    "INVALID_SYNTAX": (
        "Python syntax error detected by the language parser.",
        "Review and correct the statement syntax at or before the indicated position.",
    ),
}


def _classify_syntax_error(exc: SyntaxError) -> Tuple[str, str, str]:
    """Classify a Python SyntaxError into standard SyntaxSense category, explanation, and suggestion."""
    msg = (exc.msg or "").lower()

    if "expected ':'" in msg or "expected colon" in msg:
        cat = "MISSING_COLON"
    elif isinstance(exc, IndentationError) or "indent" in msg:
        if "unexpected indent" in msg:
            cat = "UNEXPECTED_INDENT"
        elif "unindent does not match" in msg:
            cat = "UNINDENT_MISMATCH"
        else:
            cat = "INDENTATION_ERROR"
    elif (
        "was never closed" in msg
        or "unmatched" in msg
        or "does not match opening" in msg
        or "closing parenthesis" in msg
    ):
        cat = "UNMATCHED_DELIMITER"
    elif "unterminated string" in msg or "eol while scanning" in msg or "unterminated triple-quoted" in msg:
        cat = "UNTERMINATED_STRING"
    elif "cannot assign to" in msg or "illegal target for" in msg:
        cat = "INVALID_ASSIGNMENT"
    else:
        # Check text heuristic if msg is just generic "invalid syntax"
        text = (exc.text or "").strip()
        if text and re.match(r"^(if|elif|else|for|while|def|class|try|except|finally|with)\b", text) and not text.endswith(":"):
            cat = "MISSING_COLON"
        else:
            cat = "INVALID_SYNTAX"

    explanation, suggestion = HELP_MAP.get(cat, HELP_MAP["INVALID_SYNTAX"])
    return cat, explanation, suggestion


def _find_secondary_heuristics(source: str, primary_line: Optional[int]) -> List[Dict[str, Any]]:
    """Detect secondary reliable syntax errors (e.g. additional missing colons) across the file."""
    heuristics: List[Dict[str, Any]] = []
    lines = source.splitlines()

    for line_idx, line in enumerate(lines, 1):
        if primary_line is not None and line_idx == primary_line:
            continue

        stripped = line.strip()
        # Skip empty lines, comments, and continued lines
        if not stripped or stripped.startswith("#") or stripped.endswith("\\"):
            continue

        # Check for obvious compound statement headers missing colon
        # e.g. "if x > 0", "def foo()", "class Bar", "for i in range(10)"
        is_header = re.match(
            r"^(def\s+\w+\s*\([^)]*\)|class\s+\w+(\([^)]*\))?|if\b.+|elif\b.+|else|while\b.+|for\b.+|try|finally)\s*$",
            stripped,
        )
        if is_header and not stripped.endswith(":") and not stripped.endswith(";"):
            explanation, suggestion = HELP_MAP["MISSING_COLON"]
            heuristics.append({
                "category": "MISSING_COLON",
                "origin": "source_heuristic",
                "severity": "error",
                "line": line_idx,
                "column": len(line.rstrip()) + 1,
                "explanation": explanation,
                "suggestion": suggestion,
            })

    return heuristics


class PythonAnalyzer(BaseAnalyzer):
    """Python syntax analyzer using ast.parse and tokenize without executing code."""

    @property
    def language_id(self) -> str:
        return "python"

    @property
    def is_supported(self) -> bool:
        return True

    def analyze(self, code: str) -> Dict[str, Any]:
        if not code or not code.strip():
            raise ValueError("Python source code must not be empty.")

        if len(code) > MAX_SOURCE_LENGTH:
            raise ValueError(f"Python source exceeds the {MAX_SOURCE_LENGTH}-character limit.")

        parser_diagnostics: List[Dict[str, Any]] = []
        primary_category: Optional[str] = None
        primary_line: Optional[int] = None

        try:
            # 1. AST parse (safe non-executing compilation into abstract syntax tree)
            ast.parse(code)

            # 2. Tokenize pass (to catch token-level multi-line issues if any remain)
            try:
                list(tokenize.tokenize(io.BytesIO(code.encode("utf-8")).readline))
            except tokenize.TokenError as tok_err:
                msg, (t_line, t_col) = tok_err.args
                cat = "UNTERMINATED_STRING" if "unterminated" in msg.lower() else "UNMATCHED_DELIMITER"
                explanation, suggestion = HELP_MAP.get(cat, HELP_MAP["INVALID_SYNTAX"])
                parser_diagnostics.append({
                    "category": cat,
                    "origin": "parser",
                    "severity": "error",
                    "line": t_line,
                    "column": t_col + 1 if t_col is not None else None,
                    "explanation": explanation,
                    "suggestion": suggestion,
                    "parserMessage": f"[TokenError @ line {t_line}] {msg}",
                })
                primary_category = cat
                primary_line = t_line

        except SyntaxError as syntax_err:
            cat, explanation, suggestion = _classify_syntax_error(syntax_err)
            primary_category = cat
            primary_line = syntax_err.lineno
            col = syntax_err.offset if syntax_err.offset is not None else None
            parser_diagnostics.append({
                "category": cat,
                "origin": "parser",
                "severity": "error",
                "line": syntax_err.lineno,
                "column": col,
                "explanation": explanation,
                "suggestion": suggestion,
                "parserMessage": f"[{type(syntax_err).__name__} @ line {syntax_err.lineno}] {syntax_err.msg}",
            })

        # Secondary heuristics: only when errors were detected
        heuristic_diagnostics: List[Dict[str, Any]] = []
        if parser_diagnostics:
            heuristic_diagnostics = _find_secondary_heuristics(code, primary_line)

        all_diagnostics = parser_diagnostics + heuristic_diagnostics

        if not all_diagnostics:
            classification = {
                "label": "CLEAN",
                "confidence": 100.0,
                "source": "ast_parser",
            }
        else:
            classification = {
                "label": primary_category or all_diagnostics[0]["category"],
                "confidence": 95.0,
                "source": "ast_parser",
            }

        # Collect actual lexical tokens using Python's standard tokenize module
        serialized_tokens: List[Dict[str, Any]] = []
        try:
            for tok in tokenize.generate_tokens(io.StringIO(code).readline):
                if tok.type != tokenize.ENDMARKER:
                    serialized_tokens.append({
                        "type": tokenize.tok_name.get(tok.type, str(tok.type)),
                        "value": tok.string,
                        "line": tok.start[0],
                        "column": tok.start[1] + 1,
                    })
        except Exception:
            pass

        return {
            "language": "python",
            "analysisVersion": ANALYSIS_VERSION,
            "classification": classification,
            "diagnostics": all_diagnostics,
            "tokens": serialized_tokens,
            "summary": {
                "diagnosticCount": len(all_diagnostics),
                "parserDiagnosticCount": len(parser_diagnostics),
                "sourceHeuristicDiagnosticCount": len(heuristic_diagnostics),
            },
        }
