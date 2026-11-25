from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton,
    QScrollArea, QFrame, QGroupBox, QGridLayout, QSplitter
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import traceback

from src.agent import SecurityAgent


class AgentAnalysisWorker(QThread):
    """Runs local agent analysis away from the Qt GUI thread."""
    result_ready = pyqtSignal(object)

    def __init__(self, agent, source_code, language, filename):
        super().__init__()
        self.agent = agent
        self.source_code = source_code
        self.language = language
        self.filename = filename

    def run(self):
        try:
            result = self.agent.analyze(
                self.source_code, language=self.language, filename=self.filename
            )
        except Exception as exc:
            result = {
                "success": False,
                "error": f"Agent analysis failed: {exc}\n\n{traceback.format_exc()}",
                "language": self.language,
                "malware_assessment": {
                    "status": "inconclusive",
                    "headline": "MALWARE ASSESSMENT INCONCLUSIVE",
                    "summary": "The analysis raised an internal error. No clean result can be reported.",
                    "language": self.language,
                    "filename": self.filename,
                    "findings": [],
                    "scanned_lines": 0,
                    "method": "static source inspection; scan did not complete",
                },
            }
        self.result_ready.emit(result)


class AgenticWorkspace(QWidget):
    """Agentic security workspace fed directly by the Generator workspace."""

    # Publishes the latest safer alternative to the Generator workspace.
    alternative_ready = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.agent = SecurityAgent()
        self.source_code = ""
        self.annotated_code = ""
        self.language = "python"
        self.filename = ""
        self.agent_worker = None
        self._last_agent_result = None
        self.setup_ui()

    def setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(22, 20, 22, 20)
        outer.setSpacing(12)
       

        header = QHBoxLayout()
        title = QLabel("Agentic Security Analyzer")
        title.setStyleSheet("font-size:24px; font-weight:800; color:#172554;")
        header.addWidget(title)
        header.addStretch()
        badge = QLabel("● LOCAL AGENT • NO API REQUIRED")
        badge.setStyleSheet(
            "color:#15803d; background:#f0fdf4; border:1px solid #bbf7d0; "
            "padding:7px 11px; border-radius:8px; font-weight:700;"
        )
        header.addWidget(badge)
        outer.addLayout(header)

        self.malware_card = QGroupBox("Malware Behaviour Assessment")
        self.malware_card.setStyleSheet(self._group_style())
        malware_layout = QVBoxLayout(self.malware_card)
        self.malware_headline = QLabel("MALWARE ASSESSMENT WAITING FOR SOURCE CODE")
        self.malware_headline.setWordWrap(True)
        self.malware_headline.setStyleSheet(self._malware_headline_style("info"))
        malware_layout.addWidget(self.malware_headline)
        self.malware_details = QTextEdit()
        self.malware_details.setReadOnly(True)
        self.malware_details.setFixedHeight(95)
        self.malware_details.setPlainText(
            "Generate comments from the Generator workspace. The source will be scanned automatically.\n"
            "This is static source inspection: the submitted program is not executed."
        )
        self.malware_details.setStyleSheet(
            "QTextEdit { background:#f8fafc; border:1px solid #e2e8f0; border-radius:7px; "
            "padding:8px; color:#475569; font-family:Consolas; font-size:11px; }"
        )
        malware_layout.addWidget(self.malware_details)
        

        sub = QLabel(
            "The Agent receives code automatically from Generator — no copy/paste required. "
            "It observes, plans, analyzes, prioritizes, and provides safer-code recommendations where supported."
        )
        sub.setWordWrap(True)
        sub.setStyleSheet("font-size:13px; color:#64748b; padding-bottom:4px;")
        

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(
            "QScrollArea { background:transparent; border:none; } "
            "QScrollBar:vertical { width:10px; margin:2px; } "
            "QScrollBar::handle:vertical { background:#cbd5e1; border-radius:5px; min-height:30px; }"
        )

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(4, 4, 12, 20)
        layout.setSpacing(12)

# Add Malware Assessment inside the main scroll area
        layout.addWidget(self.malware_card)

