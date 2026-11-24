"""The report's result figures, drawn from the project's own saved measurements.

    python evaluation/report_figures.py        writes docs/report/figures/fig*.png

Every number comes from a file another script wrote (security_results.json, redteam_results.json,
aivsai_results.json, blind_cost.json, the cost table in results.md) or from running the compiler
itself (phase times, optimizer counts), so a figure can always be traced back and redrawn. Nothing
is typed in by hand. White background, 300 dpi, sized for a one-column report page.
"""

import json
import os
import re
import statistics
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = ROOT / "docs" / "report" / "figures"
PARC = os.environ.get("PARC_BIN", str(ROOT / "build" / "local" / "Release" / "parc.exe"))
EXAMPLES = sorted((ROOT / "examples").glob("*.parc"))

# Two series colours that differ in lightness as well as hue (layer off / layer on, before / after).
OFF, ON, GREY = "#D9822B", "#2B6CB0", "#8A94A6"
plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
    "font.family": "DejaVu Serif", "font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
    "axes.titlesize": 11, "axes.titleweight": "bold",
})


def load(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / name, dpi=300)
    plt.close(fig)
    print("wrote", name)


def label_bars(ax, bars, fmt="{:g}"):
    for bar in bars:
        h = bar.get_height()
        ax.annotate(fmt.format(h), (bar.get_x() + bar.get_width() / 2, h), xytext=(0, 2),
                    textcoords="offset points", ha="center", va="bottom", fontsize=8)


def short(name):
    return name.replace(".parc", "")


# ---------------------------------------------------------------- the compiler

def fig_phase_times():
    """Median time of each compiler phase over the 20 examples (parc metrics, compile part only)."""
    per_phase = {}
    order = []
    with tempfile.TemporaryDirectory() as tmp:
        for example in EXAMPLES:
            out = Path(tmp) / "m.json"
            subprocess.run([PARC, "metrics", str(example), "--json", str(out), "--no-native", "--no-energy",
                            "--min-ms", "1"], capture_output=True, check=False)
            if not out.is_file():
                continue
            for p in json.loads(out.read_text(encoding="utf-8"))["compile"]["phases"]:
                if p["phase"] not in per_phase:
                    order.append(p["phase"])
                per_phase.setdefault(p["phase"], []).append(p["ms"] * 1000)
    medians = [statistics.median(per_phase[p]) for p in order]
    fig, ax = plt.subplots(figsize=(6.5, 3.0))
    bars = ax.bar(order, medians, color=ON)
    label_bars(ax, bars, "{:.0f}")
    ax.set_ylabel("median time (µs)")
    ax.set_title(f"Time per compiler phase (median over {len(EXAMPLES)} example programs)")
    ax.tick_params(axis="x", rotation=25)
    save(fig, "fig04_phase_times.png")


def fig_optimizer():
    """Three-address instructions before and after the optimizer, per example (passes.json)."""
    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        for example in EXAMPLES:
            out = Path(tmp) / example.stem
            subprocess.run([PARC, "build", str(example), "--out", str(out)], capture_output=True, check=False)
            passes = out / "passes.json"
            if passes.is_file():
                d = json.loads(passes.read_text(encoding="utf-8"))
                rows.append((example.stem[:2], d["instructions_before"], d["instructions_after"]))
    names = [r[0] for r in rows]
    x = range(len(rows))
    fig, ax = plt.subplots(figsize=(6.5, 3.0))
    ax.bar([i - 0.2 for i in x], [r[1] for r in rows], 0.4, color=GREY, label="before the optimizer")
    ax.bar([i + 0.2 for i in x], [r[2] for r in rows], 0.4, color=ON, label="after")
    before, after = sum(r[1] for r in rows), sum(r[2] for r in rows)
    ax.set_xticks(list(x), names)
    ax.set_xlabel("example program (number)")
    ax.set_ylabel("IR instructions")
    ax.set_title(f"Optimizer: {before} → {after} instructions in total ({100 * (before - after) / before:.0f}% fewer)")
    ax.legend(frameon=False)
    save(fig, "fig05_optimizer.png")


def _time_ms(text):
    m = re.match(r"([\d.]+)\s*(ms|µs|ns)", text.strip())
    if not m:
        return None
    return float(m.group(1)) * {"ms": 1.0, "µs": 1e-3, "ns": 1e-6}[m.group(2)]


