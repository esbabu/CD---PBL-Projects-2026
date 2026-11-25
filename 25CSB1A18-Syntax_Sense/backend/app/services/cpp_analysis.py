"""Read-only adapter for the existing C++ syntax classifier pipeline."""

from __future__ import annotations

import os
from pathlib import Path
import re
import sys
import tempfile
import threading
import time
from typing import Any, Callable

from backend.app.logging_config import get_logger

logger = get_logger("cpp_analysis")


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MAX_SOURCE_LENGTH = 200_000
ANALYSIS_VERSION = "cpp-legacy-ml-v1"

FEATURE_COLUMNS = (
    "num_function_decls", "num_var_decls", "num_assign_exprs",
    "num_array_decls", "num_if_stmts", "num_else_stmts",
    "num_while_stmts", "num_for_stmts", "num_return_stmts",
    "num_compound_stmts", "num_expr_stmts", "total_nodes",
    "max_depth", "avg_depth", "num_leaf_nodes",
    "error_invalid_assignment", "error_unmatched_brace",
    "error_unmatched_paren", "error_missing_semicolon",
    "error_invalid_conditional", "error_invalid_loop",
    "error_invalid_type", "error_invalid_array",
    "error_invalid_func_decl", "total_error_nodes", "scope_depth_max",
    "has_orphan_else", "func_missing_return", "assign_in_condition",
    "nested_func_decl",
)

ARTIFACT_PATHS = {
    "model": PROJECT_ROOT / "model.pkl",
    "scaler": PROJECT_ROOT / "scaler.pkl",
    "label_encoder": PROJECT_ROOT / "label_encoder.pkl",
}

PARSER_ERROR_CATEGORIES = (
    "MISPLACED_KEYWORD", "INVALID_ASSIGNMENT", "INVALID_CONDITIONAL",
    "INVALID_LOOP", "INVALID_TYPE", "INVALID_ARRAY_DECL",
    "INVALID_FUNCTION_DECL", "INVALID_SWITCH", "INVALID_CLASS_DECL",
    "INVALID_NAMESPACE_DECL", "UNMATCHED_BRACE", "UNMATCHED_PARANTHESES",
    "MISSING_SEMICOLON", "INVALID_EXPRESSION", "EXTRA_TOKENS",
)

DIAGNOSTIC_HELP = {
    "MISSING_SEMICOLON": (
        "A semicolon ';' is missing at the end of a statement or declaration.",
        "Add ';' at the end of the statement or declaration.",
    ),
    "UNMATCHED_BRACE": (
        "A curly brace '{' or '}' is missing or mismatched.",
        "Match every opening brace with a closing brace.",
    ),
    "UNMATCHED_PARANTHESES": (
        "A parenthesis '(' or ')' is missing or mismatched.",
        "Match every opening parenthesis with a closing parenthesis.",
    ),
    "INVALID_ARRAY_DECL": (
        "An array declaration has unmatched square brackets.",
        "Check that each '[' has a matching ']'.",
    ),
    "INVALID_ASSIGNMENT": (
        "A literal or constant is being used as the left-hand side of an assignment.",
        "Use a variable, not a literal, on the left side of '='.",
    ),
    "INVALID_CONDITIONAL": (
        "An if statement is missing a condition in parentheses.",
        "Put the condition in parentheses after 'if'.",
    ),
    "INVALID_LOOP": (
        "A for or while loop is missing its condition in parentheses.",
        "Put the loop condition in parentheses after 'for' or 'while'.",
    ),
    "INVALID_TYPE": (
        "A declaration contains an invalid or duplicate type keyword.",
        "Use one valid type keyword in the declaration.",
    ),
    "INVALID_FUNCTION_DECL": (
        "A function declaration is missing its opening body brace.",
        "Add '{' after the function declaration.",
    ),
    "MISPLACED_KEYWORD": (
        "A keyword appears where the parser does not allow it.",
        "Move or remove the misplaced keyword.",
    ),
    "UNTERMINATED_STRING": (
        "A string literal is missing its closing quote.",
        "Add the closing double quote to the string literal.",
    ),
    "INVALID_SWITCH": (
        "A switch statement or case label is malformed.",
        "Check switch parentheses, braces, and case-label colons.",
    ),
    "INVALID_CLASS_DECL": (
        "A class or struct declaration is malformed.",
        "Add the missing opening brace after the declaration.",
    ),
    "INVALID_NAMESPACE_DECL": (
        "A namespace declaration is malformed.",
        "Add the missing opening brace after the namespace declaration.",
    ),
    "INVALID_EXPRESSION": (
        "An expression is incomplete or missing an operand.",
        "Provide the missing operand or complete the expression before ';'.",
    ),
    "EXTRA_TOKENS": (
        "An unexpected or unrecognized token was found.",
        "Remove or replace the unexpected character or token.",
    ),
}


