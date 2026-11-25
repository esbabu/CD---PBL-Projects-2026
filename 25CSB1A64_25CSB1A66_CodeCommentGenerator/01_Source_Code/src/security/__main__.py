"""
Security analyzer CLI
======================
    python -m src.security <file-or-directory> [...] [--json] [--all] [--no-trace]
        [--min-confidence low|medium|high] [--fail-on potential|confirmed] [--fix]

Analyses the given files as written (no comment generation, no ML model) and
prints findings with their evidence traces.  ``--json`` emits the full finding
schema.  Exit status is 1 when ``--fail-on`` is given and a matching finding
exists, otherwise 0 (2 for usage/parse errors).  ``--fix`` then runs the
fix-and-verify agent (``src.agent``) on each file and prints its report and diff;
files are never modified.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from ..config import configure_stdio
from .analyzer import analyze_file
from .findings import LEVELS


_SOURCE_EXTS = (".py", ".java", ".c", ".h", ".cpp", ".cc", ".cxx", ".hpp", ".cs", ".rs", ".cob", ".cbl", ".cpy")


def _iter_files(paths):
    for p in paths:
        if os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                dirs[:] = sorted(d for d in dirs if not d.startswith(".") and d not in
                                 ("__pycache__", "venv", ".venv", "node_modules"))
                for f in sorted(files):
                    if f.endswith(_SOURCE_EXTS):
                        yield os.path.join(root, f)
        else:
            yield p


def main(argv=None) -> int:
    configure_stdio()
    ap = argparse.ArgumentParser(prog="python -m src.security",
                                 description="Evidence-backed static security analysis")
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    ap.add_argument("--all", action="store_true", help="include suppressed findings")
    ap.add_argument("--no-trace", action="store_true", help="omit evidence traces")
    ap.add_argument("--min-confidence", choices=list(LEVELS), default="low")
    ap.add_argument("--fail-on", choices=["potential", "confirmed"], default=None)
    ap.add_argument("--project", action="store_true",
                    help="analyse each directory as one project (cross-file taint); "
                         "default analyses every file on its own")
    ap.add_argument("--include", action="append", default=None,
                    help="with --project: only these sub-directories (repeatable)")
    ap.add_argument("--engine", choices=["rules", "neurosymbolic"], default="rules",
                    help="rules = taint + rule engines (default); neurosymbolic = also run the ML detector "
                         "and fuse it with the rule results")
    ap.add_argument("--fix", action="store_true",
                    help="after analysis, run the fix-and-verify agent on each file and show "
                         "the verified patch (files are not modified)")
    args = ap.parse_args(argv)
    if args.fix and args.project:
        ap.error("--fix works on single files; drop --project")

    reports = []
    exit_code = 0
    if args.project:
        from .project import analyze_project
        for root in args.paths:
            prep = analyze_project(root, include=args.include)
            if args.json:
                for rep in prep.files.values():
                    rep.findings = [f for f in rep.findings
                                    if (args.all or f.status != "suppressed")
                                    and LEVELS[f.confidence] >= LEVELS[args.min_confidence]]
                print(json.dumps(prep.to_dict(), indent=2))
            else:
                for rep in prep.files.values():
                    for f in rep.findings:
                        if (args.all or f.status != "suppressed") and \
                                LEVELS[f.confidence] >= LEVELS[args.min_confidence]:
                            print(f.format_text(show_trace=not args.no_trace))
                            print()
                print(f"{root}: {len(prep.modules)} modules, {len(prep.active())} active finding(s); "
                      f"cycles: {prep.cycles or 'none'}; unresolved internal imports: "
                      f"{prep.unresolved_imports or 'none'}; parse errors: {len(prep.parse_errors)}; "
                      f"{prep.runtime_ms:.0f} ms{'' if prep.converged else ' (did not fully converge)'}")
            if prep.parse_errors:
                exit_code = 2
            if args.fail_on:
                wanted = {"potential": {"potential", "confirmed"}, "confirmed": {"confirmed"}}[args.fail_on]
                if any(f.status in wanted for f in prep.active()):
                    exit_code = max(exit_code, 1)
        return exit_code
    for path in _iter_files(args.paths):
        try:
            rep = analyze_file(path, engines=args.engine)
        except OSError as exc:
            print(f"error: {exc}", file=sys.stderr)
            exit_code = 2
            continue
        rep.findings = [f for f in rep.findings
                        if (args.all or f.status != "suppressed")
                        and LEVELS[f.confidence] >= LEVELS[args.min_confidence]]
        reports.append(rep)
        if rep.parse_error:
            exit_code = 2

    fixes = {}
    if args.fix:
        from ..agent.fixer import fix_file
        fixes = {r.file: fix_file(r.file) for r in reports if not r.parse_error and r.file.endswith(".py")}

    if args.json:
        out = [r.to_dict() for r in reports]
        for d in out:
            if d["file"] in fixes:
                d["agent_fix"] = fixes[d["file"]].to_dict()
        print(json.dumps(out, indent=2))
    else:
        total = 0
        for rep in reports:
            if rep.parse_error:
                print(f"{rep.file}: could not parse — {rep.parse_error}")
                continue
            for f in rep.findings:
                print(f.format_text(show_trace=not args.no_trace))
                print()
                total += 1
            note = "" if rep.converged else "  (analysis did not fully converge)"
            print(f"{rep.file}: {len(rep.findings)} finding(s) {rep.by_status()} "
                  f"in {rep.runtime_ms:.1f} ms{note}")
        print(f"\nTotal: {total} finding(s) in {len(reports)} file(s)")
        if fixes:
            from ..agent.__main__ import print_report
            for result in fixes.values():
                print("\n" + "=" * 70 + "\nFix-and-verify agent\n")
                print_report(result)

    if args.fail_on:
        wanted = {"potential": {"potential", "confirmed"}, "confirmed": {"confirmed"}}[args.fail_on]
        if any(f.status in wanted for r in reports for f in r.findings):
            exit_code = max(exit_code, 1)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