def fig_vm_vs_native():
    """VM against clang -O2, from the cost table of results.md section 7."""
    text = (HERE / "results.md").read_text(encoding="utf-8")
    section = text.split("## 7.")[1].split("## 8.")[0]
    rows = []
    for line in section.splitlines():
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) >= 4 and cells[0].endswith(".parc"):
            vm, native = _time_ms(cells[1]), _time_ms(cells[2])
            if vm and native:
                rows.append((cells[0][:2], vm, native))
    x = range(len(rows))
    fig, ax = plt.subplots(figsize=(6.5, 3.2))
    ax.bar([i - 0.2 for i in x], [r[1] * 1000 for r in rows], 0.4, color=OFF, label="ParC VM")
    ax.bar([i + 0.2 for i in x], [r[2] * 1000 for r in rows], 0.4, color=ON, label="clang -O2 (native)")
    ax.set_yscale("log")
    ax.set_xticks(list(x), [r[0] for r in rows])
    ax.set_xlabel("example program (number)")
    ax.set_ylabel("time per run (µs, log scale)")
    # The headline number as results.md states it (computed there from the unrounded times).
    stated = re.search(r"Native code was ([\d.]+) times faster", section)
    geo = stated.group(1) if stated else f"{statistics.geometric_mean([r[1] / r[2] for r in rows]):.1f}"
    ax.set_title(f"Run time: VM against native (geometric-mean speed-up {geo}×)")
    ax.legend(frameon=False)
    save(fig, "fig06_vm_vs_native.png")


# ---------------------------------------------------------------- the security layer

def fig_confusion():
    s = load("security_results.json")["simulated"]
    cells = [[s["tp"], s["fn"]], [s["fp"], s["tn"]]]
    fig, ax = plt.subplots(figsize=(5.2, 3.8))
    ax.imshow([[1, 0], [0, 1]], cmap="Blues", vmin=-0.6, vmax=1.6)
    for i in range(2):
        for j in range(2):
            ax.text(j, i, str(cells[i][j]), ha="center", va="center", fontsize=16, fontweight="bold")
    ax.set_xticks([0, 1], ["detected", "not detected"])
    ax.set_yticks([0, 1], [f"attacks ({s['attacks']})", f"honest cases ({s['honest']})"])
    ax.set_title(f"Attack detection (security layer on)\nprecision {100 * s['precision']:.1f}%, "
                 f"recall {100 * s['recall']:.1f}%, false alarms {100 * s['false_positive_rate']:.1f}%")
    for spine in ax.spines.values():
        spine.set_visible(False)
    save(fig, "fig07_confusion_matrix.png")


def fig_attack_success():
    """Simulated attacks that succeed, by kind: compiler gate only against gate + security layer."""
    s = load("security_results.json")["simulated"]
    kinds = s["by_kind"]
    names = [textwrap.fill(k["kind"], 14) for k in kinds]
    x = range(len(kinds))
    fig, ax = plt.subplots(figsize=(6.5, 3.4))
    b1 = ax.bar([i - 0.2 for i in x], [k["succeed_gate_only"] for k in kinds], 0.4, color=OFF,
                label=f"compiler gate only ({s['succeed_gate_only']} of {s['attacks']})")
    b2 = ax.bar([i + 0.2 for i in x], [k["succeed_with_layer"] for k in kinds], 0.4, color=ON,
                label=f"gate + security layer ({s['succeed_with_layer']} of {s['attacks']})")
    label_bars(ax, b1)
    label_bars(ax, b2)
    ax.set_xticks(list(x), names, fontsize=8)
    ax.set_ylabel("attacks that succeed")
    ax.set_title("Simulated attacks that succeed, by kind of attack")
    ax.legend(frameon=False)
    save(fig, "fig08_attack_success.png")


def fig_redteam():
    d = load("redteam_results.json")
    each = d["each"]
    names = [e["technique"] for e in each]
    x = range(len(each))
    of = each[0]["of"]
    fig, ax = plt.subplots(figsize=(6.5, 3.0))
    b1 = ax.bar([i - 0.2 for i in x], [e["of"] - e["input_detected"] for e in each], 0.4, color=OFF,
                label="got past the input word list")
    b2 = ax.bar([i + 0.2 for i in x], [e["succeeded_layer_on"] for e in each], 0.4, color=ON,
                label="succeeded with the layer on")
    label_bars(ax, b1)
    label_bars(ax, b2)
    ax.set_xticks(list(x), names)
    ax.set_ylim(0, of + 0.8)
    ax.set_ylabel(f"of {of} seed attacks")
    ax.set_xlabel("disguise applied to the attack comment")
    ax.set_title("Red team: each disguise on its own")
    ax.legend(frameon=False, loc="upper left")
    save(fig, "fig09_redteam.png")


