"""Comprehensive AST Code Analysis Engine for AST Studio.

Performs deep structural AST analysis on Python source code to detect:
1. Syntax errors
2. Undefined names
3. Type-related issues
4. Duplicate logic
5. Complex functions
6. Poor separation of responsibilities
7. Inefficient algorithms
8. Security problems
9. Maintainability issues
"""

from __future__ import annotations

import ast
import hashlib
import logging
from typing import Any, Dict, List, Optional, Tuple

from backend.ast_analyzer import analyze_code
from backend.security_attack_agent import simulate_attacks
from backend.type_analyzer import find_definite_type_errors
from backend.validator import check_undefined_names, validate_code

logger = logging.getLogger(__name__)


def _ast_subtree_hash(node: ast.AST) -> str:
    """Compute a normalized structural hash for an AST subtree (ignoring line numbers)."""
    dumped = ast.dump(node, include_attributes=False)
    return hashlib.sha256(dumped.encode("utf-8")).hexdigest()[:16]


def detect_duplicate_logic(tree: ast.AST, source_code: str) -> List[Dict[str, Any]]:
    """Detect duplicate expressions, identical branches, or repeated control subtrees."""
    findings: List[Dict[str, Any]] = []
    lines = source_code.splitlines()

    # 1. Detect duplicate conditions in if/elif chains
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            conditions_seen: Dict[str, int] = {}
            curr: Optional[ast.If] = node
            while curr is not None and isinstance(curr, ast.If):
                cond_repr = ast.unparse(curr.test).strip()
                if cond_repr in conditions_seen:
                    findings.append({
                        "id": f"DUP_COND_{curr.lineno}",
                        "category": "duplicate_logic",
                        "severity": "warning",
                        "title": "Duplicate Condition in Conditional Chain",
                        "line": curr.lineno,
                        "description": (
                            f"Condition '{cond_repr}' is duplicated from line {conditions_seen[cond_repr]}. "
                            "This branch will never execute or performs redundant evaluation."
                        ),
                        "snippet": lines[curr.lineno - 1] if 0 < curr.lineno <= len(lines) else cond_repr,
                    })
                else:
                    conditions_seen[cond_repr] = curr.lineno

                # Traverse elif branches
                if curr.orelse and len(curr.orelse) == 1 and isinstance(curr.orelse[0], ast.If):
                    curr = curr.orelse[0]
                else:
                    curr = None

    # 2. Detect repeated complex statements or duplicated subtrees within function bodies
    for func in ast.walk(tree):
        if isinstance(func, (ast.FunctionDef, ast.AsyncFunctionDef)):
            subtree_hashes: Dict[str, Tuple[int, str]] = {}
            for stmt in func.body:
                # Only check non-trivial statements (assignments, expressions with calls/ops)
                if isinstance(stmt, (ast.Assign, ast.Expr, ast.AugAssign)) and not isinstance(stmt, ast.Pass):
                    text = ast.unparse(stmt).strip()
                    if len(text) > 20:  # Ignore trivial statements like x = 1
                        shash = _ast_subtree_hash(stmt)
                        if shash in subtree_hashes:
                            orig_line, orig_text = subtree_hashes[shash]
                            findings.append({
                                "id": f"DUP_STMT_{stmt.lineno}",
                                "category": "duplicate_logic",
                                "severity": "info",
                                "title": "Duplicated Statement Subtree",
                                "line": stmt.lineno,
                                "description": (
                                    f"Statement duplicate of line {orig_line}: '{text}'. "
                                    "Consider consolidating into a reusable helper or variable."
                                ),
                                "snippet": lines[stmt.lineno - 1] if 0 < stmt.lineno <= len(lines) else text,
                            })
                        else:
                            subtree_hashes[shash] = (stmt.lineno, text)

    return findings