# Add the explanatory text inside the same scroll area
        layout.addWidget(sub)


        info = QGroupBox("How the Agent Works")
        info.setStyleSheet(self._group_style())
        info_layout = QGridLayout(info)
        info_layout.setSpacing(8)
        steps = [
            ("01", "Observe", "Receive code from Generator"),
            ("02", "Plan", "Select relevant checks"),
            ("03", "Analyze", "Security + quality analysis"),
            ("04", "Prioritize", "Risk + severity scoring"),
            ("05", "Repair", "Build safer alternative"),
            ("06", "Report", "Explain changes + review items"),
        ]
        for col, (num, name, desc) in enumerate(steps):
            box = QLabel(f"{num}\n{name}\n{desc}")
            box.setAlignment(Qt.AlignmentFlag.AlignCenter)
            box.setMinimumHeight(82)
            box.setStyleSheet(
                "background:#f8fafc; border:1px solid #e2e8f0; border-radius:9px; "
                "color:#334155; padding:7px; font-size:11px;"
            )
            info_layout.addWidget(box, 0, col)
        layout.addWidget(info)

        source_header = QHBoxLayout()
        source_title = QLabel("Source Code from Generator")
        source_title.setStyleSheet("font-size:16px; font-weight:700; color:#1e293b;")
        source_header.addWidget(source_title)
        source_header.addStretch()
        self.source_badge = QLabel("WAITING FOR GENERATOR")
        self.source_badge.setStyleSheet(
            "color:#64748b; background:#f1f5f9; border:1px solid #cbd5e1; "
            "padding:5px 9px; border-radius:7px; font-size:11px; font-weight:700;"
        )
        source_header.addWidget(self.source_badge)
        layout.addLayout(source_header)

        self.code_input = QTextEdit()
        self.code_input.setReadOnly(True)
        self.code_input.setPlaceholderText(
            "Generate comments in the Generator workspace first. The source code will appear here automatically."
        )
        self.code_input.setMinimumHeight(210)
        self.code_input.setMaximumHeight(330)
        self.code_input.setStyleSheet(self._editor_style())
        layout.addWidget(self.code_input)

        actions = QHBoxLayout()
        self.run_button = QPushButton("Analyze Generated Code")
        self.run_button.setMinimumHeight(44)
        self.run_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.run_button.setStyleSheet(self._primary_button())
        self.run_button.clicked.connect(self.run_agent)
        self.run_button.setEnabled(False)
        actions.addWidget(self.run_button)

        self.clear_button = QPushButton("Clear Analysis")
        self.clear_button.setMinimumHeight(44)
        self.clear_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_button.setStyleSheet(self._secondary_button())
        self.clear_button.clicked.connect(self.clear_analysis)
        actions.addWidget(self.clear_button)
        actions.addStretch()
        layout.addLayout(actions)

        self.status_card = QLabel(
            "Waiting for the Generator. Run 'Generate & Attach Comments' to send code to the agent."
        )
        self.status_card.setWordWrap(True)
        self.status_card.setStyleSheet(self._status_style("info"))
        layout.addWidget(self.status_card)

        activity_title = QLabel("Agent Activity")
        activity_title.setStyleSheet("font-size:16px; font-weight:700; color:#1e293b;")
        layout.addWidget(activity_title)
        self.activity = QTextEdit()
        self.activity.setReadOnly(True)
        self.activity.setMinimumHeight(150)
        self.activity.setMaximumHeight(230)
        self.activity.setStyleSheet(
            "QTextEdit { background:#0f172a; color:#dbeafe; border:0; border-radius:9px; "
            "padding:13px; font-family:Consolas; font-size:12px; }"
        )
        layout.addWidget(self.activity)

        result_title = QLabel("Agent Decision & Security Report")
        result_title.setStyleSheet("font-size:16px; font-weight:700; color:#1e293b;")
        layout.addWidget(result_title)
        self.result = QTextEdit()
        self.result.setReadOnly(True)
        self.result.setMinimumHeight(300)
        self.result.setStyleSheet(self._editor_style())
        layout.addWidget(self.result)

        secure_title = QLabel("Best Recommended Secure Alternative")
        secure_title.setStyleSheet("font-size:16px; font-weight:700; color:#166534;")
        layout.addWidget(secure_title)

        self.secure_code = QTextEdit()
        self.secure_code.setReadOnly(True)
        self.secure_code.setMinimumHeight(360)
        self.secure_code.setStyleSheet(
            "QTextEdit { background:#f0fdf4; border:1px solid #86efac; border-radius:9px; "
            "padding:14px; font-family:Consolas, 'Courier New'; font-size:13px; color:#14532d; }"
        )
        self.secure_code.setPlaceholderText(
            "The agent's safer code alternative will appear here after analysis."
        )
        layout.addWidget(self.secure_code)

        review_title = QLabel("Secure Rewrite Notes")
        review_title.setStyleSheet("font-size:16px; font-weight:700; color:#1e293b;")
        layout.addWidget(review_title)
        self.review = QTextEdit()
        self.review.setReadOnly(True)
        self.review.setMinimumHeight(180)
        self.review.setStyleSheet(self._editor_style())
        layout.addWidget(self.review)

        scroll.setWidget(content)
        outer.addWidget(scroll, 1)

    def set_source_code(self, source_code, annotated_code="", language="python", filename="", auto_analyze=True):
        """Receive source and its language directly from GeneratorWorkspace."""
        self.source_code = (source_code or "").strip()
        self.annotated_code = annotated_code or ""
        self.language = language or "python"
        self.filename = filename or ""
        self.alternative_ready.emit("", self.language)  # invalidate any older alternative
        self.code_input.setPlainText(self.source_code)

        if self.source_code:
            self.source_badge.setText("SOURCE RECEIVED ✓")
            self.source_badge.setStyleSheet(
                "color:#166534; background:#f0fdf4; border:1px solid #bbf7d0; "
                "padding:5px 9px; border-radius:7px; font-size:11px; font-weight:700;"
            )
            self.run_button.setEnabled(True)
            self.status_card.setText(
                f"{self.language.upper()} source received from Generator. The agent is ready to scan security and malware-behaviour indicators."
            )
            self.status_card.setStyleSheet(self._status_style("info"))
            if auto_analyze:
                self.run_agent()
        else:
            self.clear_analysis()

    def run_agent(self):
        """Start analysis asynchronously so an analysis exception cannot close the GUI."""
        code = self.source_code.strip()
        if not code:
            self.status_card.setText("No source code has been received from Generator yet.")
            self.status_card.setStyleSheet(self._status_style("warning"))
            return

        if self.agent_worker is not None and self.agent_worker.isRunning():
            self.status_card.setText("Analysis is already running. Please wait for the current scan to finish.")
            self.status_card.setStyleSheet(self._status_style("info"))
            return

        self.run_button.setEnabled(False)
        self.clear_button.setEnabled(False)
        self.alternative_ready.emit("", self.language)  # disable any previous result while rescanning
        self.status_card.setText(
            f"Agent is analyzing the {self.language.upper()} source. The GUI will remain responsive."
        )
        self.status_card.setStyleSheet(self._status_style("info"))
        repair_step = ("✓ Generating supported safer-code alternative..." if self.language == "python"
                       else "✓ Preparing language-specific remediation guidance...")
        self.activity.setPlainText(
            "AGENT STARTED\n\n"
            "✓ Observing code received from Generator...\n"
            f"✓ Inspecting {self.language.upper()} source structure...\n"
            "✓ Creating analysis plan...\n"
            "✓ Running security analysis...\n"
            "✓ Running code-quality checks where supported...\n"
            "✓ Correlating malware-behaviour indicators...\n"
            "✓ Prioritizing risks...\n"
            + repair_step + "\n"
            "✓ Preparing final report..."
        )

        worker = AgentAnalysisWorker(self.agent, code, self.language, self.filename)
        self.agent_worker = worker
        worker.result_ready.connect(self._on_agent_result)
        worker.finished.connect(self._on_agent_thread_finished)
        worker.start()

    def _on_agent_result(self, result):
        """Render a worker result defensively; GUI rendering errors are shown, not fatal."""
        self._last_agent_result = result
        try:
            self._render_agent_result(result)
        except Exception as exc:
            error_text = f"Could not display the analysis result: {exc}\n\n{traceback.format_exc()}"
            self.status_card.setText("Analysis finished, but displaying the report failed. See details below.")
            self.status_card.setStyleSheet(self._status_style("error"))
            self.result.setPlainText(error_text)
            self.malware_headline.setText("MALWARE ASSESSMENT INCONCLUSIVE")
            self.malware_headline.setStyleSheet(self._malware_headline_style("info"))
            self.malware_details.setPlainText(
                "The malware assessment could not be displayed because an internal error occurred. "
                "Do not interpret this as a clean scan.\n\n" + error_text
            )

    def _render_agent_result(self, result):
        # The successful SecurityAgent response stores the assessment both at
        # the top level and inside report for backwards compatibility. Read
        # either location so the malware panel never silently shows 0 lines.
        assessment = result.get("malware_assessment")
        if not assessment:
            report_payload = result.get("report") or {}
            assessment = report_payload.get("malware_assessment")
        if not assessment:
            assessment = {
                "status": "inconclusive",
                "headline": "MALWARE ASSESSMENT INCONCLUSIVE",
                "summary": "The malware scanner result was not included in the agent response. This is not a clean scan.",
                "language": self.language,
                "findings": [],
                "scanned_lines": 0,
                "method": "static source inspection",
            }
        self._render_malware_assessment(assessment)

        if not result.get("success"):
            self.status_card.setText(
                f"Agent could not complete the {self.language.upper()} analysis. Review the error below."
            )
            self.status_card.setStyleSheet(self._status_style("error"))
            self.result.setPlainText("Agent Error\n\n" + result.get("error", "Unknown agent error."))
            self.secure_code.clear()
            self.alternative_ready.emit("", self.language)
            self.review.clear()
            return

        report = result["report"]
        risk = report["risk"]
        score = report["score"]
        self.activity.append("\n\n✓ Agent decision:\n" + report["agent_decision"])
        self.result.setPlainText(
            report["text"].split("RECOMMENDED SECURE ALTERNATIVE", 1)[0].rstrip()
            + "\n\nAGENT DECISION\n" + report["agent_decision"]
        )

        alternative = report.get("secure_alternative", {})
        alternative_code = alternative.get("code", "") or ""
        self.secure_code.setPlainText(alternative_code)
        self.alternative_ready.emit(alternative_code, self.language)
        review_lines = []
        if alternative.get("changes"):
            review_lines.append("CHANGES MADE BY THE AGENT")
            review_lines.extend("• " + item for item in alternative["changes"])
        if alternative.get("limitations"):
            if review_lines:
                review_lines.append("")
            review_lines.append("MANUAL REVIEW REQUIRED")
            review_lines.extend("• " + item for item in alternative["limitations"])
        if not review_lines:
            review_lines.append("No automatic security rewrite was necessary. Continue with normal code review.")
        review_lines.append("")
        review_lines.append("The secure alternative is a defensive recommendation, not a guarantee of complete security.")
        self.review.setPlainText("\n".join(review_lines))

        if risk == "LOW":
            self.status_card.setStyleSheet(self._status_style("success"))
        elif risk == "MEDIUM":
            self.status_card.setStyleSheet(self._status_style("warning"))
        else:
            self.status_card.setStyleSheet(self._status_style("error"))
        alternative_ready = bool(alternative.get("code"))
        outcome = "Safer alternative prepared" if alternative_ready else "Remediation guidance prepared"
        self.status_card.setText(
            f"Agent complete • Risk: {risk} • Security Score: {score}/100 • {outcome}"
        )

    def _on_agent_thread_finished(self):
        worker = self.sender()
        if worker is self.agent_worker:
            self.agent_worker = None
        if worker is not None:
            worker.deleteLater()
        self.run_button.setEnabled(bool(self.source_code))
        self.clear_button.setEnabled(True)

    def _render_malware_assessment(self, assessment):
        status = assessment.get("status", "inconclusive")
        headline = assessment.get("headline", "MALWARE ASSESSMENT INCONCLUSIVE")
        summary = assessment.get("summary", "The scanner did not return a result.")
        styles = {
            "no_indicators": ("success", "#166534"),
            "suspicious": ("warning", "#9a3412"),
            "high_risk": ("error", "#991b1b"),
            "inconclusive": ("info", "#1d4ed8"),
        }
        # dict.get evaluates its default argument immediately. Referencing
        # styles["info"] here raised KeyError because "info" is a display
        # style, not one of the assessment status keys. Keep a tuple fallback
        # so both unknown statuses and normal scan outcomes render safely.
        kind, _ = styles.get(status, ("info", "#1d4ed8"))
        self.malware_headline.setText(headline)
        self.malware_headline.setStyleSheet(self._malware_headline_style(kind))
        lines = [summary, "", f"Language: {assessment.get('language', self.language)}",
                 f"Method: {assessment.get('method', 'static source inspection')} ",
                 f"Lines scanned: {assessment.get('scanned_lines', 0)}"]
        findings = assessment.get("findings", [])
        if findings:
            lines += ["", "DETECTED INDICATORS:"]
            for finding in findings:
                line_start = finding.get("line", "?")
                line_end = finding.get("line_end", line_start)
                line_label = f"line {line_start}" if line_end == line_start else f"lines {line_start}-{line_end}"
                location = f"{finding.get('filename') or self.filename or '<source>'}:{line_label}"
                lines += [
                    f"[{finding.get('severity', 'unknown').upper()}] {finding.get('id')} — {finding.get('title', 'Suspicious behaviour')}",
                    f"Where: {location} | Function: {finding.get('function', 'source/module')}",
                    f"Evidence: {finding.get('evidence', '')}",
                    f"Why flagged: {finding.get('message', '')}",
                    f"Recommended action: {finding.get('fix', '')}",
                    "",
                ]
        else:
            lines += ["", "No configured malware-behaviour indicators were found."]
        lines += ["", "Important: a clean static scan does not prove that code is malware-free. The program was not executed."]
        self.malware_details.setPlainText("\n".join(lines))

    @staticmethod
    def _malware_headline_style(kind):
        colors = {
            "success": ("#dcfce7", "#166534", "#86efac"),
            "warning": ("#fff7ed", "#9a3412", "#fdba74"),
            "error": ("#fee2e2", "#991b1b", "#fca5a5"),
            "info": ("#eff6ff", "#1d4ed8", "#bfdbfe"),
        }
        bg, fg, border = colors.get(kind, colors["info"])
        return (f"background:{bg}; color:{fg}; border:1px solid {border}; "
                "border-radius:7px; padding:9px; font-weight:800; font-size:13px;")

    def clear_analysis(self):
        """Clear results but keep the source received from Generator."""
        if self.agent_worker is not None and self.agent_worker.isRunning():
            self.status_card.setText("Please wait until the current analysis finishes before clearing its results.")
            self.status_card.setStyleSheet(self._status_style("warning"))
            return
        self.activity.clear()
        self.result.clear()
        self.secure_code.clear()
        self.alternative_ready.emit("", self.language)
        self.review.clear()
        self.malware_headline.setText("MALWARE ASSESSMENT NOT RUN")
        self.malware_headline.setStyleSheet(self._malware_headline_style("info"))
        self.malware_details.setPlainText("Run Agentic Security analysis to scan the linked source code.\nThe scanner performs static inspection and never executes submitted code.")
        if self.source_code:
            self.status_card.setText(
                "Source code is still linked from Generator. Click 'Analyze Generated Code' to run the agent again."
            )
            self.status_card.setStyleSheet(self._status_style("info"))
            self.run_button.setEnabled(True)
        else:
            self.status_card.setText(
                "Waiting for the Generator. Run 'Generate & Attach Comments' to send code to the agent."
            )
            self.status_card.setStyleSheet(self._status_style("info"))
            self.run_button.setEnabled(False)

    @staticmethod
    def _group_style():
        return (
            "QGroupBox { font-weight:700; color:#1e293b; border:1px solid #e2e8f0; "
            "border-radius:9px; margin-top:8px; padding-top:12px; background:white; } "
            "QGroupBox::title { subcontrol-origin:margin; left:12px; padding:0 5px; }"
        )

    @staticmethod
    def _editor_style():
        return (
            "QTextEdit { background:#ffffff; border:1px solid #cbd5e1; border-radius:9px; "
            "padding:12px; font-family:Consolas, 'Courier New'; font-size:13px; color:#111827; } "
            "QTextEdit:focus { border:2px solid #2563eb; }"
        )

    @staticmethod
    def _primary_button():
        return (
            "QPushButton { background:#2563eb; color:white; border:0; border-radius:8px; "
            "padding:10px 24px; font-weight:700; } "
            "QPushButton:hover { background:#1d4ed8; } "
            "QPushButton:disabled { background:#94a3b8; }"
        )

    @staticmethod
    def _secondary_button():
        return (
            "QPushButton { background:#f1f5f9; color:#334155; border:1px solid #cbd5e1; "
            "border-radius:8px; padding:10px 24px; font-weight:700; } "
            "QPushButton:hover { background:#e2e8f0; }"
        )

    @staticmethod
    def _status_style(kind):
        styles = {
            "info": "background:#eff6ff; border:1px solid #bfdbfe; color:#1d4ed8;",
            "success": "background:#f0fdf4; border:1px solid #bbf7d0; color:#15803d;",
            "warning": "background:#fff7ed; border:1px solid #fed7aa; color:#c2410c;",
            "error": "background:#fef2f2; border:1px solid #fecaca; color:#b91c1c;",
        }
        return styles.get(kind, styles["info"]) + " border-radius:9px; padding:12px; font-weight:700;"
