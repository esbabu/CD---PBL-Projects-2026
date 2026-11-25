"""
Performance workspace — model dashboards and block-wise pipeline analytics
===========================================================================
Tabs
  Comparison       the three engines side by side (accuracy, precision, recall, F1, FPR, FNR, latency)
  Rule-Based       per-language metrics, confusion matrix, per-family recall, latency
  ML Model         the same for the ML detector (+ per-language training configuration)
  Neuro-Symbolic   the same for the fusion engine
  Pipeline         block-wise time, memory and throughput per language from the benchmark,
                   and a live profile of the code in the Generator editor

All figures come from result files written by the evaluation commands:
  outputs/eval/model_comparison.json  ← python -m src.vulnml.pipeline evaluate
  outputs/vulnml/<lang>_metrics.json  ← python -m src.vulnml.pipeline train
  outputs/perf/benchmark.json         ← python -m src.perfbench
Nothing is hard-coded; a missing file shows the command that produces it.
"""
from __future__ import annotations

import json
import os
from typing import Optional

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (QHBoxLayout, QLabel, QPushButton, QScrollArea, QTableWidget, QTableWidgetItem,
                             QTabWidget, QVBoxLayout, QWidget)

from src.gui import theme

try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    _MPL = True
except ImportError:
    _MPL = False

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
EVAL = os.path.join(ROOT, "outputs", "eval", "model_comparison.json")
BENCH = os.path.join(ROOT, "outputs", "perf", "benchmark.json")
ENGINES = [("rules", "Rule-Based"), ("ml", "ML Model"), ("neurosymbolic", "Neuro-Symbolic")]
LANG_NAMES = {"python": "Python", "java": "Java", "csharp": "C#", "c": "C", "cpp": "C++", "rust": "Rust", "cobol": "COBOL"}
METRICS = ["accuracy", "precision", "recall", "f1", "fpr", "fnr"]


def _load(path: str) -> Optional[dict]:
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def _fmt(v) -> str:
    if v is None:
        return "—"
    if isinstance(v, float):
        return f"{v:,.0f}" if abs(v) >= 100 else (f"{v:.1f}" if abs(v) >= 10 else f"{v:.3f}")
    return str(v)


def _table(headers, rows) -> QTableWidget:
    t = QTableWidget(len(rows), len(headers))
    t.setHorizontalHeaderLabels(headers)
    t.verticalHeader().setVisible(False)
    t.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    for r, row in enumerate(rows):
        for c, v in enumerate(row):
            t.setItem(r, c, QTableWidgetItem(_fmt(v)))
    t.resizeColumnsToContents()
    t.resizeRowsToContents()
    t.horizontalHeader().setStretchLastSection(True)
    return t


def _fit(t: QTableWidget, max_rows: int = 12) -> QTableWidget:
    """Height that shows every row (up to max_rows) without a scroll bar."""
    rows = min(t.rowCount(), max_rows)
    h = t.horizontalHeader().height() + sum(t.rowHeight(r) for r in range(rows)) + 2 * t.frameWidth() + 4
    t.setFixedHeight(h)
    return t


def _canvas(w=10, h=3.2):
    fig = Figure(figsize=(w, h), facecolor=theme.SURFACE)
    canvas = FigureCanvas(fig)
    canvas.setMinimumHeight(int(h * 100))          # keeps charts readable inside the scroll area
    return fig, canvas


def _wrap(text: str) -> QLabel:
    lab = QLabel(text)
    lab.setWordWrap(True)
    return lab


def _scroll(w: QWidget) -> QScrollArea:
    sa = QScrollArea()
    sa.setWidgetResizable(True)
    sa.setFrameShape(QScrollArea.Shape.NoFrame)
    sa.setWidget(w)
    return sa


def _style(ax, title):
    ax.set_facecolor(theme.BG_APP)
    ax.set_title(title, color=theme.TEXT, fontsize=10, fontweight="bold")
    ax.tick_params(colors=theme.TEXT_MUTED, labelsize=8)
    for s in ax.spines.values():
        s.set_color(theme.BORDER_STRONG)
    ax.grid(True, axis="y", color=theme.BORDER, alpha=0.5)


