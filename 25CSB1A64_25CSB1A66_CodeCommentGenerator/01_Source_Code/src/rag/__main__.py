"""
RAG command line
=================
    python -m src.rag query "user input in an ldap search filter" [-k 5]
    python -m src.rag explain <file.py> [-k 3]      # findings + retrieved guidance
    python -m src.rag stats                          # what the knowledge base holds
    python -m src.rag evaluate [--out FILE]          # retrieval accuracy on OWASP labels
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from ..config import configure_stdio
from .guidance import guidance_for, retrieve
from .knowledge import KnowledgeBase
from .memory import memory_path

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))


def main(argv=None) -> int:
    configure_stdio()
    ap = argparse.ArgumentParser(prog="python -m src.rag", description="Retrieval-augmented security guidance")
    sub = ap.add_subparsers(dest="cmd", required=True)
    q = sub.add_parser("query", help="free-text search of the knowledge base")
    q.add_argument("text")
    q.add_argument("-k", type=int, default=5)
    e = sub.add_parser("explain", help="analyse a file and show guidance for each finding")
    e.add_argument("file")
    e.add_argument("-k", type=int, default=3)
    sub.add_parser("stats", help="documents in the knowledge base")
    ev = sub.add_parser("evaluate", help="retrieval accuracy on OWASP BenchmarkPython labels")
    ev.add_argument("--owasp", default=os.path.join(ROOT, ".benchmarks", "BenchmarkPython"))
    ev.add_argument("--out", default=None, help="write the result as JSON")
    args = ap.parse_args(argv)

    if args.cmd == "query":
        for i, p in enumerate(retrieve(args.text, k=args.k), 1):
            print(f"{i}. [{p.kind}] {p.rule_id} {p.title}  (score {p.score})\n   source: {p.source}")
        return 0
    if args.cmd == "stats":
        kb = KnowledgeBase.load()
        kinds = {}
        for d in kb.documents:
            kinds[d.kind] = kinds.get(d.kind, 0) + 1
        print(f"{len(kb.documents)} documents: " + ", ".join(f"{n} {k}" for k, n in sorted(kinds.items())))
        from .knowledge import security_kb
        meta = security_kb().get("meta", {})
        if meta:
            print("security knowledge base: " + json.dumps(meta.get("counts", {})))
        print(f"rules covered: {len({d.rule_id for d in kb.documents})}; fix memory: {memory_path()}")
        return 0
    if args.cmd == "explain":
        from ..security.analyzer import analyze_file
        from ..multilang.analyzer import _language_of
        from .guidance import explain_finding, format_explanation
        rep = analyze_file(args.file)
        if rep.parse_error:
            print(f"error: {rep.parse_error}", file=sys.stderr)
            return 2
        source = open(args.file, encoding="utf-8").read()
        findings = rep.active()
        print(f"{args.file}: {len(findings)} active finding(s)\n")
        language = _language_of(args.file, source, None)
        for f in findings:
            print(format_explanation(explain_finding(f, source, language)))
            print()
        return 0
    if args.cmd == "evaluate":
        from .evaluate import evaluate
        if not os.path.isdir(args.owasp):
            print(f"OWASP data missing at {args.owasp}: run python benchmarks/fetch.py", file=sys.stderr)
            return 2
        res = evaluate(args.owasp)
        m = res["micro"]
        print(f"{m['n']} labelled cases, {res['documents']} documents ({res['rules_in_index']} rules); "
              f"chance recall@1 = {res['chance_recall@1']}")
        print(f"micro: recall@1 {m['recall@1']}  recall@3 {m['recall@3']}  recall@5 {m['recall@5']}  MRR {m['mrr']}")
        print("macro: " + "  ".join(f"{k} {v}" for k, v in res["macro"].items()))
        for cat, c in res["per_category"].items():
            print(f"  {cat:<16} n={c['n']:<4} r@1 {c['recall@1']:<6} r@3 {c['recall@3']:<6} MRR {c['mrr']}")
        if args.out:
            os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
            with open(args.out, "w", encoding="utf-8") as fh:
                json.dump(res, fh, indent=2)
            print(f"written {args.out}")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
