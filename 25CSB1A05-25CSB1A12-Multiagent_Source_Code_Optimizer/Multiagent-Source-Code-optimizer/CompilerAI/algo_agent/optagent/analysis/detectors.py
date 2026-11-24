"""Specialized static detectors for algorithmic and behavioral anti-patterns."""
from __future__ import annotations

import ast
from typing import Any
from pydantic import BaseModel, Field


class DetectedPattern(BaseModel):
    kind: str
    line: int
    unit: str
    detail: str
    severity: str = "medium"
    suggested_rewrite: str | None = None


class AdvancedPatternDetector:
    """Detects manual sort, loop invariant, io in loop, mutate while iterating, and linear recursion."""

    @classmethod
    def detect_in_unit(cls, func_node: ast.FunctionDef, source_lines: list[str]) -> list[DetectedPattern]:
        patterns: list[DetectedPattern] = []

        # 1. Detect manual bubble / exchange sort
        # Pattern: nested for-loop with index compare and swap
        for node in ast.walk(func_node):
            if isinstance(node, ast.For):
                for inner in node.body:
                    if isinstance(inner, ast.For):
                        for stmt in inner.body:
                            if isinstance(stmt, ast.If):
                                # Check compare
                                if isinstance(stmt.test, ast.Compare):
                                    # Check swap in body
                                    has_swap = False
                                    for sub in stmt.body:
                                        if isinstance(sub, ast.Assign):
                                            has_swap = True
                                    if has_swap:
                                        patterns.append(DetectedPattern(
                                            kind="manual_sort",
                                            line=node.lineno,
                                            unit=func_node.name,
                                            detail="Nested loops with adjacent compare and swap (manual bubble/exchange sort).",
                                            severity="high",
                                            suggested_rewrite="Replace with built-in list.sort(key=..., reverse=...).",
                                        ))

        # 2. Detect loop-invariant expression in inner loop
        for node in ast.walk(func_node):
            if isinstance(node, ast.For):
                outer_target = node.target.id if isinstance(node.target, ast.Name) else None
                for inner in node.body:
                    if isinstance(inner, ast.For):
                        inner_target = inner.target.id if isinstance(inner.target, ast.Name) else None
                        for stmt in inner.body:
                            for sub in ast.walk(stmt):
                                if isinstance(sub, ast.BinOp) and isinstance(sub.op, ast.Div):
                                    # Check if expression uses outer_target and not inner_target
                                    names = {n.id for n in ast.walk(sub) if isinstance(n, ast.Name)}
                                    if outer_target and outer_target in names and inner_target not in names:
                                        patterns.append(DetectedPattern(
                                            kind="loop_invariant",
                                            line=stmt.lineno,
                                            unit=func_node.name,
                                            detail=f"Expression in inner loop '{ast.unparse(sub)}' depends only on outer variable '{outer_target}'.",
                                            severity="high",
                                            suggested_rewrite="Hoist invariant division out of the inner loop.",
                                        ))

        # 3. Detect I/O inside loop
        for node in ast.walk(func_node):
            if isinstance(node, ast.For):
                for stmt in node.body:
                    for sub in ast.walk(stmt):
                        if isinstance(sub, ast.Call):
                            callee = ast.unparse(sub.func)
                            if any(k in callee for k in ("get_config", "open", "read", "connect", "execute")):
                                patterns.append(DetectedPattern(
                                    kind="io_in_loop",
                                    line=stmt.lineno,
                                    unit=func_node.name,
                                    detail=f"Observable I/O call `{callee}()` invoked inside loop iteration.",
                                    severity="medium",
                                    suggested_rewrite="Hoist I/O or read lazily once outside loop with contract relaxation.",
                                ))

        # 4. Detect mutate while iterating
        for node in ast.walk(func_node):
            if isinstance(node, ast.For):
                iter_name = node.iter.id if isinstance(node.iter, ast.Name) else None
                if iter_name:
                    for stmt in ast.walk(node):
                        if isinstance(stmt, ast.Call) and isinstance(stmt.func, ast.Attribute):
                            if isinstance(stmt.func.value, ast.Name) and stmt.func.value.id == iter_name:
                                if stmt.func.attr in ("remove", "pop", "append", "extend"):
                                    patterns.append(DetectedPattern(
                                        kind="mutate_while_iterating",
                                        line=stmt.lineno,
                                        unit=func_node.name,
                                        detail=f"Container `{iter_name}` is mutated via `.{stmt.func.attr}()` while being iterated.",
                                        severity="high",
                                        suggested_rewrite="Iterate over a copy or use list comprehension filter (ChangeProposal required).",
                                    ))

        # 5. Detect linear recursion
        for node in ast.walk(func_node):
            if isinstance(node, ast.Return) and node.value:
                for sub in ast.walk(node.value):
                    if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name):
                        if sub.func.id == func_node.name:
                            patterns.append(DetectedPattern(
                                kind="linear_recursion",
                                line=node.lineno,
                                unit=func_node.name,
                                detail=f"Linear recursive call to `{func_node.name}` in return expression.",
                                severity="high",
                                suggested_rewrite="Replace with iterative loop or math builtin (e.g. math.factorial for integers).",
                            ))

        # 6. Detect hand-rolled quadratic membership / duplicate search
        for node in ast.walk(func_node):
            if isinstance(node, ast.For):
                for inner in node.body:
                    if isinstance(inner, ast.For):
                        for stmt in ast.walk(inner):
                            if isinstance(stmt, ast.Compare):
                                cmp_str = ast.unparse(stmt)
                                if "roll" in cmp_str or "==" in cmp_str:
                                    patterns.append(DetectedPattern(
                                        kind="hand_rolled_membership",
                                        line=inner.lineno,
                                        unit=func_node.name,
                                        detail="Pairwise comparison inside nested loops searching for duplicates/membership (O(n^2)).",
                                        severity="high",
                                        suggested_rewrite="Use dict/set frequency counting for O(n) lookup.",
                                    ))

        return patterns
