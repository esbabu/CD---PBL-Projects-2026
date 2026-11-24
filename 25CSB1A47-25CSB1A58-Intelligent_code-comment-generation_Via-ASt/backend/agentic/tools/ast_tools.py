"""AST analysis, structure, and type inference tool adapters for Agentic AI Layer."""

from __future__ import annotations

from typing import Any, Dict

from backend.ast_analyzer import (
    analyze_code,
    build_smart_ast_explanations,
)
from backend.type_analyzer import find_definite_type_errors
from backend.validator import check_undefined_names


def _resolve_code(args: Dict[str, Any], context: Any) -> str:
    code = args.get("source_code")
    if code is not None and isinstance(code, str):
        return code
    if context and hasattr(context, "current_code"):
        return context.current_code
    raise ValueError("No source code provided in arguments or execution context.")


def inspect_ast_structure_handler(args: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Inspect AST structural breakdown: functions, classes, imports, call count."""
    code = _resolve_code(args, context)
    analysis = analyze_code(code)
    tree_functions = [
        {
            "name": f.get("name"),
            "line": f.get("lineno"),
            "complexity": f.get("complexity", 1),
            "docstring": bool(f.get("docstring")),
        }
        for f in analysis.get("functions", [])
    ]
    tree_classes = [
        {"name": c.get("name"), "line": c.get("lineno")}
        for c in analysis.get("classes", [])
    ]
    return {
        "function_count": len(tree_functions),
        "class_count": len(tree_classes),
        "functions": tree_functions,
        "classes": tree_classes,
        "imports": analysis.get("imports", []),
        "call_count": len(analysis.get("calls", [])),
        "file_cyclomatic_complexity": analysis.get("summary", {}).get("file_cc", 1),
    }


def infer_type_errors_handler(args: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Find definite type mismatches without running code."""
    code = _resolve_code(args, context)
    errors = find_definite_type_errors(code)
    return {
        "definite_type_errors": errors,
        "error_count": len(errors),
    }


def explain_ast_semantics_handler(args: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Produce deterministic AST-grounded explanations of control flow and algorithms."""
    code = _resolve_code(args, context)
    explanations = build_smart_ast_explanations(code)
    return {
        "explanations": explanations,
        "total_explanations": len(explanations),
    }


def inspect_undefined_names_handler(args: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Detect undefined variable or function references in AST."""
    code = _resolve_code(args, context)
    undefined = check_undefined_names(code)
    return {
        "undefined_names": [
            {"name": item.get("name"), "line": item.get("line"), "message": item.get("message")}
            for item in undefined
        ],
        "count": len(undefined),
    }
