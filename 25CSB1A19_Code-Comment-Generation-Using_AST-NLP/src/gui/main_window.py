import os
import sys
import re
import traceback
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QLabel, QPushButton, QStackedWidget, QSplitter, QTextEdit, QMessageBox)
from PyQt6.QtCore import Qt, QSize, QObject, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon, QTextCursor, QTextCharFormat, QColor

from src.gui.generator_workspace import GeneratorWorkspace
from src.gui.insights_workspace import InsightsWorkspace
from src.gui.training_workspace import MLTrainingWorkspace
from src.gui.logs_workspace import LogsWorkspace
from src.gui.security_workspace import SecurityWorkspace
from src.gui.agentic_workspace import AgenticWorkspace
from src.gui.widgets import SpinningButton, ToastWidget


class StreamCapture(QObject):
    new_text = pyqtSignal(str, bool)

    def __init__(self, is_stderr=False):
        super().__init__()
        self._is_stderr = is_stderr

    def write(self, text):
        self.new_text.emit(text, self._is_stderr)

    def flush(self):
        pass


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Comment Gen Pro")
        self._status_reset_timer = QTimer(self)
        self._status_reset_timer.setSingleShot(True)
        self._status_reset_timer.timeout.connect(self._reset_status_style)
        self.setup_ui()
        self.setup_ui_connections()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self._toast_host = central_widget

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        top_header = QWidget()
        top_header.setObjectName("TopHeader")
        th_layout = QHBoxLayout(top_header)
        th_layout.setContentsMargins(16, 8, 16, 8)

        title_lbl = QLabel("Comment Gen Pro")
        title_lbl.setStyleSheet("font-weight: bold; font-size: 15px; color: #1a1a2e;")
        th_layout.addWidget(title_lbl)

        th_layout.addStretch()

        self.btn_generate = SpinningButton("Generate && Attach Comments")
        self.btn_generate.setProperty("class", "PrimaryButton")
        self.btn_generate.clicked.connect(self.trigger_generation)

        th_layout.addWidget(self.btn_generate)

        main_layout.addWidget(top_header)

        body_splitter = QSplitter(Qt.Orientation.Horizontal)

        sidebar = QWidget()
        sidebar.setObjectName("SidebarWidget")
        sidebar.setMinimumWidth(200)
        sidebar.setMaximumWidth(285)
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(16, 16, 16, 16)
        sb_layout.setSpacing(8)

        workspace_lbl = QLabel("Workspace")
        workspace_lbl.setObjectName("SidebarTitle")
        local_env_lbl = QLabel("Local Env")
        local_env_lbl.setObjectName("SidebarSubtitle")

        sb_layout.addWidget(workspace_lbl)
        sb_layout.addWidget(local_env_lbl)
        sb_layout.addSpacing(12)

        self.btn_nav_gen = QPushButton("Generator")
        self.btn_nav_gen.setProperty("class", "SidebarButton")
        self.btn_nav_gen.setProperty("active", "true")

        self.btn_nav_insights = QPushButton("Insights")
        self.btn_nav_insights.setProperty("class", "SidebarButton")

        self.btn_nav_ml = QPushButton("ML Training")
        self.btn_nav_ml.setProperty("class", "SidebarButton")

        self.btn_nav_security = QPushButton("Security")
        self.btn_nav_security.setProperty("class", "SidebarButton")

        self.btn_nav_logs = QPushButton("Logs")
        self.btn_nav_logs.setProperty("class", "SidebarButton")

        self.btn_nav_agent = QPushButton("Agentic Security")
        self.btn_nav_agent.setProperty("class", "SidebarButton")

        sb_layout.addWidget(self.btn_nav_gen)
        sb_layout.addWidget(self.btn_nav_insights)
        sb_layout.addWidget(self.btn_nav_ml)
        sb_layout.addWidget(self.btn_nav_security)
        sb_layout.addWidget(self.btn_nav_logs)
        sb_layout.addWidget(self.btn_nav_agent)

        sb_layout.addStretch()

        body_splitter.addWidget(sidebar)

        self.stacked_widget = QStackedWidget()

        self.workspace_gen = GeneratorWorkspace()
        self.stacked_widget.addWidget(self.workspace_gen)

        self.workspace_insights = InsightsWorkspace()
        self.stacked_widget.addWidget(self.workspace_insights)

        self.workspace_ml = MLTrainingWorkspace()
        self.stacked_widget.addWidget(self.workspace_ml)

        self.workspace_security = SecurityWorkspace()
        self.stacked_widget.addWidget(self.workspace_security)

        self.workspace_logs = LogsWorkspace()
        self.stacked_widget.addWidget(self.workspace_logs)

        self.workspace_agent = AgenticWorkspace()
        self.stacked_widget.addWidget(self.workspace_agent)

        content_splitter = QSplitter(Qt.Orientation.Vertical)
        content_splitter.addWidget(self.stacked_widget)

        console_widget = QWidget()
        console_widget.setObjectName("PaneContainer")
        console_layout = QVBoxLayout(console_widget)
        console_layout.setContentsMargins(0, 0, 0, 0)
        console_layout.setSpacing(0)

        console_header = QLabel("  Terminal Output")
        console_header.setStyleSheet("background: #f8f9fa; color: #495057; font-weight: 500; font-size: 12px; padding: 6px; border-bottom: 1px solid #e0e4e8;")

        self.console_output = QTextEdit()
        self.console_output.setProperty("class", "CodeEditor")
        self.console_output.setReadOnly(True)
        self.console_output.setPlaceholderText("Live system output will appear here...")
        self.console_output.setStyleSheet("font-size: 11px; color: #1a1a2e; background: #ffffff;")

        console_layout.addWidget(console_header)
        console_layout.addWidget(self.console_output)

        content_splitter.addWidget(console_widget)
        content_splitter.setSizes([600, 150])

        body_splitter.addWidget(content_splitter)

        main_layout.addWidget(body_splitter, stretch=1)

        self.statusBar().showMessage("Status: Ready")
        self._status_label = QLabel("Ready")
        self._status_label.setStyleSheet("padding: 0px 8px; color: #6c757d;")
        self.statusBar().addPermanentWidget(self._status_label)

        self.stdout_capture = StreamCapture(is_stderr=False)
        self.stdout_capture.new_text.connect(self.append_to_console)
        self.stderr_capture = StreamCapture(is_stderr=True)
        self.stderr_capture.new_text.connect(self.append_to_console)
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        sys.stdout = self.stdout_capture
        sys.stderr = self.stderr_capture

        self.toast = ToastWidget(self._toast_host)
        self.toast.hide()

        self.link_sidebar_buttons()

    def append_to_console(self, text, is_stderr=False):
        cursor = self.console_output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        fmt = QTextCharFormat()
        if is_stderr:
            fmt.setForeground(QColor("#dc2626"))
        elif re.search(r'\b(error|fail|exception|traceback)\b', text, re.IGNORECASE):
            fmt.setForeground(QColor("#dc2626"))
        elif re.search(r'\b(success|completed|saved|done|finished)\b', text, re.IGNORECASE):
            fmt.setForeground(QColor("#16a34a"))
        else:
            fmt.setForeground(QColor("#1a1a2e"))

        cursor.setCharFormat(fmt)
        cursor.insertText(text)

        self.console_output.verticalScrollBar().setValue(
            self.console_output.verticalScrollBar().maximum()
        )

    def _set_status(self, message, color="#6c757d"):
        self._status_label.setText(message)
        self._status_label.setStyleSheet(
            f"padding: 0px 8px; color: {color}; font-weight: 600;"
        )
        self.statusBar().showMessage("")

    def _reset_status_style(self):
        self._set_status("Ready", "#6c757d")

    def closeEvent(self, event):
        # Never destroy a QThread while it is running. This is a common cause
        # of abrupt application termination during generation or analysis.
        active_workers = [
            getattr(self.workspace_gen, "worker", None),
            getattr(self.workspace_agent, "agent_worker", None),
            getattr(self.workspace_ml, "worker", None),
        ]
        running = [w for w in active_workers if w is not None and w.isRunning()]
        if running:
            QMessageBox.warning(
                self,
                "Work in progress",
                "The application is still generating comments or analyzing code.\n"
                "Please wait for the current task to finish, then close the application."
            )
            event.ignore()
            return

        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr
        super().closeEvent(event)

    def link_sidebar_buttons(self):
        self.nav_buttons = [
            self.btn_nav_gen,
            self.btn_nav_insights,
            self.btn_nav_ml,
            self.btn_nav_security,
            self.btn_nav_logs,
            self.btn_nav_agent,
        ]

        def set_active(idx, active_btn):
            self.stacked_widget.setCurrentIndex(idx)
            for btn in self.nav_buttons:
                btn.setProperty("active", "true" if btn == active_btn else "false")
                btn.style().unpolish(btn)
                btn.style().polish(btn)

        self.btn_nav_gen.clicked.connect(lambda: set_active(0, self.btn_nav_gen))
        self.btn_nav_insights.clicked.connect(lambda: set_active(1, self.btn_nav_insights))
        self.btn_nav_ml.clicked.connect(lambda: set_active(2, self.btn_nav_ml))
        self.btn_nav_security.clicked.connect(lambda: set_active(3, self.btn_nav_security))
        self.btn_nav_logs.clicked.connect(lambda: set_active(4, self.btn_nav_logs))
        self.btn_nav_agent.clicked.connect(lambda: set_active(5, self.btn_nav_agent))

    def trigger_generation(self):
        if self.btn_generate.is_spinning():
            return

        idx = self.stacked_widget.currentIndex()
        if idx != 0:
            self.stacked_widget.setCurrentIndex(0)
            for btn in self.nav_buttons:
                btn.setProperty("active", "true" if btn == self.btn_nav_gen else "false")
                btn.style().unpolish(btn)
                btn.style().polish(btn)

        self._set_status("Generating...", "#2563eb")
        self.btn_generate.start_spinning("Generating...")
        self.workspace_gen.trigger_generation()

    def _on_generation_started(self):
        self._set_status("Generating...", "#2563eb")

    def _on_generation_finished(self, status, code_unused, results_dict):
        """Handle generation completion defensively so secondary panels cannot close the app."""
        self.btn_generate.stop_spinning()
        self._status_reset_timer.start(8000)

        if not ("Completed" in status or status == "Success"):
            self._set_status("✗ Generation Failed — see Output Preview", "#dc2626")
            self.toast.show_toast("Generation failed — check output for details", kind="error")
            return

        safe_msg = ""
        if results_dict:
            language = results_dict.get("language", "python")
            security_report = results_dict.get("security_report")
            if language == "python":
                try:
                    self.workspace_insights.populate_insights(results_dict)
                except Exception:
                    self.append_to_console(
                        "\n[Insights display error]\n" + traceback.format_exc() + "\n", True
                    )
                try:
                    self.workspace_security.populate(security_report)
                    self.workspace_gen.update_unsafe_pct(security_report)
                    if security_report:
                        safe_msg = f" | {security_report.module_safe_pct}% safe | {security_report.total_issues} issues"
                except Exception:
                    self.append_to_console(
                        "\n[Security display error]\n" + traceback.format_exc() + "\n", True
                    )
            else:
                self.workspace_gen.update_unsafe_pct(None)
                safe_msg = f" | {language.upper()} | Rule-Based structural comments"

            # Forward the original source to Agentic Security. Agent analysis is
            # asynchronous in AgenticWorkspace, so this signal handler stays safe.
            try:
                source_code = self.workspace_gen.input_editor.toPlainText()
                self.workspace_agent.set_source_code(
                    source_code,
                    annotated_code=code_unused,
                    language=language,
                    filename=results_dict.get("source_file", self.workspace_gen.current_filepath or ""),
                    auto_analyze=True,
                )
            except Exception:
                self.append_to_console(
                    "\n[Agentic hand-off error]\n" + traceback.format_exc() + "\n", True
                )
                self._set_status("✓ Comments generated; Agentic Security hand-off needs review", "#ca8a04")
                self.toast.show_toast("Comments generated; Agentic hand-off needs review", kind="warning")
                return

        self._set_status(f"✓ Generation Completed{safe_msg}", "#16a34a")
        self.toast.show_toast("Comments generated successfully", kind="success")

    def _apply_agent_alternative_to_generator(self, alternative_code, language):
        """Replace Generator editor contents after explicit user confirmation."""
        alternative_code = (alternative_code or "").strip("\n")
        if not alternative_code.strip():
            QMessageBox.warning(
                self,
                "No Alternative Code",
                "The Agentic Security workspace has no alternative code to apply.",
            )
            return

        current_code = self.workspace_gen.input_editor.toPlainText()
        if current_code.strip() and current_code.strip() != alternative_code.strip():
            answer = QMessageBox.question(
                self,
                "Replace Generator Code?",
                "This will replace the code currently in the Generator editor with the "
                "recommended alternative.\n\n"
                "Your original file on disk will not be overwritten. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return

        applied = self.workspace_gen.apply_alternative_code(
            alternative_code, language=language
        )
        if not applied:
            QMessageBox.warning(
                self, "Apply Failed", "The alternative code could not be placed in Generator."
            )
            return

        self.workspace_gen.clear_secure_alternative()

        # Return the user to the Generator workspace and mark it active.
        self.stacked_widget.setCurrentWidget(self.workspace_gen)
        for button in getattr(self, "nav_buttons", []):
            button.setProperty(
                "active", "true" if button is self.btn_nav_gen else "false"
            )
            button.style().unpolish(button)
            button.style().polish(button)

        self._set_status(
            "✓ Recommended alternative applied to Generator — review it and generate again",
            "#16a34a",
        )
        self.toast.show_toast(
            "Alternative code applied to Generator", kind="success"
        )

    def setup_ui_connections(self):
        self.workspace_gen.generationStarted.connect(self._on_generation_started)
        self.workspace_gen.generationFinished.connect(self._on_generation_finished)
        self.workspace_agent.alternative_ready.connect(
            self.workspace_gen.set_secure_alternative
        )
        self.workspace_gen.apply_alternative_requested.connect(
            self._apply_agent_alternative_to_generator
        )
