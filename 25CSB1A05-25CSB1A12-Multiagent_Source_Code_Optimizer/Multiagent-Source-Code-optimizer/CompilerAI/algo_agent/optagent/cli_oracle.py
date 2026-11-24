"""CLI for Step 2 Oracle: build and check."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .config import Settings
from .oracle.oracle import Oracle, build_oracle, source_sha

console = Console()


def show_oracle(bundle) -> None:
    console.print(Panel.fit(f"[bold]{bundle.entry_point}[/bold] (sha {bundle.source_sha})",
                            title="Step 2: Oracle"))
    t = Table(title="Corpus & Strength", show_lines=False)
    t.add_column("metric")
    t.add_column("value", overflow="fold")
    t.add_row("tier", f"[bold]{bundle.strength.tier}[/bold]")
    t.add_row("line coverage", f"{bundle.strength.line_coverage:.1%}")
    if bundle.mutation:
        t.add_row("mutation score", f"{bundle.mutation.score:.1%}")
    t.add_row("cases (vis/hold/total)", f"{bundle.strength.n_visible}/{bundle.strength.n_holdout}/{bundle.strength.n_cases}")
    t.add_row("scaling points", str(len(bundle.scaling)))
    t.add_row("properties", str(len(bundle.properties)))
    console.print(t)
    for w in bundle.warnings:
        console.print(f"[yellow]warning:[/yellow] {w}")
    console.print(f"\nSaved: runs/{bundle.source_sha}/oracle/oracle.json")


def cmd_build(args) -> None:
    source = Path(args.file).read_text(encoding="utf-8")
    overrides = yaml.safe_load(Path(args.overrides).read_text(encoding="utf-8")) if args.overrides else None
    s = Settings()
    oracle = build_oracle(
        source,
        entry=args.entry,
        overrides=overrides,
        use_llm=not args.no_llm,
        settings=s,
        run_mutation=not args.no_mutation,
        log=lambda msg: console.print(f"[dim]{msg}[/dim]"),
        language=getattr(args, "lang", None),
        source_name=args.file,
    )
    show_oracle(oracle.b)


def cmd_check(args) -> None:
    sha = args.sha
    if not sha and args.file:
        source = Path(args.file).read_text(encoding="utf-8")
        from .lang.detect import detect_language
        lang = detect_language(args.file, source, getattr(args, "lang", None))
        sha = source_sha(source, lang)
    if not sha:
        console.print("[red]Either --sha or original file must be specified.[/red]")
        sys.exit(1)
    oracle = Oracle.load(sha)
    cand_src = Path(args.candidate).read_text(encoding="utf-8")
    v = oracle.check(cand_src, fresh=args.fresh, scale=args.scale)
    status_style = "green" if v.passed else "red"
    console.print(Panel(f"[{status_style}]{'PASS' if v.passed else 'FAIL'}[/{status_style}]: {v.reason}",
                        title="Verdict"))
    console.print(v.feedback)
    if v.scale:
        st = Table(title="Scale results")
        st.add_column("family")
        st.add_column("mode")
        st.add_column("n")
        st.add_column("match")
        st.add_column("speedup")
        for r in v.scale:
            m_style = "green" if r["match"] else "red"
            st.add_row(r["family"], r["mode"], str(r["n"]), f"[{m_style}]{r['match']}[/{m_style}]",
                       str(r.get("speedup") or "-"))
        console.print(st)


def main() -> None:
    ap = argparse.ArgumentParser(prog="optagent-oracle")
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="build the oracle for a source file")
    b.add_argument("file")
    b.add_argument("--entry")
    b.add_argument("--overrides", help="YAML file")
    b.add_argument("--lang", help="source language (python, javascript, c, cpp)")
    b.add_argument("--no-llm", action="store_true")
    b.add_argument("--no-mutation", action="store_true")

    c = sub.add_parser("check", help="check a candidate rewrite against the oracle")
    c.add_argument("candidate", help="candidate source file")
    c.add_argument("--file", help="original source file (to derive sha)")
    c.add_argument("--sha", help="source sha directly")
    c.add_argument("--lang", help="source language (python, javascript, c, cpp)")
    c.add_argument("--fresh", type=int, default=None)
    c.add_argument("--scale", action="store_true")

    args = ap.parse_args()
    if args.cmd == "build":
        cmd_build(args)
    elif args.cmd == "check":
        cmd_check(args)


if __name__ == "__main__":
    main()

