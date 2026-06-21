"""AttendancePage — 考勤记录查询页，对齐 Figma 设计。"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from app.pages.base_page import BasePage

# ── Figma colors ──────────────────────────────────────────────────────────
_BG = "#f9f9ff"
_TEXT_PRIMARY = "#091c35"
_TEXT_SECONDARY = "#5c5f60"
_TEXT_MUTED = "#737685"
_BORDER = "#c3c6d6"
_BRAND = "#003d9b"
_WHITE = "#ffffff"
_TABLE_HEADER_BG = "#f0f3ff"
_TABLE_HOVER = "#f0f3ff"
_PRESENT_BG = "#00a3bf26"
_PRESENT_TEXT = "#005a6b"
_LATE_BG = "#ffab0026"
_LATE_TEXT = "#8f5b00"
_ABSENT_BG = "#ff563026"
_ABSENT_TEXT = "#8f271b"
_MONO = "'JetBrains Mono'"


# ── Status badge ──────────────────────────────────────────────────────────

def _status_badge(text: str) -> QFrame:
    style_map = {
        "PRESENT": (_PRESENT_BG, _PRESENT_TEXT),
        "LATE": (_LATE_BG, _LATE_TEXT),
        "ABSENT": (_ABSENT_BG, _ABSENT_TEXT),
    }
    bg, fg = style_map.get(text.upper(), ("#f0f3ff", _TEXT_SECONDARY))
    badge = QFrame()
    badge.setStyleSheet(f"background: {bg}; border-radius: 2px; padding: 2px 8px;")
    layout = QHBoxLayout(badge)
    layout.setContentsMargins(8, 2, 8, 2)
    lbl = QLabel(text.upper())
    lbl.setStyleSheet(f"color: {fg}; font-size: 12px; font-weight: 700; letter-spacing: 0.6px;")
    layout.addWidget(lbl)
    return badge


# ── Summary stat card ──────────────────────────────────────────────────────

class StatCard(QFrame):
    def __init__(self, label: str, value: str, pct: str = "", pct_color: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("attStatCard")
        self.setStyleSheet(f"""
            #attStatCard {{
                background: {_WHITE};
                border: 1px solid {_BORDER};
                border-radius: 2px;
            }}
        """)
        self.setFixedSize(221, 89)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(6)

        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {_TEXT_SECONDARY}; font-size: 12px; font-weight: 700; letter-spacing: 0.6px;")
        layout.addWidget(lbl)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        self.val_lbl = QLabel(value)
        self.val_lbl.setStyleSheet(f"color: {_TEXT_PRIMARY}; font-size: 28px; font-weight: 700;")
        row.addWidget(self.val_lbl)
        row.addStretch()
        if pct:
            self.pct_lbl = QLabel(pct)
            self.pct_lbl.setStyleSheet(f"color: {pct_color}; font-size: 14px; font-weight: 600;")
            row.addWidget(self.pct_lbl)
        layout.addLayout(row)


# ═══════════════════════════════════════════════════════════════════════════

class AttendancePage(BasePage):
    """考勤明细：筛选栏 + 统计摘要 + 表格 + 分页。"""

    def setup_ui(self):
        self.setObjectName("attendancePage")
        self.setStyleSheet(f"background: transparent;")

        root = QVBoxLayout(self)
        root.setContentsMargins(32, 32, 32, 32)
        root.setSpacing(0)

        # ═══════════════════════════════════════════════════════════════
        # Page Header
        # ═══════════════════════════════════════════════════════════════
        header = QFrame()
        header.setFixedHeight(64)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(0, 0, 0, 0)

        left = QVBoxLayout()
        left.setContentsMargins(0, 0, 0, 0)
        left.setSpacing(0)
        title = QLabel("Attendance Records")
        title.setStyleSheet(f"color: {_TEXT_PRIMARY}; font-size: 32px; font-weight: 700; letter-spacing: -0.64px;")
        left.addWidget(title)
        subtitle = QLabel("Review and manage historical check-in data.")
        subtitle.setStyleSheet(f"color: {_TEXT_SECONDARY}; font-size: 14px;")
        left.addWidget(subtitle)
        h_layout.addLayout(left)
        h_layout.addStretch()

        export_btn = QPushButton("  Export CSV")
        export_btn.setObjectName("exportCsvBtn")
        export_btn.setStyleSheet(f"""
            #exportCsvBtn {{
                background: {_WHITE};
                border: 1px solid {_BORDER};
                border-radius: 2px;
                color: {_BRAND};
                font-size: 16px;
                padding: 8px 16px;
            }}
            #exportCsvBtn:hover {{ background: {_TABLE_HEADER_BG}; }}
        """)
        export_btn.setFixedHeight(42)
        export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        h_layout.addWidget(export_btn)

        root.addWidget(header)
        root.addSpacing(24)

        # ═══════════════════════════════════════════════════════════════
        # Filter Bar
        # ═══════════════════════════════════════════════════════════════
        filter_bar = QFrame()
        filter_bar.setObjectName("filterBar")
        filter_bar.setStyleSheet(f"""
            #filterBar {{
                background: {_WHITE};
                border: 1px solid {_BORDER};
                border-radius: 2px;
            }}
        """)
        filter_bar.setFixedHeight(100)
        filter_layout = QHBoxLayout(filter_bar)
        filter_layout.setContentsMargins(16, 16, 16, 16)
        filter_layout.setSpacing(16)

        self.date_combo = self._filter_dropdown("DATE RANGE", "Last 7 Days")
        self.course_combo = self._filter_dropdown("COURSE", "All Courses")
        self.status_combo = self._filter_dropdown("STATUS", "All Statuses")

        filter_layout.addWidget(self.date_combo)
        filter_layout.addWidget(self.course_combo)
        filter_layout.addWidget(self.status_combo)
        filter_layout.addStretch()

        search_btn = QPushButton("Search")
        search_btn.setObjectName("searchBtn")
        search_btn.setStyleSheet(f"""
            #searchBtn {{
                background: {_BRAND};
                border: none;
                border-radius: 2px;
                color: {_WHITE};
                font-size: 16px;
                font-weight: 600;
                padding: 8px 24px;
            }}
            #searchBtn:hover {{ background: #002b6a; }}
        """)
        search_btn.setFixedHeight(40)
        search_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        filter_layout.addWidget(search_btn, alignment=Qt.AlignmentFlag.AlignBottom)

        root.addWidget(filter_bar)
        root.addSpacing(16)

        # ═══════════════════════════════════════════════════════════════
        # Summary Bar
        # ═══════════════════════════════════════════════════════════════
        summary = QHBoxLayout()
        summary.setContentsMargins(0, 0, 0, 0)
        summary.setSpacing(24)

        self.stat_total = StatCard("TOTAL RECORDS", "—")
        self.stat_present = StatCard("PRESENT", "—", pct="—", pct_color=_PRESENT_TEXT)
        self.stat_late = StatCard("LATE", "—", pct="—", pct_color=_LATE_TEXT)
        self.stat_absent = StatCard("ABSENT", "—", pct="—", pct_color=_ABSENT_TEXT)

        summary.addWidget(self.stat_total)
        summary.addWidget(self.stat_present)
        summary.addWidget(self.stat_late)
        summary.addWidget(self.stat_absent)
        root.addLayout(summary)
        root.addSpacing(16)

        # ═══════════════════════════════════════════════════════════════
        # Data Table
        # ═══════════════════════════════════════════════════════════════
        table_container = QFrame()
        table_container.setObjectName("tableContainer")
        table_container.setStyleSheet(f"""
            #tableContainer {{
                background: {_WHITE};
                border: 1px solid {_BORDER};
                border-radius: 2px;
            }}
        """)

        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(1, 1, 1, 1)
        table_layout.setSpacing(0)

        self.table = QTableWidget()
        self.table.setObjectName("attTable")
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "STUDENT NAME", "STUDENT ID", "COURSE",
            "CHECK-IN TIME", "STATUS", "CONFIDENCE", "ACTIONS"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(False)
        self.table.setStyleSheet(f"""
            #attTable {{
                border: none;
                background: {_WHITE};
                font-size: 13px;
            }}
            #attTable::item {{
                padding: 12px 16px;
                border-bottom: 1px solid {_BORDER};
                color: {_TEXT_PRIMARY};
            }}
            #attTable::item:selected {{
                background: {_TABLE_HEADER_BG};
                color: {_TEXT_PRIMARY};
            }}
            QHeaderView::section {{
                background: {_TABLE_HEADER_BG};
                color: {_TEXT_SECONDARY};
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 0.6px;
                border: none;
                border-bottom: 1px solid {_BORDER};
                padding: 16px;
            }}
        """)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        table_layout.addWidget(self.table, 1)

        # ═══════════════════════════════════════════════════════════════
        # Pagination
        # ═══════════════════════════════════════════════════════════════
        pagination = QFrame()
        pagination.setObjectName("pagination")
        pagination.setStyleSheet(f"""
            #pagination {{
                background: {_BG};
                border-top: 1px solid {_BORDER};
            }}
        """)
        pagination.setFixedHeight(48)
        pag_layout = QHBoxLayout(pagination)
        pag_layout.setContentsMargins(16, 12, 16, 12)

        self.pag_label = QLabel("Showing 0 of 0 entries")
        self.pag_label.setStyleSheet(f"color: {_TEXT_SECONDARY}; font-size: 14px;")
        pag_layout.addWidget(self.pag_label)
        pag_layout.addStretch()

        # Page buttons
        pag_nav = QHBoxLayout()
        pag_nav.setSpacing(4)
        for p in ["1", "2", "3", "..."]:
            btn = QPushButton(p)
            btn.setFixedSize(28, 28)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            is_active = p == "1"
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {_BRAND if is_active else "transparent"};
                    border: none;
                    border-radius: 2px;
                    color: {_WHITE if is_active else _TEXT_SECONDARY};
                    font-size: {14 if is_active else 14}px;
                    font-weight: {700 if is_active else 400};
                }}
                QPushButton:hover {{
                    background: {_TABLE_HEADER_BG if not is_active else _BRAND};
                    color: {_TEXT_PRIMARY if not is_active else _WHITE};
                }}
            """)
            pag_nav.addWidget(btn)
        pag_layout.addLayout(pag_nav)

        table_layout.addWidget(pagination)
        root.addWidget(table_container, 1)

    # ── Filter dropdown helper ──

    def _filter_dropdown(self, label: str, default: str) -> QFrame:
        container = QFrame()
        container.setFixedSize(257, 66)
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(8)

        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {_TEXT_SECONDARY}; font-size: 12px; font-weight: 700; letter-spacing: 0.6px;")
        vbox.addWidget(lbl)

        shell = QFrame()
        shell.setObjectName("filterDropdown")
        shell.setStyleSheet(f"""
            #filterDropdown {{
                background: {_BG};
                border: 1px solid {_BORDER};
                border-radius: 2px;
            }}
        """)
        shell.setFixedHeight(42)
        shell_layout = QHBoxLayout(shell)
        shell_layout.setContentsMargins(12, 8, 12, 8)

        combo = QComboBox()
        combo.setObjectName("filterCombo")
        combo.addItems([default])
        combo.setStyleSheet(f"""
            QComboBox#filterCombo {{
                background: transparent;
                border: none;
                color: {_TEXT_PRIMARY};
                font-size: 16px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border: none;
            }}
        """)
        shell_layout.addWidget(combo, 1)

        vbox.addWidget(shell)
        return container

    # ── Data ──

    def bind(self):
        pass

    def refresh(self):
        self._load_demo()

    def _load_demo(self):
        """Load demo data to match Figma layout."""
        data = [
            ("Alex Chen",      "STU-9281", "CS101", "08:55:12 AM", "PRESENT", "99.8%"),
            ("Sarah Jenkins",  "STU-4412", "CS101", "08:58:45 AM", "PRESENT", "98.2%"),
            ("Marcus Johnson", "STU-7734", "CS101", "09:12:05 AM", "LATE",    "95.4%"),
            ("Emily Davis",    "STU-1190", "CS101", "--:--:--",    "ABSENT",  "--"),
            ("David Kim",      "STU-5521", "ENG202","10:45:22 AM", "PRESENT", "99.9%"),
            ("Priya Patel",    "STU-8832", "ENG202","10:52:10 AM", "PRESENT", "72.1%"),
        ]
        self.table.setRowCount(len(data))
        for r, (name, sid, course, time, status, conf) in enumerate(data):
            for c, val in enumerate([name, sid, course, time]):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
                if status == "ABSENT":
                    item.setForeground(Qt.GlobalColor.gray)
                self.table.setItem(r, c, item)

            # Status column — use custom widget
            self.table.setCellWidget(r, 4, _status_badge(status))

            conf_item = QTableWidgetItem(conf)
            conf_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(r, 5, conf_item)

        # Summary bar
        self.stat_total.val_lbl.setText("1,248")
        self.stat_present.val_lbl.setText("1,102")
        self.stat_present.pct_lbl.setText("88%")
        self.stat_late.val_lbl.setText("94")
        self.stat_late.pct_lbl.setText("7.5%")
        self.stat_absent.val_lbl.setText("52")
        self.stat_absent.pct_lbl.setText("4.5%")

        self.pag_label.setText("Showing 1 to 6 of 1,248 entries")