def _confusion(ax, cm, title):
    import numpy as np
    m = np.array([[cm["tn"], cm["fp"]], [cm["fn"], cm["tp"]]])
    ax.imshow(m, cmap="Blues")
    for (i, j), v in np.ndenumerate(m):
        ax.text(j, i, str(v), ha="center", va="center", fontsize=11,
                color="white" if v > m.max() / 2 else theme.TEXT, fontweight="bold")
    ax.set_xticks([0, 1], ["pred. safe", "pred. vulnerable"], fontsize=8)
    ax.set_yticks([0, 1], ["safe", "vulnerable"], fontsize=8)
    ax.set_title(title, color=theme.TEXT, fontsize=10, fontweight="bold")


class _ProfileWorker(QThread):
    done = pyqtSignal(object)

    def __init__(self, code: str, language: str):
        super().__init__()
        self.code, self.language = code, language

    def run(self):
        import tempfile
        from src import perf
        from src.languages import LANGUAGES
        from src.perfbench import run_file
        ext = LANGUAGES[self.language].extensions[0]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "editor" + ext)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(self.code)
            try:
                run_file(path, self.language)                       # warm-up
                with perf.profile(memory=False) as t:
                    info = run_file(path, self.language)
                with perf.profile(memory=True) as m:
                    run_file(path, self.language)
                self.done.emit({"time": t.by_block(), "mem": m.by_block(), "total_ms": t.total_ms, **info})
            except Exception as exc:                                # shown in the panel, never raised
                self.done.emit({"error": f"{type(exc).__name__}: {exc}"})


