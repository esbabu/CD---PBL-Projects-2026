"""CLI command for Step 5: Verification ladder."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .config import Settings
from .intent.pipeline import IntentExtractor
from .oracle.builder import OracleBuilder
from .oracle.oracle import Oracle, source_sha
from .verify.ladder import Ladder


def main():
    parser = argparse.ArgumentParser(description="Verify a candidate against an algorithm's oracle using the verification ladder.")
    parser.add_argument("original", help="Path to original Python source file")
    parser.add_argument("candidate", help="Path to candidate Python source file")
    parser.add_argument("--overrides", help="Path to overrides YAML file")
    parser.add_argument("--fresh", type=int, default=None, help="Number of fresh differential test inputs")
    args = parser.parse_args()

    console = Console()
    settings = Settings()

    orig_path = Path(args.original)
    cand_path = Path(args.candidate)

    if not orig_path.exists():
        console.print(f"[red]Error: Original file {orig_path} does not exist.[/red]")
        sys.exit(1)
    if not cand_path.exists():
        console.print(f"[red]Error: Candidate file {cand_path} does not exist.[/red]")
        sys.exit(1)

    orig_src = orig_path.read_text(encoding="utf-8")
    cand_src = cand_path.read_text(encoding="utf-8")

    overrides = None
    if args.overrides:
        overrides = yaml.safe_load(Path(args.overrides).read_text(encoding="utf-8"))

    sha = source_sha(orig_src)
    oracle_json = Path(settings.runs_dir) / sha / "oracle" / "oracle.json"

    if oracle_json.exists():
        console.print(f"[green]Loading existing oracle for {sha}...[/green]")
        oracle = Oracle.load(sha, settings)
    else:
        console.print(f"[yellow]Building oracle for {orig_path.name}...[/yellow]")
        intent = IntentExtractor(settings, use_llm=False).run(orig_src, overrides=overrides, source_name=orig_path.name)
        bundle = OracleBuilder(settings, use_llm=False, log=lambda *a: None).build(intent, run_mutation=True)
        oracle = Oracle(bundle, settings)

    console.print(f"Running verification ladder for [bold]{cand_path.name}[/bold]...")
    ladder = Ladder(oracle, settings, log=console.print)
    evidence = ladder.verify(cand_src, fresh_override=args.fresh)

    table = Table(title=f"Verification Ladder Results ({cand_path.name})")
    table.add_column("Rung", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Details", style="white")
    table.add_column("Time (s)", justify="right")

    for r in evidence.rungs:
        if r.skipped:
            status = "[yellow]SKIPPED[/yellow]"
        elif r.passed:
            status = "[green]PASSED[/green]"
        else:
            status = "[red]FAILED[/red]"
        det = r.reason if not r.passed else str(r.details)
        table.add_row(r.rung, status, det[:70], f"{r.elapsed_s:.3f}")

    console.print(table)

    tier_color = "green" if evidence.passed else "red"
    summary = (
        f"Result: [{tier_color}]{'ACCEPTED' if evidence.passed else 'REJECTED'}[/{tier_color}]\n"
        f"Evidence Tier: [bold {tier_color}]{evidence.tier}[/bold {tier_color}] (Raw: {evidence.raw_tier})\n"
    )
    if evidence.capped_by:
        summary += f"[yellow]Tier capped by: {evidence.capped_by}[/yellow]\n"
    if evidence.warnings:
        summary += f"Warnings: {len(evidence.warnings)}\n"
    if evidence.counterexamples:
        summary += f"Counterexamples: {len(evidence.counterexamples)}\n"
        for i, ce in enumerate(evidence.counterexamples[:2], 1):
            summary += f"  [{i}] {ce.case_id} -> {ce.violations[0].detail if ce.violations else ''}\n"

    console.print(Panel(summary, title="Evidence Summary", expand=False))


if __name__ == "__main__":
    main()

