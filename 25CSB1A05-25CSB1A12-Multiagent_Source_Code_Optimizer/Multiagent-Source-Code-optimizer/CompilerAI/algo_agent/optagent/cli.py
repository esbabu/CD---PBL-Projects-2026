from __future__ import annotations
import argparse
import sys
from pathlib import Path

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .analysis.static_facts import AmbiguousEntry
from .intent.pipeline import IntentError, IntentExtractor

console = Console()


def show(b) -> None:
    fn = b.module_facts.functions[b.entry_point]
    console.print(Panel.fit(f"[bold]{b.entry_point}[/bold]  (sha {b.source_sha})", title="Step 1: Intent"))

    t = Table(title="Static facts", show_lines=False)
    t.add_column("fact"); t.add_column("value", overflow="fold")
    t.add_row("mutated params", str(fn.mutated_params or "none"))
    t.add_row("effects", "; ".join(f"{e.kind.value}@L{e.line}" for e in fn.effects) or "none")
    t.add_row("raises / implicit", f"{fn.raises or '-'} / {fn.implicit_raises or '-'}")
    t.add_row("loops (count/depth)", f"{fn.loop_count}/{fn.max_loop_depth}")
    t.add_row("recursive", str(fn.is_recursive or fn.in_recursive_cycle))
    t.add_row("sorts", "; ".join(f"{s.kind}({s.detail})" for s in fn.sort_uses) or "none")
    t.add_row("unordered iteration", str([p.line for p in fn.unordered_iterations] or "none"))
    t.add_row("cost patterns", "\n".join(f"L{p.line} {p.kind}: {p.detail}" for p in fn.cost_patterns) or "none")
    console.print(t)

    ok = sum(r.status == "ok" for r in b.golden_seed)
    ex = sum(r.status == "exception" for r in b.golden_seed)
    console.print(f"[bold]Golden executions:[/bold] {len(b.golden_seed)} "
                  f"(ok={ok}, exception={ex}, nondeterministic={sum(bool(r.nondeterministic_fields) for r in b.golden_seed)})")

    v = b.validation
    console.print(f"[bold]Spec validation:[/bold] {v.status}  "
                  f"scores per round: {[r.score for r in v.rounds]}")
    console.print(Panel(b.spec.summary or "-", title=f"Spec v{b.spec.version}"))

    c = Table(title="Preservation contract")
    for col in ("aspect", "level", "applies", "source", "why"):
        c.add_column(col, overflow="fold")
    for it in b.contract:
        style = "red" if it.level.value == "must_preserve" else "green"
        c.add_row(it.aspect.value, f"[{style}]{it.level.value}[/{style}]", "yes" if it.applicable else "-",
                  it.source.value, it.rationale[:110])
    console.print(c)
    for w in b.warnings:
        console.print(f"[yellow]warning:[/yellow] {w}")
    console.print(f"\nSaved: runs/{b.source_sha}/intent.json")


def main() -> None:
    ap = argparse.ArgumentParser(prog="optagent")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("analyze", help="run Step 1 on a source file")
    a.add_argument("file")
    a.add_argument("--entry")
    a.add_argument("--overrides", help="YAML file")
    a.add_argument("--lang", help="source language (python, javascript, c, cpp)")
    a.add_argument("--no-llm", action="store_true", help="static + dynamic only (no Ollama needed)")

    opt = sub.add_parser("optimize", help="run end-to-end algorithm optimization on a source file")
    opt.add_argument("file")
    opt.add_argument("--entry")
    opt.add_argument("--overrides", help="YAML file")
    opt.add_argument("--lang", help="source language (python, javascript, c, cpp)")
    opt.add_argument("--no-llm", action="store_true", help="no LLM calls")
    opt.add_argument("--max-candidates", type=int, default=10)

    ev = sub.add_parser("eval", help="run evaluation harness and regression benchmarks")
    ev.add_argument("--dataset", help="Path to JSON dataset file")
    ev.add_argument("--benchmark", default="auto", choices=["auto", "pie", "effibench", "mercury", "ecco", "generic"])
    ev.add_argument("--regression", action="store_true", default=False)
    ev.add_argument("--ablate", action="store_true", default=False)
    ev.add_argument("--export-dpo", help="Path to export DPO preference pairs (JSONL)")
    ev.add_argument("--output", help="Path to save evaluation result JSON")
    ev.add_argument("--markdown", help="Path to save evaluation report Markdown")
    args = ap.parse_args()

    if args.cmd == "eval":
        from .cli_eval import main as eval_main
        sys.argv = [sys.argv[0]] + sys.argv[2:]
        eval_main()
        sys.exit(0)

    if args.cmd == "optimize":
        from .agent import OptimizerAgent, OptimizeRequest
        from .config import Settings
        from rich.markdown import Markdown
        overrides = yaml.safe_load(Path(args.overrides).read_text(encoding="utf-8")) if args.overrides else None
        if args.lang:
            overrides = dict(overrides or {}, language=args.lang)
        req = OptimizeRequest(
            source=Path(args.file).read_text(encoding="utf-8"),
            entry=args.entry,
            overrides=overrides,
            use_llm=not args.no_llm,
            language=args.lang,
            source_name=args.file,
        )
        res = OptimizerAgent(Settings(), log=console.print).run(req)
        if res.status != "ok":
            console.print(f"[red]{res.message}[/red]")
            if res.candidates:
                console.print(f"[yellow]Candidates: {res.candidates}[/yellow]")
            sys.exit(1)
        if res.report:
            from .report.render import render_markdown
            md = render_markdown(res.report)
            console.print(Markdown(md))
        sys.exit(0)

    overrides = yaml.safe_load(Path(args.overrides).read_text()) if args.overrides else None
    try:
        bundle = IntentExtractor(use_llm=not args.no_llm).run(
            Path(args.file).read_text(encoding="utf-8"), entry=args.entry, overrides=overrides,
            source_name=args.file, language=args.lang)
    except AmbiguousEntry as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(2)
    except IntentError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)
    show(bundle)


if __name__ == "__main__":
    main()