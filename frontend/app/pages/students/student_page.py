"""StudentPage — 学生管理（CRUD + 人脸注册），对齐 Figma 设计。"""
from __future__ import annotations

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.models.student import Student
from app.pages.base_page import BasePage
from app.services.student_service import student_service

# ── Figma 颜色 ──────────────────────────────────────────────────────────
_BG = "#f9f9ff"
_TEXT_PRIMARY = "#091c35"
_TEXT_SECONDARY = "#5c5f60"
_TEXT_MUTED = "#737685"
_TEXT_PLACEHOLDER = "#6b7280"
_BORDER = "#c3c6d6"
_BRAND = "#003d9b"
_WHITE = "#ffffff"
_TABLE_HEADER_BG = "#e7eeff"  # Figma 表头
_TABLE_ROW_ALT = "#f9f9ff"  # Figma 斑马色
_REGISTERED_BG = "#0052cc"  # Figma 绿色标签背景
_REGISTERED_TEXT = "#c4d2ff"  # Figma 绿色标签文字
_UNREGISTERED_BG = "#ffdad6"
_UNREGISTERED_TEXT = "#93000a"
_MONO = "'JetBrains Mono'"


# ── Status badge ─────────────────────────────────────────────────────────

def _face_status_badge(registered: bool) -> QFrame:
    text = "Registered" if registered else "Not Registered"
    bg = _REGISTERED_BG if registered else _UNREGISTERED_BG
    fg = _REGISTERED_TEXT if registered else _UNREGISTERED_TEXT

    badge = QFrame()
    badge.setStyleSheet(f"background: {bg}; border-radius: 2px;")
    layout = QHBoxLayout(badge)
    layout.setContentsMargins(8, 2, 8, 2)
    lbl = QLabel(text)
    lbl.setStyleSheet(f"color: {fg}; font-size: 12px; font-weight: 700; letter-spacing: 0.6px;")
    layout.addWidget(lbl)
    return badge


# ── Async worker for API calls ──────────────────────────────────────────

class ApiWorker(QThread):
    """后台线程调用 student service，完成后发出信号。"""
    finished = Signal(object)  # ApiResult

    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self._fn = fn
        self._args = args
        self._kwargs = kwargs

    def run(self):
        result = self._fn(*self._args, **self._kwargs)
        self.finished.emit(result)


# ═══════════════════════════════════════════════════════════════════════