def fig_aivsai():
    """Per match: how many attack comments got past the input word list, how many attacks succeeded with
    the layer off and on, and how many harmful fixes the model wrote that the compiler gate refused."""
    d = load("aivsai_results.json")
    runs = d["runs"]
    series = [
        ("reached the model\n(past the word list)", GREY,
         lambda rows: sum(r["on"]["reached_model"] for rows_ in [rows] for r in rows_ if not r["wasted"])),
        ("succeeded, layer off", OFF, lambda rows: sum(r["off"]["broken"] for r in rows if not r["wasted"])),
        ("succeeded, layer on", ON, lambda rows: sum(r["on"]["broken"] for r in rows if not r["wasted"])),
        ("fix with print() written,\nrefused by the gate", "#6B8E23",
         lambda rows: sum(any("print" in reason for reason in r["off"]["refused"]) for r in rows if not r["wasted"])),
    ]
    names = [("vs stand-in" if "stand-in" in run["matchup"] else "vs Gemini") + "\n" + run["goal"] for run in runs]
    x = range(len(runs))
    width = 0.2
    fig, ax = plt.subplots(figsize=(6.5, 3.4))
    for j, (label, colour, count) in enumerate(series):
        bars = ax.bar([i + (j - 1.5) * width for i in x], [count(run["rows"]) for run in runs], width,
                      color=colour, label=label)
        label_bars(ax, bars)
    rounds = len(runs[0]["rows"])
    ax.set_xticks(list(x), names)
    ax.set_ylim(0, rounds + 4)
    ax.set_ylabel(f"of {rounds} rounds")
    ax.set_title("AI against AI: Gemini writes a new attack each round")
    ax.legend(frameon=False, ncol=2, fontsize=8, loc="upper center")
    save(fig, "fig10_ai_vs_ai.png")


def fig_unseen_by_language():
    """Unseen attacks that reach the model, by language, with the layer off, on, and in blind mode."""
    sys.path.insert(0, str(ROOT / "explorer"))
    os.environ.setdefault("PARC_AGENT_LLM", "none")
    import app as explorer  # noqa: E402
    data = explorer.app.test_client().post("/api/blind", json={}).get_json()
    groups = [("English", data["attacks"]["English"]), ("other languages", data["attacks"]["other"])]
    configs = [("off", "layer off", GREY), ("rules", "layer on", OFF), ("blind", "layer on, blind mode", ON)]
    x = range(len(groups))
    fig, ax = plt.subplots(figsize=(6.0, 3.0))
    for j, (cid, label, colour) in enumerate(configs):
        bars = ax.bar([i + (j - 1) * 0.27 for i in x], [g[1]["reached"][cid] for g in groups], 0.27,
                      color=colour, label=label)
        label_bars(ax, bars)
    ax.set_xticks(list(x), [f"{name} ({g['of']} attacks)" for name, g in groups])
    ax.set_ylabel("attacks that reach the model")
    ax.set_title("Unseen attacks written by a model that never saw the rules")
    ax.set_ylim(0, 14)
    ax.legend(frameon=False, ncol=3, loc="upper center", fontsize=8)
    save(fig, "fig11_unseen_by_language.png")


def fig_blind_cost():
    d = load("blind_cost.json")
    s = d["summary"]
    items = [("correct", "Correct"), ("cause", "Gives the\ncause"), ("clear", "Clear to\na student"),
             ("context", "Relates it to what\nthe code is for")]
    x = range(len(items))
    fig, ax = plt.subplots(figsize=(6.0, 3.0))
    b1 = ax.bar([i - 0.2 for i in x], [s["shown"][k] for k, _ in items], 0.4, color=ON, label="comments shown")
    b2 = ax.bar([i + 0.2 for i in x], [s["blind"][k] for k, _ in items], 0.4, color=OFF, label="blind mode")
    label_bars(ax, b1)
    label_bars(ax, b2)
    ax.set_xticks(list(x), [name for _, name in items])
    ax.set_ylim(0, s["scored"] + 5)
    ax.set_ylabel(f"of {s['scored']} explanations")
    ax.set_title(f"What blind mode costs: {s['shown']['total']} vs {s['blind']['total']} of {5 * s['scored']} rubric points")
    ax.legend(frameon=False, ncol=2, loc="upper center")
    save(fig, "fig12_blind_cost.png")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    fig_phase_times()
    fig_optimizer()
    fig_vm_vs_native()
    fig_confusion()
    fig_attack_success()
    fig_redteam()
    fig_aivsai()
    fig_unseen_by_language()
    fig_blind_cost()


if __name__ == "__main__":
    main()
