"""
Markdown tables for the dataset, ML training, engine comparison and block-wise profile.

    python docs/figures/make_tables.py > docs/figures/results_tables.md

Every number is read from the result files (see make_figures.py); nothing is typed by hand.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
LN = {"python": "Python", "java": "Java", "csharp": "C#", "c": "C", "cpp": "C++", "rust": "Rust", "cobol": "COBOL"}
ENG = [("rules", "Rule-based"), ("ml", "ML"), ("neurosymbolic", "Neuro-symbolic")]


def load(*p):
    path = os.path.join(ROOT, *p)
    return json.load(open(path, encoding="utf-8")) if os.path.isfile(path) else None


def f(v, d=3):
    if v is None:
        return "—"
    if isinstance(v, float):
        return f"{v:.{d}f}"
    if isinstance(v, int):
        return f"{v:,}"
    return str(v)


def table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "|".join("---" for _ in head) + "|"]
    out += ["| " + " | ".join(f(c) if not isinstance(c, str) else c for c in r) + " |" for r in rows]
    return "\n".join(out)


def dataset():
    m = load("datasets", "security_dataset", "v1", "manifest.json")
    st = m["statistics"]
    print("### Dataset summary\n")
    lp = st["long_programs"]
    print(table(["Item", "Value"], [
        ["Samples", st["samples"]], ["Lines of code", st["total_lines_of_code"]], ["Split groups", st["groups"]],
        ["Distinct CWEs", st["distinct_cwes"]], ["Vulnerable / safe", f"{st['by_label']['vulnerable']:,} / {st['by_label']['safe']:,}"],
        ["Train / val / test", f"{st['by_split']['train']:,} / {st['by_split']['val']:,} / {st['by_split']['test']:,}"],
        ["Long programs", f"{lp['count']} ({lp['min_lines']:,}–{lp['max_lines']:,} lines; {lp['lines']:,} lines; "
                          f"{lp['planted_vulnerabilities']:,} planted vulnerabilities)"],
        ["Files with more than one vulnerability class", st["multi_vulnerability_files"]],
        ["Rejected by validation", len(m["validation"]["rejected"])]]))
    print("\n### Samples per language\n")
    rows = []
    for l in LN:
        rows.append([LN[l], st["by_language"].get(l, 0), st["by_language_and_label"].get(f"{l}/vulnerable", 0),
                     st["by_language_and_label"].get(f"{l}/safe", 0),
                     "/".join(f"{st['by_language_and_split'].get(f'{l}/{s}', 0):,}" for s in ("train", "val", "test")),
                     st["lines_by_language"].get(l, 0)])
    print(table(["Language", "Samples", "Vulnerable", "Safe", "Train/val/test", "Lines"], rows))
    print("\n### Samples per source\n")
    print(table(["Source", "Samples"], [[k, v] for k, v in st["by_source"].items()]))
    print("\n### Vulnerable samples by family (top 15)\n")
    fam = [(k.replace("(per-location rules)", "long programs (labelled per location)"), v) for k, v in
           sorted(st["vulnerable_by_family"].items(), key=lambda kv: -kv[1])[:15]]
    print(table(["Family", "Vulnerable samples"], fam))


def training():
    print("\n### ML detector: tuning on validation, one score on test\n")
    rows = []
    for l in LN:
        m, c = load("outputs", "vulnml", f"{l}_metrics.json"), load("outputs", "vulnml", f"{l}_config.json")
        if not m or "test_binary" not in m:
            continue
        b = m["test_binary"]
        ch = c["chosen"]
        rows.append([LN[l] + (" (small-n)" if c.get("small_n") else ""),
                     f"{c['counts']['train']:,}/{c['counts']['val']:,}/{c['counts']['test']:,}",
                     f"C={ch['C']}, n-grams {tuple(ch['ngram'])}", f(ch["val_f1"]), b["accuracy"], b["precision"],
                     b["recall"], b["f1"], b["fpr"], b["fnr"], m["test_family"]["accuracy"], f(m["train_seconds"], 1)])
    print(table(["Language", "Train/val/test", "Chosen", "Val F1", "Acc", "P", "R", "F1", "FPR", "FNR", "Family acc",
                 "Train s"], rows))


def comparison():
    ev = load("outputs", "eval", "model_comparison.json")
    if not ev:
        return
    print("\n### Three engines on the same test units (all languages)\n")
    o = ev["overall"]
    print(table(["Engine", "n", "Acc", "P", "R", "F1", "FPR", "FNR", "TP", "FP", "FN", "TN"],
                [[lab, o[k]["n"], o[k]["accuracy"], o[k]["precision"], o[k]["recall"], o[k]["f1"], o[k]["fpr"],
                  o[k]["fnr"], o[k]["confusion"]["tp"], o[k]["confusion"]["fp"], o[k]["confusion"]["fn"],
                  o[k]["confusion"]["tn"]] for k, lab in ENG]))
    print("\n### By language (F1, with precision / recall)\n")
    rows = []
    for l, d in ev["by_language"].items():
        rows.append([LN[l], d["rules"]["n"]] + [f"{f(d[k]['f1'])} ({f(d[k]['precision'], 2)} / {f(d[k]['recall'], 2)})"
                                                 for k, _ in ENG])
    print(table(["Language", "Units", "Rule-based", "ML", "Neuro-symbolic"], rows))
    print("\n### By source (F1 / recall / FPR)\n")
    rows = []
    for s, d in ev["by_source"].items():
        rows.append([s, d["rules"]["n"]] + [f"{f(d[k]['f1'])} / {f(d[k]['recall'])} / {f(d[k]['fpr'])}" for k, _ in ENG])
    print(table(["Source", "Units", "Rule-based", "ML", "Neuro-symbolic"], rows))
    sc = ev.get("juliet_in_rule_scope")
    if sc:
        print("\n### Juliet recall inside / outside the rules' CWE scope\n")
        rows = [[LN[l], v["in_scope_n"], v["out_of_scope_n"]] +
                [f"{f(v[f'{k}_recall_in_scope'])} / {f(v[f'{k}_recall_out_of_scope'])}" for k, _ in ENG]
                for l, v in sc.items()]
        print(table(["Language", "In scope", "Out of scope", "Rule-based", "ML", "Neuro-symbolic"], rows))
    print("\n### Long test programs: exact (rule, line) matches\n")
    rows = []
    for l, v in ev["locations_long_programs"].get("rules", {}).items():
        ns = ev["locations_long_programs"]["neurosymbolic"][l]
        rows.append([LN[l], v["programs"], v["lines"], v["tp"], v["fp"], v["fn"], v["precision"], v["recall"],
                     f"{ns['tp']}/{ns['fp']}/{ns['fn']}"])
    print(table(["Language", "Programs", "Lines", "TP", "FP", "FN", "P", "R", "Neuro-symbolic TP/FP/FN"], rows))
    print("\n### Mean latency per unit (ms)\n")
    lat = ev["latency_ms"]
    rows = []
    for l in LN:
        r = [LN[l]]
        for k, _ in ENG:
            a, b = lat.get(f"{k}:{l}"), lat.get(f"{k}_long:{l}")
            r.append(f"{f(a['mean'], 1) if a else '—'} / {f(b['mean'], 0) if b else '—'}")
        rows.append(r)
    print(table(["Language", "Rule-based (small / long file)", "ML (small / long)", "Neuro-symbolic (small / long)"], rows))


def perf():
    b = load("outputs", "perf", "benchmark.json")
    if not b:
        return
    print(f"\n### Block-wise profile ({b['machine']['processor'] or b['machine']['platform']}, "
          f"{b['machine']['cpus']} logical CPUs, Python {b['machine']['python']})\n")
    langs = list(b["languages"])
    groups = list(b["languages"][langs[0]]["groups"])
    rows = [[g] + [f(b["languages"][l]["groups"][g]["mean_ms_per_file"], 1) for l in langs] +
            [f"{b['overall_groups'][g]['share'] * 100:.1f}%"] for g in groups]
    print(table(["Block (mean ms per file)"] + [LN[l] for l in langs] + ["Share"], rows))
    print("\n### End to end\n")
    rows = []
    for l in langs:
        d = b["languages"][l]
        e = d["end_to_end"]
        peak = max((v["peak_kb"] for v in d["groups"].values() if v.get("peak_kb") is not None), default=None)
        rows.append([LN[l], d["files"], d["lines"], f(e["mean_ms_per_file"], 0), f(e["p95_ms_per_file"], 0),
                     f(e["lines_per_second"], 0), f(e["peak_kb_memory_pass"] / 1024, 1) if e["peak_kb_memory_pass"] else "—",
                     d["bottleneck"]])
    print(table(["Language", "Files", "Lines", "Mean ms/file", "p95 ms/file", "Lines/s", "Peak heap MB", "Bottleneck"],
                rows))
    print(f"\nOverall bottleneck: **{b['overall_bottleneck']}**. Process RSS {b['process_rss_mb']['start']} → "
          f"{b['process_rss_mb']['end']} MB.")


SECTIONS = {"dataset": dataset, "training": training, "comparison": comparison, "perf": perf}


def render(name: str) -> str:
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        SECTIONS[name]()
    return buf.getvalue().strip("\n")


def inject(path: str) -> None:
    """Replace the text between <!-- BEGIN:name --> and <!-- END:name --> with fresh tables."""
    import re
    text = open(path, encoding="utf-8").read()
    for name in SECTIONS:
        pat = re.compile(rf"(<!-- BEGIN:{name} -->).*?(<!-- END:{name} -->)", re.S)
        if pat.search(text):
            body = render(name)
            text = pat.sub(lambda m: m.group(1) + "\n" + body + "\n" + m.group(2), text)
    open(path, "w", encoding="utf-8", newline="\n").write(text)
    print("updated", path)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2 and sys.argv[1] == "--inject":
        for p in sys.argv[2:]:
            inject(p)
    else:
        for name in (sys.argv[1:] or SECTIONS):
            print(render(name) + "\n")
