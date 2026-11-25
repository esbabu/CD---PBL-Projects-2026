from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QTextEdit,
    QLabel,
    QTreeWidget,
    QTreeWidgetItem,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QStackedWidget,
    QFrame,
    QProgressBar,
    QListWidget,
    QListWidgetItem,
)

from PyQt6.QtGui import (
    QColor,
    QBrush,
)

from PyQt6.QtCore import Qt

from src.gui.ast_graph_widget import AstGraphWidget
from src.gui.context_graph_widget import ContextGraphWidget
from src.gui.eval_graph_widget import EvalGraphWidget


# ============================================================
# EMPTY STATE
# ============================================================

_EMPTY_STATE_STYLE = (
    "color: #9ca3af;"
    "font-size: 14px;"
    "padding: 40px;"
    "background: transparent;"
    "border: none;"
)


def _make_empty_state(message):

    label = QLabel(message)

    label.setAlignment(
        Qt.AlignmentFlag.AlignCenter
    )

    label.setStyleSheet(
        _EMPTY_STATE_STYLE
    )

    label.setWordWrap(True)

    return label


# ============================================================
# INSIGHTS WORKSPACE
# ============================================================

class InsightsWorkspace(QWidget):

    def __init__(
        self,
        parent=None
    ):

        super().__init__(parent)

        self._populated = False

        self.setup_ui()

    # ========================================================
    # QUALITY CARD
    # ========================================================

    def _create_quality_card(
        self,
        title,
        value,
        accent_color,
    ):

        card = QFrame()

        card.setFrameShape(
            QFrame.Shape.StyledPanel
        )

        card.setMinimumHeight(105)

        card.setStyleSheet(
            f"""
            QFrame {{
                background-color: #ffffff;
                border: 1px solid #d9dee7;
                border-radius: 10px;
            }}

            QFrame:hover {{
                border: 1px solid {accent_color};
            }}
            """
        )

        card_layout = QVBoxLayout(card)

        card_layout.setContentsMargins(
            12,
            10,
            12,
            10
        )

        card_layout.setSpacing(5)

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title_label = QLabel(title)

        title_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        title_label.setStyleSheet(
            f"""
            QLabel {{
                color: {accent_color};
                font-size: 12px;
                font-weight: bold;
                border: none;
                background: transparent;
            }}
            """
        )

        card_layout.addWidget(title_label)

        # ----------------------------------------------------
        # VALUE
        # ----------------------------------------------------

        value_label = QLabel(value)

        value_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        value_label.setStyleSheet(
            """
            QLabel {
                color: #111827;
                font-size: 22px;
                font-weight: bold;
                border: none;
                background: transparent;
            }
            """
        )

        card_layout.addWidget(value_label)

        # ----------------------------------------------------
        # PROGRESS BAR
        # ----------------------------------------------------

        progress = QProgressBar()

        progress.setRange(0, 100)

        progress.setValue(0)

        progress.setTextVisible(False)

        progress.setFixedHeight(7)

        progress.setStyleSheet(
            f"""
            QProgressBar {{
                background-color: #edf0f4;
                border: none;
                border-radius: 3px;
            }}

            QProgressBar::chunk {{
                background-color: {accent_color};
                border-radius: 3px;
            }}
            """
        )

        card_layout.addWidget(progress)

        card.value_label = value_label
        card.progress = progress

        return card

    # ========================================================
    # QUALITY FUNCTION PANEL
    # ========================================================

    def _create_quality_function_panel(
        self,
        title,
        color,
        background,
        border_color,
    ):

        frame = QFrame()

        frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: {background};
                border: 1px solid {border_color};
                border-radius: 10px;
            }}
            """
        )

        frame_layout = QVBoxLayout(frame)

        frame_layout.setContentsMargins(
            10,
            10,
            10,
            10
        )

        frame_layout.setSpacing(6)

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title_label = QLabel(title)

        title_label.setStyleSheet(
            f"""
            QLabel {{
                color: {color};
                font-size: 12px;
                font-weight: bold;
                border: none;
                background: transparent;
            }}
            """
        )

        frame_layout.addWidget(title_label)

        # ----------------------------------------------------
        # FUNCTION LIST
        # ----------------------------------------------------

        function_list = QListWidget()

        function_list.setMinimumHeight(170)

        function_list.setStyleSheet(
            f"""
            QListWidget {{
                background-color: transparent;
                border: none;
                color: {color};
                font-size: 11px;
            }}

            QListWidget::item {{
                padding: 6px;
                border-radius: 5px;
            }}

            QListWidget::item:hover {{
                background-color: {background};
                border: 1px solid {border_color};
            }}
            """
        )

        frame_layout.addWidget(function_list)

        return frame, function_list

    # ========================================================
    # LANGUAGE DETECTION
    # ========================================================

    def detect_language(
        self,
        pipeline_results
    ):
        """
        Detect the programming language.

        The current compiler pipeline is Python-AST based,
        so Python is the actively supported language.
        """

        source_file = pipeline_results.get(
            "source_file"
        )

        if source_file:

            source_file = str(
                source_file
            ).lower()

            if source_file.endswith(".py"):
                return "Python"

            if source_file.endswith(".pyw"):
                return "Python"

            if source_file.endswith(".js"):
                return "JavaScript"

            if source_file.endswith(".jsx"):
                return "JavaScript"

            if source_file.endswith(".ts"):
                return "TypeScript"

            if source_file.endswith(".cpp"):
                return "C++"

            if source_file.endswith(".cc"):
                return "C++"

            if source_file.endswith(".cxx"):
                return "C++"

            if source_file.endswith(".c"):
                return "C"

            if source_file.endswith(".java"):
                return "Java"

            if source_file.endswith(".html"):
                return "HTML"

            if source_file.endswith(".css"):
                return "CSS"

        # Current AST pipeline
        return "Python"

    # ========================================================
    # SETUP UI
    # ========================================================

    def setup_ui(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            16,
            16,
            16,
            16
        )

        layout.setSpacing(8)

        # ====================================================
        # MAIN TITLE
        # ====================================================

        title = QLabel(
            "Insights & Code Visualizer"
        )

        title.setStyleSheet(
            """
            QLabel {
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 8px;
                color: #1a1a2e;
            }
            """
        )

        layout.addWidget(title)

        # ====================================================
        # CODE QUALITY TITLE
        # ====================================================

        quality_title = QLabel(
            "CODE QUALITY ANALYSIS"
        )

        quality_title.setStyleSheet(
            """
            QLabel {
                font-size: 13px;
                font-weight: bold;
                color: #1e293b;
                margin-top: 2px;
                margin-bottom: 2px;
            }
            """
        )

        layout.addWidget(quality_title)

        # ====================================================
        # QUALITY CARDS
        # ====================================================

        quality_layout = QHBoxLayout()

        quality_layout.setSpacing(10)

        # GOOD
        self.quality_good = (
            self._create_quality_card(
                "GOOD",
                "0.00%",
                "#16a34a"
            )
        )

        # MEDIUM
        self.quality_medium = (
            self._create_quality_card(
                "MEDIUM",
                "0.00%",
                "#d97706"
            )
        )

        # POOR
        self.quality_poor = (
            self._create_quality_card(
                "POOR",
                "0.00%",
                "#dc2626"
            )
        )

        # FUNCTIONS
        self.quality_total = (
            self._create_quality_card(
                "FUNCTIONS",
                "0",
                "#2563eb"
            )
        )

        # LANGUAGE
        self.language_card = (
            self._create_quality_card(
                "LANGUAGE",
                "Python",
                "#7c3aed"
            )
        )

        # Smaller language text
        self.language_card.value_label.setStyleSheet(
            """
            QLabel {
                color: #111827;
                font-size: 18px;
                font-weight: bold;
                border: none;
                background: transparent;
            }
            """
        )

        quality_layout.addWidget(
            self.quality_good
        )

        quality_layout.addWidget(
            self.quality_medium
        )

        quality_layout.addWidget(
            self.quality_poor
        )

        quality_layout.addWidget(
            self.quality_total
        )

        quality_layout.addWidget(
            self.language_card
        )

        layout.addLayout(
            quality_layout
        )

        # ====================================================
        # QUALITY INFORMATION
        # ====================================================

        quality_info = QFrame()

        quality_info.setStyleSheet(
            """
            QFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
            """
        )

        quality_info_layout = QHBoxLayout(
            quality_info
        )

        quality_info_layout.setContentsMargins(
            12,
            8,
            12,
            8
        )

        quality_info_layout.setSpacing(20)

        self.quality_rule_label = QLabel(
            "Classification: "
            "Good = 0 issues  •  "
            "Medium = 1–2 issues  •  "
            "Poor = 3+ issues"
        )

        self.quality_rule_label.setStyleSheet(
            """
            QLabel {
                color: #475569;
                font-size: 11px;
                border: none;
                background: transparent;
            }
            """
        )

        self.quality_rule_label.setWordWrap(True)

        quality_info_layout.addWidget(
            self.quality_rule_label
        )

        self.quality_summary_label = QLabel(
            "0 Good  •  0 Medium  •  0 Poor"
        )

        self.quality_summary_label.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.quality_summary_label.setStyleSheet(
            """
            QLabel {
                color: #334155;
                font-size: 11px;
                font-weight: bold;
                border: none;
                background: transparent;
            }
            """
        )

        quality_info_layout.addWidget(
            self.quality_summary_label
        )

        layout.addWidget(
            quality_info
        )

        # ====================================================
        # TABS
        # ====================================================

        self.tabs = QTabWidget()

        # ====================================================
        # QUALITY DETAILS
        # ====================================================

        self.quality_details_widget = QWidget()

        quality_details_layout = QVBoxLayout(
            self.quality_details_widget
        )

        quality_details_layout.setContentsMargins(
            12,
            12,
            12,
            12
        )

        quality_details_layout.setSpacing(10)

        quality_details_title = QLabel(
            "Function-Level Code Quality"
        )

        quality_details_title.setStyleSheet(
            """
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #1e293b;
                border: none;
                background: transparent;
            }
            """
        )

        quality_details_layout.addWidget(
            quality_details_title
        )

        quality_details_description = QLabel(
            "Functions are classified using the static-analysis "
            "findings generated by the compiler-analysis pipeline. "
            "Informational findings do not reduce the quality "
            "classification."
        )

        quality_details_description.setWordWrap(True)

        quality_details_description.setStyleSheet(
            """
            QLabel {
                color: #64748b;
                font-size: 11px;
                padding-bottom: 5px;
                border: none;
                background: transparent;
            }
            """
        )

        quality_details_layout.addWidget(
            quality_details_description
        )

        quality_columns = QHBoxLayout()

        quality_columns.setSpacing(10)

        (
            self.good_quality_frame,
            self.good_functions_list
        ) = self._create_quality_function_panel(
            "✓ GOOD FUNCTIONS",
            "#15803d",
            "#f0fdf4",
            "#bbf7d0"
        )

        (
            self.medium_quality_frame,
            self.medium_functions_list
        ) = self._create_quality_function_panel(
            "⚠ MEDIUM FUNCTIONS",
            "#b45309",
            "#fffbeb",
            "#fde68a"
        )

        (
            self.poor_quality_frame,
            self.poor_functions_list
        ) = self._create_quality_function_panel(
            "✗ POOR FUNCTIONS",
            "#b91c1c",
            "#fef2f2",
            "#fecaca"
        )

        quality_columns.addWidget(
            self.good_quality_frame
        )

        quality_columns.addWidget(
            self.medium_quality_frame
        )

        quality_columns.addWidget(
            self.poor_quality_frame
        )

        quality_details_layout.addLayout(
            quality_columns
        )

        self.tabs.addTab(
            self.quality_details_widget,
            "Quality Details"
        )

        # ====================================================
        # AST FEATURES
        # ====================================================

        self.tree_ast = QTreeWidget()

        self.tree_ast.setHeaderLabels(
            [
                "AST Node",
                "Details"
            ]
        )

        self.tree_ast.header().setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.ResizeToContents
        )

        self._empty_ast = _make_empty_state(
            "Run code generation to populate AST features.\n\n"
            "The AST tree will show functions, classes, "
            "parameters, and complexity metrics."
        )

        self._stack_ast = QStackedWidget()

        self._stack_ast.addWidget(
            self._empty_ast
        )

        self._stack_ast.addWidget(
            self.tree_ast
        )

        self.tabs.addTab(
            self._stack_ast,
            "AST Features"
        )

        # ====================================================
        # AST GRAPH
        # ====================================================

        self.ast_graph = AstGraphWidget()

        self.ast_graph.setStyleSheet(
            "background-color: #ffffff;"
        )

        self._empty_ast_graph = _make_empty_state(
            "Run code generation to visualize the AST graph.\n\n"
            "An interactive tree graph will display "
            "nodes and their relationships."
        )

        self._stack_ast_graph = QStackedWidget()

        self._stack_ast_graph.addWidget(
            self._empty_ast_graph
        )

        self._stack_ast_graph.addWidget(
            self.ast_graph
        )

        self.tabs.addTab(
            self._stack_ast_graph,
            "AST Graph"
        )

        # ====================================================
        # CONTEXT GRAPH
        # ====================================================

        self.tree_ctx = QTreeWidget()

        self.tree_ctx.setHeaderLabels(
            [
                "Function",
                "Context Data"
            ]
        )

        self.tree_ctx.header().setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.ResizeToContents
        )

        self._empty_ctx = _make_empty_state(
            "Run code generation to see context graph data.\n\n"
            "Function complexity, internal/external calls, "
            "and security warnings will appear here."
        )

        self._stack_ctx = QStackedWidget()

        self._stack_ctx.addWidget(
            self._empty_ctx
        )

        self._stack_ctx.addWidget(
            self.tree_ctx
        )

        self.tabs.addTab(
            self._stack_ctx,
            "Context Graph"
        )

        # ====================================================
        # CALL GRAPH
        # ====================================================

        self.call_graph = ContextGraphWidget()

        self.call_graph.setStyleSheet(
            "background-color: #ffffff;"
        )

        self._empty_call = _make_empty_state(
            "Run code generation to visualize the call graph.\n\n"
            "An interactive force-directed graph will "
            "display function call relationships."
        )

        self._stack_call = QStackedWidget()

        self._stack_call.addWidget(
            self._empty_call
        )

        self._stack_call.addWidget(
            self.call_graph
        )

        self.tabs.addTab(
            self._stack_call,
            "Call Graph"
        )

        # ====================================================
        # IR DUMP
        # ====================================================

        self.tab_ir = QTextEdit()

        self.tab_ir.setProperty(
            "class",
            "CodeEditor"
        )

        self.tab_ir.setReadOnly(True)

        self._empty_ir = _make_empty_state(
            "Run code generation to view the "
            "Intermediate Representation.\n\n"
            "The IR dump shows the internal representation "
            "used by the comment generator."
        )

        self._stack_ir = QStackedWidget()

        self._stack_ir.addWidget(
            self._empty_ir
        )

        self._stack_ir.addWidget(
            self.tab_ir
        )

        self.tabs.addTab(
            self._stack_ir,
            "IR Dump"
        )

        # ====================================================
        # ANALYSIS REPORT
        # ====================================================

        self.table_analysis = QTableWidget()

        self.table_analysis.setColumnCount(4)

        self.table_analysis.setHorizontalHeaderLabels(
            [
                "Severity",
                "Pattern",
                "Function",
                "Message"
            ]
        )

        self.table_analysis.horizontalHeader().setStretchLastSection(
            True
        )

        self.table_analysis.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.table_analysis.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self._empty_analysis = _make_empty_state(
            "Run code generation to see the analysis report.\n\n"
            "Pattern findings with severity, function, "
            "and message details will appear here."
        )

        self._stack_analysis = QStackedWidget()

        self._stack_analysis.addWidget(
            self._empty_analysis
        )

        self._stack_analysis.addWidget(
            self.table_analysis
        )

        self.tabs.addTab(
            self._stack_analysis,
            "Analysis Report"
        )

        # ====================================================
        # EVALUATION
        # ====================================================

        self.eval_graph = EvalGraphWidget()

        self.tabs.addTab(
            self.eval_graph,
            "Evaluation"
        )

        # ====================================================
        # MAIN LAYOUT
        # ====================================================

        layout.addWidget(
            self.tabs
        )

    # ========================================================
    # POPULATE INSIGHTS
    # ========================================================

    def populate_insights(
        self,
        pipeline_results
    ):

        self._populated = True

        # ====================================================
        # GET PIPELINE DATA
        # ====================================================

        mf = pipeline_results.get(
            "mf"
        )

        cg = pipeline_results.get(
            "cg"
        )

        ir_module = pipeline_results.get(
            "ir"
        )

        analysis_report = pipeline_results.get(
            "analysis"
        )

        # ====================================================
        # LANGUAGE
        # ====================================================

        language = self.detect_language(
            pipeline_results
        )

        self.language_card.value_label.setText(
            language
        )

        self.language_card.progress.setValue(
            100
        )

        # ====================================================
        # FUNCTION COUNT
        # ====================================================

        function_count = 0

        if mf is not None:

            try:

                function_count = len(
                    mf.functions
                )

            except (
                AttributeError,
                TypeError
            ):

                function_count = 0

        elif ir_module is not None:

            try:

                function_count = len(
                    ir_module.functions
                )

            except (
                AttributeError,
                TypeError
            ):

                function_count = 0

        # ====================================================
        # QUALITY
        # ====================================================

        quality = {
            "good": 0.0,
            "medium": 0.0,
            "poor": 0.0,
        }

        if analysis_report is not None:

            try:

                quality = (
                    analysis_report.quality_percentages(
                        total_functions=function_count
                    )
                )

            except (
                AttributeError,
                TypeError
            ):

                quality = getattr(
                    analysis_report,
                    "quality_distribution",
                    quality
                )

        good_pct = float(
            quality.get(
                "good",
                0.0
            )
        )

        medium_pct = float(
            quality.get(
                "medium",
                0.0
            )
        )

        poor_pct = float(
            quality.get(
                "poor",
                0.0
            )
        )

        # ====================================================
        # GOOD CARD
        # ====================================================

        self.quality_good.value_label.setText(
            f"{good_pct:.2f}%"
        )

        self.quality_good.progress.setValue(
            max(
                0,
                min(
                    100,
                    int(
                        round(
                            good_pct
                        )
                    )
                )
            )
        )

        # ====================================================
        # MEDIUM CARD
        # ====================================================

        self.quality_medium.value_label.setText(
            f"{medium_pct:.2f}%"
        )

        self.quality_medium.progress.setValue(
            max(
                0,
                min(
                    100,
                    int(
                        round(
                            medium_pct
                        )
                    )
                )
            )
        )

        # ====================================================
        # POOR CARD
        # ====================================================

        self.quality_poor.value_label.setText(
            f"{poor_pct:.2f}%"
        )

        self.quality_poor.progress.setValue(
            max(
                0,
                min(
                    100,
                    int(
                        round(
                            poor_pct
                        )
                    )
                )
            )
        )

        # ====================================================
        # FUNCTIONS CARD
        # ====================================================

        self.quality_total.value_label.setText(
            str(function_count)
        )

        self.quality_total.progress.setValue(
            100 if function_count > 0 else 0
        )

        # ====================================================
        # FUNCTION COUNTS
        # ====================================================

        good_count = round(
            (
                good_pct
                / 100
            )
            * function_count
        )

        medium_count = round(
            (
                medium_pct
                / 100
            )
            * function_count
        )

        poor_count = round(
            (
                poor_pct
                / 100
            )
            * function_count
        )

        self.quality_summary_label.setText(
            f"{good_count} Good  •  "
            f"{medium_count} Medium  •  "
            f"{poor_count} Poor"
        )

        # ====================================================
        # FUNCTION-LEVEL QUALITY
        # ====================================================

        self.good_functions_list.clear()

        self.medium_functions_list.clear()

        self.poor_functions_list.clear()

        function_issues = {}

        # ----------------------------------------------------
        # Add every function with zero issues initially
        # ----------------------------------------------------

        if mf is not None:

            try:

                for func in mf.functions:

                    function_issues[
                        func.name
                    ] = 0

            except (
                AttributeError,
                TypeError
            ):

                pass

        # ----------------------------------------------------
        # Count warning/error findings
        # ----------------------------------------------------

        if analysis_report is not None:

            try:

                findings = (
                    analysis_report.findings
                )

            except AttributeError:

                findings = []

            for finding in findings:

                if finding.severity in (
                    "warning",
                    "error"
                ):

                    function_name = (
                        finding.function_name
                    )

                    function_issues[
                        function_name
                    ] = (
                        function_issues.get(
                            function_name,
                            0
                        )
                        + 1
                    )

        # ====================================================
        # CLASSIFICATION
        # ====================================================

        good_functions = []

        medium_functions = []

        poor_functions = []

        for (
            function_name,
            issue_count
        ) in function_issues.items():

            if issue_count == 0:

                good_functions.append(
                    (
                        function_name,
                        issue_count
                    )
                )

            elif issue_count <= 2:

                medium_functions.append(
                    (
                        function_name,
                        issue_count
                    )
                )

            else:

                poor_functions.append(
                    (
                        function_name,
                        issue_count
                    )
                )

        # ====================================================
        # SORT
        # ====================================================

        good_functions.sort(
            key=lambda x: x[0].lower()
        )

        medium_functions.sort(
            key=lambda x: x[0].lower()
        )

        poor_functions.sort(
            key=lambda x: x[0].lower()
        )

        # ====================================================
        # GOOD FUNCTIONS
        # ====================================================

        for (
            function_name,
            issue_count
        ) in good_functions:

            item = QListWidgetItem(
                f"✓  {function_name}"
            )

            item.setToolTip(
                "Good quality — "
                "no warning/error findings."
            )

            self.good_functions_list.addItem(
                item
            )

        # ====================================================
        # MEDIUM FUNCTIONS
        # ====================================================

        for (
            function_name,
            issue_count
        ) in medium_functions:

            issue_text = (
                "issue"
                if issue_count == 1
                else "issues"
            )

            item = QListWidgetItem(
                f"⚠  {function_name} "
                f"— {issue_count} {issue_text}"
            )

            item.setToolTip(
                f"Medium quality — "
                f"{issue_count} warning/error finding(s)."
            )

            self.medium_functions_list.addItem(
                item
            )

        # ====================================================
        # POOR FUNCTIONS
        # ====================================================

        for (
            function_name,
            issue_count
        ) in poor_functions:

            issue_text = (
                "issue"
                if issue_count == 1
                else "issues"
            )

            item = QListWidgetItem(
                f"✗  {function_name} "
                f"— {issue_count} {issue_text}"
            )

            item.setToolTip(
                f"Poor quality — "
                f"{issue_count} warning/error finding(s)."
            )

            self.poor_functions_list.addItem(
                item
            )

        # ====================================================
        # EMPTY STATES
        # ====================================================

        if not good_functions:

            self.good_functions_list.addItem(
                "No Good functions"
            )

        if not medium_functions:

            self.medium_functions_list.addItem(
                "No Medium functions"
            )

        if not poor_functions:

            self.poor_functions_list.addItem(
                "No Poor functions"
            )

        # ====================================================
        # AST FEATURES
        # ====================================================

        self.tree_ast.clear()

        if mf:

            self._stack_ast.setCurrentIndex(1)

            self._stack_ast_graph.setCurrentIndex(1)

            root_funcs = QTreeWidgetItem(
                self.tree_ast,
                [
                    "Functions",
                    f"{len(mf.functions)} found"
                ]
            )

            for func in mf.functions:

                f_item = QTreeWidgetItem(
                    root_funcs,
                    [
                        func.name,
                        f"Line {func.lineno}"
                    ]
                )

                # Parameters
                if func.params:

                    p_root = QTreeWidgetItem(
                        f_item,
                        [
                            "Parameters",
                            ""
                        ]
                    )

                    for p in func.params:

                        p_desc = p.name

                        if p.annotation:

                            p_desc += (
                                f": "
                                f"{p.annotation}"
                            )

                        if p.default:

                            p_desc += (
                                f" = "
                                f"{p.default}"
                            )

                        QTreeWidgetItem(
                            p_root,
                            [
                                "Param",
                                p_desc
                            ]
                        )

                # Returns
                QTreeWidgetItem(
                    f_item,
                    [
                        "Returns",
                        func.return_annotation
                        or "None"
                    ]
                )

                # Complexity
                QTreeWidgetItem(
                    f_item,
                    [
                        "Complexity",
                        (
                            f"Loops: "
                            f"{func.loops}, "
                            f"Conditionals: "
                            f"{func.conditionals}"
                        )
                    ]
                )

            # Classes
            root_classes = QTreeWidgetItem(
                self.tree_ast,
                [
                    "Classes",
                    f"{len(mf.classes)} found"
                ]
            )

            for cls in mf.classes:

                c_item = QTreeWidgetItem(
                    root_classes,
                    [
                        cls.name,
                        f"Line {cls.lineno}"
                    ]
                )

                if cls.bases:

                    QTreeWidgetItem(
                        c_item,
                        [
                            "Bases",
                            ", ".join(
                                cls.bases
                            )
                        ]
                    )

                if cls.methods:

                    QTreeWidgetItem(
                        c_item,
                        [
                            "Methods",
                            ", ".join(
                                cls.methods
                            )
                        ]
                    )

            self.tree_ast.expandAll()

            self.ast_graph.set_data(
                mf
            )

        # ====================================================
        # CONTEXT GRAPH
        # ====================================================

        self.tree_ctx.clear()

        if cg:

            self._stack_ctx.setCurrentIndex(1)

            self._stack_call.setCurrentIndex(1)

            for fc in cg.function_contexts:

                item = QTreeWidgetItem(
                    self.tree_ctx,
                    [
                        fc.name,
                        fc.complexity_label
                    ]
                )

                # Complexity colors
                if (
                    fc.complexity_label
                    == "simple"
                ):

                    item.setForeground(
                        1,
                        QBrush(
                            QColor(
                                "#16a34a"
                            )
                        )
                    )

                elif (
                    fc.complexity_label
                    == "moderate"
                ):

                    item.setForeground(
                        1,
                        QBrush(
                            QColor(
                                "#ca8a04"
                            )
                        )
                    )

                elif (
                    fc.complexity_label
                    in (
                        "complex",
                        "very_complex"
                    )
                ):

                    item.setForeground(
                        1,
                        QBrush(
                            QColor(
                                "#dc2626"
                            )
                        )
                    )

                # Internal calls
                if fc.calls_internal:

                    QTreeWidgetItem(
                        item,
                        [
                            "Internal Calls",
                            ", ".join(
                                fc.calls_internal
                            )
                        ]
                    )

                # External calls
                if fc.calls_external:

                    QTreeWidgetItem(
                        item,
                        [
                            "External Calls",
                            ", ".join(
                                fc.calls_external
                            )
                        ]
                    )

                # Security warnings
                security_issues = getattr(
                    fc,
                    "security_issues",
                    []
                )

                if security_issues:

                    sec_item = (
                        QTreeWidgetItem(
                            item,
                            [
                                "Security Warnings",
                                (
                                    f"{len(security_issues)} "
                                    f"found"
                                )
                            ]
                        )
                    )

                    sec_item.setForeground(
                        0,
                        QBrush(
                            QColor(
                                "#dc2626"
                            )
                        )
                    )

                    for sec in security_issues:

                        s_i = QTreeWidgetItem(
                            sec_item,
                            [
                                "Warning",
                                sec
                            ]
                        )

                        s_i.setForeground(
                            1,
                            QBrush(
                                QColor(
                                    "#dc2626"
                                )
                            )
                        )

            self.tree_ctx.expandAll()

            self.call_graph.set_data(
                cg
            )

        # ====================================================
        # IR DUMP
        # ====================================================

        if ir_module:

            self._stack_ir.setCurrentIndex(1)

            from src.ir import pretty_print_ir

            self.tab_ir.setPlainText(
                pretty_print_ir(
                    ir_module
                )
            )

        # ====================================================
        # ANALYSIS REPORT
        # ====================================================

        self.table_analysis.setRowCount(0)

        if (
            analysis_report
            and analysis_report.findings
        ):

            self._stack_analysis.setCurrentIndex(1)

            self.table_analysis.setRowCount(
                len(
                    analysis_report.findings
                )
            )

            for i, finding in enumerate(
                analysis_report.findings
            ):

                # Severity
                sev_item = QTableWidgetItem(
                    finding.severity.upper()
                )

                if (
                    finding.severity
                    == "warning"
                ):

                    sev_item.setForeground(
                        QBrush(
                            QColor(
                                "#ca8a04"
                            )
                        )
                    )

                elif (
                    finding.severity
                    == "error"
                ):

                    sev_item.setForeground(
                        QBrush(
                            QColor(
                                "#dc2626"
                            )
                        )
                    )

                else:

                    sev_item.setForeground(
                        QBrush(
                            QColor(
                                "#2563eb"
                            )
                        )
                    )

                self.table_analysis.setItem(
                    i,
                    0,
                    sev_item
                )

                # Pattern
                self.table_analysis.setItem(
                    i,
                    1,
                    QTableWidgetItem(
                        finding.pattern_id
                    )
                )

                # Function
                self.table_analysis.setItem(
                    i,
                    2,
                    QTableWidgetItem(
                        finding.function_name
                    )
                )

                # Message
                self.table_analysis.setItem(
                    i,
                    3,
                    QTableWidgetItem(
                        finding.message
                    )
                )

        self.table_analysis.resizeColumnsToContents()

        self.table_analysis.horizontalHeader().setStretchLastSection(
            True
        )

        # ====================================================
        # EVALUATION
        # ====================================================

        import os

        eval_path = os.path.join(
            os.path.dirname(
                os.path.abspath(
                    __file__
                )
            ),
            "..",
            "..",
            "outputs",
            "eval_report.json"
        )

        train_path = os.path.join(
            os.path.dirname(
                os.path.abspath(
                    __file__
                )
            ),
            "..",
            "..",
            "outputs",
            "training_report.json"
        )

        self.eval_graph.set_data(
            eval_json_path=eval_path,
            training_json_path=train_path
        )