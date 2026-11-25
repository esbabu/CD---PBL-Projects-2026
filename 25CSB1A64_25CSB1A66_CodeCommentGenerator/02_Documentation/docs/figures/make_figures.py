"""
Report figures for the dataset, model comparison and block-wise profiling.

    python docs/figures/make_figures.py

Reads only result files written by the project's commands:
  datasets/security_dataset/v1/manifest.json   (python -m src.dataset.build)
  outputs/eval/model_comparison.json            (python -m src.vulnml.pipeline evaluate)
  outputs/vulnml/<lang>_metrics.json            (python -m src.vulnml.pipeline train)
  outputs/perf/benchmark.json                   (python -m src.perfbench)
Writes PNGs next to this script.
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
LN = {"python": "Python", "java": "Java", "csharp": "C#", "c": "C", "cpp": "C++", "rust": "Rust", "cobol": "COBOL"}
ENG = [("rules", "Rule-based", "#2563eb"), ("ml", "ML", "#9333ea"), ("neurosymbolic", "Neuro-symbolic", "#059669")]
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})


def load(*p):
    return json.load(open(os.path.join(ROOT, *p), encoding="utf-8"))


def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, name), dpi=170)
    plt.close(fig)
    print("wrote", name)


def dataset_fig():
    st = load("datasets", "security_dataset", "v1", "manifest.json")["statistics"]
    langs = list(LN)
    fig, (a, b) = plt.subplots(1, 2, figsize=(10, 3.4))
    vul = [st["by_language_and_label"].get(f"{l}/vulnerable", 0) for l in langs]
    safe = [st["by_language_and_label"].get(f"{l}/safe", 0) for l in langs]
    x = np.arange(len(langs))
    a.bar(x - 0.2, vul, 0.4, color="#dc2626", label="vulnerable")
    a.bar(x + 0.2, safe, 0.4, color="#94a3b8", label="safe")
    for i, (v, s) in enumerate(zip(vul, safe)):
        a.text(i - 0.2, v, str(v), ha="center", va="bottom", fontsize=6)
        a.text(i + 0.2, s, str(s), ha="center", va="bottom", fontsize=6)
    a.set_xticks(x, [LN[l] for l in langs])
    a.set_yscale("log")
    a.set_ylabel("samples (log)")
    a.set_title("(a) Samples per language")
    a.legend(frameon=False)
    loc = [st["lines_by_language"][l] / 1000 for l in langs]
    b.bar([LN[l] for l in langs], loc, color="#2563eb")
    b.set_ylabel("thousand lines")
    b.set_title("(b) Lines of code per language")
    for i, v in enumerate(loc):
        b.text(i, v, f"{v:.0f}k", ha="center", va="bottom", fontsize=7)
    save(fig, "fig_dataset.png")


def comparison_fig():
    ev = load("outputs", "eval", "model_comparison.json")
    fig, (a, b) = plt.subplots(1, 2, figsize=(10.5, 3.4))
    ms = ["accuracy", "precision", "recall", "f1"]
    x = np.arange(len(ms))
    for i, (k, lab, c) in enumerate(ENG):
        a.bar(x + (i - 1) * 0.27, [ev["overall"][k][m] or 0 for m in ms], 0.27, label=lab, color=c)
    a.set_xticks(x, ["Accuracy", "Precision", "Recall", "F1"])
    a.set_ylim(0, 1.05)
    a.set_title("(a) All languages, held-out test units")
    a.legend(frameon=False, fontsize=8)
    langs = [l for l in LN if l in ev["by_language"]]
    x = np.arange(len(langs))
    for i, (k, lab, c) in enumerate(ENG):
        b.bar(x + (i - 1) * 0.27, [ev["by_language"][l][k]["f1"] or 0 for l in langs], 0.27, color=c, label=lab)
    b.set_xticks(x, [LN[l] for l in langs])
    b.set_ylim(0, 1.05)
    b.set_title("(b) F1 by language")
    save(fig, "fig_model_comparison.png")
    fig, axs = plt.subplots(1, 3, figsize=(10, 3))
    for ax, (k, lab, _) in zip(axs, ENG):
        cm = ev["overall"][k]["confusion"]
        m = np.array([[cm["tn"], cm["fp"]], [cm["fn"], cm["tp"]]])
        ax.imshow(m, cmap="Blues")
        for (i, j), v in np.ndenumerate(m):
            ax.text(j, i, f"{v:,}", ha="center", va="center", color="white" if v > m.max() / 2 else "black",
                    fontweight="bold")
        ax.set_xticks([0, 1], ["pred. safe", "pred. vuln."])
        ax.set_yticks([0, 1], ["safe", "vulnerable"])
        ax.set_title(lab)
    save(fig, "fig_model_confusion.png")


def perf_fig():
    bench = load("outputs", "perf", "benchmark.json")
    langs = [l for l in LN if l in bench["languages"]]
    groups = list(bench["languages"][langs[0]]["groups"])
    colors = plt.cm.tab10(np.linspace(0, 1, len(groups)))
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 3.8), gridspec_kw={"width_ratios": [1.4, 1]})
    left = np.zeros(len(langs))
    for g, c in zip(groups, colors):
        v = np.array([bench["languages"][l]["groups"][g]["mean_ms_per_file"] for l in langs])
        a.barh([LN[l] for l in langs], v, left=left, color=c, label=g)
        left += v
    a.set_xlabel("mean ms per file (test files: long programs + small programs)")
    a.set_title("(a) Time per block and language")
    a.legend(fontsize=6.5, frameon=False, loc="lower right")
    og = bench["overall_groups"]
    names = sorted(og, key=lambda g: og[g]["share"])
    b.barh(names, [og[g]["share"] * 100 for g in names], color="#9333ea")
    b.set_xlabel("% of measured time, all languages")
    b.set_title("(b) Share of time per block")
    save(fig, "fig_block_profile.png")


if __name__ == "__main__":
    dataset_fig()
    if os.path.isfile(os.path.join(ROOT, "outputs", "eval", "model_comparison.json")):
        comparison_fig()
    if os.path.isfile(os.path.join(ROOT, "outputs", "perf", "benchmark.json")):
        perf_fig()