def detect_separation_of_responsibilities(tree: ast.AST, source_code: str) -> List[Dict[str, Any]]:
    """Detect functions or classes with poor separation of responsibilities (God functions/classes)."""
    findings: List[Dict[str, Any]] = []
    lines = source_code.splitlines()

    io_call_names = {
        "open", "read", "write", "print", "input", "socket", "connect",
        "send", "recv", "get", "post", "put", "delete", "request", "execute",
    }

    for node in ast.walk(tree):
        # 1. Functions with too many parameters (> 5)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            total_args = (
                len(node.args.posonlyargs)
                + len(node.args.args)
                + len(node.args.kwonlyargs)
            )
            # Subtract 'self' or 'cls' if in a class
            first_arg = node.args.args[0].arg if node.args.args else ""
            if first_arg in {"self", "cls"}:
                total_args -= 1

            if total_args > 5:
                findings.append({
                    "id": f"SEP_ARGS_{node.lineno}",
                    "category": "poor_separation_of_responsibilities",
                    "severity": "warning",
                    "title": "Excessive Parameter Count",
                    "line": node.lineno,
                    "function": node.name,
                    "description": (
                        f"Function '{node.name}' accepts {total_args} parameters (threshold: 5). "
                        "High parameter counts indicate coupled responsibilities; consider a parameter object or dataclass."
                    ),
                    "snippet": lines[node.lineno - 1] if 0 < node.lineno <= len(lines) else f"def {node.name}(...)",
                })

            # 2. Mixed Concerns: Mixing raw I/O with heavy algorithmic calculation in the same function
            has_io = False
            has_nested_loops = False
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    call_name = ""
                    if isinstance(child.func, ast.Name):
                        call_name = child.func.id.lower()
                    elif isinstance(child.func, ast.Attribute):
                        call_name = child.func.attr.lower()
                    if call_name in io_call_names:
                        has_io = True
                elif isinstance(child, (ast.For, ast.While, ast.AsyncFor)):
                    for sub in ast.walk(child):
                        if sub is not child and isinstance(sub, (ast.For, ast.While, ast.AsyncFor)):
                            has_nested_loops = True

            if has_io and has_nested_loops:
                findings.append({
                    "id": f"SEP_MIXED_{node.lineno}",
                    "category": "poor_separation_of_responsibilities",
                    "severity": "warning",
                    "title": "Mixed Concerns (I/O & Heavy Algorithmic Processing)",
                    "line": node.lineno,
                    "function": node.name,
                    "description": (
                        f"Function '{node.name}' combines network/filesystem I/O operations with nested computational loops. "
                        "Separate data access / I/O from core algorithmic processing for modularity and testability."
                    ),
                    "snippet": lines[node.lineno - 1] if 0 < node.lineno <= len(lines) else f"def {node.name}(...)",
                })

        # 3. God Classes: classes with excessive method counts (> 12) or responsibilities
        elif isinstance(node, ast.ClassDef):
            method_count = sum(
                1 for item in node.body if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
            )
            if method_count > 12:
                findings.append({
                    "id": f"SEP_GOD_CLASS_{node.lineno}",
                    "category": "poor_separation_of_responsibilities",
                    "severity": "info",
                    "title": "High Method Fan-Out (God Class Smell)",
                    "line": node.lineno,
                    "class": node.name,
                    "description": (
                        f"Class '{node.name}' defines {method_count} methods. "
                        "Consider decomposing into smaller, single-responsibility collaborators."
                    ),
                    "snippet": lines[node.lineno - 1] if 0 < node.lineno <= len(lines) else f"class {node.name}:",
                })

    return findings


def detect_inefficient_algorithms(tree: ast.AST, source_code: str) -> List[Dict[str, Any]]:
    """Detect algorithmic inefficiencies such as quadratic loops, repeated len calls, and string concatenation in loops."""
    findings: List[Dict[str, Any]] = []
    lines = source_code.splitlines()

    for node in ast.walk(tree):
        # 1. Quadratic loop patterns: nested loops iterating collections
        if isinstance(node, (ast.For, ast.While, ast.AsyncFor)):
            for child in ast.iter_child_nodes(node):
                for sub in ast.walk(child):
                    if isinstance(sub, (ast.For, ast.While, ast.AsyncFor)):
                        findings.append({
                            "id": f"ALGO_QUAD_{node.lineno}",
                            "category": "inefficient_algorithms",
                            "severity": "warning",
                            "title": "Nested Loop Algorithmic Bottleneck (O(n^2) or higher)",
                            "line": node.lineno,
                            "description": (
                                f"Nested loop detected at lines {node.lineno} -> {sub.lineno}. "
                                "Iterating collections in nested loops produces O(n^2) time complexity. "
                                "Consider replacing inner linear scans with dictionary/set lookups or vectorized operations."
                            ),
                            "snippet": lines[node.lineno - 1] if 0 < node.lineno <= len(lines) else "for ...:",
                        })
                        break

        # 2. String concatenation in a loop: `s += ...` creates O(n^2) string allocations
        if isinstance(node, (ast.For, ast.While, ast.AsyncFor)):
            for child in ast.walk(node):
                if (
                    isinstance(child, ast.AugAssign)
                    and isinstance(child.op, ast.Add)
                    and isinstance(child.target, ast.Name)
                ):
                    findings.append({
                        "id": f"ALGO_STR_CONCAT_{child.lineno}",
                        "category": "inefficient_algorithms",
                        "severity": "warning",
                        "title": "Inefficient String Concatenation in Loop",
                        "line": child.lineno,
                        "description": (
                            f"Repeated string concatenation on '{child.target.id}' inside a loop. "
                            "Strings are immutable in Python; repeated concatenation results in quadratic memory allocation. "
                            "Use a list accumulator with str.join() instead."
                        ),
                        "snippet": lines[child.lineno - 1] if 0 < child.lineno <= len(lines) else f"{child.target.id} += ...",
                    })

    return findings


