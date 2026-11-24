"""AST Structural Patch Safety Validator for AST Studio.

Performs robust structural validation of candidate patches prior to acceptance:
- Parses resulting source with AST
- Compares function signatures (parameters, defaults, types)
- Compares class definitions (methods, base classes)
- Inspects imports (prohibiting unapproved or dangerous imports)
- Checks changed AST structures
- Detects removed functionality or deleted public symbols
- Detects newly introduced security findings
- Validates preservation requirements
"""

from __future__ import annotations

import ast
import logging
from typing import Any, Dict, List, Optional, Set, Tuple

from backend.security_attack_agent import simulate_attacks
from backend.validator import validate_code

logger = logging.getLogger(__name__)

# Dangerous imports that should never be introduced into code candidates
DANGEROUS_IMPORTS: Set[str] = {
    "ctypes",
    "pty",
    "pdb",
    "code",
    "importlib",
    "socketserver",
}

# Standard approved libraries that defensive patches are permitted to introduce
DEFAULT_APPROVED_DEFENSIVE_IMPORTS: Set[str] = {
    "ast",
    "re",
    "json",
    "os",
    "shlex",
    "subprocess",
    "math",
    "pathlib",
    "tempfile",
    "secrets",
    "hashlib",
    "urllib.parse",
    "dataclasses",
    "typing",
}


def _get_signature_dict(node: ast.FunctionDef | ast.AsyncFunctionDef) -> Dict[str, Any]:
    """Extract a normalized dictionary representing a function's callable interface."""
    args = node.args
    posonly = [a.arg for a in args.posonlyargs]
    pos = [a.arg for a in args.args]
    kwonly = [a.arg for a in args.kwonlyargs]
    vararg = args.vararg.arg if args.vararg else None
    kwarg = args.kwarg.arg if args.kwarg else None

    # Count parameters that have defaults
    num_defaults = len(args.defaults)
    num_kw_defaults = sum(1 for d in args.kw_defaults if d is not None)

    return {
        "name": node.name,
        "posonlyargs": posonly,
        "args": pos,
        "kwonlyargs": kwonly,
        "vararg": vararg,
        "kwarg": kwarg,
        "num_defaults": num_defaults,
        "num_kw_defaults": num_kw_defaults,
        "total_params": len(posonly) + len(pos) + len(kwonly),
        "return_annotation": ast.unparse(node.returns) if node.returns else None,
    }


