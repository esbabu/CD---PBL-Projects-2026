"""
Retrieval evaluation
=====================
Does free-text retrieval find knowledge about the *right* vulnerability when it
is given only the vulnerable code?

Data: OWASP BenchmarkPython (``.benchmarks/BenchmarkPython``), the test cases
labelled as real vulnerabilities. Ground truth is OWASP's own category label,
mapped to rules (sqli → SEC005, xpathi → SEC020, ...); the analyzer is not run.
Query: the request-handling function of the test case, with the benchmark's
own names (``BenchmarkTest00042``) removed. A hit at rank k means one of the top
k retrieved rule cards / examples belongs to a correct rule.

    python -m src.rag evaluate [--out outputs/benchmarks/final/rag_retrieval_eval.json]
"""
from __future__ import annotations

import json
import os
import re
from collections import defaultdict
from typing import Dict, List, Tuple

from .knowledge import KnowledgeBase

CATEGORY_RULES: Dict[str, Tuple[str, ...]] = {
    "cmdi": ("SEC002",), "codeinj": ("SEC001",), "deserialization": ("SEC009", "SEC010"),
    "hash": ("SEC004",), "pathtraver": ("SEC013",), "sqli": ("SEC005",), "weakrand": ("SEC011",),
    "xss": ("SEC014",), "redirect": ("SEC017",), "xxe": ("SEC018",), "ldapi": ("SEC019",),
    "xpathi": ("SEC020",), "trustbound": ("SEC028",), "securecookie": ("SEC044",),
}


def _cases(owasp_dir: str) -> List[dict]:
    rows = []
    with open(os.path.join(owasp_dir, "expectedresults-0.1.csv"), encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            test, cat, real, *_ = line.strip().split(",")
            if real == "true" and cat in CATEGORY_RULES:
                rows.append({"test": test, "category": cat})
    return rows


def _query(path: str) -> str:
    src = open(path, encoding="utf-8").read()
    body = src.split("_post():", 1)[-1].split("@app.route", 1)[0]
    return re.sub(r"BenchmarkTest\d+", "", body)


def evaluate(owasp_dir: str, ks=(1, 3, 5)) -> dict:
    kb = KnowledgeBase.load(include_memory=False)
    per_cat = defaultdict(lambda: {"n": 0, **{f"hit@{k}": 0 for k in ks}, "rr": 0.0})
    for case in _cases(owasp_dir):
        path = os.path.join(owasp_dir, "testcode", f"{case['test']}.py")
        if not os.path.isfile(path):
            continue
        wanted = set(CATEGORY_RULES[case["category"]])
        ranked = []                       # distinct rules in rank order
        for d, _ in kb.search(_query(path), k=60):
            if d.rule_id not in ranked:
                ranked.append(d.rule_id)
        c = per_cat[case["category"]]
        c["n"] += 1
        rank = next((i + 1 for i, r in enumerate(ranked) if r in wanted), None)
        for k in ks:
            c[f"hit@{k}"] += int(rank is not None and rank <= k)
        c["rr"] += 1.0 / rank if rank else 0.0
    total = {"n": sum(c["n"] for c in per_cat.values())}
    for k in ks:
        total[f"recall@{k}"] = round(sum(c[f"hit@{k}"] for c in per_cat.values()) / total["n"], 3)
    total["mrr"] = round(sum(c["rr"] for c in per_cat.values()) / total["n"], 3)
    cats = {cat: {"n": c["n"], **{f"recall@{k}": round(c[f"hit@{k}"] / c["n"], 3) for k in ks},
                  "mrr": round(c["rr"] / c["n"], 3)} for cat, c in sorted(per_cat.items())}
    macro = {f"recall@{k}": round(sum(v[f"recall@{k}"] for v in cats.values()) / len(cats), 3) for k in ks}
    return {"dataset": "OWASP BenchmarkPython (true-vulnerability cases)",
            "ground_truth": "OWASP category label mapped to rules; the analyzer is not used",
            "query": "request-handling function of each test case (benchmark names removed)",
            "documents": len(kb.documents), "rules_in_index": len({d.rule_id for d in kb.documents}),
            "chance_recall@1": round(1 / len({d.rule_id for d in kb.documents}), 3),
            "micro": total, "macro": macro, "per_category": cats}
