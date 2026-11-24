"""Project-Level Code Intelligence and Architectural Metrics Engine.

Provides multi-file code intelligence across the entire workspace:
- Project-wide AST and type error aggregation
- Cross-file dead code detection (uncalled, unimported, unexported callables)
- Cross-file code duplication detection (identical AST subtrees across modules)
- Cyclomatic complexity distribution (AST-derived estimate) and
  Maintainability Index (MI) using token-based Halstead Volume
- Documentation coverage tracking (functions, classes, modules)
- Algorithmic and performance optimization recommendations

Terminology note:
  *Complexity* figures are AST-derived estimates (decision-point counting),
  not results of a full control-flow-graph (CFG) analysis.
  *Halstead Volume* is a token-based estimate computed with Python's tokenize
  module, not a full semantic Halstead implementation.
"""

from __future__ import annotations

import ast
import hashlib
import io
import math
import token
import tokenize
from typing import Any, Dict, List, Optional, Set

from backend.ast_analyzer import calculate_cc
from backend.code_analysis_engine import analyze_code_comprehensively
from backend.project.analyzer import ProjectAnalyzer
from backend.project.workspace import ProjectWorkspace
from backend.rules import summarize_quality


def _compute_halstead_volume(code: str) -> float:
    """Calculate Halstead Volume as a *token-based* estimate from tokenized Python source.

    Uses Python's ``tokenize`` module — not a parsed AST or full semantic analysis — to
    classify each token as an operator (OP tokens and reserved keywords) or operand
    (NAME / NUMBER / STRING tokens).

    V = (N1 + N2) * log2(n1 + n2)
    where:
    - n1 = count of unique operators and keywords  (vocabulary)
    - n2 = count of unique operands (identifiers, constants, strings)
    - N1 = total operator occurrences
    - N2 = total operand occurrences

    This is a good approximation of the classic Halstead metric but is not identical
    to a full Halstead implementation that distinguishes all operator kinds at the
    semantic level (e.g. function-call parentheses vs. grouping parentheses).
    """
    if not code.strip():
        return 1.0
    operators: Set[str] = set()
    operands: Set[str] = set()
    n_operators = 0
    n_operands = 0
    _KEYWORDS = {
        "def", "class", "return", "if", "elif", "else", "for", "while",
        "try", "except", "finally", "with", "as", "import", "from",
        "pass", "break", "continue", "raise", "yield", "lambda", "global",
        "nonlocal", "assert", "del", "match", "case", "async", "await",
        "and", "or", "not", "is", "in",
    }
    try:
        tokens = tokenize.generate_tokens(io.StringIO(code).readline)
        for tok_type, tok_str, _, _, _ in tokens:
            if tok_type == token.OP or tok_str in _KEYWORDS:
                operators.add(tok_str)
                n_operators += 1
            elif tok_type in (token.NAME, token.NUMBER, token.STRING):
                operands.add(tok_str)
                n_operands += 1
    except (tokenize.TokenError, IndentationError, SyntaxError):
        n_operators = max(1, len(code.split()) // 3)
        n_operands = max(1, len(code.split()) // 2)
        operators = set(str(i) for i in range(min(10, n_operators)))
        operands = set(str(i) for i in range(min(10, n_operands)))

    vocabulary = len(operators) + len(operands)
    length = n_operators + n_operands
    if vocabulary <= 1 or length <= 0:
        return 1.0
    return max(1.0, length * math.log2(vocabulary))


def _compute_maintainability_index(
    loc: int,
    cc: int,
    num_operators: int = 10,
    num_operands: int = 10,
    halstead_volume: Optional[float] = None,
) -> float:
    """Calculate the Maintainability Index (MI) score (0 to 100) based on
    token-based Halstead Volume, AST-derived cyclomatic complexity (CC), and LOC."""
    if loc <= 0:
        return 100.0
    if halstead_volume is None:
        halstead_volume = max(
            1.0,
            (num_operators + num_operands) * math.log2(max(2.0, num_operators + num_operands)),
        )
    raw_mi = 171.0 - 5.2 * math.log(max(1.0, halstead_volume)) - 0.23 * cc - 16.2 * math.log(loc)
    normalized = max(0.0, raw_mi * 100.0 / 171.0)
    return round(min(100.0, normalized), 1)


class ProjectCodeIntelligence:
    """Computes project-scale metrics, dead code, duplicates, and health diagnostics."""

    def __init__(self, workspace: ProjectWorkspace) -> None:
        self.workspace = workspace
        self.analyzer = ProjectAnalyzer(workspace)

    def analyze_all_files(self) -> Dict[str, Any]:
        """Run deep 9-domain AST analysis across every Python file in the workspace."""
        py_files = self.workspace.list_python_files()
        file_results: Dict[str, Dict[str, Any]] = {}
        all_warnings: List[Dict[str, Any]] = []

        for rel_path in py_files:
            try:
                code = self.workspace.read_file(rel_path)
                res = analyze_code_comprehensively(code)
                file_results[rel_path] = res
                all_warnings.extend(res.get("findings", []))
            except Exception as exc:
                file_results[rel_path] = {
                    "syntax_valid": False,
                    "findings": [{"id": "PARSE_ERR", "severity": "error", "title": str(exc), "line": 1}],
                }

        summary = summarize_quality(all_warnings)
        return {
            "total_files_analyzed": len(py_files),
            "overall_quality_score": summary["score"],
            "score_method": summary.get("score_method", ""),
            "blockers_present": summary.get("blockers_present", False),
            "total_findings": len(all_warnings),
            "findings_by_file": file_results,
            "summary": summary,
        }

    def detect_dead_code(self) -> List[Dict[str, Any]]:
        """Identify functions and classes defined in the project that are never called or imported."""
        py_files = self.workspace.list_python_files()
        defined_callables: Dict[str, Dict[str, Any]] = {}
        referenced_identifiers: Set[str] = set()

        for rel_path in py_files:
            try:
                tree = ast.parse(self.workspace.read_file(rel_path))
            except (OSError, SyntaxError):
                continue

            is_test_file = "test" in rel_path.lower()
            exported_all: Set[str] = set()

            for node in ast.walk(tree):
                # Track __all__ exports
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == "__all__":
                            if isinstance(node.value, (ast.List, ast.Tuple, ast.Set)):
                                for elt in node.value.elts:
                                    if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                        exported_all.add(elt.value)

                # Record all loaded identifiers
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    referenced_identifiers.add(node.id)
                elif isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Load):
                    referenced_identifiers.add(node.attr)

                # Collect function & class definitions
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    name = node.name
                    # Ignore special dunder methods, test functions, and __all__ exports
                    if (
                        not name.startswith("__")
                        and not name.startswith("test_")
                        and not is_test_file
                        and name not in exported_all
                    ):
                        key = f"{rel_path}:{node.lineno}:{name}"
                        defined_callables[key] = {
                            "name": name,
                            "type": "function" if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) else "class",
                            "file": rel_path,
                            "line": node.lineno,
                        }

        dead_code: List[Dict[str, Any]] = []
        for key, item in defined_callables.items():
            name = item["name"]
            # If name is never referenced anywhere else in the project
            # (Note: referenced_identifiers contains all loaded names across all files)
            if name not in referenced_identifiers:
                dead_code.append({
                    "id": f"DEAD_CODE_{item['file']}_{item['line']}",
                    "name": name,
                    "kind": item["type"],
                    "file_path": item["file"],
                    "line": item["line"],
                    "description": (
                        f"{item['type'].capitalize()} '{name}' is defined at line {item['line']} "
                        f"in '{item['file']}', but is never called, referenced, or exported in the project."
                    ),
                    "remediation": f"Verify whether '{name}' is dead code; remove it or expose it in __all__ if part of public API.",
                })

        return dead_code

    def detect_cross_file_duplicates(self) -> List[Dict[str, Any]]:
        """Identify identical or near-identical function implementations across different modules."""
        py_files = self.workspace.list_python_files()
        function_hashes: Dict[str, List[Dict[str, Any]]] = {}

        for rel_path in py_files:
            try:
                tree = ast.parse(self.workspace.read_file(rel_path))
            except (OSError, SyntaxError):
                continue

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Compute structural hash of function body (excluding docstring and attributes)
                    body_stmts = node.body[1:] if (
                        node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant)
                    ) else node.body

                    if len(body_stmts) >= 3:  # Only compare substantial functions
                        dumped = "".join(ast.dump(stmt, include_attributes=False) for stmt in body_stmts)
                        shash = hashlib.sha256(dumped.encode("utf-8")).hexdigest()[:16]
                        function_hashes.setdefault(shash, []).append({
                            "function_name": node.name,
                            "file_path": rel_path,
                            "line": node.lineno,
                        })

        duplicates: List[Dict[str, Any]] = []
        for shash, occurrences in function_hashes.items():
            if len(occurrences) > 1:
                # Group distinct files or locations
                files = list({occ["file_path"] for occ in occurrences})
                duplicates.append({
                    "id": f"DUP_FUNC_{shash}",
                    "occurrences_count": len(occurrences),
                    "distinct_files": files,
                    "locations": occurrences,
                    "description": (
                        f"Identical function AST logic duplicated across {len(occurrences)} locations: "
                        + ", ".join(f"{occ['file_path']}:{occ['line']} ({occ['function_name']})" for occ in occurrences)
                    ),
                    "remediation": "Extract duplicate logic into a shared utility function.",
                })

        return duplicates

    def calculate_project_metrics(self) -> Dict[str, Any]:
        """Compute complexity distribution, Maintainability Index, and documentation coverage."""
        py_files = self.workspace.list_python_files()
        total_functions = 0
        documented_functions = 0
        total_classes = 0
        documented_classes = 0
        total_modules = len(py_files)
        documented_modules = 0

        complexities: List[int] = []
        high_complexity_functions: List[Dict[str, Any]] = []
        module_mi_scores: Dict[str, float] = {}

        for rel_path in py_files:
            try:
                code = self.workspace.read_file(rel_path)
                tree = ast.parse(code)
            except (OSError, SyntaxError):
                continue

            loc = len(code.splitlines())
            file_cc = 1

            if ast.get_docstring(tree) is not None:
                documented_modules += 1

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    total_functions += 1
                    if ast.get_docstring(node) is not None:
                        documented_functions += 1

                    # Count decision points using unified AST complexity calculator
                    fn_cc = calculate_cc(node)
                    file_cc += fn_cc
                    complexities.append(fn_cc)
                    if fn_cc > 10:
                        high_complexity_functions.append({
                            "name": node.name,
                            "file": rel_path,
                            "line": node.lineno,
                            "cyclomatic_complexity": fn_cc,
                        })

                elif isinstance(node, ast.ClassDef):
                    total_classes += 1
                    if ast.get_docstring(node) is not None:
                        documented_classes += 1

            module_hv = _compute_halstead_volume(code)
            module_mi = _compute_maintainability_index(loc, file_cc, halstead_volume=module_hv)
            module_mi_scores[rel_path] = module_mi

        avg_cc = round(sum(complexities) / max(1, len(complexities)), 1)
        max_cc = max(complexities) if complexities else 1
        avg_mi = round(sum(module_mi_scores.values()) / max(1, len(module_mi_scores)), 1)

        fn_doc_pct = round((documented_functions / max(1, total_functions)) * 100.0, 1)
        cls_doc_pct = round((documented_classes / max(1, total_classes)) * 100.0, 1)
        mod_doc_pct = round((documented_modules / max(1, total_modules)) * 100.0, 1)
        overall_doc_pct = round(
            ((documented_functions + documented_classes + documented_modules)
             / max(1, total_functions + total_classes + total_modules)) * 100.0, 1
        )

        return {
            "maintainability_index": avg_mi,
            "maintainability_rating": "A" if avg_mi >= 80 else "B" if avg_mi >= 65 else "C" if avg_mi >= 50 else "D",
            "module_maintainability_indices": module_mi_scores,
            "average_cyclomatic_complexity": avg_cc,
            "maximum_cyclomatic_complexity": max_cc,
            "high_complexity_functions_count": len(high_complexity_functions),
            "high_complexity_functions": high_complexity_functions,
            "documentation_coverage": {
                "overall_percentage": overall_doc_pct,
                "functions_percentage": fn_doc_pct,
                "classes_percentage": cls_doc_pct,
                "modules_percentage": mod_doc_pct,
                "total_functions": total_functions,
                "documented_functions": documented_functions,
                "total_classes": total_classes,
                "documented_classes": documented_classes,
                "total_modules": total_modules,
                "documented_modules": documented_modules,
            },
        }
