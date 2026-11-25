"""
ML detector: per-function predictions for a file
==================================================
For every function the saved model (``model.load``) gives the most likely
family, P(vulnerable) = 1 − P(safe), and the tokens that drove the prediction.
Functions are cut from the source with the same front ends the compiler uses
(tree-sitter / the COBOL parser for other languages, ``ast`` for Python).
"""
from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from . import model as mlmodel
from .dataset import normalise


@dataclass
class MLPrediction:
    function: str
    line: int
    end_line: int
    family: str                      # most likely non-safe family
    p_vulnerable: float              # 1 - P(safe)
    p_family: float                  # P(family)
    evidence: List[Tuple[str, float]] = field(default_factory=list)


def _predict(m, items: List[Tuple[str, int, int, str]], lang: str) -> List[MLPrediction]:
    if m is None or not items:
        return []
    pipe = m["pipeline"]
    texts = [normalise(code, lang) for _, _, _, code in items]
    X = pipe.named_steps["tfidf"].transform(texts)          # transformed once, reused by explain()
    probs = pipe.named_steps["clf"].predict_proba(X)
    classes = list(pipe.classes_)
    safe_i = classes.index("safe") if "safe" in classes else None
    out = []
    for k, ((name, a, b, _), text, row) in enumerate(zip(items, texts, probs)):
        p_safe = row[safe_i] if safe_i is not None else 0.0
        best = max((i for i in range(len(classes)) if i != safe_i), key=lambda i: row[i])
        fam = classes[best]
        out.append(MLPrediction(name, a, b, fam, round(1.0 - float(p_safe), 3), round(float(row[best]), 3),
                                mlmodel.explain(m, text, fam, x=X[k])))
    return out


SMALL_N = ("rust", "cobol")


def predict_lowered(mod, lang: str) -> List[MLPrediction]:
    """Predictions for every function of a lowered (multi-language) module.

    Languages in ``SMALL_N`` (Rust, COBOL) have models trained on a few dozen custom samples only;
    they are evaluated and reported, but not used by the neuro-symbolic engine.
    """
    if lang in SMALL_N:
        return []
    m = mlmodel.load(lang)
    if m is None:
        return []
    from ..multilang.lower import text
    src = mod.source.encode("utf-8")
    items = []
    for q, info in mod.functions.items():
        if info.node is None:
            continue
        items.append((q, info.fn.source_lineno, info.fn.end_lineno, text(info.node, src)))
    return _predict(m, items, lang)


def predict_python(source: str) -> List[MLPrediction]:
    m = mlmodel.load("python")
    if m is None:
        return []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    lines = source.splitlines()
    items = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            code = "\n".join(lines[node.lineno - 1:node.end_lineno])
            items.append((node.name, node.lineno, node.end_lineno, code))
    return _predict(m, items, "python")