def detect_maintainability_issues(tree: ast.AST, source_code: str) -> List[Dict[str, Any]]:
    """Detect maintainability smells: broad exception clauses, missing docstrings, and dead code."""
    findings: List[Dict[str, Any]] = []
    lines = source_code.splitlines()

    for node in ast.walk(tree):
        # 1. Broad exception handling: `except:` or `except Exception: pass`
        if isinstance(node, ast.ExceptHandler):
            is_broad = node.type is None or (
                isinstance(node.type, ast.Name) and node.type.id in {"Exception", "BaseException"}
            )
            is_silent = len(node.body) == 1 and isinstance(node.body[0], ast.Pass)
            if is_broad and is_silent:
                findings.append({
                    "id": f"MAINT_EXC_SILENT_{node.lineno}",
                    "category": "maintainability_issues",
                    "severity": "warning",
                    "title": "Silent Broad Exception Suppression",
                    "line": node.lineno,
                    "description": (
                        "Silent exception handler (`except: pass` or `except Exception: pass`) suppresses unexpected errors, "
                        "making debugging and failure triage difficult."
                    ),
                    "snippet": lines[node.lineno - 1] if 0 < node.lineno <= len(lines) else "except Exception: pass",
                })

        # 2. Public functions/classes without docstrings
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if not node.name.startswith("_") and ast.get_docstring(node, clean=False) is None:
                findings.append({
                    "id": f"MAINT_DOC_MISSING_{node.lineno}",
                    "category": "maintainability_issues",
                    "severity": "info",
                    "title": f"Missing Docstring on Public {type(node).__name__[:-3]}",
                    "line": node.lineno,
                    "name": node.name,
                    "description": (
                        f"Public {type(node).__name__[:-3].lower()} '{node.name}' has no docstring explaining its purpose, "
                        "parameters, or return semantics."
                    ),
                    "snippet": lines[node.lineno - 1] if 0 < node.lineno <= len(lines) else f"def {node.name}(...):",
                })

    return findings


