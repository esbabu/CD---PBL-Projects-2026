from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QSplitter, QTextEdit, QLineEdit, QRadioButton,
                             QFileDialog, QButtonGroup, QMessageBox, QProgressBar, QComboBox,
                             QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer, QPropertyAnimation
from PyQt6.QtGui import QFont, QColor, QTextCharFormat, QTextCursor, QSyntaxHighlighter
import sys
import os
import traceback

from src.main import run_pipeline
from src.logger import PipelineLogger
from src.gui.syntax_highlighter import PythonSyntaxHighlighter
from src.ml.trainer import load_ast_model
from src.multilang.universal_commenter import UniversalCommenter, SUPPORTED_LANGUAGES, LANGUAGE_LABELS
from pathlib import Path

_SPINNER_FRAMES = ["\u28f7", "\u28ef", "\u28df", "\u28dd", "\u28d9", "\u28d1",
                   "\u28c1", "\u2881", "\u2882", "\u2884", "\u2888", "\u2890",
                   "\u28a0", "\u28e0", "\u28f0", "\u28f8"]


class GeneratorWorker(QThread):
    # Keep Qt's inherited finished() signal intact. Result delivery uses a
    # separate signal so the GUI cannot mistake "result ready" for "thread ended".
    result_ready = pyqtSignal(str, str, object)
    status = pyqtSignal(str)

    def __init__(self, code_text, engine, output_dir, source_filename=None, language="python"):
        super().__init__()
        self.code_text = code_text
        self.engine = engine
        self.output_dir = output_dir
        self.source_filename = source_filename or "pasted_source.py"
        self.language = language

    def run(self):
        try:
            self.status.emit("Setting up source file...")
            os.makedirs(self.output_dir, exist_ok=True)
            ext = Path(self.source_filename).suffix.lower()
            expected_language = SUPPORTED_LANGUAGES.get(ext)
            if ext not in SUPPORTED_LANGUAGES or expected_language != self.language:
                ext = {"python": ".py", "c": ".c", "cpp": ".cpp", "java": ".java",
                       "javascript": ".js", "typescript": ".ts", "tsx": ".tsx"}.get(self.language, ".txt")
            tmp_in = os.path.join(self.output_dir, "gui_tmp_in" + ext)
            with open(tmp_in, "w", encoding="utf-8", newline="") as handle:
                handle.write(self.code_text)

            if self.language == "python":
                logger = PipelineLogger(input_file=tmp_in)
                ast_model = None
                engine = self.engine
                if engine in ("ml", "neurosymbolic"):
                    self.status.emit("Loading AST+NLP ML model...")
                    try:
                        ast_model = load_ast_model(output_dir="outputs")
                        if ast_model is None:
                            raise RuntimeError("No trained AST+NLP model found. Train from the ML Training tab first.")
                    except Exception:
                        self.status.emit("ML model unavailable; falling back to Rule-Based mode...")
                        engine = "rule_based"
                        ast_model = None

                self.status.emit("Running Python AST comment-generation pipeline...")
                annotated, comments, mf, cg, attach_result, ir_module, analysis_report, security_report = \
                    run_pipeline(tmp_in, logger, ast_model=ast_model,
                                 strict_ml=(engine in ("ml", "neurosymbolic")), engine=engine)
                out_file = os.path.join(self.output_dir, "gui_annotated.py")
                with open(out_file, "w", encoding="utf-8", newline="") as handle:
                    handle.write(annotated)
                self.status.emit("Saving Python pipeline logs...")
                logger.set_output_file(out_file)
                logger.save(os.path.join(self.output_dir, "logs"))
                results_dict = {
                    "mf": mf, "cg": cg, "ir": ir_module, "analysis": analysis_report,
                    "security_report": security_report, "language": "python",
                    "source_file": self.source_filename, "source_code": self.code_text, "multilang": False,
                }
            else:
                self.status.emit(f"Parsing {LANGUAGE_LABELS.get(self.language, self.language)} source and generating documentation comments...")
                commenter = UniversalCommenter()
                annotated, multi_report = commenter.generate_comments(
                    self.code_text, filename=self.source_filename, language=self.language
                )
                out_file = os.path.join(self.output_dir, "gui_annotated" + ext)
                with open(out_file, "w", encoding="utf-8", newline="") as handle:
                    handle.write(annotated)
                self.status.emit(f"Parser mode: {multi_report.get('parser', 'unknown')}")
                if multi_report.get("parser") != "tree-sitter":
                    self.status.emit(multi_report.get("note", "Fallback declaration scanner was used."))
                self.status.emit("Saving multi-language analysis summary...")
                results_dict = {
                    "mf": None, "cg": None, "ir": None, "analysis": None,
                    "security_report": None, "language": self.language,
                    "source_file": self.source_filename, "source_code": self.code_text,
                    "multilang": True, "multilang_report": multi_report,
                }
            self.result_ready.emit("Success", annotated, results_dict)
        except Exception as exc:
            err = traceback.format_exc()
            self.result_ready.emit(f"Error: {exc}\n\n{err}", "", None)


