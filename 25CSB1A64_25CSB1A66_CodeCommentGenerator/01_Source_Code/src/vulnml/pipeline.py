"""
Reproducible ML training, validation and testing — and independent evaluation of all three engines
=================================================================================================
    python -m src.vulnml.pipeline train      [--dataset datasets/security_dataset/v1]
    python -m src.vulnml.pipeline evaluate   [--limit-per-language N]
    python -m src.vulnml.pipeline all

train
  For every language: function-level samples of the dataset (Juliet functions, OWASP handlers,
  custom templates and their variants, coverage snippets) → normalised tokens (``dataset.normalise``)
  → TF-IDF + logistic regression. Hyperparameters are chosen on the **validation** split (grid over
  C and n-gram range, scored by vulnerable-vs-safe F1); the chosen model is refit on train + val and
  scored once on **test**. Splits come from the dataset (70/15/15 by group), so related samples never
  cross splits. Artifacts: ``outputs/vulnml/<lang>.joblib``, ``<lang>_config.json``,
  ``<lang>_metrics.json``.

evaluate
  Scores the **rule-based**, **ML** and **neuro-symbolic** engines independently on the same held-out
  test samples:
    * function-level: every test function / small program (vulnerable vs safe) and every function of
      the test long programs (vulnerable when it holds a planted vulnerability);
    * location-level (long programs): exact (rule, line) matches for the rule-based and neuro-symbolic
      engines (the ML engine predicts per function and has no line output).
  Metrics: accuracy, precision, recall, F1, false-positive rate, false-negative rate, binary confusion
  matrix — overall, per language, per source and per vulnerability family — plus per-sample latency.
  Output: ``outputs/eval/model_comparison.json``.
"""
from __future__ import annotations

import argparse
import ast
import gzip
import json
import os
import re
import statistics
import sys
import time
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATASET = os.path.join(ROOT, "datasets", "security_dataset", "v1")
MODEL_DIR = os.path.join(ROOT, "outputs", "vulnml")
EVAL_DIR = os.path.join(ROOT, "outputs", "eval")
LANGS = ("python", "java", "csharp", "c", "cpp", "rust", "cobol")
GRID = [{"C": c, "ngram": ng} for c in (1.0, 4.0, 16.0) for ng in ((1, 1), (1, 2))]
SEED = 7


def load_samples(dataset: str = DATASET) -> List[dict]:
    with gzip.open(os.path.join(dataset, "samples.jsonl.gz"), "rt", encoding="utf-8") as fh:
        return [json.loads(l) for l in fh]


def _owasp_handler(code: str) -> str:
    body = code.split("_post():", 1)[-1].split("@app.route", 1)[0]
    return re.sub(r"BenchmarkTest\d+", "T", body)


def ml_items(samples: List[dict]) -> List[dict]:
    """Function-level ML items: (language, split, text, label, family, source, group)."""
    from .dataset import normalise
    items = []
    for s in samples:
        if s["source"] == "custom-long":
            continue
        if s["source"] == "owasp":
            code = _owasp_handler(s["code"])
        else:
            code = s.get("function_code") or s.get("code") or ""
        label = s["family"] if s["label"] == "vulnerable" and s.get("family") else ("safe" if s["label"] == "safe" else None)
        if label is None:
            continue
        items.append({"language": s["language"], "split": s["split"], "text": normalise(code, s["language"]),
                      "label": label, "source": s["source"], "group": s["group"], "id": s["id"]})
    return items


def _pipe(C: float, ngram):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    return Pipeline([("tfidf", TfidfVectorizer(token_pattern=r"\S+", ngram_range=tuple(ngram), min_df=1,
                                               max_features=40000, sublinear_tf=True, lowercase=False)),
                     ("clf", LogisticRegression(max_iter=3000, C=C, random_state=SEED))])


