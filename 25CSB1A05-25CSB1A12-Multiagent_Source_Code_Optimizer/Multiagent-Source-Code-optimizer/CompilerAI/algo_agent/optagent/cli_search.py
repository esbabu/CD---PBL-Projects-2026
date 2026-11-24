"""CLI command for Step 6: Algorithm optimization search controller."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from .bench.runner import BenchmarkRunner
from .complexity.analyzer import Analyzer
from .config import Settings
from .intent.pipeline import IntentExtractor
from .oracle.builder import OracleBuilder
from .oracle.oracle import Oracle, source_sha
from .proposers.ensemble import ProposerEnsemble
from .search.controller import SearchController
from .search.schemas import SearchBudget
from .verify.ladder import Ladder


def main():
    parser = argparse.ArgumentParser(description="Run optimization search over algorithm transformations.")
    parser.add_argument("source", help="Path to Python source file to optimize")
    parser.add_argument("--overrides", help="Path to overrides YAML file")
    parser.add_argument("--max-candidates", type=int, default=10, help="Candidate budget")
    args = parser.parse_args()

    console = Console()
    settings = Settings()

    src_path = Path(args.source)
    if not src_path.exists():
        console.print(f"[red]Error: Source file {src_path} does not exist.[/red]")
        sys.exit(1)

    src = src_path.read_text(encoding="utf-8")
    overrides = None
    if args.overrides:
        overrides = yaml.safe_load(Path(args.overrides).read_text(encoding="utf-8"))

    sha = source_sha(src)
    oracle_json = Path(settings.runs_dir) / sha / "oracle" / "oracle.json"

    intent = IntentExtractor(settings, use_llm=False).run(src, overrides=overrides, source_name=src_path.name)
    if oracle_json.exists():
        console.print(f"[green]Loading existing oracle for {sha}...[/green]")
        oracle = Oracle.load(sha, settings)
    else:
        console.print(f"[yellow]Building oracle for {src_path.name}...[/yellow]")
        bundle = OracleBuilder(settings, use_llm=False, log=console.print).build(intent, run_mutation=True)
        oracle = Oracle(bundle, settings)

    console.print("[cyan]Analyzing complexity and bottlenecks...[/cyan]")
    analyzer = Analyzer(settings, log=console.print)
    analysis = analyzer.analyze(intent, oracle)

    console.print("[magenta]Initializing proposers, verifier, and bench runner...[/magenta]")
    proposers = ProposerEnsemble(settings, use_llm=False)
    ladder = Ladder(oracle, settings, log=console.print)
    bench = BenchmarkRunner(oracle, settings, log=console.print)

    controller = SearchController(oracle, analysis, proposers, ladder, bench, settings, log=console.print)
    console.print("[bold green]Starting Pareto optimization search...[/bold green]")
    budget = SearchBudget(max_candidates=args.max_candidates)
    res = controller.run(budget)

    # Display Pareto Front
    table = Table(title="Pareto Front (Time vs Space)")
    table.add_column("Candidate ID", style="cyan")
    table.add_column("Speedup", style="bold green", justify="right")
    table.add_column("Mem Ratio", style="bold magenta", justify="right")
    table.add_column("Evidence Tier", style="bold yellow")
    table.add_column("Claimed Complexity", style="white")

    for pt in res.pareto_front:
        table.add_row(
            pt.candidate_id,
            f"{pt.speedup:.2f}x",
            f"{pt.mem_ratio:.2f}x",
            pt.evidence_tier,
            f"{pt.time_complexity} / {pt.space_complexity}",
        )
    console.print(table)

    if res.best_candidate:
        console.print(Panel(
            Syntax(res.best_candidate.source, "python", line_numbers=True),
            title=f"Best Candidate: {res.best_candidate.id} ({res.best_candidate.proposer})",
            subtitle=res.best_candidate.rationale,
            expand=False,
        ))
    else:
        console.print("[yellow]No strictly better candidate was found.[/yellow]")


if __name__ == "__main__":
    main()

