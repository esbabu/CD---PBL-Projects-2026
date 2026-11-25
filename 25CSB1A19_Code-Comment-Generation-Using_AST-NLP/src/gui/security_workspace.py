from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QPushButton,
    QStackedWidget,
    QTextEdit,
    QTabWidget,
)

from PyQt6.QtGui import QColor, QBrush
from PyQt6.QtCore import Qt

from src.gui.security_graph_widget import SecurityGraphWidget


# ============================================================
# SECURITY WORKSPACE
# ============================================================

class SecurityWorkspace(QWidget):

    def __init__(self, parent=None):

        super().__init__(parent)

        self._security_report = None
        self._populated = False

        self.ai_worker = None

        self.setup_ui()

    # ========================================================
    # MAIN UI
    # ========================================================

    def setup_ui(self):

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            20,
            18,
            20,
            18
        )

        main_layout.setSpacing(12)

        # ====================================================
        # HEADER
        # ====================================================

        header_layout = QHBoxLayout()

        title = QLabel(
            "Security Analysis"
        )

        title.setStyleSheet(
            """
            QLabel {
                font-size: 25px;
                font-weight: bold;
                color: #172554;
            }
            """
        )

        header_layout.addWidget(title)

        header_layout.addStretch()

        # Safety score

        self.safety_score_label = QLabel(
            "Safety Score: N/A"
        )

        self.safety_score_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.safety_score_label.setStyleSheet(
            """
            QLabel {
                font-size: 15px;
                font-weight: bold;
                color: #6b7280;
                padding: 9px 18px;
                background: #f3f4f6;
                border-radius: 10px;
            }
            """
        )

        header_layout.addWidget(
            self.safety_score_label
        )

        # Unsafe percentage

        self.unsafe_pct_label = QLabel(
            "N/A"
        )

        self.unsafe_pct_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.unsafe_pct_label.setStyleSheet(
            """
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #6b7280;
                padding: 9px 15px;
                background: #f3f4f6;
                border-radius: 10px;
            }
            """
        )

        header_layout.addWidget(
            self.unsafe_pct_label
        )

        main_layout.addLayout(
            header_layout
        )

        # ====================================================
        # TABS
        # ====================================================

        self.tabs = QTabWidget()

        self.tabs.setDocumentMode(True)

        self.tabs.setStyleSheet(
            """
            QTabWidget::pane {
                border: 1px solid #e5e7eb;
                border-radius: 10px;
                background: #ffffff;
                top: -1px;
            }

            QTabBar {
                background: #ffffff;
            }

            QTabBar::tab {
                background: #f3f4f6;
                color: #374151;
                padding: 11px 20px;
                margin-right: 4px;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                font-weight: bold;
            }

            QTabBar::tab:selected {
                background: #2563eb;
                color: white;
                border: 1px solid #2563eb;
            }

            QTabBar::tab:hover {
                background: #dbeafe;
                color: #1d4ed8;
            }

            QScrollBar:vertical {
                background: #f1f5f9;
                width: 12px;
                margin: 2px;
                border-radius: 6px;
            }

            QScrollBar::handle:vertical {
                background: #94a3b8;
                min-height: 40px;
                border-radius: 6px;
            }

            QScrollBar::handle:vertical:hover {
                background: #64748b;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QScrollBar:horizontal {
                height: 10px;
                background: #f1f5f9;
            }

            QScrollBar::handle:horizontal {
                background: #94a3b8;
                border-radius: 5px;
            }
            """
        )

        main_layout.addWidget(
            self.tabs,
            stretch=1
        )

        # Create tabs

        self.create_overview_tab()

        self.create_issues_tab()


    # ========================================================
    # OVERVIEW TAB
    # ========================================================

    def create_overview_tab(self):

        page = QWidget()

        layout = QVBoxLayout(page)

        layout.setContentsMargins(
            15,
            15,
            15,
            15
        )

        layout.setSpacing(10)

        self._empty_state = QLabel(
            "Run code generation to perform security analysis.\n\n"
            "Safety scores, function security scores, "
            "and security issue information will appear here."
        )

        self._empty_state.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self._empty_state.setWordWrap(True)

        self._empty_state.setStyleSheet(
            """
            QLabel {
                color: #9ca3af;
                font-size: 15px;
                padding: 30px;
            }
            """
        )

        self.security_graph = SecurityGraphWidget()

        self._graph_stack = QStackedWidget()

        self._graph_stack.addWidget(
            self._empty_state
        )

        self._graph_stack.addWidget(
            self.security_graph
        )

        layout.addWidget(
            self._graph_stack
        )

        self.tabs.addTab(
            page,
            "📊 Overview"
        )

    # ========================================================
    # SECURITY ISSUES TAB
    # ========================================================

    def create_issues_tab(self):

        page = QWidget()

        layout = QVBoxLayout(page)

        layout.setContentsMargins(
            15,
            15,
            15,
            15
        )

        layout.setSpacing(10)

        title = QLabel(
            "Security Issues Detail"
        )

        title.setStyleSheet(
            """
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #172554;
                padding: 5px;
            }
            """
        )

        layout.addWidget(title)

        description = QLabel(
            "Detected security issues from the project's "
            "existing static security analyzer."
        )

        description.setStyleSheet(
            """
            QLabel {
                color: #6b7280;
                font-size: 13px;
                padding-bottom: 5px;
            }
            """
        )

        layout.addWidget(
            description
        )

        self.table = QTableWidget()

        self.table.setColumnCount(5)

        self.table.setHorizontalHeaderLabels(
            [
                "Severity",
                "Pattern",
                "Function",
                "Line",
                "Message / Remediation"
            ]
        )

        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.table.setAlternatingRowColors(
            True
        )

        self.table.verticalHeader().setVisible(
            False
        )

        self.table.horizontalHeader().setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.ResizeToContents
        )

        self.table.horizontalHeader().setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.ResizeToContents
        )

        self.table.horizontalHeader().setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.ResizeToContents
        )

        self.table.horizontalHeader().setSectionResizeMode(
            3,
            QHeaderView.ResizeMode.ResizeToContents
        )

        self.table.horizontalHeader().setSectionResizeMode(
            4,
            QHeaderView.ResizeMode.Stretch
        )

        layout.addWidget(
            self.table
        )

        self.tabs.addTab(
            page,
            "⚠️ Security Issues"
        )

    # ========================================================
    # POPULATE EXISTING SECURITY REPORT
    # ========================================================

    def populate(self, security_report):

        self._security_report = security_report

        if not security_report:

            if not self._populated:

                self._graph_stack.setCurrentIndex(
                    0
                )

            self.safety_score_label.setText(
                "Safety Score: N/A"
            )

            self.safety_score_label.setStyleSheet(
                """
                QLabel {
                    font-size: 15px;
                    font-weight: bold;
                    color: #6b7280;
                    padding: 9px 18px;
                    background: #f3f4f6;
                    border-radius: 10px;
                }
                """
            )

            self.unsafe_pct_label.setText(
                "N/A"
            )

            self.unsafe_pct_label.setStyleSheet(
                """
                QLabel {
                    font-size: 14px;
                    font-weight: bold;
                    color: #6b7280;
                    padding: 9px 15px;
                    background: #f3f4f6;
                    border-radius: 10px;
                }
                """
            )

            return

        self._populated = True

        self._graph_stack.setCurrentIndex(
            1
        )

        safe_pct = security_report.module_safe_pct

        unsafe_pct = round(
            100.0 - safe_pct,
            1
        )

        # ----------------------------------------------------
        # Safety color
        # ----------------------------------------------------

        if safe_pct >= 80:

            color = "#16a34a"
            background = "#f0fdf4"

        elif safe_pct >= 50:

            color = "#ca8a04"
            background = "#fefce8"

        else:

            color = "#dc2626"
            background = "#fef2f2"

        self.safety_score_label.setText(
            f"Safety: {safe_pct}% safe"
        )

        self.safety_score_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 15px;
                font-weight: bold;
                color: {color};
                padding: 9px 18px;
                background: {background};
                border-radius: 10px;
            }}
            """
        )

        # ----------------------------------------------------
        # Unsafe percentage
        # ----------------------------------------------------

        if unsafe_pct > 20:

            unsafe_color = "#dc2626"

        elif unsafe_pct > 0:

            unsafe_color = "#ca8a04"

        else:

            unsafe_color = "#16a34a"

        self.unsafe_pct_label.setText(
            f"{unsafe_pct}% unsafe"
        )

        self.unsafe_pct_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 14px;
                font-weight: bold;
                color: {unsafe_color};
                padding: 9px 15px;
                background: #f8fafc;
                border-radius: 10px;
            }}
            """
        )

        # ----------------------------------------------------
        # Existing security graph
        # ----------------------------------------------------

        self.security_graph.set_data(
            security_report
        )

        # ----------------------------------------------------
        # Existing issues table
        # ----------------------------------------------------

        self.table.setRowCount(0)

        if security_report.issues:

            self.table.setRowCount(
                len(
                    security_report.issues
                )
            )

            for i, issue in enumerate(
                security_report.issues
            ):

                severity = (
                    issue.severity.lower()
                )

                severity_item = QTableWidgetItem(
                    severity.upper()
                )

                severity_colors = {
                    "critical": "#dc2626",
                    "high": "#ea580c",
                    "medium": "#ca8a04",
                    "low": "#2563eb",
                }

                severity_item.setForeground(
                    QBrush(
                        QColor(
                            severity_colors.get(
                                severity,
                                "#6b7280"
                            )
                        )
                    )
                )

                self.table.setItem(
                    i,
                    0,
                    severity_item
                )

                self.table.setItem(
                    i,
                    1,
                    QTableWidgetItem(
                        issue.pattern_id
                    )
                )

                self.table.setItem(
                    i,
                    2,
                    QTableWidgetItem(
                        issue.function_name
                    )
                )

                self.table.setItem(
                    i,
                    3,
                    QTableWidgetItem(
                        str(issue.lineno)
                    )
                )

                message = issue.message

                if issue.remediation:

                    message += (
                        " | Fix: "
                        + issue.remediation
                    )

                self.table.setItem(
                    i,
                    4,
                    QTableWidgetItem(
                        message
                    )
                )