class StudentPage(BasePage):
    """学生列表 + 添加表单 + 删除 + 人脸注册入口。"""

    def setup_ui(self):
        self.setObjectName("studentPage")
        self.setStyleSheet("background: transparent;")
        self._workers: list[ApiWorker] = []

        root = QVBoxLayout(self)
        root.setContentsMargins(32, 32, 32, 32)
        root.setSpacing(0)

        # ── Page Header ──
        header = QFrame()
        header.setFixedHeight(68)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(0, 0, 0, 0)

        left = QVBoxLayout()
        left.setContentsMargins(0, 0, 0, 0)
        left.setSpacing(0)
        title = QLabel("Student Management")
        title.setStyleSheet(f"color: {_TEXT_PRIMARY}; font-size: 32px; font-weight: 700; letter-spacing: -0.64px;")
        left.addWidget(title)
        subtitle = QLabel("Register, edit and manage student profiles.")
        subtitle.setStyleSheet(f"color: {_TEXT_SECONDARY}; font-size: 16px;")
        left.addWidget(subtitle)
        h_layout.addLayout(left)
        h_layout.addStretch()

        root.addWidget(header)
        root.addSpacing(24)

        # ── Bento: Form (left) + Table (right) ──
        bento = QHBoxLayout()
        bento.setContentsMargins(0, 0, 0, 0)
        bento.setSpacing(24)

        # ── Left: Register Student Form ──
        form_card = QFrame()
        form_card.setObjectName("studentFormCard")
        form_card.setStyleSheet(f"""
            #studentFormCard {{
                background: {_WHITE};
                border: 1px solid {_BORDER};
                border-radius: 8px;
            }}
        """)
        form_card.setFixedWidth(350)

        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(24, 24, 24, 24)
        form_layout.setSpacing(0)

        # Form heading
        heading = QLabel("Register Student")
        heading.setStyleSheet(f"color: {_TEXT_PRIMARY}; font-size: 20px; font-weight: 600;")
        form_layout.addWidget(heading)
        form_layout.addSpacing(24)

        # ── Student ID ──
        form_layout.addWidget(self._label("STUDENT ID"))
        form_layout.addSpacing(4)
        self.student_id_input = QLineEdit()
        self.student_id_input.setPlaceholderText("e.g. STU-8492")
        self._style_input(self.student_id_input)
        form_layout.addWidget(self.student_id_input)
        form_layout.addSpacing(20)

        # ── Full Name ──
        form_layout.addWidget(self._label("FULL NAME"))
        form_layout.addSpacing(4)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("First Last")
        self._style_input(self.name_input)
        form_layout.addWidget(self.name_input)
        form_layout.addSpacing(20)

        # ── Gender ──
        form_layout.addWidget(self._label("GENDER"))
        form_layout.addSpacing(4)
        gender_row = QHBoxLayout()
        gender_row.setContentsMargins(0, 0, 0, 0)
        gender_row.setSpacing(16)
        self.gender_group = QButtonGroup(self)
        for val, text in [("male", "Male"), ("female", "Female"), ("other", "Other")]:
            rb = QRadioButton(text)
            rb.setStyleSheet(f"""
                QRadioButton {{
                    color: {_TEXT_PRIMARY};
                    font-size: 14px;
                    spacing: 6px;
                }}
                QRadioButton::indicator {{
                    width: 16px;
                    height: 16px;
                    border-radius: 8px;
                    border: 2px solid {_BORDER};
                }}
                QRadioButton::indicator:checked {{
                    background: {_BRAND};
                    border: 2px solid {_BRAND};
                }}
            """)
            self.gender_group.addButton(rb, len(self.gender_group.buttons()))
            setattr(self, f"_gender_{val}", rb)
            gender_row.addWidget(rb)
        gender_row.addStretch()
        form_layout.addLayout(gender_row)
        form_layout.addSpacing(20)

        # ── Class Assignment ──
        form_layout.addWidget(self._label("CLASS ASSIGNMENT"))
        form_layout.addSpacing(4)
        self.class_combo = QComboBox()
        self.class_combo.setObjectName("classCombo")
        self.class_combo.addItem("Select a class...")
        self.class_combo.setStyleSheet(f"""
            QComboBox#classCombo {{
                background: {_BG};
                border: 1px solid {_BORDER};
                border-radius: 2px;
                color: {_TEXT_PRIMARY};
                font-size: 14px;
                padding: 8px 12px;
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
        self.class_combo.setFixedHeight(40)
        form_layout.addWidget(self.class_combo)
        form_layout.addSpacing(24)

        # ── Add button ──
        self.add_btn = QPushButton("  Add to Directory")
        self.add_btn.setObjectName("addStudentBtn")
        self.add_btn.setStyleSheet(f"""
            #addStudentBtn {{
                background: {_BRAND};
                border: none;
                border-radius: 2px;
                color: {_WHITE};
                font-size: 14px;
                font-weight: 600;
                padding: 10px;
            }}
            #addStudentBtn:hover {{ background: #002b6a; }}
        """)
        self.add_btn.setFixedHeight(40)
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        form_layout.addWidget(self.add_btn)
        form_layout.addStretch()

        bento.addWidget(form_card)

        # ── Right: Data Table ──
        table_card = QFrame()
        table_card.setObjectName("studentTableCard")
        table_card.setStyleSheet(f"""
            #studentTableCard {{
                background: {_WHITE};
                border: 1px solid {_BORDER};
                border-radius: 8px;
            }}
        """)
        table_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(1, 1, 1, 1)
        table_layout.setSpacing(0)

        # ── Filter bar ──
        filter_bar = QFrame()
        filter_bar.setObjectName("tableFilterBar")
        filter_bar.setStyleSheet(f"""
            #tableFilterBar {{
                background: {_WHITE};
                border-bottom: 1px solid {_BORDER};
                border-radius: 8px 8px 0 0;
            }}
        """)
        filter_bar.setFixedHeight(66)
        filter_layout = QHBoxLayout(filter_bar)
        filter_layout.setContentsMargins(16, 16, 16, 16)
        filter_layout.setSpacing(12)

        # Filter label
        filter_icon = QLabel("⏏")
        filter_icon.setStyleSheet(f"color: {_TEXT_SECONDARY}; font-size: 14px;")
        filter_layout.addWidget(filter_icon)

        filter_label = QLabel("FILTER BY CLASS:")
        filter_label.setStyleSheet(f"color: {_TEXT_SECONDARY}; font-size: 12px; font-weight: 700; letter-spacing: 0.6px;")
        filter_layout.addWidget(filter_label)

        self.filter_combo = QComboBox()
        self.filter_combo.setObjectName("filterCombo")
        self.filter_combo.setFixedWidth(91)
        self.filter_combo.addItem("All Classes")
        self.filter_combo.setStyleSheet(f"""
            QComboBox#filterCombo {{
                background: {_BG};
                border: 1px solid {_BORDER};
                border-radius: 2px;
                color: {_TEXT_PRIMARY};
                font-size: 14px;
                padding: 6px 8px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 16px;
            }}
            QComboBox::down-arrow {{
                image: none;
            }}
        """)
        self.filter_combo.setFixedHeight(34)
        filter_layout.addWidget(self.filter_combo)
        filter_layout.addStretch()

        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search ID or Name")
        self.search_input.setFixedWidth(256)
        self.search_input.setFixedHeight(34)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background: {_BG};
                border: 1px solid {_BORDER};
                border-radius: 2px;
                color: {_TEXT_PRIMARY};
                font-size: 14px;
                padding: 6px 12px 6px 28px;
            }}
            QLineEdit::placeholder {{ color: {_TEXT_PLACEHOLDER}; }}
        """)
        # ponytail: search icon overlay skipped, text hint suffices
        filter_layout.addWidget(self.search_input)

        table_layout.addWidget(filter_bar)

        # ── Table ──
        self.table = QTableWidget()
        self.table.setObjectName("studentTable")
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "STUDENT ID", "NAME", "GENDER", "CLASS", "FACE STATUS", "ACTIONS"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(f"""
            #studentTable {{
                border: none;
                background: {_WHITE};
                font-size: 13px;
                alternate-background-color: {_TABLE_ROW_ALT};
            }}
            #studentTable::item {{
                padding: 12px 16px;
                border-bottom: 1px solid {_BORDER};
                color: {_TEXT_PRIMARY};
            }}
            #studentTable::item:selected {{
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

        # ── Pagination ──
        pagination = QFrame()
        pagination.setObjectName("studentPagination")
        pagination.setStyleSheet(f"""
            #studentPagination {{
                background: {_BG};
                border-top: 1px solid {_BORDER};
                border-radius: 0 0 8px 8px;
            }}
        """)
        pagination.setFixedHeight(48)
        pag_layout = QHBoxLayout(pagination)
        pag_layout.setContentsMargins(16, 12, 16, 12)

        self.pag_label = QLabel("Showing 0 of 0 entries")
        self.pag_label.setStyleSheet(f"color: {_TEXT_SECONDARY}; font-size: 14px;")
        pag_layout.addWidget(self.pag_label)
        pag_layout.addStretch()

        # Page nav buttons
        pag_nav = QHBoxLayout()
        pag_nav.setSpacing(4)
        for p in ["1", "2", "3", "▶"]:
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
                    font-size: 14px;
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
        bento.addWidget(table_card, 1)

        root.addLayout(bento)
        root.addStretch(1)

    # ── Helpers ──

    @staticmethod
    def _label(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {_TEXT_SECONDARY}; font-size: 12px; font-weight: 700; letter-spacing: 0.6px;")
        return lbl

    @staticmethod
    def _style_input(w: QLineEdit):
        w.setStyleSheet(f"""
            QLineEdit {{
                background: {_BG};
                border: 1px solid {_BORDER};
                border-radius: 2px;
                color: {_TEXT_PRIMARY};
                font-size: 14px;
                padding: 10px 12px;
            }}
            QLineEdit::placeholder {{ color: {_TEXT_PLACEHOLDER}; }}
        """)
        w.setFixedHeight(40)

    @staticmethod
    def _action_btn(text: str, color: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setFixedSize(28, 28)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {_BORDER};
                border-radius: 4px;
                color: {color};
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: {_TABLE_HEADER_BG};
            }}
        """)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        return btn

    # ── Bind signals ──

    def bind(self):
        self.add_btn.clicked.connect(self._add_student)
        self.filter_combo.currentIndexChanged.connect(self._on_filter)
        self.search_input.textChanged.connect(self._on_search)

    # ── Page lifecycle ──

    def refresh(self):
        self._load_classes()
        self._load_students()

    def on_enter(self, **kwargs):
        super().on_enter(**kwargs)

    # ── Data loading ──

    def _load_classes(self):
        def _on_result(result):
            if result.ok and isinstance(result.data, list):
                self._class_map = {}
                current = self.class_combo.currentText()
                self.class_combo.blockSignals(True)
                self.class_combo.clear()
                self.class_combo.addItem("Select a class...")
                self.filter_combo.blockSignals(True)
                self.filter_combo.clear()
                self.filter_combo.addItem("All Classes")
                for cls in result.data:
                    cid = cls.get("id")
                    cname = cls.get("name", "")
                    label = f"{cname}" if cid else cname
                    self.class_combo.addItem(label, cid)
                    self.filter_combo.addItem(label, cid)
                    if cid is not None:
                        self._class_map[cid] = cname
                # Restore selection
                idx = self.class_combo.findText(current)
                if idx >= 0:
                    self.class_combo.setCurrentIndex(idx)
                self.class_combo.blockSignals(False)
                self.filter_combo.blockSignals(False)
            else:
                self._class_map = {}

        worker = ApiWorker(student_service.list_classes)
        worker.finished.connect(_on_result)
        worker.finished.connect(worker.deleteLater)
        worker.finished.connect(lambda w=worker: self._workers.remove(w) if w in self._workers else None)
        self._workers.append(worker)
        worker.start()

    def _load_students(self, params: dict = None):
        def _on_result(result):
            if result.ok:
                students_data = result.data if isinstance(result.data, list) else []
                self._students = [Student(**s) if not isinstance(s, Student) else s for s in students_data]
            else:
                self._students = []
            self._render_table()

        worker = ApiWorker(student_service.list, params or {})
        worker.finished.connect(_on_result)
        worker.finished.connect(worker.deleteLater)
        worker.finished.connect(lambda w=worker: self._workers.remove(w) if w in self._workers else None)
        self._workers.append(worker)
        worker.start()

    def _render_table(self):
        students = getattr(self, '_students', [])
        self.table.setRowCount(len(students))
        for r, stu in enumerate(students):
            class_name = self._class_map.get(stu.class_id, f"Class {stu.class_id}" if stu.class_id else "—")
            row_data = [stu.student_no, stu.name, stu.gender.upper() if stu.gender else "—", class_name]
            for c, val in enumerate(row_data):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(r, c, item)

            # Face status badge
            self.table.setCellWidget(r, 4, _face_status_badge(stu.has_face))

            # Actions: view / edit / delete
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 0, 4, 0)
            actions_layout.setSpacing(4)

            view_btn = self._action_btn("👁", _TEXT_SECONDARY)
            view_btn.clicked.connect(lambda checked, s=stu: self._view_student(s))

            edit_btn = self._action_btn("✎", _TEXT_SECONDARY)
            edit_btn.clicked.connect(lambda checked, s=stu: self._edit_student(s))

            del_btn = self._action_btn("✕", _TEXT_SECONDARY)
            del_btn.clicked.connect(lambda checked, s=stu: self._delete_student(s))

            actions_layout.addWidget(view_btn)
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(del_btn)
            actions_layout.addStretch()
            self.table.setCellWidget(r, 5, actions_widget)

        total = len(students)
        self.pag_label.setText(f"Showing {total} of {total} entries")

    # ── CRUD operations ──

    def _add_student(self):
        student_id = self.student_id_input.text().strip()
        name = self.name_input.text().strip()
        checked = self.gender_group.checkedButton()
        gender = checked.text().lower() if checked else ""
        class_id = self.class_combo.currentData()

        if not student_id or not name:
            QMessageBox.warning(self, "Validation", "Student ID and Name are required.")
            return

        def _on_result(result):
            if result.ok:
                self.student_id_input.clear()
                self.name_input.clear()
                if checked := self.gender_group.checkedButton():
                    self.gender_group.setExclusive(False)
                    checked.setChecked(False)
                    self.gender_group.setExclusive(True)
                self.class_combo.setCurrentIndex(0)
                self._load_students()
            else:
                QMessageBox.critical(self, "Error", f"Failed to add student: {result.message}")

        worker = ApiWorker(student_service.create, student_id, name, gender, class_id)
        worker.finished.connect(_on_result)
        worker.finished.connect(worker.deleteLater)
        worker.finished.connect(lambda w=worker: self._workers.remove(w) if w in self._workers else None)
        self._workers.append(worker)
        worker.start()

    def _view_student(self, stu: Student):
        # ponytail: view as info dialog, full detail page if needed
        msg = (
            f"ID: {stu.student_no}\n"
            f"Name: {stu.name}\n"
            f"Gender: {stu.gender}\n"
            f"Class: {self._class_map.get(stu.class_id, '—')}\n"
            f"Face Registered: {'Yes' if stu.has_face else 'No'}"
        )
        QMessageBox.information(self, f"Student: {stu.name}", msg)

    def _edit_student(self, stu: Student):
        # ponytail: field-by-field dialog, full edit form view if needed
        self.student_id_input.setText(stu.student_no)
        self.name_input.setText(stu.name)
        gender_map = {"male": 0, "female": 1, "other": 2}
        idx = gender_map.get(stu.gender.lower())
        if idx is not None and (btn := self.gender_group.button(idx)):
            btn.setChecked(True)
        for i in range(self.class_combo.count()):
            if self.class_combo.itemData(i) == stu.class_id:
                self.class_combo.setCurrentIndex(i)
                break
        # Scroll to top of form
        QMessageBox.information(self, "Edit Student",
                                "Form populated. Modify fields and click 'Add to Directory' to save.")

    def _delete_student(self, stu: Student):
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete student '{stu.name}' ({stu.student_no})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        def _on_result(result):
            if result.ok:
                self._load_students()
            else:
                QMessageBox.critical(self, "Error", f"Failed to delete: {result.message}")

        worker = ApiWorker(student_service.delete, stu.id)
        worker.finished.connect(_on_result)
        worker.finished.connect(worker.deleteLater)
        worker.finished.connect(lambda w=worker: self._workers.remove(w) if w in self._workers else None)
        self._workers.append(worker)
        worker.start()

    # ── Filter / Search ──

    def _on_filter(self):
        class_id = self.filter_combo.currentData()
        params = {}
        if class_id is not None:
            params["class_id"] = class_id
        self._load_students(params)

    def _on_search(self, text: str):
        params = {}
        if text.strip():
            params["search"] = text.strip()
        class_id = self.filter_combo.currentData()
        if class_id is not None:
            params["class_id"] = class_id
        self._load_students(params)
