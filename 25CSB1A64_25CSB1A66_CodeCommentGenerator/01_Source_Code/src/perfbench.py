"""
Block-wise pipeline benchmark
==============================
    python -m src.perfbench [--small 8] [--long 2] [--out outputs/perf/benchmark.json]

For every language, on real files from the dataset's test split (long programs of 1,000-2,000 lines
and small programs), it runs the whole tool and measures each block with ``src.perf``:

  parsing & AST            pipeline.parse, pipeline.validate
  features & preprocessing pipeline.extract, pipeline.analyze
  comment generation       pipeline.generate, pipeline.attach
  IR & CFG                 pipeline.build_ir, pipeline.analysis (CFG + data-flow patterns),
                           security.ir_lowering / security.parse_and_ir_lowering
  data flow & taint        security.cfg_dataflow_taint
  vulnerability detection  security.rules_and_findings, security.memory_safety
  ML model                 ml.predict
  neuro-symbolic fusion    neurosymbolic.fuse
  RAG retrieval            rag.retrieve (explain_finding for each finding)
  agentic remediation      agent.fix_and_verify (with agent.strategy, agent.verify_patch) — Python files

Two passes: a timing pass (no tracemalloc) and a memory pass (tracemalloc + psutil RSS) on the long
programs, because tracemalloc slows Python down several times. Before measuring, one warm-up file per
language loads parsers and models; that cold start is recorded separately. Output:
``outputs/perf/benchmark.json``.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import statistics
import sys
import time
from collections import defaultdict
from typing import Dict, List

from . import perf

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
LANGS = ("python", "java", "csharp", "c", "cpp", "rust", "cobol")
GROUPS = {
    "Parsing & AST": ["pipeline.parse", "pipeline.validate"],
    "Features & preprocessing": ["pipeline.extract", "pipeline.analyze"],
    "Comment generation": ["pipeline.generate", "pipeline.attach"],
    "IR & CFG": ["pipeline.build_ir", "pipeline.analysis", "security.ir_lowering", "security.parse_and_ir_lowering",
                 "security.parse"],
    "Data flow & taint": ["security.cfg_dataflow_taint"],
    "Vulnerability detection (rules)": ["security.rules_and_findings", "security.memory_safety"],
    "ML model": ["ml.predict"],
    "Neuro-symbolic fusion": ["neurosymbolic.fuse"],
    "RAG retrieval": ["rag.retrieve"],
    "Agentic remediation": ["agent.fix_and_verify"],
}
LEAVES = [b for bs in GROUPS.values() for b in bs]


def _files(small: int, long_: int) -> Dict[str, List[dict]]:
    from .vulnml.pipeline import load_samples
    out = defaultdict(list)
    for s in load_samples():
        if s["split"] != "test" or not s.get("path"):
            continue
        kind = "long" if s["source"] == "custom-long" else "small"
        lst = out[(s["language"], kind)]
        if len(lst) < (long_ if kind == "long" else small):
            lst.append(s)
    return out


def run_file(path: str, lang: str, explain: int = 5) -> dict:
    """Everything the tool does for one file, each part inside perf blocks."""
    from .logger import PipelineLogger
    from .main import run_pipeline
    from .rag import explain_finding
    from .security.analyzer import analyze_file
    src = open(path, encoding="utf-8").read()
    lines = src.count("\n") + 1
    with perf.block("e2e", lines=lines):
        r = run_pipeline(path, PipelineLogger(input_file=path))
        ns = analyze_file(path, engines="neurosymbolic")
        for f in ns.active()[:explain]:
            explain_finding(f, src, lang)
        if lang == "python":
            from .agent.fixer import fix_source_profiled
            fix_source_profiled(src, path, guidance=True)
    return {"lines": lines, "findings": len(ns.active()), "comments": len(r.comments)}


def benchmark(small: int = 8, long_: int = 2) -> dict:
    import psutil
    files = _files(small, long_)
    proc = psutil.Process()
    result = {"machine": {"python": sys.version.split()[0], "platform": platform.platform(),
                          "processor": platform.processor(), "cpus": os.cpu_count()},
              "config": {"small_files_per_language": small, "long_files_per_language": long_},
              "languages": {}, "cold_start": {}}
    rss_start = proc.memory_info().rss
    for lang in LANGS:
        targets = files.get((lang, "long"), []) + files.get((lang, "small"), [])
        if not targets:
            continue
        # warm-up (parsers, models, knowledge base) — recorded as cold start
        with perf.profile(memory=False) as cold:
            run_file(os.path.join(ROOT, targets[0]["path"]), lang)
        result["cold_start"][lang] = {"total_ms": cold.total_ms, "blocks": {k: v["total_ms"] for k, v in
                                                                           cold.by_block().items()}}
        # timing pass
        per_file = []
        with perf.profile(memory=False) as prof:
            for s in targets:
                t0 = time.perf_counter()
                info = run_file(os.path.join(ROOT, s["path"]), lang)
                per_file.append({"path": s["path"], "kind": "long" if s["source"] == "custom-long" else "small",
                                 "ms": round((time.perf_counter() - t0) * 1000, 2), **info})
        blocks = prof.by_block()
        # memory pass (long programs, or the first file)
        mem_targets = [s for s in targets if s["source"] == "custom-long"] or targets[:1]
        rss0 = proc.memory_info().rss
        with perf.profile(memory=True) as mprof:
            for s in mem_targets:
                run_file(os.path.join(ROOT, s["path"]), lang)
        mem_blocks = mprof.by_block()
        for k, v in blocks.items():
            if k in mem_blocks:
                v["peak_kb"] = mem_blocks[k]["peak_kb"]
                v["mean_peak_kb"] = mem_blocks[k]["mean_peak_kb"]
        e2e = blocks.get("e2e", {})
        leaf_total = sum(blocks[b]["total_ms"] for b in LEAVES if b in blocks)
        groups = {}
        for g, names in GROUPS.items():
            tot = sum(blocks[b]["total_ms"] for b in names if b in blocks)
            peaks = [blocks[b]["peak_kb"] for b in names if b in blocks and blocks[b].get("peak_kb") is not None]
            groups[g] = {"total_ms": round(tot, 2), "share_of_measured": round(tot / leaf_total, 4) if leaf_total else 0,
                         "mean_ms_per_file": round(tot / len(targets), 2), "peak_kb": max(peaks) if peaks else None}
        bottleneck = max(groups.items(), key=lambda kv: kv[1]["total_ms"])[0]
        lines = sum(f["lines"] for f in per_file)
        result["languages"][lang] = {
            "files": len(per_file), "lines": lines, "per_file": per_file, "blocks": blocks, "groups": groups,
            "end_to_end": {"total_ms": e2e.get("total_ms"), "mean_ms_per_file": e2e.get("mean_ms"),
                           "median_ms_per_file": e2e.get("median_ms"), "p95_ms_per_file": e2e.get("p95_ms"),
                           "lines_per_second": round(lines / (e2e["total_ms"] / 1000), 1) if e2e.get("total_ms") else None,
                           "files_per_second": round(len(per_file) / (e2e["total_ms"] / 1000), 3) if e2e.get("total_ms") else None,
                           "peak_kb_memory_pass": mem_blocks.get("e2e", {}).get("peak_kb"),
                           "rss_delta_kb_memory_pass": round((proc.memory_info().rss - rss0) / 1024, 1)},
            "bottleneck": bottleneck}
        print(f"{lang}: {len(per_file)} files, {lines} lines, e2e {e2e.get('total_ms')} ms "
              f"({result['languages'][lang]['end_to_end']['lines_per_second']} lines/s); bottleneck: {bottleneck}")
    result["process_rss_mb"] = {"start": round(rss_start / 2 ** 20, 1), "end": round(proc.memory_info().rss / 2 ** 20, 1)}
    # overall group totals
    tot = defaultdict(float)
    for L in result["languages"].values():
        for g, v in L["groups"].items():
            tot[g] += v["total_ms"]
    s = sum(tot.values())
    result["overall_groups"] = {g: {"total_ms": round(v, 1), "share": round(v / s, 4) if s else 0} for g, v in tot.items()}
    result["overall_bottleneck"] = max(tot.items(), key=lambda kv: kv[1])[0] if tot else None
    return result


def show(res: dict) -> None:
    """Print a saved benchmark: end-to-end per language, then the share of every block."""
    print(f"{'language':9}{'files':>6}{'lines':>7}{'ms/file':>10}{'lines/s':>9}{'peak MB':>9}  bottleneck")
    for lang, d in res["languages"].items():
        e = d["end_to_end"]
        peak = (e.get("peak_kb_memory_pass") or 0) / 1024
        print(f"{lang:9}{d['files']:>6}{d['lines']:>7}{e['mean_ms_per_file']:>10.0f}{e['lines_per_second']:>9.0f}"
              f"{peak:>9.1f}  {d['bottleneck']}")
    print("\nshare of measured time, all languages:")
    for g, v in sorted(res["overall_groups"].items(), key=lambda kv: -kv[1]["share"]):
        print(f"  {g:34}{v['share'] * 100:6.1f} %  {v['total_ms'] / 1000:8.1f} s")
    print(f"overall bottleneck: {res['overall_bottleneck']}")


def main(argv=None) -> int:
    from .config import configure_stdio
    configure_stdio()
    ap = argparse.ArgumentParser(prog="python -m src.perfbench")
    ap.add_argument("--small", type=int, default=8)
    ap.add_argument("--long", type=int, default=2)
    ap.add_argument("--out", default=os.path.join(ROOT, "outputs", "perf", "benchmark.json"))
    ap.add_argument("--show", action="store_true", help="print the saved benchmark instead of running it")
    args = ap.parse_args(argv)
    if args.show:
        show(json.load(open(args.out, encoding="utf-8")))
        return 0
    res = benchmark(args.small, args.long)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    json.dump(res, open(args.out, "w"), indent=1)
    print(f"overall bottleneck: {res['overall_bottleneck']}; written {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
