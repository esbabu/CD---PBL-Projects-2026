"""Empirical complexity analysis: fitting time and space data to candidate models."""
from __future__ import annotations

import math
import numpy as np
from scipy import stats
from .schemas import FitResult


MODELS = [
    ("O(1)", lambda n: np.ones_like(n, dtype=float)),
    ("O(log n)", lambda n: np.log2(np.maximum(n, 2.0))),
    ("O(n)", lambda n: n.astype(float)),
    ("O(n log n)", lambda n: n * np.log2(np.maximum(n, 2.0))),
    ("O(n^2)", lambda n: n.astype(float) ** 2),
    ("O(n^2 log n)", lambda n: (n.astype(float) ** 2) * np.log2(np.maximum(n, 2.0))),
    ("O(n^3)", lambda n: n.astype(float) ** 3),
    ("O(2^n)", lambda n: np.power(2.0, np.minimum(n.astype(float), 30.0))),
]

# Order for worst-case dominance
COMPLEXITY_RANK = {
    "O(1)": 0,
    "O(log n)": 1,
    "O(n)": 2,
    "O(n log n)": 3,
    "O(n^2)": 4,
    "O(n^2 log n)": 5,
    "O(n^3)": 6,
    "O(2^n)": 7,
}


def fit_curve(ns: list[int | float], ys: list[float], family: str = "all", mode: str = "all") -> FitResult:
    """Fit data (ns, ys) against candidate models using regression and AIC/BIC."""
    if len(ns) < 2:
        return FitResult(
            model="O(1)",
            formula="y = c",
            r2=1.0,
            confidence=0.5,
            family=family,
            mode=mode,
            n_points=len(ns),
            points=list(zip(ns, ys)),
        )

    n_arr = np.array(ns, dtype=float)
    y_arr = np.array(ys, dtype=float)
    n_pts = len(n_arr)

    # Clean non-finite or non-positive
    valid = np.isfinite(n_arr) & np.isfinite(y_arr) & (n_arr > 0) & (y_arr >= 0)
    n_arr = n_arr[valid]
    y_arr = y_arr[valid]
    n_pts = len(n_arr)

    if n_pts < 2:
        return FitResult(
            model="O(1)", formula="y = c", r2=1.0, confidence=0.5,
            family=family, mode=mode, n_points=n_pts, points=list(zip(ns, ys)),
        )

    ss_tot = np.sum((y_arr - np.mean(y_arr)) ** 2)
    # Check if data is essentially constant
    if ss_tot < 1e-12 or (np.max(y_arr) - np.min(y_arr)) < 1e-9:
        return FitResult(
            model="O(1)",
            formula=f"y = {np.mean(y_arr):.6f}",
            r2=1.0,
            aic=0.0,
            bic=0.0,
            confidence=1.0,
            family=family,
            mode=mode,
            n_points=n_pts,
            points=list(zip(n_arr.tolist(), y_arr.tolist())),
        )

    # Optional: Log-log degree estimate
    # ln(y) = alpha * ln(n) + beta (for y > 0)
    pos_mask = (y_arr > 1e-9) & (n_arr > 1)
    log_alpha = 1.0
    if np.sum(pos_mask) >= 3:
        try:
            slope, _, r_val, _, _ = stats.linregress(np.log(n_arr[pos_mask]), np.log(y_arr[pos_mask]))
            if np.isfinite(slope) and r_val ** 2 > 0.8:
                log_alpha = max(0.0, slope)
        except Exception:
            pass

    best_result: FitResult | None = None
    best_bic = float("inf")

    for name, basis_fn in MODELS:
        try:
            basis = basis_fn(n_arr)
            if not np.all(np.isfinite(basis)):
                continue

            if name == "O(1)":
                # y = c
                c = np.mean(y_arr)
                pred = np.full_like(y_arr, c)
                k = 1
                formula = f"y = {c:.6e}"
            else:
                # Linear regression y = a * basis + b
                # We expect a > 0 for complexity scaling
                X = np.vstack([basis, np.ones_like(basis)]).T
                # Solve least squares
                coeffs, residuals, _, _ = np.linalg.lstsq(X, y_arr, rcond=None)
                a, b = coeffs[0], coeffs[1]
                if a <= 0:
                    # Negative scaling coefficient makes no physical sense for upper bound
                    continue
                pred = a * basis + b
                k = 2
                formula = f"y = {a:.4e} * {name[2:-1]} + {b:.4e}"

            ss_res = np.sum((y_arr - pred) ** 2)
            r2 = max(0.0, 1.0 - (ss_res / ss_tot)) if ss_tot > 0 else 1.0

            # Compute AIC and BIC
            mse = max(ss_res / n_pts, 1e-15)
            aic = n_pts * np.log(mse) + 2 * k
            bic = n_pts * np.log(mse) + k * np.log(n_pts)

            # Confidence based on r2 and point count
            confidence = min(1.0, max(0.0, r2 * (1.0 - 1.0 / (n_pts + 1))))

            # Model selection: prefer lower BIC, but require reasonable R^2
            if r2 >= 0.80 and bic < best_bic:
                best_bic = bic
                best_result = FitResult(
                    model=name,
                    formula=formula,
                    r2=round(float(r2), 4),
                    aic=round(float(aic), 2),
                    bic=round(float(bic), 2),
                    confidence=round(float(confidence), 3),
                    family=family,
                    mode=mode,
                    n_points=n_pts,
                    points=list(zip(n_arr.tolist(), y_arr.tolist())),
                )
        except Exception:
            continue

    if not best_result:
        # Fallback to closest model based on log-log degree
        if log_alpha < 0.3:
            chosen = "O(1)"
        elif log_alpha < 0.7:
            chosen = "O(log n)"
        elif log_alpha < 1.3:
            chosen = "O(n)"
        elif log_alpha < 1.7:
            chosen = "O(n log n)"
        elif log_alpha < 2.5:
            chosen = "O(n^2)"
        else:
            chosen = "O(n^3)"

        best_result = FitResult(
            model=chosen,
            formula=f"degree ~ {log_alpha:.2f}",
            r2=0.85,
            confidence=0.7,
            family=family,
            mode=mode,
            n_points=n_pts,
            points=list(zip(n_arr.tolist(), y_arr.tolist())),
        )

    return best_result


