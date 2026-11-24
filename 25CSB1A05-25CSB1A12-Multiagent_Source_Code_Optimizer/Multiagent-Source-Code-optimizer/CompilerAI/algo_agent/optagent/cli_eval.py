"""CLI command for Step 9: Running evaluation harness, benchmark adapters, ablations, and metrics."""
from __future__ import annotations

import argparse
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .config import Settings
from .eval.adapter import load_benchmark_dataset
from .eval.harness import EvalHarness
from .eval.schemas import EvalSuiteResult


def render_evaluation_markdown(res: EvalSuiteResult) -> str:
    """Render a markdown summary of the evaluation results."""
    lines = [
        "# OptAgent Step 9: Evaluation Suite Report",
        "",
        f"- **Total Tasks**: {res.total_tasks}",
        f"- **Correctness Rate**: {res.correctness_rate * 100:.1f}%",
        f"- **Geometric Mean Speedup**: {res.avg_speedup:.2f}x",
        f"- **Asymptotic Improvement Rate**: {res.asymptotic_improvement_rate * 100:.1f}%",
        f"- **False-Claim Rate**: {res.false_claim_rate * 100:.1f}%",
        f"- **Total Elapsed Time**: {res.elapsed_s:.2f}s",
        "",
        "## Task Summary",
        "",
        "| Task Name | Benchmark | Verified | Evidence Tier | Speedup | Memory Ratio | Asymptotic | Time (s) |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for e in res.task_evaluations:
        v_str = "YES" if e.verified else "NO"
        a_str = "YES" if e.asymptotic_improved else "NO"
        lines.append(
            f"| `{e.name}` | {e.benchmark} | {v_str} | {e.evidence_tier} | {e.speedup:.2f}x | {e.mem_ratio:.2f}x | {a_str} | {e.elapsed_s:.2f} |"
        )

    if res.speedup_distribution.max > 0:
        sd = res.speedup_distribution
        lines.extend([
            "",
            "## Speedup Distribution",
            "",
            f"- **Min**: {sd.min:.2f}x",
            f"- **P25**: {sd.p25:.2f}x",
            f"- **Median (P50)**: {sd.median:.2f}x",
            f"- **P75**: {sd.p75:.2f}x",
            f"- **P90**: {sd.p90:.2f}x",
            f"- **Max**: {sd.max:.2f}x",
            f"- **Geometric Mean**: {sd.geom_mean:.2f}x",
        ])

    if res.ablations:
        lines.extend([
            "",
            "## Ablation Study Results",
            "",
            "| Variant | Category | Correctness | Speedup | Delta Correctness | Delta Speedup |",
            "|---|---|---|---|---|---|",
        ])
        for a in res.ablations:
            lines.append(
                f"| {a.variant.name} | {a.variant.category} | {a.correctness_rate * 100:.1f}% | {a.avg_speedup:.2f}x | {a.delta_correctness * 100:+.1f}% | {a.delta_speedup:+.2f}x |"
            )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Run OptAgent evaluation suite on benchmarks or regression tasks.")
    parser.add_argument("--dataset", help="Path to JSON/JSONL dataset file (PIE/EffiBench/Mercury/ECCO format)")
    parser.add_argument("--benchmark", default="auto", choices=["auto", "pie", "effibench", "mercury", "ecco", "generic"], help="Benchmark format")
    parser.add_argument("--regression", action="store_true", default=False, help="Run permanent regression suite")
    parser.add_argument("--ablate", action="store_true", default=False, help="Run ablation study across proposers and rungs")
    parser.add_argument("--export-dpo", help="Path to export DPO preference pairs (JSONL)")
    parser.add_argument("--output", help="Path to save evaluation result JSON")
    parser.add_argument("--markdown", help="Path to save evaluation report Markdown")
    args = parser.parse_args()

    console = Console()
    settings = Settings()
    harness = EvalHarness(settings, log=console.print)

    if args.dataset:
        console.print(f"[cyan]Loading dataset from {args.dataset} (format: {args.benchmark})...[/cyan]")
        tasks = load_benchmark_dataset(args.dataset, benchmark_type=args.benchmark)
    else:
        console.print("[cyan]Loading permanent regression suite...[/cyan]")
        tasks = EvalHarness.get_regression_suite()

    console.print(f"Running evaluation on [bold]{len(tasks)}[/bold] task(s)...")
    res = harness.run_suite(tasks, run_ablations=args.ablate, harvest_prefs=bool(args.export_dpo))

    # Task Table
    table = Table(title="Evaluation Suite: Tasks Breakdown")
    table.add_column("Task Name", style="cyan")
    table.add_column("Benchmark", style="dim")
    table.add_column("Verified", style="bold")
    table.add_column("Tier", style="yellow")
    table.add_column("Speedup", style="bold green", justify="right")
    table.add_column("Mem Ratio", style="bold magenta", justify="right")
    table.add_column("Asymptotic", style="blue")
    table.add_column("Time (s)", justify="right")

    for e in res.task_evaluations:
        status_col = "[green]YES[/green]" if e.verified else "[red]NO[/red]"
        asymp_col = "[green]YES[/green]" if e.asymptotic_improved else "NO"
        table.add_row(
            e.name,
            e.benchmark,
            status_col,
            e.evidence_tier,
            f"{e.speedup:.2f}x",
            f"{e.mem_ratio:.2f}x",
            asymp_col,
            f"{e.elapsed_s:.2f}",
        )
    console.print(table)

    # Speedup Distribution Table
    sd = res.speedup_distribution
    dist_table = Table(title="Speedup & Resource Distribution", show_lines=False)
    dist_table.add_column("Metric", style="cyan")
    dist_table.add_column("Min", justify="right")
    dist_table.add_column("P25", justify="right")
    dist_table.add_column("Median (P50)", justify="right", style="bold green")
    dist_table.add_column("P75", justify="right")
    dist_table.add_column("P90", justify="right")
    dist_table.add_column("Max", justify="right", style="bold green")
    dist_table.add_column("Geom Mean", justify="right", style="bold cyan")
    dist_table.add_row(
        "Speedup (x)",
        f"{sd.min:.2f}x",
        f"{sd.p25:.2f}x",
        f"{sd.median:.2f}x",
        f"{sd.p75:.2f}x",
        f"{sd.p90:.2f}x",
        f"{sd.max:.2f}x",
        f"{sd.geom_mean:.2f}x",
    )
    md_dist = res.memory_distribution
    dist_table.add_row(
        "Mem Ratio",
        f"{md_dist.min:.2f}x",
        f"{md_dist.p25:.2f}x",
        f"{md_dist.median:.2f}x",
        f"{md_dist.p75:.2f}x",
        f"{md_dist.p90:.2f}x",
        f"{md_dist.max:.2f}x",
        f"{md_dist.mean:.2f}x",
    )
    console.print(dist_table)

    # Ablations Table (if requested)
    if res.ablations:
        ab_table = Table(title="Ablation Analysis (Relative Deltas vs Baseline)")
        ab_table.add_column("Ablation Variant", style="cyan")
        ab_table.add_column("Category", style="dim")
        ab_table.add_column("Correctness", justify="right")
        ab_table.add_column("Speedup", justify="right")
        ab_table.add_column("Delta Correctness", justify="right")
        ab_table.add_column("Delta Speedup", justify="right")

        for ab in res.ablations:
            dc_style = "green" if ab.delta_correctness >= 0 else "red"
            ds_style = "green" if ab.delta_speedup >= 0 else "yellow"
            ab_table.add_row(
                ab.variant.name,
                ab.variant.category,
                f"{ab.correctness_rate * 100:.1f}%",
                f"{ab.avg_speedup:.2f}x",
                f"[{dc_style}]{ab.delta_correctness * 100:+.1f}%[/{dc_style}]",
                f"[{ds_style}]{ab.delta_speedup:+.2f}x[/{ds_style}]",
            )
        console.print(ab_table)

    summary = (
        f"Total Tasks: {res.total_tasks}\n"
        f"Correctness Rate: [bold green]{res.correctness_rate * 100:.1f}%[/bold green] (Ground-truth gate: 100%)\n"
        f"Average Speedup: [bold green]{res.avg_speedup:.2f}x[/bold green]\n"
        f"Asymptotic Improvement Rate: {res.asymptotic_improvement_rate * 100:.1f}%\n"
        f"False-Claim Rate: [bold {'red' if res.false_claim_rate > 0 else 'green'}]{res.false_claim_rate * 100:.1f}%[/bold {'red' if res.false_claim_rate > 0 else 'green'}] (Target: 0.0%)\n"
        f"Total Elapsed Time: {res.elapsed_s:.2f}s"
    )
    console.print(Panel(summary, title="Step 9 Evaluation Summary", expand=False))

    # Export outputs if requested
    if args.output:
        EvalHarness.save_suite_result(res, args.output)
        console.print(f"[green]Saved evaluation result JSON to {args.output}[/green]")

    if args.markdown:
        md_text = render_evaluation_markdown(res)
        Path(args.markdown).write_text(md_text, encoding="utf-8")
        console.print(f"[green]Saved evaluation report Markdown to {args.markdown}[/green]")

    if args.export_dpo:
        from .eval.self_improve import PreferenceHarvester
        count = PreferenceHarvester.export_dpo_jsonl(res.preference_pairs, args.export_dpo)
        console.print(f"[green]Exported {count} DPO preference pairs to {args.export_dpo}[/green]")


if __name__ == "__main__":
    main()
