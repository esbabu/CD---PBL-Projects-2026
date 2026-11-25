try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib.ticker import MaxNLocator
    _MPL_OK = True
except ImportError:
    _MPL_OK = False

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from src.gui import theme


class SecurityGraphWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

        if not _MPL_OK:
            self._label = QLabel("Install matplotlib for security charts: pip install matplotlib")
            self._label.setStyleSheet("color: #6c757d; padding: 20px;")
            self._layout.addWidget(self._label)
            self._fig = None
            return

        self._fig = Figure(figsize=(12, 3), facecolor=theme.SURFACE)
        self._canvas = FigureCanvas(self._fig)
        self._layout.addWidget(self._canvas)

    def set_data(self, security_report=None):
        if not _MPL_OK or not self._fig:
            return

        self._fig.clear()
        self._fig.set_facecolor(theme.SURFACE)

        if security_report is None:
            ax = self._fig.add_subplot(111, facecolor=theme.BG_APP)
            ax.text(0.5, 0.5, "No security data.\nRun analysis first.",
                    ha="center", va="center", fontsize=14, color=theme.TEXT_MUTED)
            ax.set_xticks([])
            ax.set_yticks([])
            self._canvas.draw()
            return

        grid = self._fig.add_gridspec(1, 4, width_ratios=[1.0, 1.0, 1.5, 1.6])
        scores = security_report.function_scores
        issues = security_report.issues
        by_sev = security_report.by_severity
        safe_pct = security_report.module_safe_pct

        ax1 = self._fig.add_subplot(grid[0, 0], facecolor=theme.BG_APP)
        safe_count = sum(1 for s in scores.values() if s >= 80)
        unsafe_count = len(scores) - safe_count
        if scores:
            labels = ["Safe", "Unsafe"]
            sizes = [safe_count, unsafe_count]
            colors = [theme.SUCCESS, theme.DANGER]
            explode = [0.05 if unsafe_count > 0 else 0]
            # Labels go in a legend: beside a small pie they collide with the
            # percentages.  Empty slices get no percentage text.
            wedges, texts, autotexts = ax1.pie(
                sizes, colors=colors, startangle=90, radius=1.15, pctdistance=0.55,
                autopct=lambda pct: f"{pct:.0f}%" if pct >= 1 else "",
                textprops={"color": theme.SURFACE, "fontsize": 9, "fontweight": "bold"},
            )
            ax1.legend(wedges, labels, loc="upper center", bbox_to_anchor=(0.5, 0.02),
                       ncol=2, fontsize=8, frameon=False)
        else:
            ax1.text(0.5, 0.5, "N/A", ha="center", va="center", color=theme.TEXT_MUTED, fontsize=16)
        ax1.set_title(f"Safety: {safe_pct}% Safe", color=theme.TEXT, fontsize=10, fontweight="bold")

        ax2 = self._fig.add_subplot(grid[0, 1], facecolor=theme.BG_APP)
        if by_sev:
            sev_order = ["critical", "high", "medium", "low"]
            sev_colors = {"critical": theme.DANGER, "high": theme.ORANGE, "medium": theme.WARNING, "low": theme.ACCENT}
            labels = [s for s in sev_order if by_sev.get(s, 0) > 0]
            values = [by_sev.get(s, 0) for s in labels]
            colors = [sev_colors.get(s, theme.GRAY) for s in labels]
            short = {"critical": "Crit", "high": "High", "medium": "Med", "low": "Low"}
            ax2.bar([short[l] for l in labels], values, color=colors, edgecolor=theme.BORDER_STRONG, width=0.5)
            for i, v in enumerate(values):
                ax2.text(i, v, str(v), ha="center", va="bottom", color=theme.TEXT, fontsize=9)
            # headroom so the value labels never run into the title
            ax2.set_ylim(0, max(values) * 1.25)
            ax2.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax2.set_title("Issues by Severity", color=theme.TEXT, fontsize=10, fontweight="bold")
        ax2.tick_params(colors=theme.TEXT_MUTED, labelsize=8)
        ax2.set_ylabel("Count", color=theme.TEXT_SECONDARY, fontsize=10)
        for spine in ax2.spines.values():
            spine.set_color(theme.BORDER_STRONG)
        ax2.grid(True, axis="y", color=theme.BORDER, alpha=0.5)

        ax3 = self._fig.add_subplot(grid[0, 2], facecolor=theme.BG_APP)
        if scores:
            names = list(scores.keys())[:12]
            vals = [scores[n] for n in names]
            bar_colors = [theme.SUCCESS if v >= 80 else theme.WARNING if v >= 50 else theme.DANGER for v in vals]
            y_pos = range(len(names))
            ax3.barh(y_pos, vals, color=bar_colors, edgecolor=theme.BORDER_STRONG, height=0.6)
            ax3.set_yticks(list(y_pos))
            short = [n.split("@")[0].rsplit(".", 1)[-1][:22] for n in names]   # method name only: keeps the charts wide
            ax3.set_yticklabels(short, color=theme.TEXT, fontsize=8)
            ax3.set_xlim(0, 100)
            ax3.axvline(x=80, color=theme.SUCCESS, linestyle="--", alpha=0.5, linewidth=1)
        ax3.set_title("Function Security Scores", color=theme.TEXT, fontsize=10, fontweight="bold")
        ax3.set_xlabel("Score (0-100)", color=theme.TEXT_SECONDARY, fontsize=10)
        ax3.tick_params(colors=theme.TEXT_MUTED)
        for spine in ax3.spines.values():
            spine.set_color(theme.BORDER_STRONG)
        ax3.grid(True, axis="x", color=theme.BORDER, alpha=0.5)

        ax4 = self._fig.add_subplot(grid[0, 3], facecolor=theme.BG_APP)
        # The nine vulnerability classes: the eight original OWASP classes + Others (all shown, zeros included).
        from src.security.categories import CLASSES, count_by_class
        counts9 = count_by_class(i.pattern_id for i in issues)
        labels9 = [CLASSES[k][0] for k in counts9][::-1]
        values9 = list(counts9.values())[::-1]
        colors9 = [theme.GRAY if lab == "Others" else theme.PURPLE for lab in labels9]
        ax4.barh(labels9, values9, color=colors9, edgecolor=theme.BORDER_STRONG, height=0.62)
        for i, v in enumerate(values9):
            if v:
                ax4.text(v, i, f" {v}", ha="left", va="center", color=theme.TEXT, fontsize=8)
        ax4.set_xlim(0, max(1, max(values9)) * 1.35)
        ax4.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax4.set_title("Vulnerability classes", color=theme.TEXT, fontsize=10, fontweight="bold")
        ax4.tick_params(colors=theme.TEXT_MUTED, labelsize=8)
        ax4.set_xlabel("Count", color=theme.TEXT_SECONDARY, fontsize=10)
        for spine in ax4.spines.values():
            spine.set_color(theme.BORDER_STRONG)
        ax4.grid(True, axis="x", color=theme.BORDER, alpha=0.5)

        self._fig.tight_layout(pad=1.2, w_pad=2.0)
        self._canvas.draw()