def compare_function_signatures(
    orig_tree: ast.AST,
    cand_tree: ast.AST,
) -> Tuple[bool, List[str]]:
    """Verify that all original functions exist in candidate and retain compatible signatures."""
    issues: List[str] = []

    orig_funcs: Dict[str, Dict[str, Any]] = {
        node.name: _get_signature_dict(node)
        for node in ast.walk(orig_tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }

    cand_funcs: Dict[str, Dict[str, Any]] = {
        node.name: _get_signature_dict(node)
        for node in ast.walk(cand_tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }

    # 1. Missing functions
    for name, orig_sig in orig_funcs.items():
        if name not in cand_funcs:
            issues.append(f"Candidate removed function '{name}'.")
            continue

        cand_sig = cand_funcs[name]

        # 2. Check parameter name preservation and backwards-compatible calling
        orig_all_args = orig_sig["posonlyargs"] + orig_sig["args"]
        cand_all_args = cand_sig["posonlyargs"] + cand_sig["args"]

        # Check if existing required positional arguments were deleted or renamed
        orig_required_count = len(orig_all_args) - orig_sig["num_defaults"]
        cand_required_count = len(cand_all_args) - cand_sig["num_defaults"]

        # If original callers pass N arguments, candidate must accept at least that
        for idx, arg_name in enumerate(orig_all_args):
            if idx < len(cand_all_args):
                cand_arg = cand_all_args[idx]
                if cand_arg != arg_name:
                    issues.append(
                        f"Function '{name}' parameter #{idx + 1} renamed from '{arg_name}' to '{cand_arg}', breaking positional calls."
                    )
            else:
                issues.append(
                    f"Function '{name}' removed parameter '{arg_name}'."
                )

        # Ensure candidate did not introduce new required parameters without defaults
        if cand_required_count > orig_required_count:
            new_required = cand_all_args[orig_required_count:cand_required_count]
            issues.append(
                f"Function '{name}' added new required parameter(s) {new_required} without defaults, breaking existing callers."
            )

    return (not issues, issues)


def compare_class_definitions(
    orig_tree: ast.AST,
    cand_tree: ast.AST,
) -> Tuple[bool, List[str]]:
    """Verify that class definitions, base classes, and public methods are preserved."""
    issues: List[str] = []

    def extract_classes(tree: ast.AST) -> Dict[str, Dict[str, Any]]:
        classes = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                bases = [ast.unparse(b).strip() for b in node.bases]
                methods = {
                    item.name
                    for item in node.body
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                }
                classes[node.name] = {"bases": bases, "methods": methods}
        return classes

    orig_classes = extract_classes(orig_tree)
    cand_classes = extract_classes(cand_tree)

    for cls_name, orig_info in orig_classes.items():
        if cls_name not in cand_classes:
            issues.append(f"Candidate removed class '{cls_name}'.")
            continue

        cand_info = cand_classes[cls_name]

        # Check base classes
        for base in orig_info["bases"]:
            if base not in cand_info["bases"]:
                issues.append(
                    f"Class '{cls_name}' removed inheritance base '{base}'."
                )

        # Check method preservation (public methods should not be dropped)
        for method in orig_info["methods"]:
            if not method.startswith("_") and method not in cand_info["methods"]:
                issues.append(
                    f"Class '{cls_name}' removed public method '{method}'."
                )

    return (not issues, issues)


def inspect_imports(
    orig_tree: ast.AST,
    cand_tree: ast.AST,
    allowed_new_roots: Optional[Set[str]] = None,
) -> Tuple[bool, List[str]]:
    """Inspect import modifications, rejecting dangerous or unapproved new dependencies."""
    issues: List[str] = []
    allowed = (allowed_new_roots or set()).union(DEFAULT_APPROVED_DEFENSIVE_IMPORTS)

    def get_imported_roots(tree: ast.AST) -> Set[str]:
        roots = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    roots.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    roots.add(node.module.split(".")[0])
        return roots

    orig_roots = get_imported_roots(orig_tree)
    cand_roots = get_imported_roots(cand_tree)

    new_roots = cand_roots - orig_roots

    for r in new_roots:
        if r in DANGEROUS_IMPORTS:
            issues.append(f"Candidate introduced blacklisted/dangerous import '{r}'.")
        elif r not in allowed:
            issues.append(f"Candidate introduced unauthorized external dependency or import '{r}'.")

    return (not issues, issues)


def detect_new_security_issues(
    orig_code: str,
    cand_code: str,
) -> Tuple[bool, List[str]]:
    """Run static security attack simulations and verify zero newly introduced vulnerabilities."""
    issues: List[str] = []

    orig_sim = simulate_attacks(orig_code)
    cand_sim = simulate_attacks(cand_code)

    orig_scenarios = {
        (s.get("category"), s.get("cwe"), s.get("name"))
        for s in orig_sim.get("attack_scenarios", [])
    }
    cand_scenarios = {
        (s.get("category"), s.get("cwe"), s.get("name"))
        for s in cand_sim.get("attack_scenarios", [])
    }

    new_vulnerabilities = cand_scenarios - orig_scenarios
    if new_vulnerabilities:
        for cat, cwe, name in new_vulnerabilities:
            issues.append(
                f"Candidate introduced new static security vulnerability: [{cwe}] {name} ({cat})."
            )

    return (not issues, issues)


def check_untargeted_functions_preserved(
    orig_tree: ast.AST,
    cand_tree: ast.AST,
    target_functions: Optional[Set[str]] = None,
) -> Tuple[bool, List[str]]:
    """Verify that functions not targeted for optimization or remediation remain unchanged."""
    if not target_functions:
        return (True, [])

    issues: List[str] = []

    def get_function_nodes(tree: ast.AST) -> Dict[str, ast.AST]:
        return {
            node.name: node
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }

    orig_nodes = get_function_nodes(orig_tree)
    cand_nodes = get_function_nodes(cand_tree)

    for name, orig_node in orig_nodes.items():
        if name not in target_functions and name in cand_nodes:
            cand_node = cand_nodes[name]
            # Compare dumped AST of untargeted functions
            if ast.dump(orig_node, include_attributes=False) != ast.dump(cand_node, include_attributes=False):
                issues.append(
                    f"Untargeted function '{name}' was modified. Changes must be minimal and scoped to target functions."
                )

    return (not issues, issues)


def validate_patch_structural_safety(
    orig_code: str,
    cand_code: str,
    target_functions: Optional[Set[str]] = None,
    allowed_new_imports: Optional[Set[str]] = None,
) -> Dict[str, Any]:
    """Perform end-to-end structural validation on candidate code before supervisor acceptance."""
    all_issues: List[str] = []
    checks: Dict[str, Any] = {}

    # 1. Parse AST of both codes
    syntax_res = validate_code(cand_code)
    checks["syntax_valid"] = syntax_res is True
    if syntax_res is not True:
        all_issues.append(f"Candidate has syntax errors: {syntax_res}")
        return {
            "is_safe": False,
            "checks": checks,
            "issues": all_issues,
            "rejection_reason": "; ".join(all_issues),
        }

    try:
        orig_tree = ast.parse(orig_code)
        cand_tree = ast.parse(cand_code)
    except SyntaxError as exc:
        all_issues.append(f"AST parsing failed: {exc}")
        return {
            "is_safe": False,
            "checks": checks,
            "issues": all_issues,
            "rejection_reason": "; ".join(all_issues),
        }

    # 2. Function signatures
    sig_ok, sig_issues = compare_function_signatures(orig_tree, cand_tree)
    checks["signatures_compatible"] = sig_ok
    if not sig_ok:
        all_issues.extend(sig_issues)

    # 3. Class definitions
    cls_ok, cls_issues = compare_class_definitions(orig_tree, cand_tree)
    checks["classes_preserved"] = cls_ok
    if not cls_ok:
        all_issues.extend(cls_issues)

    # 4. Imports inspection
    imp_ok, imp_issues = inspect_imports(orig_tree, cand_tree, allowed_new_roots=allowed_new_imports)
    checks["imports_valid"] = imp_ok
    if not imp_ok:
        all_issues.extend(imp_issues)

    # 5. Untargeted functions preservation (minimal patch scope)
    scope_ok, scope_issues = check_untargeted_functions_preserved(
        orig_tree, cand_tree, target_functions=target_functions
    )
    checks["patch_scope_minimal"] = scope_ok
    if not scope_ok:
        all_issues.extend(scope_issues)

    # 6. Security regressions
    sec_ok, sec_issues = detect_new_security_issues(orig_code, cand_code)
    checks["security_regressions_zero"] = sec_ok
    if not sec_ok:
        all_issues.extend(sec_issues)

    is_safe = len(all_issues) == 0

    return {
        "is_safe": is_safe,
        "checks": checks,
        "issues": all_issues,
        "rejection_reason": "; ".join(all_issues) if all_issues else None,
        "acceptance_explanation": (
            "Candidate passed all structural safety checks: syntax valid, function signatures preserved, "
            "class definitions intact, imports authorized, untargeted functions unchanged, and zero security regressions."
            if is_safe
            else None
        ),
    }