def analyze_code_comprehensively(source_code: str) -> Dict[str, Any]:
    """Execute complete, 9-domain AST analysis on Python source code.

    Domains:
    1. Syntax errors
    2. Undefined names
    3. Type-related issues
    4. Duplicate logic
    5. Complex functions
    6. Poor separation of responsibilities
    7. Inefficient algorithms
    8. Security problems
    9. Maintainability issues
    """
    results: Dict[str, Any] = {
        "syntax_valid": True,
        "syntax_errors": [],
        "undefined_names": [],
        "type_issues": [],
        "duplicate_logic": [],
        "complex_functions": [],
        "separation_of_responsibilities": [],
        "inefficient_algorithms": [],
        "security_problems": [],
        "maintainability_issues": [],
        "total_findings_count": 0,
        "findings": [],
    }

    # 1. Syntax Verification
    syntax_res = validate_code(source_code)
    if syntax_res is not True:
        results["syntax_valid"] = False
        error_item = {
            "id": "SYNTAX_ERR_001",
            "category": "syntax_errors",
            "severity": "critical",
            "title": "Python Syntax Error",
            "description": str(syntax_res),
            "line": 1,
        }
        results["syntax_errors"].append(error_item)
        results["findings"].append(error_item)
        results["total_findings_count"] = 1
        return results

    try:
        tree = ast.parse(source_code)
    except SyntaxError as exc:
        results["syntax_valid"] = False
        error_item = {
            "id": "SYNTAX_ERR_001",
            "category": "syntax_errors",
            "severity": "critical",
            "title": "Python Syntax Error",
            "line": exc.lineno or 1,
            "description": f"Syntax error at line {exc.lineno}: {exc.msg}",
        }
        results["syntax_errors"].append(error_item)
        results["findings"].append(error_item)
        results["total_findings_count"] = 1
        return results

    # 2. Undefined Names
    raw_undefined = check_undefined_names(source_code)
    for u in raw_undefined:
        finding = {
            "id": f"UNDEF_NAME_{u['lineno']}_{u['name']}",
            "category": "undefined_names",
            "severity": "error",
            "title": f"Undefined Name '{u['name']}'",
            "line": u["lineno"],
            "name": u["name"],
            "description": f"Name '{u['name']}' is used without being defined, imported, or assigned.",
            "snippet": u.get("line_text", ""),
        }
        results["undefined_names"].append(finding)
        results["findings"].append(finding)

    # 3. Type-Related Issues
    type_errs = find_definite_type_errors(tree)
    for t in type_errs:
        finding = {
            "id": f"TYPE_ERR_{t['line']}_{t.get('variable', '')}",
            "category": "type_related_issues",
            "severity": "error",
            "title": "Static Type Mismatch",
            "line": t["line"],
            "description": t["message"],
            "snippet": t.get("evidence", ""),
        }
        results["type_issues"].append(finding)
        results["findings"].append(finding)

    # 4. Duplicate Logic
    dup_logic = detect_duplicate_logic(tree, source_code)
    results["duplicate_logic"].extend(dup_logic)
    results["findings"].extend(dup_logic)

    # 5. Complex Functions
    base_analysis = analyze_code(source_code)
    for f in base_analysis.get("functions", []):
        cc = f.get("cyclomatic_complexity", 1)
        depth = f.get("nesting_depth", 0)
        lines_count = f.get("statement_count", 0)
        if cc > 10 or depth > 3 or lines_count > 40:
            finding = {
                "id": f"COMPLEX_FUNC_{f.get('line', 1)}_{f.get('name', '')}",
                "category": "complex_functions",
                "severity": "warning" if cc > 15 else "info",
                "title": f"High Complexity Function '{f.get('name')}'",
                "line": f.get("line", 1),
                "function": f.get("name"),
                "cyclomatic_complexity": cc,
                "nesting_depth": depth,
                "statement_count": lines_count,
                "description": (
                    f"Function '{f.get('name')}' has cyclomatic complexity {cc} (threshold: 10) "
                    f"and nesting depth {depth} (threshold: 3). Refactor into smaller helper functions."
                ),
            }
            results["complex_functions"].append(finding)
            results["findings"].append(finding)

    # 6. Poor Separation of Responsibilities
    sep_findings = detect_separation_of_responsibilities(tree, source_code)
    results["separation_of_responsibilities"].extend(sep_findings)
    results["findings"].extend(sep_findings)

    # 7. Inefficient Algorithms
    ineff_findings = detect_inefficient_algorithms(tree, source_code)
    results["inefficient_algorithms"].extend(ineff_findings)
    results["findings"].extend(ineff_findings)

    # 8. Security Problems (16 CWE categories)
    sec_attack_results = simulate_attacks(source_code)
    for scenario in sec_attack_results.get("attack_scenarios", []):
        finding = {
            "id": f"SEC_{scenario.get('cwe', 'CWE')}_{scenario.get('target_line', 1)}",
            "category": "security_problems",
            "severity": scenario.get("severity", "high").lower(),
            "cwe": scenario.get("cwe"),
            "title": scenario.get("name"),
            "line": scenario.get("target_line", 1),
            "description": scenario.get("mitigation", "Security vulnerability detected."),
            "evidence": scenario.get("vulnerable_code", ""),
            "sink": scenario.get("sink", ""),
        }
        results["security_problems"].append(finding)
        results["findings"].append(finding)

    # 9. Maintainability Issues
    maint_findings = detect_maintainability_issues(tree, source_code)
    results["maintainability_issues"].extend(maint_findings)
    results["findings"].extend(maint_findings)

    results["total_findings_count"] = len(results["findings"])
    return results