class PerformanceWorkspace(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.code_provider = None              # set by the main window: () -> (code, language)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 16, 24, 16)
        head = QHBoxLayout()
        title = QLabel("Performance")
        title.setProperty("class", "PageTitle")
        head.addWidget(title)
        head.addStretch()
        self.btn_reload = QPushButton("Reload results")
        self.btn_reload.setProperty("class", "SecondaryButton")
        self.btn_reload.clicked.connect(lambda _=False: self.reload())
        head.addWidget(self.btn_reload)
        lay.addLayout(head)
        self.caption = QLabel("")
        self.caption.setProperty("class", "Caption")
        self.caption.setWordWrap(True)
        lay.addWidget(self.caption)
        self.tabs = QTabWidget()
        lay.addWidget(self.tabs)
        self._worker = None
        self.reload()

    # ── building ─────────────────────────────────────────────────────────
    def reload(self):
        self.tabs.clear()
        ev, bench = _load(EVAL), _load(BENCH)
        self.eval_data, self.bench_data = ev, bench
        parts = []
        parts.append(f"model evaluation: {os.path.relpath(EVAL, ROOT)}" if ev else
                     "no model evaluation yet — run: python -m src.vulnml.pipeline all")
        parts.append(f"benchmark: {os.path.relpath(BENCH, ROOT)}" if bench else
                     "no benchmark yet — run: python -m src.perfbench")
        self.caption.setText("   ·   ".join(parts))
        self.tabs.addTab(_scroll(self._comparison_tab(ev)), "Comparison")
        for key, label in ENGINES:
            self.tabs.addTab(_scroll(self._model_tab(ev, key, label)), label)
        self.tabs.addTab(_scroll(self._pipeline_tab(bench)), "Pipeline")

    def _empty(self, text: str) -> QWidget:
        w = QLabel(text)
        w.setProperty("class", "EmptyState")
        w.setWordWrap(True)
        return w

    def _latency(self, ev, engine: str, lang: Optional[str] = None) -> Optional[float]:
        vals = [v for k, v in ev.get("latency_ms", {}).items()
                if k.split(":")[0] == engine and (lang is None or k.endswith(":" + lang))]
        if not vals:
            return None
        n = sum(v["n"] for v in vals)
        return round(sum(v["mean"] * v["n"] for v in vals) / n, 3) if n else None

    def _comparison_tab(self, ev) -> QWidget:
        if not ev:
            return self._empty("Run python -m src.vulnml.pipeline all to evaluate the three engines.")
        w = QWidget()
        lay = QVBoxLayout(w)
        o = ev["overall"]
        rows = [[label] + [o[k].get(m) for m in METRICS] + [o[k]["n"], self._latency(ev, k)] for k, label in ENGINES]
        lay.addWidget(_wrap(f"Same held-out test units ({ev['unit']}); decision rules: "
                            + "; ".join(f"{l}: {ev['decision'][k]}" for k, l in ENGINES)))
        t = _table(["Engine", "Accuracy", "Precision", "Recall", "F1", "FPR", "FNR", "n", "Mean latency (ms)"], rows)
        _fit(t)
        lay.addWidget(t)
        if _MPL:
            fig, canvas = _canvas(12, 3.4)
            ax1 = fig.add_subplot(1, 3, 1)
            import numpy as np
            x = np.arange(4)
            for i, (k, label) in enumerate(ENGINES):
                vals = [o[k].get(m) or 0 for m in ("accuracy", "precision", "recall", "f1")]
                ax1.bar(x + (i - 1) * 0.27, vals, 0.27, label=label,
                        color=[theme.ACCENT, theme.PURPLE, theme.SUCCESS][i])
            ax1.set_xticks(x, ["Acc", "Prec", "Rec", "F1"])
            ax1.set_ylim(0, 1.05)
            ax1.legend(fontsize=7)
            _style(ax1, "Overall metrics")
            ax2 = fig.add_subplot(1, 3, 2)
            langs = [l for l in ev["by_language"]]
            x = np.arange(len(langs))
            for i, (k, label) in enumerate(ENGINES):
                ax2.bar(x + (i - 1) * 0.27, [ev["by_language"][l][k].get("f1") or 0 for l in langs], 0.27,
                        color=[theme.ACCENT, theme.PURPLE, theme.SUCCESS][i], label=label)
            ax2.set_xticks(x, [LANG_NAMES.get(l, l) for l in langs], fontsize=8)
            ax2.set_ylim(0, 1.05)
            _style(ax2, "F1 by language")
            ax3 = fig.add_subplot(1, 3, 3)
            lat = [self._latency(ev, k) or 0 for k, _ in ENGINES]
            bars = ax3.bar([l for _, l in ENGINES], lat, color=[theme.ACCENT, theme.PURPLE, theme.SUCCESS])
            for b, v in zip(bars, lat):
                ax3.text(b.get_x() + b.get_width() / 2, v, f"{v:.1f}", ha="center", va="bottom", fontsize=8,
                         color=theme.TEXT)
            _style(ax3, "Mean latency per unit (ms)")
            fig.tight_layout()
            lay.addWidget(canvas)
        return w

    def _model_tab(self, ev, key: str, label: str) -> QWidget:
        if not ev:
            return self._empty("Run python -m src.vulnml.pipeline all.")
        w = QWidget()
        lay = QVBoxLayout(w)
        rows = []
        for lang, d in ev["by_language"].items():
            m = d[key]
            extra = []
            if key == "ml":
                cfg = _load(os.path.join(ROOT, "outputs", "vulnml", f"{lang}_config.json")) or {}
                ch = cfg.get("chosen", {})
                extra = [f"C={ch.get('C')} ngram={ch.get('ngram')}" if ch else "—"]
            rows.append([LANG_NAMES.get(lang, lang)] + [m.get(x) for x in METRICS] + [m["n"], self._latency(ev, key, lang)]
                        + extra)
        heads = ["Language", "Accuracy", "Precision", "Recall", "F1", "FPR", "FNR", "n", "Mean latency (ms)"]
        if key == "ml":
            heads.append("Chosen hyperparameters")
        t = _table(heads, rows)
        _fit(t)
        lay.addWidget(t)
        loc = ev.get("locations_long_programs", {}).get(key)
        if loc:
            lay.addWidget(_wrap("Long programs, exact (rule, line) matches: " + "; ".join(
                f"{LANG_NAMES.get(l, l)} P {_fmt(v['precision'])} R {_fmt(v['recall'])}" for l, v in loc.items())))
        if _MPL:
            fig, canvas = _canvas(12, 3.2)
            _confusion(fig.add_subplot(1, 3, 1), ev["overall"][key]["confusion"], f"{label}: confusion (all languages)")
            ax = fig.add_subplot(1, 3, 2)
            fams = [(f, v.get(key)) for f, v in ev.get("by_family_recall", {}).items() if v.get(key) is not None and v["n"] >= 5]
            fams = sorted(fams, key=lambda kv: kv[1])[-14:]
            ax.barh([f for f, _ in fams], [v for _, v in fams], color=theme.PURPLE)
            ax.set_xlim(0, 1)
            ax.tick_params(labelsize=7)
            _style(ax, "Recall by vulnerability family (n ≥ 5)")
            ax3 = fig.add_subplot(1, 3, 3)
            langs = list(ev["by_language"])
            ax3.bar([LANG_NAMES.get(l, l) for l in langs], [self._latency(ev, key, l) or 0 for l in langs],
                    color=theme.ACCENT)
            ax3.set_yscale("log")
            _style(ax3, "Mean latency per unit (ms, log)")
            fig.tight_layout()
            lay.addWidget(canvas)
        return w

    def _pipeline_tab(self, bench) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        row = QHBoxLayout()
        self.btn_profile = QPushButton("Profile editor code")
        self.btn_profile.setProperty("class", "PrimaryButton")
        self.btn_profile.setToolTip("Run the whole tool on the Generator editor's code and measure every block "
                                    "(timing pass + memory pass).")
        self.btn_profile.clicked.connect(lambda _=False: self.profile_editor())
        row.addWidget(self.btn_profile)
        self.profile_label = QLabel("")
        self.profile_label.setWordWrap(True)
        row.addWidget(self.profile_label, 1)
        lay.addLayout(row)
        self.live_holder = QVBoxLayout()
        lay.addLayout(self.live_holder)
        if not bench:
            lay.addWidget(self._empty("Run python -m src.perfbench for the block-wise benchmark."))
            return w
        langs = list(bench["languages"])
        rows = []
        for l in langs:
            d = bench["languages"][l]
            e = d["end_to_end"]
            rows.append([LANG_NAMES.get(l, l), d["files"], d["lines"], e["mean_ms_per_file"], e["p95_ms_per_file"],
                         e["lines_per_second"], e["peak_kb_memory_pass"], d["bottleneck"]])
        t = _table(["Language", "Files", "Lines", "Mean ms/file", "p95 ms/file", "Lines/s", "Peak heap (KB)", "Bottleneck"],
                   rows)
        _fit(t)
        lay.addWidget(t)
        if _MPL:
            import numpy as np
            fig, canvas = _canvas(12, 3.6)
            ax = fig.add_subplot(1, 2, 1)
            groups = list(next(iter(bench["languages"].values()))["groups"])
            left = np.zeros(len(langs))
            colors = [theme.ACCENT, theme.TEAL, theme.GRAY, theme.ORANGE, theme.DANGER, theme.PURPLE, theme.SUCCESS,
                      theme.WARNING, "#0ea5e9", "#a3a3a3"]
            for i, g in enumerate(groups):
                vals = np.array([bench["languages"][l]["groups"][g]["mean_ms_per_file"] for l in langs])
                ax.barh([LANG_NAMES.get(l, l) for l in langs], vals, left=left, label=g, color=colors[i % len(colors)])
                left += vals
            ax.legend(fontsize=6, loc="upper right")
            _style(ax, "Mean time per file by block (ms)")
            ax2 = fig.add_subplot(1, 2, 2)
            og = bench["overall_groups"]
            names = sorted(og, key=lambda g: og[g]["total_ms"])
            ax2.barh(names, [og[g]["share"] * 100 for g in names], color=theme.PURPLE)
            ax2.tick_params(labelsize=7)
            _style(ax2, f"Share of time, all languages (%); bottleneck: {bench['overall_bottleneck']}")
            fig.tight_layout()
            lay.addWidget(canvas)
        return w

    # ── live profile ─────────────────────────────────────────────────────
    def profile_editor(self):
        if self.code_provider is None:
            return
        code, language = self.code_provider()
        if not code.strip():
            self.profile_label.setText("The Generator editor is empty.")
            return
        self.btn_profile.setEnabled(False)
        self.profile_label.setText(f"Profiling {LANG_NAMES.get(language, language)} code…")
        self._worker = _ProfileWorker(code, language)
        self._worker.done.connect(self._show_profile)
        self._worker.start()

    def _show_profile(self, res: dict):
        self.btn_profile.setEnabled(True)
        while self.live_holder.count():
            item = self.live_holder.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        if "error" in res:
            self.profile_label.setText("Profiling failed: " + res["error"])
            return
        tb, mb = res["time"], res["mem"]
        self.profile_label.setText(f"Editor code: {res['lines']} lines, {res['findings']} findings, "
                                   f"{res['comments']} comments; end-to-end {tb.get('e2e', {}).get('total_ms')} ms "
                                   "(after a warm-up run; memory measured in a second pass)")
        names = [k for k in tb if k != "e2e"]
        rows = [[k, tb[k]["calls"], tb[k]["total_ms"], (mb.get(k) or {}).get("peak_kb")] for k in names]
        t = _table(["Block", "Calls", "Time (ms)", "Peak heap (KB)"], rows)
        _fit(t, 10)
        self.live_holder.addWidget(t)
        self.live_rows = rows


__all__ = ["PerformanceWorkspace"]
