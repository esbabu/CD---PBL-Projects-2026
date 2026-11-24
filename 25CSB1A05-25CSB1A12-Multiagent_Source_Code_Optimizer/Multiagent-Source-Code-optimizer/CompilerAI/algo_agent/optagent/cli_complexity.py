"""CLI for Step 3 Complexity Analyzer."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .complexity.analyzer import Analyzer
from .config import Settings
from .intent.pipeline import IntentExtractor
from .oracle.builder import OracleBuilder

console = Console()


def show_analysis(bundle) -> None:
    console.print(Panel.fit(f"[bold]{bundle.entry_point}[/bold] (sha {bundle.source_sha})",
                            title="Step 3: Complexity Analysis"))
    fn = bundle.functions.get(bundle.entry_point)
    if fn:
        t = Table(title="Complexity Summary", show_lines=False)
        t.add_column("aspect")
        t.add_column("static")
        t.add_column("empirical")
        t.add_column("reconciled", style="bold green")

        emp_t = f"{fn.time_fit.model} (R^2={fn.time_fit.r2:.2f})" if fn.time_fit else "-"
        emp_s = f"{fn.space_fit.model}" if fn.space_fit else "-"
        t.add_row("time", fn.static_time, emp_t, fn.reconciled_time)
        t.add_row("space", fn.static_space, emp_s, fn.reconciled_space)
        console.print(t)

    if bundle.bottlenecks:
        bt = Table(title="Ranked Bottlenecks", show_lines=False)
        bt.add_column("line")
        bt.add_column("pattern")
        bt.add_column("share of time")
        bt.add_column("hits")
        bt.add_column("code", overflow="fold")
        for b in bundle.bottlenecks:
            bt.add_row(f"L{b.line}", b.pattern, f"{b.share_of_time:.1%}", str(b.hits), b.code)
        console.print(bt)

    if bundle.findings:
        console.print("\n[bold]Findings:[/bold]")
        for f in bundle.findings:
            console.print(f"  • {f}")

    console.print(f"\nSaved: runs/{bundle.source_sha}/analysis/analysis.json")


def main() -> None:
    ap = argparse.ArgumentParser(prog="optagent-complexity")
    ap.add_argument("file", help="Python file to analyze")
    ap.add_argument("--entry", help="Entry function name")
    ap.add_argument("--overrides", help="YAML overrides file")
    ap.add_argument("--no-oracle", action="store_true", help="Skip oracle building (static + profiling only)")
    args = ap.parse_args()

    s = Settings()
    source = Path(args.file).read_text(encoding="utf-8")
    overrides = yaml.safe_load(Path(args.overrides).read_text(encoding="utf-8")) if args.overrides else None

    console.print(f"[bold]Step 1: Extracting intent for {args.file}...[/bold]")
    intent = IntentExtractor(s, use_llm=False).run(source, entry=args.entry, overrides=overrides, source_name=args.file)

    oracle = None
    if not args.no_oracle:
        console.print("[bold]Step 2: Building oracle for scaling measurements...[/bold]")
        oracle = OracleBuilder(s, use_llm=False, log=lambda m: console.print(f"[dim]{m}[/dim]")).build(intent)

    console.print("[bold]Step 3: Running complexity analyzer...[/bold]")
    analyzer = Analyzer(s, log=lambda m: console.print(f"[dim]{m}[/dim]"))
    bundle = analyzer.analyze(intent, oracle)
    show_analysis(bundle)


if __name__ == "__main__":
    main()

