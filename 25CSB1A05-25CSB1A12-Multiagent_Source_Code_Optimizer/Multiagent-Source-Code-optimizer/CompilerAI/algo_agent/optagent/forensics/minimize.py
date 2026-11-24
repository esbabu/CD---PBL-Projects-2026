"""Delta-debugging minimizer: reduces failing inputs to minimal reproducers."""
from __future__ import annotations

import ast
from typing import Callable
from pydantic import BaseModel


class MinimizeResult(BaseModel):
    minimized_source: str
    reproducing_signature: str
    units_remaining: list[str]
    statements_count: int


class Minimizer:
    """Automated delta-debugging over AST units and statements."""

    @classmethod
    def minimize(
        cls,
        source: str,
        signature: str,
        test_fn: Callable[[str], bool],
    ) -> MinimizeResult:
        """Delta-debug source until signature reproduces with minimum AST nodes."""
        # 1. Parse into AST
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return MinimizeResult(
                minimized_source=source,
                reproducing_signature=signature,
                units_remaining=[],
                statements_count=len(source.splitlines()),
            )

        # 2. Extract top-level statement nodes
        original_nodes = list(tree.body)

        # Try removing functions one by one
        current_nodes = list(original_nodes)
        changed = True
        while changed:
            changed = False
            for i in range(len(current_nodes)):
                candidate = current_nodes[:i] + current_nodes[i + 1:]
                if not candidate:
                    continue
                cand_tree = ast.Module(body=candidate, type_ignores=[])
                try:
                    cand_src = ast.unparse(cand_tree)
                except Exception:
                    continue
                if test_fn(cand_src):
                    current_nodes = candidate
                    changed = True
                    break

        final_tree = ast.Module(body=current_nodes, type_ignores=[])
        final_src = ast.unparse(final_tree)
        units = [n.name for n in current_nodes if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]

        return MinimizeResult(
            minimized_source=final_src,
            reproducing_signature=signature,
            units_remaining=units,
            statements_count=len(current_nodes),
        )
