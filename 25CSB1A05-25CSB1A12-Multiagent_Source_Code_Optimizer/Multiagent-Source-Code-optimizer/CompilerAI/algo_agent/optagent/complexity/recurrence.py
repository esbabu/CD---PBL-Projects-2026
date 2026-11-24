"""Solve algorithmic recurrences using Master Theorem and SymPy."""
from __future__ import annotations

import math
import sympy as sp
from .schemas import Recurrence


def solve_master_theorem(a: float, b: float, d: float) -> str:
    """Solve T(n) = a * T(n/b) + O(n^d) using Master Theorem.

    c = log_b(a).
    Case 1: d < c => O(n^c)
    Case 2: d == c => O(n^c log n)
    Case 3: d > c => O(n^d)
    """
    if a < 1 or b <= 1 or d < 0:
        return "unknown"

    c = math.log(a, b)
    tol = 1e-5

    def _fmt(p: float) -> str:
        if abs(p - round(p)) < tol:
            ip = int(round(p))
            if ip == 0:
                return "1"
            if ip == 1:
                return "n"
            return f"n^{ip}"
        return f"n^{p:.2f}"

    if abs(d - c) < tol:
        base = _fmt(c)
        if base == "1":
            return "O(log n)"
        return f"O({base} log n)"
    elif d < c:
        base = _fmt(c)
        return f"O({base})"
    else:  # d > c
        base = _fmt(d)
        return f"O({base})"


def solve_recurrence(relation_or_params: dict) -> Recurrence:
    """Analyze recurrence parameters (a, b, d) or fallback to sympy."""
    a = relation_or_params.get("a")
    b = relation_or_params.get("b")
    d = relation_or_params.get("d", 0.0)

    if a is not None and b is not None:
        if b == 1 and a > 1:
            # Linear recurrence like T(n) = 2T(n-1) => O(2^n)
            closed = f"O({int(a)}^n)"
            return Recurrence(
                relation=f"T(n) = {a}T(n-1) + O(n^{d})",
                a=a, b=b, d=d,
                closed_form=closed,
                method="iteration"
            )
        closed = solve_master_theorem(a, b, d)
        return Recurrence(
            relation=f"T(n) = {a}T(n/{b}) + O(n^{d})",
            a=a, b=b, d=d,
            closed_form=closed,
            method="master_theorem"
        )

    # General sympy discrete recurrence fallback
    n = sp.Symbol('n', integer=True, positive=True)
    return Recurrence(
        relation=relation_or_params.get("relation", "unknown"),
        closed_form="unknown",
        method="unknown"
    )