def binary_metrics(y_true: List[bool], y_pred: List[bool]) -> dict:
    tp = sum(t and p for t, p in zip(y_true, y_pred))
    tn = sum((not t) and (not p) for t, p in zip(y_true, y_pred))
    fp = sum((not t) and p for t, p in zip(y_true, y_pred))
    fn = sum(t and (not p) for t, p in zip(y_true, y_pred))
    n = len(y_true)
    prec = tp / (tp + fp) if tp + fp else None
    rec = tp / (tp + fn) if tp + fn else None
    f1 = 2 * prec * rec / (prec + rec) if prec and rec else (0.0 if prec is not None and rec is not None else None)
    r = lambda x: round(x, 4) if x is not None else None
    return {"n": n, "positives": tp + fn, "negatives": tn + fp, "accuracy": r((tp + tn) / n) if n else None,
            "precision": r(prec), "recall": r(rec), "f1": r(f1),
            "fpr": r(fp / (fp + tn)) if fp + tn else None, "fnr": r(fn / (fn + tp)) if fn + tp else None,
            "confusion": {"tn": tn, "fp": fp, "fn": fn, "tp": tp}}


# ---------------------------------------------------------------------------
# training
# ---------------------------------------------------------------------------

def train(dataset: str = DATASET) -> dict:
    import joblib
    from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
    samples = load_samples(dataset)
    items = ml_items(samples)
    report = {}
    os.makedirs(MODEL_DIR, exist_ok=True)
    for lang in LANGS:
        rows = [i for i in items if i["language"] == lang]
        tr = [i for i in rows if i["split"] == "train"]
        va = [i for i in rows if i["split"] == "val"]
        te = [i for i in rows if i["split"] == "test"]
        if len({i["label"] for i in tr}) < 2 or not va or not te:
            report[lang] = {"skipped": "not enough labelled data in every split",
                            "counts": {"train": len(tr), "val": len(va), "test": len(te)}}
            continue
        t0 = time.time()
        tuning = []
        for params in GRID:
            p = _pipe(params["C"], params["ngram"])
            p.fit([i["text"] for i in tr], [i["label"] for i in tr])
            pred = p.predict([i["text"] for i in va])
            m = binary_metrics([i["label"] != "safe" for i in va], [y != "safe" for y in pred])
            tuning.append({**params, "ngram": list(params["ngram"]), "val_f1": m["f1"], "val_accuracy": m["accuracy"]})
        best = max(tuning, key=lambda t: (t["val_f1"] or 0, t["val_accuracy"] or 0, -t["C"]))
        final = _pipe(best["C"], best["ngram"])
        final.fit([i["text"] for i in tr + va], [i["label"] for i in tr + va])
        train_s = time.time() - t0
        t1 = time.perf_counter()
        pred = list(final.predict([i["text"] for i in te]))
        infer_ms = (time.perf_counter() - t1) * 1000 / max(1, len(te))
        y_true = [i["label"] for i in te]
        bm = binary_metrics([y != "safe" for y in y_true], [y != "safe" for y in pred])
        labels = sorted(set(y_true) | set(pred))
        fam = {"accuracy": round(accuracy_score(y_true, pred), 4),
               "macro_f1": round(f1_score(y_true, pred, average="macro", zero_division=0), 4),
               "labels": labels, "confusion": confusion_matrix(y_true, pred, labels=labels).tolist()}
        per_source = {src: binary_metrics([i["label"] != "safe" for i in te if i["source"] == src],
                                          [p != "safe" for i, p in zip(te, pred) if i["source"] == src])
                      for src in sorted({i["source"] for i in te})}
        joblib.dump({"pipeline": final, "language": lang, "classes": list(final.classes_)},
                    os.path.join(MODEL_DIR, f"{lang}.joblib"), compress=3)
        config = {"language": lang, "dataset": os.path.relpath(dataset, ROOT).replace("\\", "/"), "seed": SEED,
                  "features": "TF-IDF over normalised tokens (comments removed, strings STR, numbers NUM, "
                              "label-leaking identifiers and access modifiers masked), max 40,000 features",
                  "model": "LogisticRegression (lbfgs, max_iter 3000)", "grid": [{**g, "ngram": list(g["ngram"])}
                                                                                  for g in GRID],
                  "selection": "best vulnerable-vs-safe F1 on the validation split", "chosen": best,
                  "refit_on": "train + validation", "counts": {"train": len(tr), "val": len(va), "test": len(te)},
                  "train_labels": dict(Counter(i["label"] for i in tr)),
                  "small_n": len(tr) < 200,
                  "used_by_neurosymbolic_engine": len(tr) >= 200}
        metrics = {"language": lang, "test_binary": bm, "test_family": fam, "test_by_source": per_source,
                   "tuning": tuning, "train_seconds": round(train_s, 1), "inference_ms_per_function": round(infer_ms, 3)}
        json.dump(config, open(os.path.join(MODEL_DIR, f"{lang}_config.json"), "w"), indent=1)
        json.dump(metrics, open(os.path.join(MODEL_DIR, f"{lang}_metrics.json"), "w"), indent=1)
        report[lang] = {"chosen": best, "test_binary": bm, "family_accuracy": fam["accuracy"], "counts": config["counts"]}
        print(f"{lang}: train {len(tr)} / val {len(va)} / test {len(te)}; chosen C={best['C']} ngram={best['ngram']}; "
              f"test F1 {bm['f1']} (P {bm['precision']} R {bm['recall']} FPR {bm['fpr']}), family acc {fam['accuracy']}")
    from . import model as _m
    _m._CACHE.clear()
    json.dump(report, open(os.path.join(MODEL_DIR, "training_report.json"), "w"), indent=1)
    return report


