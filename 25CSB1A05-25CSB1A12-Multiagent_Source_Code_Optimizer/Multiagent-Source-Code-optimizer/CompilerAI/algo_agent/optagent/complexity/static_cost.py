"""Symbolic static cost analysis leveraging ModuleFacts and AST walk."""
from __future__ import annotations

import ast
from ..schemas import FunctionFacts, IntentBundle, ModuleFacts
from .recurrence import solve_recurrence


# Known library call complexities
CALL_COSTS = {
    "sorted": "O(n log n)",
    "sort": "O(n log n)",
    "list.remove": "O(n)",
    "list.pop": "O(n)",  # pop(0)
    "list.index": "O(n)",
    "list.count": "O(n)",
    "min": "O(n)",
    "max": "O(n)",
    "sum": "O(n)",
}


class StaticCostAnalyzer:
    def __init__(self, intent: IntentBundle):
        self.intent = intent
        self.mod = intent.module_facts

    def analyze_function(self, name: str) -> tuple[str, str, list[str]]:
        """Return (static_time, static_space, findings)."""
        fn = self.mod.functions.get(name)
        if not fn:
            return "O(1)", "O(1)", ["Function not found in static facts."]

        findings: list[str] = []

        # 1. Recursive functions
        if fn.is_recursive or fn.in_recursive_cycle:
            if fn.branching_self_calls >= 2:
                time_c = "O(2^n)"
                space_c = "O(n)"
                findings.append(f"Recursive function with {fn.branching_self_calls} branching calls: estimated {time_c} time, {space_c} stack space.")
                return time_c, space_c, findings
            else:
                time_c = "O(n)"
                space_c = "O(n)"
                findings.append("Single-branch recursive call: estimated linear time and stack space.")
                return time_c, space_c, findings

        # 2. Iterative functions: loop nesting and cost patterns
        depth = fn.max_loop_depth
        time_order = depth  # 0 -> O(1), 1 -> O(n), 2 -> O(n^2), etc.
        has_log = False

        # Check cost patterns detected in Step 1
        for p in fn.cost_patterns:
            if p.in_loop:
                if p.kind == "linear_membership":
                    # O(n) membership inside a loop increases polynomial degree by 1
                    time_order = max(time_order, depth + 1)
                    findings.append(f"L{p.line} linear membership ('in list') inside loop of depth {depth}: scales like O(n^{time_order}).")
                elif p.kind in ("string_concat", "quadratic_append"):
                    time_order = max(time_order, depth + 1)
                    findings.append(f"L{p.line} pattern {p.kind} inside loop: increases time complexity.")

        # Check sort uses
        for s in fn.sort_uses:
            if s.in_loop:
                time_order = max(time_order, depth)
                has_log = True
                findings.append(f"L{s.line} sort inside loop: adds O(n log n) factor.")
            else:
                if time_order < 1:
                    time_order = 1
                    has_log = True
                elif time_order == 1 and not fn.cost_patterns:
                    has_log = True

        # Format time complexity
        if time_order == 0:
            time_c = "O(1)"
        elif time_order == 1:
            time_c = "O(n log n)" if has_log else "O(n)"
        elif time_order == 2:
            time_c = "O(n^2 log n)" if has_log else "O(n^2)"
        elif time_order == 3:
            time_c = "O(n^3)"
        else:
            time_c = f"O(n^{time_order})"

        # 3. Space complexity: inspect allocations in AST
        space_c = self._estimate_space(fn, depth, findings)

        return time_c, space_c, findings

    def _estimate_space(self, fn: FunctionFacts, depth: int, findings: list[str]) -> str:
        """Estimate auxiliary space complexity from AST structures and local facts."""
        if getattr(self.intent, "language", "python") != "python":
            return "O(n)" if depth > 0 else "O(1)"
        try:
            tree = ast.parse(self.intent.source)
        except Exception:
            return "O(1)"

        short_name = fn.name.split(".")[-1]
        fn_node = None
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == short_name:
                fn_node = node
                break

        if not fn_node:
            return "O(1)"

        grows_in_loop = False
        comprehension = False
        collection_copy = False

        for node in ast.walk(fn_node):
            if isinstance(node, (ast.ListComp, ast.DictComp, ast.SetComp)):
                comprehension = True
            # Appending or inserting into a list/dict/set
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr in ("append", "add", "extend", "insert", "setdefault"):
                    grows_in_loop = True
            # Subscript assignment inside loop: counts[w] = ...
            if isinstance(node, ast.Assign) and depth > 0:
                for target in node.targets:
                    if isinstance(target, ast.Subscript):
                        grows_in_loop = True
            # Full copy: list(x), set(x), dict(x)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in ("list", "set", "dict") and node.args:
                    collection_copy = True

        if (grows_in_loop and depth > 0) or comprehension or collection_copy:
            findings.append("Allocates collection(s) populated during execution: estimated O(n) auxiliary space.")
            return "O(n)"

        return "O(1)"