def _legacy_pipeline() -> tuple[Callable[..., Any], Callable[..., Any], Callable[..., Any]]:
    """Import legacy modules only when an analysis is requested."""
    for candidate in [PROJECT_ROOT, Path.cwd(), Path(__file__).resolve().parents[2]]:
        candidate_str = str(candidate)
        if candidate.is_dir() and candidate_str not in sys.path:
            sys.path.insert(0, candidate_str)

    from lexer import tokenize_file_clean
    from cpp_parser import build_ast
    from ast_features import extract_features

    return tokenize_file_clean, build_ast, extract_features


_CACHED_ARTIFACTS: tuple[Any, Any, Any] | None = None
_ARTIFACTS_LOCK = threading.Lock()


def _clear_artifact_cache() -> None:
    """Clear in-memory artifact cache (primarily for testing and cache reset)."""
    global _CACHED_ARTIFACTS
    with _ARTIFACTS_LOCK:
        _CACHED_ARTIFACTS = None


def _load_artifacts() -> tuple[Any, Any, Any]:
    """Load and cache existing, read-only model artifacts from the project root.

    Thread-safe lazy initialization ensures artifacts (model, scaler, label_encoder)
    are deserialized at most once per application lifecycle. Missing or corrupted
    artifacts raise a RuntimeError with clear diagnostic context.
    """
    global _CACHED_ARTIFACTS
    if _CACHED_ARTIFACTS is not None:
        logger.debug("C++ ML artifacts cache hit")
        return _CACHED_ARTIFACTS

    with _ARTIFACTS_LOCK:
        if _CACHED_ARTIFACTS is not None:
            logger.debug("C++ ML artifacts cache hit")
            return _CACHED_ARTIFACTS

        resolved = {}
        missing = []
        for key in ("model", "scaler", "label_encoder"):
            target_path = ARTIFACT_PATHS.get(key)
            if target_path and target_path.is_file():
                resolved[key] = target_path
            else:
                filename = f"{key}.pkl"
                fallback = next((c for c in [Path.cwd() / filename, PROJECT_ROOT / filename] if c.is_file()), None)
                if fallback and (target_path == PROJECT_ROOT / filename or target_path is None):
                    resolved[key] = fallback
                else:
                    missing.append(str(target_path or filename))

        if missing:
            logger.error("Missing C++ classifier artifact(s): %s", ", ".join(missing))
            raise RuntimeError(f"Missing C++ classifier artifact(s): {', '.join(missing)}")

        import joblib

        logger.info("Loading C++ ML classifier artifacts from project root")
        load_start = time.perf_counter()
        try:
            model = joblib.load(resolved["model"])
            scaler = joblib.load(resolved["scaler"])
            label_encoder = joblib.load(resolved["label_encoder"])
        except Exception as exc:
            logger.error("Failed to load C++ classifier artifacts: %s", exc)
            raise RuntimeError(f"Corrupted or unreadable C++ classifier artifact(s): {exc}") from exc

        duration_ms = (time.perf_counter() - load_start) * 1000
        logger.info("Successfully loaded and cached C++ ML artifacts in %.2fms", duration_ms)
        _CACHED_ARTIFACTS = (model, scaler, label_encoder)
        return _CACHED_ARTIFACTS


def _source_diagnostics(source: str) -> list[dict[str, Any]]:
    """Collect the existing predictor's non-executing source-level checks."""
    diagnostics: list[dict[str, Any]] = []
    brace_count = paren_count = bracket_count = 0

    for line_number, line in enumerate(source.splitlines(), 1):
        line_clean = re.sub(r"//.*", "", line)
        line_clean = re.sub(r"/\*.*?\*/", "", line_clean)

        quote_count = len(re.findall(r'(?<!\\)"', line_clean))
        if quote_count % 2:
            diagnostics.append(_diagnostic("UNTERMINATED_STRING", "source_heuristic", line_number))

        for character in line_clean:
            if character == "{":
                brace_count += 1
            elif character == "}":
                brace_count -= 1
            elif character == "(":
                paren_count += 1
            elif character == ")":
                paren_count -= 1
            elif character == "[":
                bracket_count += 1
            elif character == "]":
                bracket_count -= 1

        stripped = line.rstrip()
        clean_stripped = re.sub(r"//.*", "", stripped).strip()
        is_control_flow = re.match(r"^(for|while|if|else\s+if)\b", clean_stripped)
        is_preprocessor = clean_stripped.startswith("#")
        is_declaration = re.search(
            r"\b(int|float|double|char|bool|void|string)\b.*[^{};]$", clean_stripped
        )
        if (
            clean_stripped
            and not is_preprocessor
            and not clean_stripped.endswith((";", "{", "}", ":"))
            and not is_control_flow
            and is_declaration
        ):
            diagnostics.append(
                _diagnostic(
                    "MISSING_SEMICOLON",
                    "source_heuristic",
                    line_number,
                    len(stripped) + 1,
                )
            )

    if brace_count:
        diagnostics.append(_diagnostic("UNMATCHED_BRACE", "source_heuristic"))
    if paren_count:
        diagnostics.append(_diagnostic("UNMATCHED_PARANTHESES", "source_heuristic"))
    if bracket_count:
        diagnostics.append(_diagnostic("INVALID_ARRAY_DECL", "source_heuristic"))
    return diagnostics


