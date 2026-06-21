"""AttendancePage — 考勤记录查询页，对齐 Figma 设计。"""
from __future__ import annotations

from PySide6.QtCore import QThread, Qt, Signal
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
from app.services.attendance_service import attendance_service
from app.services.course_service import course_service

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


# ── Worker — 后台取数据 ─────────────────────────────────────────────────

class AttendanceWorker(QThread):
    finished = Signal(object)

    def __init__(self, fn, params=None):
        super().__init__()
        self._fn = fn
        self._params = params

    def run(self):
        try:
            result = self._fn(self._params) if self._params else self._fn()
        except Exception as e:
            result = type("R", (), {"ok": False, "data": None, "message": str(e)})()
        self.finished.emit(result)


# ═══════════════════════════════════════════════════════════════════════════

class AttendancePage(BasePage):
    """考勤明细：筛选栏 + 统计摘要 + 表格 + 分页。"""

    def __init__(self, parent=None):
        self._workers: list[QThread] = []
        self._current_page = 1
        self._course_map: dict[str, int] = {}
        super().__init__(parent)

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

        self.export_btn = QPushButton("  Export CSV")
        self.export_btn.setObjectName("exportCsvBtn")
        self.export_btn.setStyleSheet(f"""
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
        self.export_btn.setFixedHeight(42)
        self.export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.export_btn.setVisible(False)  # ponytail: hide, add when needed
        h_layout.addWidget(self.export_btn)

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

        self.date_combo = self._filter_dropdown("DATE RANGE", ["Last 7 Days", "Today", "This Month", "All Time"])
        self.course_combo = self._filter_dropdown("COURSE", ["All Courses"])
        self.status_combo = self._filter_dropdown("STATUS", ["All Statuses", "Present", "Late", "Absent"])

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
        search_btn.clicked.connect(self._on_search)
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
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "STUDENT NAME", "STUDENT ID", "COURSE",
            "CHECK-IN TIME", "STATUS", "CONFIDENCE",
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

        # prev / next buttons
        self.prev_btn = QPushButton("Prev")
        self.prev_btn.setFixedHeight(28)
        self.prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.prev_btn.setStyleSheet(self._pag_btn_style())
        self.prev_btn.clicked.connect(self._prev_page)
        pag_layout.addWidget(self.prev_btn)

        self.page_label = QLabel("Page 1")
        self.page_label.setStyleSheet(f"color: {_TEXT_PRIMARY}; font-size: 14px; padding: 0 12px;")
        pag_layout.addWidget(self.page_label)

        self.next_btn = QPushButton("Next")
        self.next_btn.setFixedHeight(28)
        self.next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_btn.setStyleSheet(self._pag_btn_style())
        self.next_btn.clicked.connect(self._next_page)
        pag_layout.addWidget(self.next_btn)

        table_layout.addWidget(pagination)
        root.addWidget(table_container, 1)

    @staticmethod
    def _pag_btn_style() -> str:
        return f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {_BORDER};
                border-radius: 2px;
                color: {_TEXT_SECONDARY};
                font-size: 13px;
                padding: 0 12px;
            }}
            QPushButton:hover {{
                background: {_TABLE_HEADER_BG};
                color: {_TEXT_PRIMARY};
            }}
        """

    # ── Filter dropdown helper ──

    def _filter_dropdown(self, label: str, items: list[str]) -> QFrame:
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
        combo.addItems(items)
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

    # ── Lifecycle ──

    def bind(self):
        """加载课程列表到筛选器（页面首次展示时调用）。"""
        self._fetch_courses()

    def refresh(self):
        """页面切回时重新加载。"""
        self._current_page = 1
        self._fetch_records()
        self._fetch_stats()

    # ── API calls ──

    def _fetch_courses(self):
        w = AttendanceWorker(course_service.list)
        w.finished.connect(self._handle_courses)
        w.finished.connect(w.deleteLater)
        self._workers.append(w)
        w.start()

    def _fetch_records(self):
        params = self._build_query_params()
        params["page"] = self._current_page
        params["per_page"] = 15
        w = AttendanceWorker(attendance_service.list_records, params)
        w.finished.connect(self._handle_records)
        w.finished.connect(w.deleteLater)
        self._workers.append(w)
        w.start()

    def _fetch_stats(self):
        params = self._build_query_params()
        w = AttendanceWorker(attendance_service.get_statistics, params)
        w.finished.connect(self._handle_stats)
        w.finished.connect(w.deleteLater)
        self._workers.append(w)
        w.start()

    def _build_query_params(self) -> dict:
        params = {}

        # ponytail: date range mapped to date_from/date_to
        date_text = self.date_combo.findChild(QComboBox).currentText()
        if date_text == "Today":
            from datetime import date
            params["date_from"] = str(date.today())
            params["date_to"] = str(date.today())
        elif date_text == "This Month":
            from datetime import date
            today = date.today()
            params["date_from"] = today.replace(day=1).isoformat()
            params["date_to"] = str(today)
        # "Last 7 Days" / "All Time" → 不传参，后端默认 last 7 days

        course_text = self.course_combo.findChild(QComboBox).currentText()
        if course_text and course_text != "All Courses":
            if course_text in self._course_map:
                params["course_id"] = self._course_map[course_text]

        status_text = self.status_combo.findChild(QComboBox).currentText()
        if status_text and status_text != "All Statuses":
            params["status"] = status_text.lower()

        return params

    # ── Handle responses ──

    def _handle_courses(self, result):
        self._workers = [w for w in self._workers if not w.isFinished()]
        if not result.ok:
            return
        courses = result.data or []
        combo = self.course_combo.findChild(QComboBox)
        current = combo.currentText()
        combo.clear()
        combo.addItem("All Courses")
        self._course_map = {}
        for c in courses:
            name = c.get("name", "")
            combo.addItem(name)
            self._course_map[name] = c["id"]
        # restore selection
        idx = combo.findText(current)
        if idx >= 0:
            combo.setCurrentIndex(idx)

    def _handle_records(self, result):
        self._workers = [w for w in self._workers if not w.isFinished()]
        if not result.ok:
            return
        body = result.data or {}
        records = body.get("records", body if isinstance(body, list) else [])
        total = body.get("total", len(records))
        page = body.get("page", self._current_page)
        per_page = body.get("per_page", 15)

        self.table.setRowCount(0)
        self.table.setRowCount(len(records))

        for r, rec in enumerate(records):
            # Student name
            self.table.setItem(r, 0, QTableWidgetItem(rec.get("student_name", "")))
            # Student ID / student_no — from student relation if present
            sid = rec.get("student_no", "")
            if not sid and rec.get("student_id"):
                sid = str(rec["student_id"])
            self.table.setItem(r, 1, QTableWidgetItem(sid))
            # Course
            self.table.setItem(r, 2, QTableWidgetItem(rec.get("course_name", "")))
            # Check-in time
            raw_time = rec.get("checkin_time", "")
            display_time = raw_time
            if raw_time and "T" in raw_time:
                display_time = raw_time.replace("T", " ")
            self.table.setItem(r, 3, QTableWidgetItem(display_time))
            # Status badge
            status = rec.get("status", "").upper()
            col = self.table.cellWidget(r, 4)
            if col:
                self.table.removeCellWidget(r, 4)
            self.table.setCellWidget(r, 4, _status_badge(status))
            # Confidence
            conf = rec.get("confidence")
            if conf is not None:
                conf_text = f"{float(conf) * 100:.1f}%"
            else:
                conf_text = "--"
            conf_item = QTableWidgetItem(conf_text)
            conf_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
            if status == "ABSENT":
                conf_item.setForeground(Qt.GlobalColor.gray)
            self.table.setItem(r, 5, conf_item)

        # Pagination label
        start = (page - 1) * per_page + 1 if total > 0 else 0
        end = min(page * per_page, total)
        self.pag_label.setText(f"Showing {start} to {end} of {total} entries")
        self.page_label.setText(f"Page {page}")
        self.prev_btn.setEnabled(page > 1)
        self.next_btn.setEnabled(end < total)

    def _handle_stats(self, result):
        self._workers = [w for w in self._workers if not w.isFinished()]
        if not result.ok:
            return
        s = result.data or {}
        total = s.get("total", 0)
        present = s.get("present", 0)
        late = s.get("late", 0)
        absent = s.get("absent", 0)
        rate = s.get("rate", 0.0)

        self.stat_total.val_lbl.setText(str(total))
        self.stat_present.val_lbl.setText(str(present))
        self.stat_present.pct_lbl.setText(f"{rate:.1f}%")

        late_pct = round(late / total * 100, 1) if total else 0.0
        absent_pct = round(absent / total * 100, 1) if total else 0.0
        self.stat_late.val_lbl.setText(str(late))
        self.stat_late.pct_lbl.setText(f"{late_pct}%")
        self.stat_absent.val_lbl.setText(str(absent))
        self.stat_absent.pct_lbl.setText(f"{absent_pct}%")

    # ── Pagination ──

    def _on_search(self):
        self._current_page = 1
        self._fetch_records()
        self._fetch_stats()

    def _prev_page(self):
        if self._current_page > 1:
            self._current_page -= 1
            self._fetch_records()

    def _next_page(self):
        self._current_page += 1
        self._fetch_records()
