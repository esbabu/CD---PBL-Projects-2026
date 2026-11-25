"""
Fix-and-verify agent CLI
=========================
    python -m src.agent <file.py> [--out patched.py] [--llm] [--json] [--max-attempts N] [--trace]
                                  [--learn] [--no-guidance]

Analyses the file, patches each finding it has a strategy for, verifies every
patch with the analyzer and prints, per finding, the strategy that worked or
"needs manual fix" (with retrieved guidance from the RAG knowledge base),
followed by a unified diff. ``--learn`` stores every verified fix in the RAG fix
memory so later runs can retrieve it. The input file is never
modified; ``--out`` writes the patched copy. Exit status: 0, or 2 if the file
cannot be read or parsed.
"""
from __future__ import annotations

import argparse
import json
import sys

from ..config import configure_stdio
from .fixer import FIXED, FixResult, fix_file


def print_report(result: FixResult, show_trace: bool = False, out=None) -> None:
    out = out or sys.stdout
    if result.parse_error:
        print(f"{result.filepath}: cannot analyse — {result.parse_error}", file=out)
        return
    if show_trace:
        print("Agent trace", file=out)
        for step in result.steps:
            print("  " + step.format(), file=out)
        print(file=out)
    if not result.outcomes:
        print(f"{result.filepath}: no active security findings — nothing to fix.", file=out)
        return
    print(f"{result.filepath}: {len(result.outcomes)} finding(s)", file=out)
    for i, o in enumerate(result.outcomes, 1):
        where = f"{o.rule_id} {o.title} in {o.function}() line {o.line}"
        if o.status == FIXED:
            print(f"  {i:>2}. [fixed]  {where}\n        fixed by {o.strategy}: {o.reason}", file=out)
        else:
            print(f"  {i:>2}. [manual] {where}\n        needs manual fix — {o.reason}", file=out)
            for g in o.guidance[:2]:
                print(f"        guidance [{g['kind']}] {g['title']} — {g['source']}", file=out)
    c = result.counts()
    print(f"\n{c['fixed']} fixed and verified, {c['needs_manual_fix']} need a manual fix, "
          f"{c['rejected_patches']} patch(es) rejected by verification; active findings "
          f"{result.findings_before} → {result.findings_after}.", file=out)
    diff = result.diff()
    if diff:
        print("\n" + diff, file=out)


def main(argv=None) -> int:
    configure_stdio()
    ap = argparse.ArgumentParser(prog="python -m src.agent",
                                 description="Fix security findings and verify every patch with the analyzer")
    ap.add_argument("file")
    ap.add_argument("--out", help="write the patched copy here (the input is never modified)")
    ap.add_argument("--llm", action="store_true",
                    help="as a last attempt, ask a local Ollama model (skipped if none is running)")
    ap.add_argument("--json", action="store_true", help="emit the full result, trace and diff as JSON")
    ap.add_argument("--max-attempts", type=int, default=3, help="strategies tried per finding (default 3)")
    ap.add_argument("--trace", action="store_true", help="print every agent step")
    ap.add_argument("--learn", action="store_true",
                    help="store verified fixes in the RAG fix memory (outputs/rag/fix_memory.jsonl)")
    ap.add_argument("--no-guidance", action="store_true",
                    help="do not attach retrieved guidance to findings that need a manual fix")
    args = ap.parse_args(argv)

    try:
        result = fix_file(args.file, max_attempts=args.max_attempts, use_llm=args.llm,
                          learn=args.learn, guidance=not args.no_guidance)
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.out and not result.parse_error:
        with open(args.out, "w", encoding="utf-8", newline="") as fh:
            fh.write(result.patched)
    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print_report(result, show_trace=args.trace)
        if args.out and not result.parse_error:
            print(f"Patched copy written to {args.out}")
    return 2 if result.parse_error else 0


if __name__ == "__main__":
    sys.exit(main())