# ---------------------------------------------------------------------------
# evaluation of the three engines on the same held-out samples
# ---------------------------------------------------------------------------

def _wrap_function(code: str, lang: str) -> str:
    if lang == "java":
        return "class EvalWrapper {\n" + code + "\n}\n"
    if lang == "csharp":
        return "class EvalWrapper {\n" + code + "\n}\n"
    return code


def _analyze(code: str, path: str, lang: str, engines: str):
    if lang == "python":
        from ..security.analyzer import analyze_source as py
        rep = py(code, path)
        if engines == "neurosymbolic":
            from .fusion import fuse_python
            rep.findings = fuse_python(rep.findings, code, path)
        return rep
    from ..multilang.analyzer import analyze_source as ml
    return ml(code, path, lang, engines=engines)


def _function_spans(code: str, lang: str) -> List[Tuple[str, int, int, str]]:
    """(name, start line, end line, function code) of every function in a file."""
    lines = code.splitlines()
    if lang == "python":
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return []
        return [(n.name, n.lineno, n.end_lineno, "\n".join(lines[n.lineno - 1:n.end_lineno]))
                for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    if lang == "cobol":
        from ..multilang.cobol import tokenize
        toks = tokenize(code)
        proc_line = next((x.line for x in toks if x.up == "PROCEDURE"), 0)
        heads = [(t.up, t.line) for k, t in enumerate(toks) if k + 1 < len(toks) and toks[k + 1].text == "."
                 and t.col <= 11 and (k == 0 or toks[k - 1].text == ".") and t.up not in ("GOBACK", "EXIT")
                 and t.line > proc_line]
        out = []
        for (name, ln), nxt in zip(heads, heads[1:] + [("", len(lines) + 1)]):
            out.append((name, ln, nxt[1] - 1, "\n".join(lines[ln - 1:nxt[1] - 1])))
        return out
    from ..multilang.lower import lower_source
    mod = lower_source(code, lang)
    return [(i.fn.name, i.fn.source_lineno, i.fn.end_lineno, "\n".join(lines[i.fn.source_lineno - 1:i.fn.end_lineno]))
            for i in mod.functions.values()]


def _ml_predict(texts: List[str], lang: str) -> List[float]:
    from . import model as mlmodel
    from .dataset import normalise
    m = mlmodel.load(lang)
    if m is None or not texts:
        return [None] * len(texts)
    pipe = m["pipeline"]
    classes = list(pipe.classes_)
    si = classes.index("safe") if "safe" in classes else None
    probs = pipe.predict_proba([normalise(t, lang) for t in texts])
    return [1.0 - float(r[si]) if si is not None else 1.0 for r in probs]


def evaluate(dataset: str = DATASET, limit_per_language: Optional[int] = None) -> dict:
    from .families import family_of_rule
    samples = [s for s in load_samples(dataset) if s["split"] == "test"]
    by_lang = defaultdict(list)
    for s in samples:
        by_lang[s["language"]].append(s)
    rows: List[dict] = []                    # one row per evaluated function-level unit
    loc_rows: List[dict] = []                # long-program location-level results
    latency: Dict[str, List[float]] = defaultdict(list)
    for lang in LANGS:
        units = by_lang.get(lang, [])
        short = [s for s in units if s["source"] != "custom-long"]
        longs = [s for s in units if s["source"] == "custom-long"]
        if limit_per_language:
            short = short[:limit_per_language]
        # ── function samples and small programs ──
        for s in short:
            if s["source"] == "juliet":
                code = _wrap_function(s["code"], lang)
                fn_range = None
            else:
                code = s["code"]
                fn_range = None
                if s["source"] == "owasp":
                    spans = [x for x in _function_spans(code, "python") if x[0].endswith("_post")]
                    fn_range = (spans[0][1], spans[0][2]) if spans else None
            path = s.get("path") or f"eval_{s['id']}{'.py' if lang == 'python' else ''}"
            truth = s["label"] == "vulnerable"
            row = {"language": lang, "source": s["source"], "id": s["id"], "truth": truth,
                   "family": s.get("family")}
            for engine in ("rules", "neurosymbolic"):
                t0 = time.perf_counter()
                rep = _analyze(code, path, lang, engine)
                latency[f"{engine}:{lang}"].append((time.perf_counter() - t0) * 1000)
                act = [f for f in rep.active() if fn_range is None or fn_range[0] <= f.line <= fn_range[1]]
                row[engine] = bool(act)
                row[engine + "_family_hit"] = bool(s.get("family")) and any(
                    family_of_rule(f.rule_id) == s.get("family") for f in act)
            text = _owasp_handler(code) if s["source"] == "owasp" else (s.get("function_code") or s["code"])
            t0 = time.perf_counter()
            p = _ml_predict([text], lang)[0]
            latency[f"ml:{lang}"].append((time.perf_counter() - t0) * 1000)
            row["ml"] = (p >= 0.5) if p is not None else None
            row["ml_p"] = p
            rows.append(row)
            if len(rows) % 250 == 0:
                print(f"  {lang}: {len(rows)} units", flush=True)
        # ── long programs: functions and exact locations ──
        for s in longs:
            code = open(os.path.join(ROOT, s["path"]), encoding="utf-8").read()
            truth_locs = {(l["rule"], l["line"]) for l in s["locations"]}
            spans = _function_spans(code, lang)
            res = {}
            for engine in ("rules", "neurosymbolic"):
                t0 = time.perf_counter()
                rep = _analyze(code, s["path"], lang, engine)
                latency[f"{engine}_long:{lang}"].append((time.perf_counter() - t0) * 1000)
                res[engine] = rep.active()
                got = {(f.rule_id, f.line) for f in rep.active()}
                loc_rows.append({"language": lang, "engine": engine, "program": s["path"], "lines": s["lines"],
                                 "tp": len(got & truth_locs), "fp": len(got - truth_locs), "fn": len(truth_locs - got)})
            t0 = time.perf_counter()
            probs = _ml_predict([sp[3] for sp in spans], lang)
            latency[f"ml_long:{lang}"].append((time.perf_counter() - t0) * 1000)
            for (name, a, b, _), p in zip(spans, probs):
                truth = any(a <= ln <= b for _, ln in truth_locs)
                row = {"language": lang, "source": "custom-long", "id": f"{s['id']}:{name}", "truth": truth,
                       "family": None, "ml": (p >= 0.5) if p is not None else None, "ml_p": p}
                for engine in ("rules", "neurosymbolic"):
                    row[engine] = any(a <= f.line <= b for f in res[engine])
                rows.append(row)
        print(f"{lang}: {len(short)} samples, {len(longs)} long programs evaluated")

    def metrics_for(sel, engine):
        sel = [r for r in sel if r.get(engine) is not None]
        return binary_metrics([r["truth"] for r in sel], [r[engine] for r in sel])

    engines = ("rules", "ml", "neurosymbolic")
    out = {"dataset": os.path.relpath(dataset, ROOT).replace("\\", "/"), "split": "test",
           "unit": "function (or one-function program); long programs contribute every function",
           "decision": {"rules": "any active finding in the function", "ml": "P(vulnerable) >= 0.5",
                        "neurosymbolic": "any active finding after fusion (rule findings, agreements, SEC064)"},
           "overall": {e: metrics_for(rows, e) for e in engines},
           "by_language": {l: {e: metrics_for([r for r in rows if r["language"] == l], e) for e in engines}
                           for l in LANGS if any(r["language"] == l for r in rows)},
           "by_source": {src: {e: metrics_for([r for r in rows if r["source"] == src], e) for e in engines}
                         for src in sorted({r["source"] for r in rows})},
           "by_family_recall": {}, "locations_long_programs": {}, "latency_ms": {}}
    fams = sorted({r["family"] for r in rows if r.get("family")})
    for fam in fams:
        sel = [r for r in rows if r.get("family") == fam and r["truth"]]
        out["by_family_recall"][fam] = {"n": len(sel), **{e: round(sum(bool(r.get(e)) for r in sel) / len(sel), 4)
                                                          for e in engines if sel}}
    out["juliet_in_rule_scope"] = in_scope_recall(rows)
    for engine in ("rules", "neurosymbolic"):
        for l in LANGS:
            sel = [r for r in loc_rows if r["engine"] == engine and r["language"] == l]
            if not sel:
                continue
            tp, fp, fn = (sum(r[k] for r in sel) for k in ("tp", "fp", "fn"))
            P = tp / (tp + fp) if tp + fp else None
            R = tp / (tp + fn) if tp + fn else None
            out["locations_long_programs"].setdefault(engine, {})[l] = {
                "programs": len(sel), "lines": sum(r["lines"] for r in sel), "tp": tp, "fp": fp, "fn": fn,
                "precision": round(P, 4) if P is not None else None, "recall": round(R, 4) if R is not None else None,
                "f1": round(2 * P * R / (P + R), 4) if P and R else None}
    for k, v in latency.items():
        out["latency_ms"][k] = {"n": len(v), "mean": round(statistics.fmean(v), 3), "median": round(statistics.median(v), 3),
                                "p95": round(sorted(v)[max(0, int(round(0.95 * len(v))) - 1)], 3), "total": round(sum(v), 1)}
    os.makedirs(EVAL_DIR, exist_ok=True)
    json.dump(out, open(os.path.join(EVAL_DIR, "model_comparison.json"), "w"), indent=1)
    json.dump(rows, open(os.path.join(EVAL_DIR, "model_comparison_rows.json"), "w"))
    return out


def rule_families() -> Dict[str, set]:
    """language -> vulnerability families that at least one implemented rule covers."""
    from ..security.coverage import rule_languages
    from .families import family_of_rule
    out: Dict[str, set] = defaultdict(set)
    for rule, langs in rule_languages().items():
        fam = family_of_rule(rule)
        if fam:
            for l in langs:
                out[l].add(fam)
    return out


def in_scope_recall(rows: List[dict]) -> dict:
    """Recall on Juliet vulnerable functions whose family has a rule in that language (and outside it)."""
    fams = rule_families()
    res = {}
    for l in ("java", "csharp", "c", "cpp"):
        vul = [r for r in rows if r["language"] == l and r["source"] == "juliet" and r["truth"]]
        ins = [r for r in vul if r.get("family") in fams[l]]
        outs = [r for r in vul if r.get("family") not in fams[l]]
        res[l] = {"in_scope_n": len(ins), "out_of_scope_n": len(outs)}
        for e in ("rules", "ml", "neurosymbolic"):
            res[l][f"{e}_recall_in_scope"] = round(sum(bool(r.get(e)) for r in ins) / len(ins), 4) if ins else None
            res[l][f"{e}_recall_out_of_scope"] = round(sum(bool(r.get(e)) for r in outs) / len(outs), 4) if outs else None
    return res


def main(argv=None) -> int:
    from ..config import configure_stdio
    configure_stdio()
    ap = argparse.ArgumentParser(prog="python -m src.vulnml.pipeline")
    ap.add_argument("cmd", choices=["train", "evaluate", "all"])
    ap.add_argument("--dataset", default=DATASET)
    ap.add_argument("--limit-per-language", type=int, default=None)
    args = ap.parse_args(argv)
    if args.cmd in ("train", "all"):
        train(args.dataset)
    if args.cmd in ("evaluate", "all"):
        out = evaluate(args.dataset, args.limit_per_language)
        for e, m in out["overall"].items():
            print(f"{e:>14}: n {m['n']}  acc {m['accuracy']}  P {m['precision']}  R {m['recall']}  F1 {m['f1']}  "
                  f"FPR {m['fpr']}  FNR {m['fnr']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
