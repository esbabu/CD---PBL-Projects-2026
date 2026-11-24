"""CLI for Step 4 Proposers."""
from __future__ import annotations

import argparse
from pathlib import Path

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from .complexity.analyzer import Analyzer
from .config import Settings
from .intent.pipeline import IntentExtractor
from .proposers.ensemble import ProposerEnsemble

console = Console()


def main() -> None:
    ap = argparse.ArgumentParser(prog="optagent-proposers")
    ap.add_argument("file", help="Python file to optimize")
    ap.add_argument("--entry", help="Entry point name")
    ap.add_argument("--overrides", help="YAML overrides file")
    ap.add_argument("--use-llm", action="store_true", help="Enable LLM proposer")
    args = ap.parse_args()

    s = Settings()
    source = Path(args.file).read_text(encoding="utf-8")
    overrides = yaml.safe_load(Path(args.overrides).read_text(encoding="utf-8")) if args.overrides else None

    console.print(f"[bold]Analyzing {args.file}...[/bold]")
    intent = IntentExtractor(s, use_llm=False).run(source, entry=args.entry, overrides=overrides, source_name=args.file)
    analyzer = Analyzer(s, log=lambda *a: None)
    analysis = analyzer.analyze(intent)

    console.print("[bold]Generating candidates...[/bold]")
    ensemble = ProposerEnsemble(s, use_llm=args.use_llm)
    cands = ensemble.propose_candidates(intent, analysis)

    console.print(f"[green]Emitted {len(cands)} candidate(s):[/green]\n")
    for i, c in enumerate(cands, 1):
        console.print(Panel(
            Syntax(c.source, "python", theme="monokai", line_numbers=True),
            title=f"Candidate {i}: {c.id} ({c.proposer})",
            subtitle=f"{c.rationale} | Time: {c.claimed_time}, Space: {c.claimed_space}"
        ))


if __name__ == "__main__":
    main()

