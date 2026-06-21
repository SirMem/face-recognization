"""CoursePage — 课程管理页面，对齐 Figma 设计。"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
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
_TEXT_PLACEHOLDER = "#6b7280"
_BORDER = "#c3c6d6"
_BRAND = "#003d9b"
_WHITE = "#ffffff"
_TABLE_HEADER_BG = "#f0f3ff"
_INPUT_BG = "#f9f9ff"
_MONO = "'JetBrains Mono'"


class CoursePage(BasePage):
    """课程列表 + 添加表单，对齐 Figma。"""

    def setup_ui(self):
        self.setObjectName("coursePage")
        self.setStyleSheet("background: transparent;")

        root = QVBoxLayout(self)
        root.setContentsMargins(32, 32, 32, 32)
        root.setSpacing(0)

        # ════════════════════════════════════════════════════
        # Page Header
        # ════════════════════════════════════════════════════
        header = QFrame()
        header.setFixedHeight(68)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(0, 0, 0, 0)

        left = QVBoxLayout()
        left.setContentsMargins(0, 0, 0, 0)
        left.setSpacing(0)
        title = QLabel("Course Management")
        title.setStyleSheet(f"color: {_TEXT_PRIMARY}; font-size: 32px; font-weight: 700; letter-spacing: -0.64px;")
        left.addWidget(title)
        subtitle = QLabel("Configure and manage academic course schedules.")
        subtitle.setStyleSheet(f"color: {_TEXT_SECONDARY}; font-size: 16px;")
        left.addWidget(subtitle)
        h_layout.addLayout(left)
        h_layout.addStretch()

        root.addWidget(header)
        root.addSpacing(24)

        # ════════════════════════════════════════════════════
        # Bento Grid: Form (left) + Table (right)
        # ════════════════════════════════════════════════════
        bento = QHBoxLayout()
        bento.setContentsMargins(0, 0, 0, 0)
        bento.setSpacing(24)

        # ── Left: Add Course Form ──
        form_card = QFrame()
        form_card.setObjectName("courseFormCard")
        form_card.setStyleSheet(f"""
            #courseFormCard {{
                background: {_WHITE};
                border: 1px solid {_BORDER};
                border-radius: 8px;
            }}
        """)
        form_card.setFixedWidth(303)

        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(24, 24, 24, 24)
        form_layout.setSpacing(0)

        # Form heading
        heading = QLabel("  Add New Course")
        heading.setStyleSheet(f"color: {_TEXT_PRIMARY}; font-size: 20px; font-weight: 600;")
        form_layout.addWidget(heading)
        form_layout.addSpacing(24)

        # Course name
        form_layout.addWidget(self._label("COURSE NAME"))
        form_layout.addSpacing(4)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Advanced Mathematics")
        self.name_input.setStyleSheet(f"""
            QLineEdit {{
                background: {_INPUT_BG};
                border: 1px solid {_BORDER};
                border-radius: 4px;
                color: {_TEXT_PRIMARY};
                font-size: 14px;
                padding: 10px 12px;
            }}
            QLineEdit::placeholder {{ color: {_TEXT_PLACEHOLDER}; }}
        """)
        self.name_input.setFixedHeight(40)
        form_layout.addWidget(self.name_input)
        form_layout.addSpacing(20)

        # Teacher
        form_layout.addWidget(self._label("TEACHER"))
        form_layout.addSpacing(4)
        self.teacher_combo = QComboBox()
        self.teacher_combo.setObjectName("teacherCombo")
        self.teacher_combo.addItem("Select an instructor")
        self.teacher_combo.setStyleSheet(f"""
            QComboBox#teacherCombo {{
                background: {_INPUT_BG};
                border: 1px solid {_BORDER};
                border-radius: 4px;
                color: {_TEXT_PRIMARY};
                font-size: 14px;
                padding: 8px 12px;
            }}
        """)
        self.teacher_combo.setFixedHeight(40)
        form_layout.addWidget(self.teacher_combo)
        form_layout.addSpacing(20)

        # Schedule
        form_layout.addWidget(self._label("SCHEDULE"))
        form_layout.addSpacing(4)
        self.schedule_input = QLineEdit()
        self.schedule_input.setPlaceholderText("e.g. Mon/Wed 10:00 AM")
        self.schedule_input.setStyleSheet(f"""
            QLineEdit {{
                background: {_INPUT_BG};
                border: 1px solid {_BORDER};
                border-radius: 4px;
                color: {_TEXT_PRIMARY};
                font-size: 14px;
                padding: 10px 12px;
            }}
            QLineEdit::placeholder {{ color: {_TEXT_PLACEHOLDER}; }}
        """)
        self.schedule_input.setFixedHeight(40)
        form_layout.addWidget(self.schedule_input)
        form_layout.addSpacing(20)

        # Submit
        self.add_btn = QPushButton("  Add Course")
        self.add_btn.setObjectName("addCourseBtn")
        self.add_btn.setStyleSheet(f"""
            #addCourseBtn {{
                background: {_BRAND};
                border: none;
                border-radius: 4px;
                color: {_WHITE};
                font-size: 14px;
                font-weight: 600;
                padding: 10px;
            }}
            #addCourseBtn:hover {{ background: #002b6a; }}
        """)
        self.add_btn.setFixedHeight(40)
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        form_layout.addWidget(self.add_btn)
        form_layout.addStretch()

        bento.addWidget(form_card)

        # ── Right: Active Courses Table ──
        table_card = QFrame()
        table_card.setObjectName("courseTableCard")
        table_card.setStyleSheet(f"""
            #courseTableCard {{
                background: {_WHITE};
                border: 1px solid {_BORDER};
                border-radius: 8px;
            }}
        """)
        table_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(1, 1, 1, 1)
        table_layout.setSpacing(0)

        # Table header tools
        tools = QFrame()
        tools.setObjectName("tableTools")
        tools.setStyleSheet(f"""
            #tableTools {{
                background: {_BG}cc;
                border-bottom: 1px solid {_BORDER};
            }}
        """)
        tools.setFixedHeight(69)
        tool_layout = QHBoxLayout(tools)
        tool_layout.setContentsMargins(16, 16, 16, 16)

        tbl_title = QLabel("Active Courses")
        tbl_title.setStyleSheet(f"color: {_TEXT_PRIMARY}; font-size: 24px; font-weight: 600; letter-spacing: -0.24px;")
        tool_layout.addWidget(tbl_title)
        tool_layout.addStretch()

        filter_btn = QPushButton("⫸")
        filter_btn.setFixedSize(36, 36)
        filter_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {_BORDER};
                border-radius: 6px;
                color: {_TEXT_SECONDARY};
                font-size: 16px;
            }}
            QPushButton:hover {{ background: {_TABLE_HEADER_BG}; }}
        """)
        filter_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        tool_layout.addWidget(filter_btn)

        table_layout.addWidget(tools)

        # Table
        self.table = QTableWidget()
        self.table.setObjectName("courseTable")
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["COURSE ID", "COURSE NAME", "TEACHER", "SCHEDULE", "ACTIONS"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(False)
        self.table.setStyleSheet(f"""
            #courseTable {{
                border: none;
                background: {_WHITE};
                font-size: 13px;
            }}
            #courseTable::item {{
                padding: 12px 16px;
                border-bottom: 1px solid {_BORDER};
                color: {_TEXT_PRIMARY};
            }}
            #courseTable::item:selected {{
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
                padding: 14px 16px;
            }}
        """)
        table_layout.addWidget(self.table, 1)

        # Footer
        footer = QFrame()
        footer.setObjectName("courseFooter")
        footer.setStyleSheet(f"""
            #courseFooter {{
                background: {_BG}cc;
                border-top: 1px solid {_BORDER};
            }}
        """)
        footer.setFixedHeight(53)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(16, 16, 16, 16)

        self.footer_label = QLabel("Showing 0 of 0 courses")
        self.footer_label.setStyleSheet(f"color: {_TEXT_SECONDARY}; font-size: 14px;")
        footer_layout.addWidget(self.footer_label)
        footer_layout.addStretch()

        pag_nav = QHBoxLayout()
        pag_nav.setSpacing(4)
        for _dir in ["◀", "▶"]:
            btn = QPushButton(_dir)
            btn.setFixedSize(28, 28)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: none;
                    border-radius: 2px;
                    color: {_TEXT_SECONDARY};
                    font-size: 12px;
                }}
                QPushButton:hover {{ background: {_TABLE_HEADER_BG}; }}
            """)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            pag_nav.addWidget(btn)
        footer_layout.addLayout(pag_nav)

        table_layout.addWidget(footer)
        bento.addWidget(table_card, 1)

        root.addLayout(bento)
        root.addStretch(1)

    # ── Helpers ──

    @staticmethod
    def _label(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {_TEXT_SECONDARY}; font-size: 12px; font-weight: 700; letter-spacing: 0.6px;")
        return lbl

    # ── Data ──

    def bind(self):
        self.add_btn.clicked.connect(self._add_course)

    def refresh(self):
        self._load_demo()

    def _load_demo(self):
        self._demo_courses = [
            ("CS101", "Intro to Computer Science", "Dr. Alan Turing", "Mon/Wed 10:00 AM"),
            ("ENG202", "Advanced Composition", "Prof. Maya Angelou", "Tue/Thu 2:00 PM"),
        ]
        self._render_table()

    def _render_table(self):
        courses = getattr(self, '_demo_courses', [])
        self.table.setRowCount(len(courses))
        for r, (cid, name, teacher, sched) in enumerate(courses):
            for c, val in enumerate([cid, name, teacher, sched]):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(r, c, item)
            # Actions column
            del_btn = QPushButton("✕")
            del_btn.setFixedSize(28, 28)
            del_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: 1px solid {_BORDER};
                    border-radius: 4px;
                    color: {_TEXT_SECONDARY};
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background: #ffdad6;
                    color: #ba1a1a;
                }}
            """)
            del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            del_btn.clicked.connect(lambda _, row=r: self._delete_course(row))
            self.table.setCellWidget(r, 4, del_btn)

        total = len(courses)
        self.footer_label.setText(f"Showing {total} of {total} courses")

    def _add_course(self):
        name = self.name_input.text().strip()
        teacher = self.teacher_combo.currentText()
        sched = self.schedule_input.text().strip()
        if not name:
            return
        cid = f"CRS{len(getattr(self, '_demo_courses', [])) + 1:03d}"
        if not hasattr(self, '_demo_courses'):
            self._demo_courses = []
        self._demo_courses.append((cid, name, teacher, sched))
        self._render_table()
        self.name_input.clear()
        self.schedule_input.clear()

    def _delete_course(self, row: int):
        if 0 <= row < len(getattr(self, '_demo_courses', [])):
            self._demo_courses.pop(row)
            self._render_table()
