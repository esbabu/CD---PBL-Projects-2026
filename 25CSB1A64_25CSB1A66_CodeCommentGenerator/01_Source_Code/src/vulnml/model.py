"""
ML detector model: TF-IDF + logistic regression per language
==============================================================
Input: a function's normalised tokens (``dataset.normalise``). Output: a probability
per family plus ``safe``. The models in ``outputs/vulnml/`` are trained by
``src.vulnml.pipeline`` on the security dataset (hyperparameters chosen per language
on the validation split). ``train_language`` below is the earlier Juliet-only trainer,
kept as a library function; the CLI no longer calls it.

A linear model was chosen on purpose: it trains in seconds on a CPU, needs no
GPU or download, and every prediction can be explained by the tokens with the
largest contribution — the neuro-symbolic engine shows them as evidence.

    python -m src.vulnml.pipeline train   # all languages → outputs/vulnml/<lang>.joblib + config + metrics
"""
from __future__ import annotations

import json
import os
import time
from collections import Counter
from typing import Dict, List, Optional, Tuple

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODEL_DIR = os.environ.get("CCG_VULNML_DIR", os.path.join(ROOT, "outputs", "vulnml"))
LANGS = ("java", "c", "cpp", "csharp", "python")


def _pipeline():
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    return Pipeline([
        ("tfidf", TfidfVectorizer(token_pattern=r"\S+", ngram_range=(1, 2), min_df=2, max_features=30000,
                                  sublinear_tf=True, lowercase=False)),
        ("clf", LogisticRegression(max_iter=3000, C=16.0)),
    ])


def _metrics(y_true: List[str], y_pred: List[str]) -> dict:
    from sklearn.metrics import accuracy_score, classification_report, f1_score, precision_recall_fscore_support
    vt = [y != "safe" for y in y_true]
    vp = [y != "safe" for y in y_pred]
    p, r, f, _ = precision_recall_fscore_support(vt, vp, average="binary", zero_division=0)
    labels = sorted(set(y_true) | set(y_pred))
    rep = classification_report(y_true, y_pred, labels=labels, zero_division=0, output_dict=True)
    return {"n": len(y_true),
            "binary": {"precision": round(p, 3), "recall": round(r, 3), "f1": round(f, 3)},
            "family_accuracy": round(accuracy_score(y_true, y_pred), 3),
            "family_macro_f1": round(f1_score(y_true, y_pred, average="macro", zero_division=0), 3),
            "per_family": {k: {"precision": round(v["precision"], 3), "recall": round(v["recall"], 3),
                               "f1": round(v["f1-score"], 3), "support": int(v["support"])}
                           for k, v in rep.items() if k in labels}}


def train_language(lang: str, per_cwe: int = 150) -> dict:
    """Train, evaluate on the held-out split, then refit on all data and save."""
    import joblib

    from .dataset import juliet_samples, owasp_samples, split
    t0 = time.time()
    if lang == "python":
        pairs = owasp_samples()
        train = [s for s, sp in pairs if sp == "dev"]
        test = [s for s, sp in pairs if sp == "heldout"]
        data_name = "OWASP BenchmarkPython (dev → held-out template families)"
    else:
        samples = juliet_samples(lang, per_cwe=per_cwe)
        train, test = split(samples)
        data_name = f"NIST SARD Juliet 1.3 ({lang}); split by functional variant, 20 % held out"
    pipe = _pipeline()
    pipe.fit([s.text for s in train], [s.label for s in train])
    pred = list(pipe.predict([s.text for s in test]))
    m = _metrics([s.label for s in test], pred)
    # refit on everything for the shipped model
    final = _pipeline()
    final.fit([s.text for s in train + test], [s.label for s in train + test])
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump({"pipeline": final, "language": lang, "classes": list(final.classes_)},
                os.path.join(MODEL_DIR, f"{lang}.joblib"), compress=3)
    out = {"language": lang, "data": data_name, "train_functions": len(train), "test_functions": len(test),
           "train_labels": dict(Counter(s.label for s in train).most_common()), "metrics_heldout": m,
           "seconds": round(time.time() - t0, 1)}
    with open(os.path.join(MODEL_DIR, f"{lang}_metrics.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    return out


_CACHE: Dict[str, object] = {}


def load(lang: str):
    """The saved model for ``lang`` (C models serve C++ files too when no C++ model exists), or None."""
    import joblib
    key = lang
    if key not in _CACHE:
        path = os.path.join(MODEL_DIR, f"{lang}.joblib")
        if not os.path.isfile(path) and lang == "cpp":
            path = os.path.join(MODEL_DIR, "c.joblib")
        _CACHE[key] = joblib.load(path) if os.path.isfile(path) else None
    return _CACHE[key]


def explain(model, text: str, label: str, k: int = 6, x=None) -> List[Tuple[str, float]]:
    """Tokens with the largest positive contribution to ``label`` for this input.

    ``x`` is the input's TF-IDF row when the caller has already transformed it.
    """
    pipe = model["pipeline"]
    vec, clf = pipe.named_steps["tfidf"], pipe.named_steps["clf"]
    if x is None:
        x = vec.transform([text])
    classes = list(clf.classes_)
    if label not in classes:
        return []
    row = clf.coef_[classes.index(label)] if clf.coef_.shape[0] > 1 else clf.coef_[0]
    names = model.get("_feature_names")
    if names is None:                       # building the 40,000 names is costly: once per model
        names = model["_feature_names"] = vec.get_feature_names_out()
    contrib = [(names[j], float(x[0, j] * row[j])) for j in x.nonzero()[1]]
    return sorted([c for c in contrib if c[1] > 0], key=lambda c: -c[1])[:k]