def fit_scaling_data(scaling_points: list) -> tuple[FitResult, list[FitResult]]:
    """Group scaling points by (family, mode), fit each, and return the worst-case dominating fit."""
    by_group: dict[tuple[str, str], list[tuple[int, float]]] = {}
    for p in scaling_points:
        if getattr(p, "status", None) == "ok" and getattr(p, "orig_time_s", None) is not None:
            fam = getattr(p, "family", "default")
            mode = getattr(p, "mode", "default")
            n = getattr(p, "n", 0)
            t = getattr(p, "orig_time_s", 0.0)
            if n > 0 and t > 0:
                by_group.setdefault((fam, mode), []).append((n, t))

    all_fits: list[FitResult] = []
    for (fam, mode), pts in by_group.items():
        if len(pts) >= 2:
            pts.sort(key=lambda x: x[0])
            ns = [x[0] for x in pts]
            ys = [x[1] for x in pts]
            fit = fit_curve(ns, ys, family=fam, mode=mode)
            all_fits.append(fit)

    if not all_fits:
        # If no points grouped, fit everything together
        all_pts = []
        for p in scaling_points:
            if getattr(p, "status", None) == "ok" and getattr(p, "orig_time_s", None) is not None:
                n = getattr(p, "n", 0)
                t = getattr(p, "orig_time_s", 0.0)
                if n > 0 and t > 0:
                    all_pts.append((n, t))
        if len(all_pts) >= 2:
            all_pts.sort(key=lambda x: x[0])
            dominant = fit_curve([x[0] for x in all_pts], [x[1] for x in all_pts])
            return dominant, [dominant]
        return FitResult(model="O(1)", confidence=0.0), []

    # Worst-case family dominates: highest complexity rank, break ties with r2
    dominant = max(all_fits, key=lambda f: (COMPLEXITY_RANK.get(f.model, 0), f.r2))
    return dominant, all_fits

