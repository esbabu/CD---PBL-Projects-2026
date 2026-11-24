"""Reconciliation between static cost predictions and empirical curve fits."""
from __future__ import annotations

from .empirical import COMPLEXITY_RANK
from .schemas import FitResult


def reconcile_complexity(
    static_time: str,
    static_space: str,
    time_fit: FitResult | None,
    space_fit: FitResult | None,
) -> tuple[str, str, list[str]]:
    """Reconcile static and empirical findings. Disagreements become recorded findings."""
    findings: list[str] = []

    # 1. Time complexity reconciliation
    if not time_fit or time_fit.r2 < 0.70:
        reconciled_time = static_time
        findings.append(f"Empirical time fit has low confidence (R^2 = {getattr(time_fit, 'r2', 0.0):.2f}); relying on static analysis: {static_time}.")
    elif time_fit.model == static_time:
        reconciled_time = static_time
        findings.append(f"Static prediction and empirical measurement agree on {static_time} (empirical R^2 = {time_fit.r2:.3f}).")
    else:
        # Disagreement
        static_rank = COMPLEXITY_RANK.get(static_time, 2)
        emp_rank = COMPLEXITY_RANK.get(time_fit.model, 2)
        if emp_rank < static_rank:
            # e.g. Static O(n^2), Empirical O(n) (e.g., early exit or best-case inputs)
            reconciled_time = static_time
            findings.append(
                f"Disagreement: static analysis predicts worst-case {static_time}, but empirical fit observed {time_fit.model} (R^2 = {time_fit.r2:.3f}). "
                f"Preserving worst-case {static_time}; empirical may reflect early-exit or average-case scaling."
            )
        else:
            # Empirical shows higher cost than static.
            # If static established a tight structural bound (e.g. depth 1 + linear membership => O(n^2)),
            # small-N empirical fitting can overshoot due to cache / timing noise.
            if static_time in ("O(n^2)", "O(n log n)", "O(n)") and time_fit.n_points <= 10:
                reconciled_time = static_time
                findings.append(
                    f"Disagreement: static analysis proves {static_time} upper bound, but small-N empirical measurement fitted {time_fit.model} (R^2 = {time_fit.r2:.3f}). "
                    f"Attributing to small-N warmup/noise; reconciling to theoretical upper bound {static_time}."
                )
            else:
                reconciled_time = time_fit.model
                findings.append(
                    f"Disagreement: static analysis predicted {static_time}, but empirical measurement scaled as {time_fit.model} (R^2 = {time_fit.r2:.3f}). "
                    f"Adopted empirical {time_fit.model} due to observed runtime scaling."
                )

    # 2. Space complexity reconciliation
    # Auxiliary space: if static analysis proves no auxiliary collections or recursion are allocated,
    # it is O(1) auxiliary space regardless of input argument sizes in memory.
    if static_space == "O(1)":
        reconciled_space = "O(1)"
        if space_fit and space_fit.model != "O(1)":
            findings.append(f"Static analysis proves O(1) auxiliary space (tracemalloc measured input argument scaling {space_fit.model}).")
        else:
            findings.append("Static prediction and empirical memory agree on O(1).")
    elif not space_fit or space_fit.r2 < 0.70:
        reconciled_space = static_space
        findings.append(f"Relying on static space analysis: {static_space}.")
    else:
        reconciled_space = static_space if COMPLEXITY_RANK.get(static_space, 0) >= COMPLEXITY_RANK.get(space_fit.model, 0) else space_fit.model
        findings.append(f"Space reconciliation: static={static_space}, empirical={space_fit.model}; using {reconciled_space}.")

    return reconciled_time, reconciled_space, findings
