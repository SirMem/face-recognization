"""CoursePage — 课程管理 + 班级管理，对接后端 API。"""
from __future__ import annotations

from PySide6.QtCore import QThread, Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QMessageBox,
)

from app.pages.base_page import BasePage
from app.services.course_service import course_service
from app.services.student_service import student_service
from app.core.event_bus import signal_bus

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


# ── Worker — 后台取数据 ─────────────────────────────────────────────────

class CourseWorker(QThread):
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

class CoursePage(BasePage):
    """课程/班级管理页 — 用 Tab 切换课程与班级管理。"""

    def __init__(self, parent=None):
        self._workers: list[QThread] = []
        super().__init__(parent)

    def setup_ui(self):
        self.setObjectName("coursePage")
        self.setStyleSheet("background: transparent;")

        root = QVBoxLayout(self)
        root.setContentsMargins(32, 32, 32, 32)
        root.setSpacing(0)

        # ── Header ──
        header = QFrame()
        header.setFixedHeight(68)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(0, 0, 0, 0)

        left = QVBoxLayout()
        left.setContentsMargins(0, 0, 0, 0)
        left.setSpacing(0)
        title = QLabel("管理")
        title.setStyleSheet(f"color: {_TEXT_PRIMARY}; font-size: 32px; font-weight: 700; letter-spacing: -0.64px;")
        left.addWidget(title)
        subtitle = QLabel("配置课程和班级分组。")
        subtitle.setStyleSheet(f"color: {_TEXT_SECONDARY}; font-size: 16px;")
        left.addWidget(subtitle)
        h_layout.addLayout(left)
        h_layout.addStretch()

        root.addWidget(header)
        root.addSpacing(24)

        # ── Tab widget ──
        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none; background: transparent;
            }}
            QTabBar::tab {{
                background: {_BG}; color: {_TEXT_SECONDARY};
                font-size: 14px; font-weight: 600;
                padding: 10px 24px;
                border: 1px solid {_BORDER};
                border-bottom: none;
                border-radius: 6px 6px 0 0;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background: {_WHITE}; color: {_BRAND};
            }}
        """)

        tabs.addTab(self._build_courses_tab(), "课程")
        tabs.addTab(self._build_classes_tab(), "班级")

        root.addWidget(tabs)
        root.addStretch(1)

    # ── Tab 1: 课程管理 ─────────────────────────────────────────────────

    def _build_courses_tab(self) -> QWidget:
        tab = QWidget()
        tab.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)

        # ── Form ──
        form_card = QFrame()
        form_card.setObjectName("courseFormCard")
        form_card.setStyleSheet(f"""
            #courseFormCard {{
                background: {_WHITE}; border: 1px solid {_BORDER}; border-radius: 8px;
            }}
        """)
        form_card.setFixedWidth(303)

        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(24, 24, 24, 24)
        form_layout.setSpacing(0)

        heading = QLabel("  添加课程")
        heading.setStyleSheet(f"color: {_TEXT_PRIMARY}; font-size: 20px; font-weight: 600;")
        form_layout.addWidget(heading)
        form_layout.addSpacing(24)

        form_layout.addWidget(self._label("课程名称"))
        form_layout.addSpacing(4)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("例如 高等数学")
        self._style_input(self.name_input)
        form_layout.addWidget(self.name_input)
        form_layout.addSpacing(20)

        form_layout.addWidget(self._label("上课时间"))
        form_layout.addSpacing(4)
        self.schedule_input = QLineEdit()
        self.schedule_input.setPlaceholderText("例如 周一/三 10:00")
        self._style_input(self.schedule_input)
        form_layout.addWidget(self.schedule_input)
        form_layout.addSpacing(20)

        self.add_btn = QPushButton("  添加课程")
        self.add_btn.setObjectName("addCourseBtn")
        self.add_btn.setStyleSheet(f"""
            #addCourseBtn {{
                background: {_BRAND}; border: none; border-radius: 4px;
                color: {_WHITE}; font-size: 14px; font-weight: 600; padding: 10px;
            }}
            #addCourseBtn:hover {{ background: #002b6a; }}
        """)
        self.add_btn.setFixedHeight(40)
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        form_layout.addWidget(self.add_btn)
        form_layout.addStretch()

        layout.addWidget(form_card)

        # ── Table ──
        table_card = QFrame()
        table_card.setObjectName("courseTableCard")
        table_card.setStyleSheet(f"""
            #courseTableCard {{
                background: {_WHITE}; border: 1px solid {_BORDER}; border-radius: 8px;
            }}
        """)
        table_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(1, 1, 1, 1)
        table_layout.setSpacing(0)

        tools = QFrame()
        tools.setObjectName("tableTools")
        tools.setStyleSheet(f"""
            #tableTools {{
                background: {_BG}cc; border-bottom: 1px solid {_BORDER};
            }}
        """)
        tools.setFixedHeight(69)
        tool_layout = QHBoxLayout(tools)
        tool_layout.setContentsMargins(16, 16, 16, 16)
        tbl_title = QLabel("课程列表")
        tbl_title.setStyleSheet(f"color: {_TEXT_PRIMARY}; font-size: 24px; font-weight: 600; letter-spacing: -0.24px;")
        tool_layout.addWidget(tbl_title)
        tool_layout.addStretch()
        table_layout.addWidget(tools)

        self.course_table = QTableWidget()
        self.course_table.setObjectName("courseTable")
        self.course_table.setColumnCount(4)
        self.course_table.setHorizontalHeaderLabels(["课程编号", "课程名称", "上课时间", "操作"])
        self.course_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.course_table.verticalHeader().setVisible(False)
        self.course_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.course_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._style_table(self.course_table)
        table_layout.addWidget(self.course_table, 1)

        footer = QFrame()
        footer.setObjectName("courseFooter")
        footer.setStyleSheet(f"""
            #courseFooter {{
                background: {_BG}cc; border-top: 1px solid {_BORDER};
            }}
        """)
        footer.setFixedHeight(53)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(16, 16, 16, 16)
        self.footer_label = QLabel("共 0 门课程")
        self.footer_label.setStyleSheet(f"color: {_TEXT_SECONDARY}; font-size: 14px;")
        footer_layout.addWidget(self.footer_label)
        footer_layout.addStretch()
        table_layout.addWidget(footer)

        layout.addWidget(table_card, 1)
        return tab

    # ── Tab 2: 班级管理 ─────────────────────────────────────────────────

    def _build_classes_tab(self) -> QWidget:
        tab = QWidget()
        tab.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)

        # ── Form ──
        form_card = QFrame()
        form_card.setObjectName("classFormCard")
        form_card.setStyleSheet(f"""
            #classFormCard {{
                background: {_WHITE}; border: 1px solid {_BORDER}; border-radius: 8px;
            }}
        """)
        form_card.setFixedWidth(303)

        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(24, 24, 24, 24)
        form_layout.setSpacing(0)

        heading = QLabel("  添加班级")
        heading.setStyleSheet(f"color: {_TEXT_PRIMARY}; font-size: 20px; font-weight: 600;")
        form_layout.addWidget(heading)
        form_layout.addSpacing(24)

        form_layout.addWidget(self._label("班级名称"))
        form_layout.addSpacing(4)
        self.class_name_input = QLineEdit()
        self.class_name_input.setPlaceholderText("例如 一班")
        self._style_input(self.class_name_input)
        form_layout.addWidget(self.class_name_input)
        form_layout.addSpacing(20)

        form_layout.addWidget(self._label("年级"))
        form_layout.addSpacing(4)
        self.grade_input = QLineEdit()
        self.grade_input.setPlaceholderText("例如 高一")
        self._style_input(self.grade_input)
        form_layout.addWidget(self.grade_input)
        form_layout.addSpacing(24)

        self.add_class_btn = QPushButton("  添加班级")
        self.add_class_btn.setObjectName("addClassBtn")
        self.add_class_btn.setStyleSheet(f"""
            #addClassBtn {{
                background: {_BRAND}; border: none; border-radius: 4px;
                color: {_WHITE}; font-size: 14px; font-weight: 600; padding: 10px;
            }}
            #addClassBtn:hover {{ background: #002b6a; }}
        """)
        self.add_class_btn.setFixedHeight(40)
        self.add_class_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        form_layout.addWidget(self.add_class_btn)
        form_layout.addStretch()

        layout.addWidget(form_card)

        # ── Table ──
        table_card = QFrame()
        table_card.setObjectName("classTableCard")
        table_card.setStyleSheet(f"""
            #classTableCard {{
                background: {_WHITE}; border: 1px solid {_BORDER}; border-radius: 8px;
            }}
        """)
        table_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(1, 1, 1, 1)
        table_layout.setSpacing(0)

        tools = QFrame()
        tools.setObjectName("classTableTools")
        tools.setStyleSheet(f"""
            #classTableTools {{
                background: {_BG}cc; border-bottom: 1px solid {_BORDER};
            }}
        """)
        tools.setFixedHeight(69)
        tool_layout = QHBoxLayout(tools)
        tool_layout.setContentsMargins(16, 16, 16, 16)
        tbl_title = QLabel("全部班级")
        tbl_title.setStyleSheet(f"color: {_TEXT_PRIMARY}; font-size: 24px; font-weight: 600; letter-spacing: -0.24px;")
        tool_layout.addWidget(tbl_title)
        tool_layout.addStretch()
        table_layout.addWidget(tools)

        self.class_table = QTableWidget()
        self.class_table.setObjectName("classTable")
        self.class_table.setColumnCount(4)
        self.class_table.setHorizontalHeaderLabels(["班级编号", "班级名称", "年级", "操作"])
        self.class_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.class_table.verticalHeader().setVisible(False)
        self.class_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.class_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._style_table(self.class_table)
        table_layout.addWidget(self.class_table, 1)

        layout.addWidget(table_card, 1)
        return tab

    # ── Shared helpers ──

    @staticmethod
    def _label(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {_TEXT_SECONDARY}; font-size: 12px; font-weight: 700; letter-spacing: 0.6px;")
        return lbl

    @staticmethod
    def _style_input(w: QLineEdit):
        w.setStyleSheet(f"""
            QLineEdit {{
                background: {_INPUT_BG}; border: 1px solid {_BORDER}; border-radius: 4px;
                color: {_TEXT_PRIMARY}; font-size: 14px; padding: 10px 12px;
            }}
            QLineEdit::placeholder {{ color: {_TEXT_PLACEHOLDER}; }}
        """)
        w.setFixedHeight(40)

    @staticmethod
    def _style_table(t: QTableWidget):
        t.setStyleSheet(f"""
            #courseTable, #classTable {{
                border: none; background: {_WHITE}; font-size: 13px;
            }}
            #courseTable::item, #classTable::item {{
                padding: 12px 16px; border-bottom: 1px solid {_BORDER}; color: {_TEXT_PRIMARY};
            }}
            #courseTable::item:selected, #classTable::item:selected {{
                background: {_TABLE_HEADER_BG}; color: {_TEXT_PRIMARY};
            }}
            QHeaderView::section {{
                background: {_TABLE_HEADER_BG}; color: {_TEXT_SECONDARY};
                font-size: 12px; font-weight: 700; letter-spacing: 0.6px;
                border: none; border-bottom: 1px solid {_BORDER}; padding: 14px 16px;
            }}
        """)

    # ── Lifecycle ──

    def bind(self):
        self.add_btn.clicked.connect(self._add_course)
        self.add_class_btn.clicked.connect(self._add_class)
        signal_bus.course_created.connect(self._fetch_courses)
        signal_bus.course_deleted.connect(self._fetch_courses)

    def refresh(self):
        self._fetch_courses()
        self._fetch_classes()

    # ── Course API calls ──

    def _fetch_courses(self):
        w = CourseWorker(course_service.list)
        w.finished.connect(self._handle_courses)
        w.finished.connect(w.deleteLater)
        self._workers.append(w)
        w.start()

    def _add_course(self):
        name = self.name_input.text().strip()
        sched = self.schedule_input.text().strip()
        if not name:
            return
        self.add_btn.setEnabled(False)
        w = CourseWorker(lambda: course_service.create(name, "", sched))
        w.finished.connect(self._handle_created)
        w.finished.connect(w.deleteLater)
        self._workers.append(w)
        w.start()

    def _delete_course(self, course_id: int):
        w = CourseWorker(lambda: course_service.delete(course_id))
        w.finished.connect(lambda r: self._handle_deleted(r, course_id))
        w.finished.connect(w.deleteLater)
        self._workers.append(w)
        w.start()

    def _handle_courses(self, result):
        self._workers = [w for w in self._workers if not w.isFinished()]
        if not result.ok:
            return
        courses = result.data or []
        self._courses = courses
        self._render_course_table()

    def _handle_created(self, result):
        self._workers = [w for w in self._workers if not w.isFinished()]
        self.add_btn.setEnabled(True)
        if not result.ok:
            return
        self.name_input.clear()
        self.schedule_input.clear()
        self._fetch_courses()

    def _handle_deleted(self, result, course_id: int):
        self._workers = [w for w in self._workers if not w.isFinished()]
        if not result.ok:
            return
        self._fetch_courses()

    def _render_course_table(self):
        courses = getattr(self, '_courses', [])
        self.course_table.setRowCount(len(courses))
        for r, c in enumerate(courses):
            self.course_table.setItem(r, 0, QTableWidgetItem(str(c.get("id", ""))))
            self.course_table.setItem(r, 1, QTableWidgetItem(c.get("name", "")))
            self.course_table.setItem(r, 2, QTableWidgetItem(c.get("schedule", "")))
            del_btn = QPushButton("删除")
            del_btn.setFixedSize(40, 28)
            del_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; border: 1px solid {_BORDER}; border-radius: 4px;
                    color: {_TEXT_SECONDARY}; font-size: 12px;
                }}
                QPushButton:hover {{ background: #ffdad6; color: #ba1a1a; }}
            """)
            del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            del_btn.clicked.connect(lambda _, cid=c["id"]: self._delete_course(cid))
            self.course_table.setCellWidget(r, 3, del_btn)

        total = len(courses)
        self.footer_label.setText(f"共 {total} 门课程")

    # ── Class API calls ──

    def _fetch_classes(self):
        w = CourseWorker(student_service.list_classes)
        w.finished.connect(self._handle_classes)
        w.finished.connect(w.deleteLater)
        self._workers.append(w)
        w.start()

    def _add_class(self):
        name = self.class_name_input.text().strip()
        grade = self.grade_input.text().strip()
        if not name:
            QMessageBox.warning(self, "校验提示", "班级名称不能为空。")
            return
        self.add_class_btn.setEnabled(False)
        w = CourseWorker(lambda: student_service.create_class(name, grade))
        w.finished.connect(self._handle_class_created)
        w.finished.connect(w.deleteLater)
        self._workers.append(w)
        w.start()

    def _handle_classes(self, result):
        self._workers = [w for w in self._workers if not w.isFinished()]
        if not result.ok:
            return
        classes = result.data or []
        self._classes = classes
        self._render_class_table()

    def _handle_class_created(self, result):
        self._workers = [w for w in self._workers if not w.isFinished()]
        self.add_class_btn.setEnabled(True)
        if not result.ok:
            QMessageBox.critical(self, "错误", f"创建班级失败: {result.message}")
            return
        self.class_name_input.clear()
        self.grade_input.clear()
        self._fetch_classes()

    def _render_class_table(self):
        classes = getattr(self, '_classes', [])
        self.class_table.setRowCount(len(classes))
        for r, c in enumerate(classes):
            self.class_table.setItem(r, 0, QTableWidgetItem(str(c.get("id", ""))))
            self.class_table.setItem(r, 1, QTableWidgetItem(c.get("name", "")))
            self.class_table.setItem(r, 2, QTableWidgetItem(c.get("grade", "")))
            del_btn = QPushButton("删除")
            del_btn.setFixedSize(40, 28)
            del_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; border: 1px solid {_BORDER}; border-radius: 4px;
                    color: {_TEXT_SECONDARY}; font-size: 12px;
                }}
                QPushButton:hover {{ background: #ffdad6; color: #ba1a1a; }}
            """)
            del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            del_btn.clicked.connect(lambda _, cid=c["id"]: self._delete_class(cid))
            self.class_table.setCellWidget(r, 3, del_btn)

    def _delete_class(self, class_id: int):
        w = CourseWorker(lambda: student_service.delete_class(class_id))
        w.finished.connect(lambda r: self._handle_class_deleted(r, class_id))
        w.finished.connect(w.deleteLater)
        self._workers.append(w)
        w.start()

    def _handle_class_deleted(self, result, _class_id):
        self._workers = [w for w in self._workers if not w.isFinished()]
        if not result.ok:
            return
        self._fetch_classes()