class GeneratorWorkspace(QWidget):
    generationStarted = pyqtSignal()
    generationFinished = pyqtSignal(str, str, object)
    apply_alternative_requested = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_filepath = None
        self._is_generating = False
        self.worker = None
        self._step_spinner_frame = 0
        self._step_spinner_timer = QTimer(self)
        self._step_spinner_timer.setInterval(80)
        self._step_spinner_timer.timeout.connect(self._tick_step_spinner)
        self._current_step_line = None
        self._completed_steps = []
        self._secure_alternative_code = ""
        self._secure_alternative_language = "python"
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QWidget()
        header.setObjectName("WorkspaceHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 12, 16, 12)

        engine_group = QWidget()
        engine_layout = QHBoxLayout(engine_group)
        engine_layout.setContentsMargins(4, 4, 4, 4)
        engine_layout.setSpacing(8)

        self.btn_rule = QRadioButton("Rule-Based")
        self.btn_neuro = QRadioButton("Neurosymbolic")
        self.btn_ml = QRadioButton("ML-Based")
        self.btn_rule.setChecked(True)

        self.engine_btn_group = QButtonGroup(self)
        self.engine_btn_group.addButton(self.btn_rule, 1)
        self.engine_btn_group.addButton(self.btn_neuro, 2)
        self.engine_btn_group.addButton(self.btn_ml, 3)

        engine_layout.addWidget(self.btn_rule)
        engine_layout.addWidget(self.btn_neuro)
        engine_layout.addWidget(self.btn_ml)

        # Explicit language selector: file extensions auto-select a language,
        # while pasted code can be assigned manually.
        self.language_combo = QComboBox()
        self.language_combo.addItem("Auto Detect", "auto")
        for label, key in [("Python", "python"), ("C", "c"), ("C++", "cpp"),
                           ("Java", "java"), ("JavaScript", "javascript"),
                           ("TypeScript", "typescript"), ("TypeScript (TSX)", "tsx")]:
            self.language_combo.addItem(label, key)
        self.language_combo.currentIndexChanged.connect(self._update_engine_options)
        header_layout.addWidget(QLabel("Language:"))
        header_layout.addWidget(self.language_combo)
        header_layout.addWidget(engine_group)
        header_layout.addStretch()

        self.unsafe_label = QLabel("0% unsafe")
        self.unsafe_label.setStyleSheet(
            "color: #16a34a; font-weight: bold; font-size: 13px; "
            "padding: 4px 10px; background: rgba(22,163,74,0.08); border-radius: 6px;"
        )
        header_layout.addWidget(self.unsafe_label)

        dir_layout = QHBoxLayout()
        dir_label = QLabel("Output Dir:")
        dir_label.setStyleSheet("color: #495057; font-weight: 500; font-size: 14px;")

        self.out_dir_input = QLineEdit("./out/annotated")
        self.out_dir_input.setProperty("class", "DirInput")
        self.out_dir_input.setMinimumWidth(250)

        dir_layout.addWidget(dir_label)
        dir_layout.addWidget(self.out_dir_input)
        header_layout.addLayout(dir_layout)

        layout.addWidget(header)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(3)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        input_pane = QWidget()
        input_pane.setObjectName("PaneContainer")
        input_layout = QVBoxLayout(input_pane)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(0)

        input_header = QWidget()
        input_header.setObjectName("EditorPaneHeader")
        ih_layout = QHBoxLayout(input_header)
        ih_layout.setContentsMargins(16, 8, 16, 8)
        self.input_title = QLabel("Input Source Code")
        ih_title = self.input_title
        self.btn_pick_file = QPushButton("Pick File")
        self.btn_pick_file.setProperty("class", "SecondaryButton")
        self.btn_pick_file.clicked.connect(self.pick_file)
        ih_layout.addWidget(ih_title)
        ih_layout.addStretch()
        ih_layout.addWidget(self.btn_pick_file)

        self.input_editor = QTextEdit()
        self.input_editor.setProperty("class", "CodeEditor")
        self.input_editor.setPlaceholderText("Paste source code, select its language, or choose a source file...")
        self.input_highlighter = PythonSyntaxHighlighter(self.input_editor.document())

        input_layout.addWidget(input_header)
        input_layout.addWidget(self.input_editor, stretch=1)

        # The secure-alternative action belongs to the Generator workspace,
        # directly below the editor whose contents it will replace.
        alternative_action = QWidget()
        alternative_action.setObjectName("AlternativeActionBar")
        alternative_action_layout = QHBoxLayout(alternative_action)
        alternative_action_layout.setContentsMargins(12, 8, 12, 8)
        alternative_action_layout.setSpacing(10)

        self.apply_alternative_button = QPushButton("Apply Alternative to Generator")
        self.apply_alternative_button.setMinimumHeight(38)
        self.apply_alternative_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.apply_alternative_button.setEnabled(False)
        self.apply_alternative_button.setToolTip(
            "Replace the input code with the alternative produced by Agentic Security."
        )
        self.apply_alternative_button.setStyleSheet(
            "QPushButton { background:#2563eb; color:white; border:0; border-radius:7px; "
            "padding:8px 14px; font-weight:700; } "
            "QPushButton:hover:enabled { background:#1d4ed8; } "
            "QPushButton:disabled { background:#cbd5e1; color:#64748b; }"
        )
        self.apply_alternative_button.clicked.connect(self._request_apply_secure_alternative)

        self.apply_alternative_note = QLabel(
            "Run Agentic Security to prepare a safer alternative."
        )
        self.apply_alternative_note.setWordWrap(True)
        self.apply_alternative_note.setStyleSheet("color:#64748b; font-size:11px;")

        alternative_action_layout.addWidget(self.apply_alternative_button)
        alternative_action_layout.addWidget(self.apply_alternative_note, stretch=1)
        input_layout.addWidget(alternative_action)

        output_pane = QWidget()
        output_pane.setObjectName("PaneContainer")
        output_layout = QVBoxLayout(output_pane)
        output_layout.setContentsMargins(0, 0, 0, 0)
        output_layout.setSpacing(0)

        output_header = QWidget()
        output_header.setObjectName("EditorPaneHeader")
        oh_layout = QHBoxLayout(output_header)
        oh_layout.setContentsMargins(16, 8, 16, 8)
        self.oh_title = QLabel("Annotated Output")
        oh_layout.addWidget(self.oh_title)
        oh_layout.addStretch()

        self.output_editor = QTextEdit()
        self.output_editor.setProperty("class", "DiffEditor")
        self.output_editor.setReadOnly(True)
        self.output_editor.setPlaceholderText("Annotated code will appear here...")
        self.output_highlighter = PythonSyntaxHighlighter(self.output_editor.document())

        output_layout.addWidget(output_header)
        output_layout.addWidget(self.output_editor)

        self._show_output_welcome()

        self.splitter.addWidget(input_pane)
        self.splitter.addWidget(output_pane)

        self.splitter.setStyleSheet("QSplitter::handle { background-color: #e0e4e8; }")

        layout.addWidget(self.splitter, stretch=1)

    def _show_output_welcome(self):
        self.oh_title.setText("Output Preview")
        self.output_editor.setHtml(
            "<div style='padding:28px; font-family:Segoe UI,Arial; color:#334155;'>"
            "<div style='font-size:24px; font-weight:700; color:#172554;'>Code Comment Generator</div>"
            "<div style='font-size:14px; color:#64748b; margin-top:8px;'>Intelligent AST + NLP comment and docstring generation</div>"
            "<hr style='border:0; border-top:1px solid #e2e8f0; margin:18px 0;'>"
            "<div style='font-size:15px; font-weight:700; color:#1e293b;'>Ready to analyze supported source code</div>"
            "<div style='font-size:13px; color:#64748b; line-height:1.6; margin-top:8px;'>"
            "1. Paste source code or choose a file (Python, C, C++, Java, JavaScript or TypeScript).<br>"
            "2. Select the language. Python supports Rule-Based, Neurosymbolic and ML-Based engines; other languages use structural Rule-Based comments.<br>"
            "3. Click <b>Generate &amp; Attach Comments</b>.<br>"
            "4. Review the annotated output and security insights here."
            "</div>"
            "<div style='margin-top:20px; padding:14px; background:#eff6ff; border:1px solid #bfdbfe; border-radius:9px; color:#1d4ed8;'>"
            "<b>Pipeline:</b> Parse → AST → Context → Generate → Attach → IR/CFG/DFA → Quality → Security"
            "</div>"
            "</div>"
        )

    def set_secure_alternative(self, code, language="python"):
        """Store the latest Agentic Security alternative and update the Generator button."""
        self._secure_alternative_code = (code or "").strip("\n")
        self._secure_alternative_language = (language or "python").strip().lower()
        ready = bool(self._secure_alternative_code.strip())
        self.apply_alternative_button.setEnabled(ready)
        if ready:
            self.apply_alternative_note.setText(
                f"A {self._secure_alternative_language.upper()} alternative is ready. "
                "Click to replace the input code after confirmation."
            )
        else:
            self.apply_alternative_note.setText(
                "No alternative is available yet. Run Agentic Security after generating code."
            )

    def clear_secure_alternative(self):
        """Disable the action after the alternative is applied or becomes stale."""
        self._secure_alternative_code = ""
        self._secure_alternative_language = "python"
        self.apply_alternative_button.setEnabled(False)
        self.apply_alternative_note.setText(
            "No alternative is available yet. Run Agentic Security after generating code."
        )

    def _request_apply_secure_alternative(self):
        if not self._secure_alternative_code.strip():
            return
        self.apply_alternative_requested.emit(
            self._secure_alternative_code,
            self._secure_alternative_language,
        )

    def apply_alternative_code(self, code, language="python"):
        """Replace the Generator editor with a reviewed alternative from Agentic Security.

        The method deliberately clears current_filepath so a later generation does
        not overwrite the user's original source file on disk.
        """
        code = (code or "").strip("\n")
        if not code.strip():
            return False

        language = (language or "python").strip().lower()
        language_aliases = {
            "py": "python", "c++": "cpp", "cc": "cpp", "cxx": "cpp",
            "js": "javascript", "jsx": "javascript", "mjs": "javascript",
            "ts": "typescript", "mts": "typescript", "cts": "typescript",
        }
        language = language_aliases.get(language, language)

        # Replace only the editor contents; do not run generation automatically.
        self.input_editor.setPlainText(code)
        self.current_filepath = None

        index = self.language_combo.findData(language)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
        else:
            self.language_combo.setCurrentIndex(0)

        self._update_engine_options()

        # Enable the Python highlighter only for Python source.
        try:
            is_python = language == "python"
            self.input_highlighter.setDocument(
                self.input_editor.document() if is_python else None
            )
            self.output_highlighter.setDocument(
                self.output_editor.document() if is_python else None
            )
        except Exception:
            pass

        # Clear stale annotated output so it cannot be mistaken for output
        # generated from the newly applied alternative.
        self._show_output_welcome()
        self.input_editor.setFocus()
        return True

    def pick_file(self):
        file_filter = (
            "Supported Source Files (*.py *.pyw *.c *.h *.cc *.cpp *.cxx *.hpp *.hh *.hxx *.java *.js *.jsx *.mjs *.cjs *.ts *.tsx *.mts *.cts);;"
            "Python (*.py *.pyw);;C/C++ (*.c *.h *.cc *.cpp *.cxx *.hpp *.hh *.hxx);;"
            "Java (*.java);;JavaScript (*.js *.jsx *.mjs *.cjs);;TypeScript (*.ts *.tsx *.mts *.cts);;All Files (*)"
        )
        filepath, _ = QFileDialog.getOpenFileName(self, "Select Source File", "", file_filter)
        if filepath:
            self.current_filepath = filepath
            with open(filepath, "r", encoding="utf-8", errors="replace") as handle:
                self.input_editor.setPlainText(handle.read())
            language = SUPPORTED_LANGUAGES.get(Path(filepath).suffix.lower())
            if language:
                index = self.language_combo.findData(language)
                if index >= 0:
                    self.language_combo.setCurrentIndex(index)
            self._update_engine_options()

    def _selected_language(self):
        selected = self.language_combo.currentData()
        code = self.input_editor.toPlainText()
        if selected and selected != "auto":
            return selected
        detected = UniversalCommenter().detect_language(self.current_filepath, code)
        return detected

    def _update_engine_options(self, *_args):
        selected = self._selected_language()
        is_python = selected in (None, "python")
        self.btn_ml.setEnabled(is_python)
        self.btn_neuro.setEnabled(is_python)
        if not is_python and (self.btn_ml.isChecked() or self.btn_neuro.isChecked()):
            self.btn_rule.setChecked(True)
        self.input_title.setText(f"Input {LANGUAGE_LABELS.get(selected, 'Source')} Code" if selected else "Input Source Code")

    def trigger_generation(self):
        # A QThread can emit its result signal a moment before its native thread
        # has fully stopped. Do not replace or destroy a still-running worker.
        if self._is_generating or (self.worker is not None and self.worker.isRunning()):
            return

        code = self.input_editor.toPlainText().strip()
        if not code:
            QMessageBox.warning(self, "No Code", "Please choose a source file or paste code first.")
            return

        language = self._selected_language()
        if not language:
            QMessageBox.warning(self, "Select Language", "Auto-detection could not identify the language. Choose Python, C, C++, Java, JavaScript or TypeScript from the Language selector.")
            return
        if language not in LANGUAGE_LABELS:
            QMessageBox.warning(self, "Unsupported Language", f"The selected language '{language}' is not supported.")
            return

        if language == "python":
            if self.btn_neuro.isChecked():
                engine = "neurosymbolic"
            elif self.btn_ml.isChecked():
                engine = "ml"
            else:
                engine = "rule_based"
        else:
            engine = "rule_based"
            if self.btn_neuro.isChecked() or self.btn_ml.isChecked():
                self.btn_rule.setChecked(True)
                QMessageBox.information(self, "Rule-Based Multi-Language Mode",
                    "The current T5-small and Neurosymbolic models are Python-AST specific. "
                    "C, C++, Java, JavaScript and TypeScript use Tree-sitter structural parsing and Rule-Based comments.")

        self._is_generating = True
        self._completed_steps = []
        self._current_step_line = None
        self.progress_bar.show()
        self.output_editor.clear()
        self.output_editor.setPlaceholderText("")
        self.oh_title.setText("Annotated Output — Generating...")
        self.input_title.setText(f"Input {LANGUAGE_LABELS.get(language, language)} Code")

        # Use the Python highlighter only for Python source; other languages are kept plain.
        try:
            self.input_highlighter.setDocument(self.input_editor.document() if language == "python" else None)
            self.output_highlighter.setDocument(self.output_editor.document() if language == "python" else None)
        except Exception:
            pass

        source_filename = self.current_filepath or f"pasted_source.{ {'python':'py','c':'c','cpp':'cpp','java':'java','javascript':'js','typescript':'ts','tsx':'tsx'}.get(language, 'txt') }"
        self.worker = GeneratorWorker(code, engine, self.out_dir_input.text().strip(),
                                      source_filename=source_filename, language=language)
        self.worker.status.connect(self._on_worker_status)
        self.worker.result_ready.connect(self.on_generation_finished)
        self.worker.finished.connect(self._on_worker_thread_finished)
        self.worker.start()
        self.generationStarted.emit()
        self._step_spinner_timer.start()

    def _on_worker_thread_finished(self):
        """Release the worker only after the native QThread has stopped."""
        worker = self.sender()
        if worker is self.worker:
            self.worker = None
        if worker is not None:
            worker.deleteLater()

    def _on_worker_status(self, msg):
        if self._current_step_line is not None:
            self._completed_steps.append(self._current_step_line)
            self._rewrite_progress()

        self._current_step_line = msg
        self._step_spinner_frame = 0
        self._rewrite_progress()

    def _rewrite_progress(self):
        cursor = self.output_editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.removeSelectedText()

        fmt_done = QTextCharFormat()
        fmt_done.setForeground(QColor("#16a34a"))
        fmt_done.setFontWeight(QFont.Weight.Normal)

        fmt_active = QTextCharFormat()
        fmt_active.setForeground(QColor("#2563eb"))
        fmt_active.setFontWeight(QFont.Weight.Bold)

        fmt_label = QTextCharFormat()
        fmt_label.setForeground(QColor("#9ca3af"))
        fmt_label.setFontWeight(QFont.Weight.Normal)

        for step in self._completed_steps:
            cursor.setCharFormat(fmt_label)
            cursor.insertText("  ")
            cursor.setCharFormat(fmt_done)
            cursor.insertText("\u2713 ")
            cursor.setCharFormat(fmt_label)
            cursor.insertText(f"{step}\n")

        if self._current_step_line:
            spinner_char = _SPINNER_FRAMES[self._step_spinner_frame % len(_SPINNER_FRAMES)]
            cursor.setCharFormat(fmt_label)
            cursor.insertText("  ")
            cursor.setCharFormat(fmt_active)
            cursor.insertText(f"{spinner_char} ")
            cursor.setCharFormat(fmt_label)
            cursor.insertText(f"{self._current_step_line}")

    def _tick_step_spinner(self):
        self._step_spinner_frame += 1
        if self._current_step_line:
            self._rewrite_progress()

    def on_generation_finished(self, status, code, results_dict):
        self._is_generating = False
        self._step_spinner_timer.stop()
        self.progress_bar.hide()

        if self._current_step_line is not None:
            self._completed_steps.append(self._current_step_line)
            self._current_step_line = None

        if status == "Success":
            self.output_editor.setPlainText(code)
            self.oh_title.setText("Annotated Output")
            self.generationFinished.emit("Generation Completed", "", results_dict)
        else:
            cursor = self.output_editor.textCursor()
            cursor.select(QTextCursor.SelectionType.Document)
            cursor.removeSelectedText()

            fmt_done = QTextCharFormat()
            fmt_done.setForeground(QColor("#16a34a"))
            fmt_err = QTextCharFormat()
            fmt_err.setForeground(QColor("#dc2626"))
            fmt_err.setFontWeight(QFont.Weight.Bold)
            fmt_label = QTextCharFormat()
            fmt_label.setForeground(QColor("#9ca3af"))

            for step in self._completed_steps:
                cursor.setCharFormat(fmt_label)
                cursor.insertText("  ")
                cursor.setCharFormat(fmt_done)
                cursor.insertText("\u2713 ")
                cursor.setCharFormat(fmt_label)
                cursor.insertText(f"{step}\n")

            cursor.setCharFormat(fmt_label)
            cursor.insertText("  ")
            cursor.setCharFormat(fmt_err)
            cursor.insertText("\u2717 Generation failed\n\n")
            cursor.setCharFormat(fmt_err)
            cursor.insertText(status)

            self.oh_title.setText("Annotated Output \u2014 Failed")
            self.generationFinished.emit("Generation Failed", "", None)

    def update_annotated_code(self, code):
        self.output_editor.setPlainText(code)

    def update_unsafe_pct(self, security_report):
        if security_report is None:
            self.unsafe_label.setText("N/A")
            self.unsafe_label.setStyleSheet(
                "color: #6c757d; font-weight: bold; font-size: 13px; "
                "padding: 4px 10px; border-radius: 6px;"
            )
            return
        unsafe_pct = round(100.0 - security_report.module_safe_pct, 1)
        if unsafe_pct > 20:
            color = "#dc2626"
            bg = "rgba(220,38,38,0.08)"
        elif unsafe_pct > 0:
            color = "#ca8a04"
            bg = "rgba(202,138,4,0.08)"
        else:
            color = "#16a34a"
            bg = "rgba(22,163,74,0.08)"
        self.unsafe_label.setText(f"{unsafe_pct}% unsafe")
        self.unsafe_label.setStyleSheet(
            f"color: {color}; font-weight: bold; font-size: 13px; "
            f"padding: 4px 10px; background: {bg}; border-radius: 6px;"
        )