def _parser_diagnostics(parse_errors: list[str]) -> list[dict[str, Any]]:
    diagnostics: list[dict[str, Any]] = []
    for error in parse_errors:
        category = next((item for item in PARSER_ERROR_CATEGORIES if item in error), "PARSER_ERROR")
        line_match = re.search(r"line\s+(\d+)", error)
        line = int(line_match.group(1)) if line_match else None
        col_match = re.search(r"column\s+(\d+)", error)
        column = int(col_match.group(1)) if col_match else None
        diagnostic = _diagnostic(category, "parser", line, column)
        diagnostic["parserMessage"] = error
        diagnostics.append(diagnostic)
    return diagnostics


def _diagnostic(category: str, origin: str, line: int | None = None, column: int | None = None) -> dict[str, Any]:
    explanation, suggestion = DIAGNOSTIC_HELP.get(
        category,
        ("The C++ parser reported a syntax issue.", "Review the parser message and nearby syntax."),
    )
    return {
        "category": category,
        "origin": origin,
        "severity": "error",
        "line": line,
        "column": column,
        "explanation": explanation,
        "suggestion": suggestion,
    }


def analyze_cpp_source(source: str) -> dict[str, Any]:
    """Analyze untrusted C++ source without executing code or writing artifacts."""
    if not isinstance(source, str):
        raise TypeError("C++ source must be a string.")
    if not source.strip():
        raise ValueError("C++ source must not be empty.")
    if len(source) > MAX_SOURCE_LENGTH:
        raise ValueError(f"C++ source exceeds the {MAX_SOURCE_LENGTH}-character limit.")

    tokenize_file_clean, build_ast, extract_features = _legacy_pipeline()
    temporary_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".cpp", encoding="utf-8", delete=False
        ) as temporary_source:
            temporary_source.write(source)
            temporary_path = temporary_source.name

        tokens = tokenize_file_clean(temporary_path)
        ast_root, parse_errors = build_ast(tokens)
        features = extract_features(ast_root, parse_errors)

        import numpy as np

        # Extract exactly 30 features with verified dimensions and float64 type
        feature_row = np.array(
            [[float(features.get(col, 0) if features.get(col) is not None else 0) for col in FEATURE_COLUMNS]],
            dtype=np.float64,
        )

        model, scaler, label_encoder = _load_artifacts()
        scaled_row = scaler.transform(feature_row)
        encoded_label = int(model.predict(scaled_row)[0])
        probabilities = model.predict_proba(scaled_row)[0]
        try:
            label = str(label_encoder.inverse_transform([encoded_label])[0])
        except Exception:
            label = str(encoded_label)

        parser_diagnostics = _parser_diagnostics(parse_errors)
        source_diagnostics = _source_diagnostics(source)
        all_diagnostics = parser_diagnostics + source_diagnostics
        diagnostic_count = len(all_diagnostics)

        if diagnostic_count == 0:
            classification = {
                "label": "CLEAN",
                "confidence": 100.0,
                "source": "model",
            }
        else:
            try:
                class_idx = list(model.classes_).index(encoded_label)
                confidence = float(probabilities[class_idx] * 100)
            except (ValueError, IndexError, AttributeError):
                confidence = float(probabilities[encoded_label] * 100) if len(probabilities) > encoded_label else 0.0

            classification = {
                "label": str(label),
                "confidence": round(confidence, 2),
                "source": "model",
            }

        serialized_tokens = [
            {
                "type": tok.get("token_type", "UNKNOWN"),
                "value": tok.get("token_value", ""),
                "line": tok.get("line", 1),
                "column": tok.get("column", 1),
            }
            for tok in tokens
        ]

        return {
            "language": "cpp",
            "analysisVersion": ANALYSIS_VERSION,
            "classification": classification,
            "diagnostics": all_diagnostics,
            "tokens": serialized_tokens,
            "summary": {
                "diagnosticCount": diagnostic_count,
                "parserDiagnosticCount": len(parser_diagnostics),
                "sourceHeuristicDiagnosticCount": len(source_diagnostics),
            },
        }
    finally:
        if temporary_path:
            try:
                os.unlink(temporary_path)
            except FileNotFoundError:
                pass
