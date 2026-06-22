"""StudentPage — 学生管理（CRUD + 人脸注册），对齐 Figma 设计。"""
from __future__ import annotations

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
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
from app.services.course_service import course_service
from app.services.student_service import student_service
from app.core.event_bus import signal_bus

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
_MONO = "'JetBrains Mono'"


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

class StudentEditDialog(QDialog):
    """编辑学生信息 + 绑定课程的对话框。"""

    def __init__(self, student: Student, class_map: dict, parent=None):
        super().__init__(parent)
        self.student = student
        self.class_map = class_map
        self._course_checkboxes: dict[int, QCheckBox] = {}
        self._all_courses: list[dict] = []
        self._selected_courses: list[int] = []
        self.setWindowTitle(f"编辑学生 — {student.name}")
        self.setMinimumWidth(420)
        self.setModal(True)
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # ── Student fields ──
        fields = QVBoxLayout()
        fields.setSpacing(12)

        # Student ID
        fields.addWidget(QLabel("学号"))
        self._no_input = QLineEdit(self.student.student_no)
        self._no_input.setStyleSheet(self._INPUT_STYLE)
        fields.addWidget(self._no_input)

        # Name
        fields.addWidget(QLabel("姓名"))
        self._name_input = QLineEdit(self.student.name)
        self._name_input.setStyleSheet(self._INPUT_STYLE)
        fields.addWidget(self._name_input)

        # Gender
        fields.addWidget(QLabel("性别"))
        gender_row = QHBoxLayout()
        gender_row.setSpacing(12)
        self._gender_group = QButtonGroup(self)
        for val, text in [("male", "男"), ("female", "女")]:
            rb = QRadioButton(text)
            rb._api_val = val
            if val == self.student.gender.lower():
                rb.setChecked(True)
            self._gender_group.addButton(rb, len(self._gender_group.buttons()))
            gender_row.addWidget(rb)
        gender_row.addStretch()
        fields.addLayout(gender_row)

        # Class
        fields.addWidget(QLabel("班级"))
        self._class_combo = QComboBox()
        self._class_combo.addItem("—", None)
        for cid, cname in sorted(self.class_map.items()):
            self._class_combo.addItem(cname, cid)
            if cid == self.student.class_id:
                self._class_combo.setCurrentIndex(self._class_combo.count() - 1)
        self._class_combo.setStyleSheet(self._COMBO_STYLE)
        fields.addWidget(self._class_combo)

        layout.addLayout(fields)

        # ── Course binding ──
        layout.addWidget(QLabel("已选课程"))
        self._courses_area = QWidget()
        self._courses_layout = QVBoxLayout(self._courses_area)
        self._courses_layout.setContentsMargins(0, 0, 0, 0)
        self._courses_layout.setSpacing(4)
        layout.addWidget(self._courses_area, 1)

        # ── Buttons ──
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _load_data(self):
        """加载课程列表和已选课程。"""
        result = course_service.list()
        if result.ok and isinstance(result.data, list):
            self._all_courses = result.data
        r2 = student_service.get_courses(self.student.id)
        if r2.ok and isinstance(r2.data, dict):
            self._selected_courses = r2.data.get("course_ids", [])
        self._render_courses()

    def _render_courses(self):
        for cb in self._course_checkboxes.values():
            cb.deleteLater()
        self._course_checkboxes.clear()
        for c in self._all_courses:
            cid = c["id"]
            cb = QCheckBox(f"{c.get('name', '')} ({c.get('schedule', '')})")
            cb.setChecked(cid in self._selected_courses)
            self._course_checkboxes[cid] = cb
            self._courses_layout.addWidget(cb)

    def _save(self):
        """保存修改的学生信息和课程绑定。"""
        data = {
            "student_no": self._no_input.text().strip(),
            "name": self._name_input.text().strip(),
            "gender": self._gender_group.checkedButton()._api_val if self._gender_group.checkedButton() else "",
            "class_id": self._class_combo.currentData(),
        }
        if not data["student_no"] or not data["name"]:
            QMessageBox.warning(self, "校验提示", "学号和姓名不能为空。")
            return

        result = student_service.update(self.student.id, data)
        if not result.ok:
            QMessageBox.critical(self, "错误", f"保存失败: {result.message}")
            return

        selected = [cid for cid, cb in self._course_checkboxes.items() if cb.isChecked()]
        student_service.set_courses(self.student.id, selected)
        self.accept()

    _INPUT_STYLE = f"""
        QLineEdit {{
            background: {_BG}; border: 1px solid {_BORDER}; border-radius: 2px;
            color: {_TEXT_PRIMARY}; font-size: 14px; padding: 8px 12px;
        }}
    """
    _COMBO_STYLE = f"""
        QComboBox {{
            background: {_BG}; border: 1px solid {_BORDER}; border-radius: 2px;
            color: {_TEXT_PRIMARY}; font-size: 14px; padding: 8px 12px;
        }}
        QComboBox QAbstractItemView {{
            background: {_WHITE}; color: {_TEXT_PRIMARY}; font-size: 14px;
            selection-background-color: {_TABLE_HEADER_BG}; selection-color: {_TEXT_PRIMARY};
        }}
    """


# ═══════════════════════════════════════════════════════════════════════

class StudentPage(BasePage):
    """学生列表 + 添加表单 + 删除 + 人脸注册入口。"""

    def setup_ui(self):
        self.setObjectName("studentPage")
        self.setStyleSheet("background: transparent;")
        self._workers: list[ApiWorker] = []
        self._face_image_path: str | None = None

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
        title = QLabel("学生管理")
        title.setStyleSheet(f"color: {_TEXT_PRIMARY}; font-size: 32px; font-weight: 700; letter-spacing: -0.64px;")
        left.addWidget(title)
        subtitle = QLabel("注册、编辑和管理学生信息。")
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
        heading = QLabel("注册学生")
        heading.setStyleSheet(f"color: {_TEXT_PRIMARY}; font-size: 20px; font-weight: 600;")
        form_layout.addWidget(heading)
        form_layout.addSpacing(24)

        # ── Student ID ──
        form_layout.addWidget(self._label("学号"))
        form_layout.addSpacing(4)
        self.student_id_input = QLineEdit()
        self.student_id_input.setPlaceholderText("例如 STU-8492")
        self._style_input(self.student_id_input)
        form_layout.addWidget(self.student_id_input)
        form_layout.addSpacing(20)

        # ── Full Name ──
        form_layout.addWidget(self._label("姓名"))
        form_layout.addSpacing(4)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("请输入姓名")
        self._style_input(self.name_input)
        form_layout.addWidget(self.name_input)
        form_layout.addSpacing(20)

        # ── Gender ──
        form_layout.addWidget(self._label("性别"))
        form_layout.addSpacing(4)
        gender_row = QHBoxLayout()
        gender_row.setContentsMargins(0, 0, 0, 0)
        gender_row.setSpacing(16)
        self.gender_group = QButtonGroup(self)
        for val, text in [("male", "男"), ("female", "女")]:
            rb = QRadioButton(text)
            rb._api_val = val  # store API value
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
        form_layout.addWidget(self._label("班级"))
        form_layout.addSpacing(4)
        self.class_combo = QComboBox()
        self.class_combo.setObjectName("classCombo")
        self.class_combo.addItem("选择班级...")
        self.class_combo.setStyleSheet(f"""
            QComboBox#classCombo {{
                background: {_BG};
                border: 1px solid {_BORDER};
                border-radius: 2px;
                color: {_TEXT_PRIMARY};
                font-size: 14px;
                padding: 8px 12px;
            }}
            QComboBox#classCombo QAbstractItemView {{
                background: {_WHITE};
                color: {_TEXT_PRIMARY};
                font-size: 14px;
                selection-background-color: {_TABLE_HEADER_BG};
                selection-color: {_TEXT_PRIMARY};
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
        form_layout.addSpacing(20)

        # ── Face Image ──
        form_layout.addWidget(self._label("人脸照片（可选）"))
        form_layout.addSpacing(4)
        face_row = QHBoxLayout()
        face_row.setContentsMargins(0, 0, 0, 0)
        face_row.setSpacing(8)
        self.face_path_label = QLabel("未选择图片")
        self.face_path_label.setStyleSheet(f"color: {_TEXT_MUTED}; font-size: 13px;")
        self.face_select_btn = QPushButton("  浏览…")
        self.face_select_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {_BORDER};
                border-radius: 2px;
                color: {_TEXT_SECONDARY};
                font-size: 13px;
                padding: 6px 12px;
            }}
            QPushButton:hover {{ background: {_TABLE_HEADER_BG}; }}
        """)
        self.face_select_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.face_select_btn.setFixedHeight(34)
        face_row.addWidget(self.face_path_label, 1)
        face_row.addWidget(self.face_select_btn)
        form_layout.addLayout(face_row)
        form_layout.addSpacing(24)

        # ── Add button ──
        self.add_btn = QPushButton("  添加到目录")
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

        filter_label = QLabel("按班级筛选：")
        filter_label.setStyleSheet(f"color: {_TEXT_SECONDARY}; font-size: 12px; font-weight: 700; letter-spacing: 0.6px;")
        filter_layout.addWidget(filter_label)

        self.filter_combo = QComboBox()
        self.filter_combo.setObjectName("filterCombo")
        self.filter_combo.setFixedWidth(91)
        self.filter_combo.addItem("全部班级")
        self.filter_combo.setStyleSheet(f"""
            QComboBox#filterCombo {{
                background: {_BG};
                border: 1px solid {_BORDER};
                border-radius: 2px;
                color: {_TEXT_PRIMARY};
                font-size: 14px;
                padding: 6px 8px;
            }}
            QComboBox#filterCombo QAbstractItemView {{
                background: {_WHITE};
                color: {_TEXT_PRIMARY};
                font-size: 14px;
                selection-background-color: {_TABLE_HEADER_BG};
                selection-color: {_TEXT_PRIMARY};
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
        self.search_input.setPlaceholderText("搜索学号或姓名")
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
            "学号", "姓名", "性别", "班级", "人脸状态", "操作"
        ])
        h = self.table.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)   # ID
        h.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)   # NAME
        h.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # GENDER
        h.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)   # CLASS
        h.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # FACE STATUS
        h.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)   # ACTIONS
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

        self.pag_label = QLabel("共 0 条记录")
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
        btn.setFixedHeight(28)
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
        self.face_select_btn.clicked.connect(self._pick_face_image)
        signal_bus.face_registered.connect(lambda _: self._load_students())

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
                self.class_combo.addItem("选择班级...")
                self.filter_combo.blockSignals(True)
                self.filter_combo.clear()
                self.filter_combo.addItem("全部班级")
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
            class_name = self._class_map.get(stu.class_id, f"班级 {stu.class_id}" if stu.class_id else "—")
            row_data = [stu.student_no, stu.name, stu.gender.upper() if stu.gender else "—", class_name]
            for c, val in enumerate(row_data):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(r, c, item)

            # Face status as text
            face_text = "已注册" if stu.has_face else "未注册"
            face_item = QTableWidgetItem(face_text)
            face_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(r, 4, face_item)

            # Actions: register face / view / edit / delete
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 0, 4, 0)
            actions_layout.setSpacing(4)

            face_btn = self._action_btn("注册人脸", _TEXT_SECONDARY)
            face_btn.clicked.connect(lambda checked, s=stu: self._register_face(s))

            view_btn = self._action_btn("查看", _TEXT_SECONDARY)
            view_btn.clicked.connect(lambda checked, s=stu: self._view_student(s))

            edit_btn = self._action_btn("编辑", _TEXT_SECONDARY)
            edit_btn.clicked.connect(lambda checked, s=stu: self._edit_student(s))

            del_btn = self._action_btn("删除", _TEXT_SECONDARY)
            del_btn.clicked.connect(lambda checked, s=stu: self._delete_student(s))

            actions_layout.addWidget(face_btn)
            actions_layout.addWidget(view_btn)
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(del_btn)
            self.table.setCellWidget(r, 5, actions_widget)

        total = len(students)
        self.pag_label.setText(f"共 {total} 条记录")

    # ── CRUD operations ──

    def _pick_face_image(self):
        """选择人脸图片。"""
        path, _ = QFileDialog.getOpenFileName(
            self, "选择人脸照片", "",
            "图片 (*.jpg *.jpeg *.png)",
        )
        if path:
            self._face_image_path = path
            self.face_path_label.setText(path.split("/")[-1].split("\\")[-1])

    def _add_student(self):
        student_id = self.student_id_input.text().strip()
        name = self.name_input.text().strip()
        checked = self.gender_group.checkedButton()
        gender = checked._api_val if checked else ""
        class_id = self.class_combo.currentData()

        if not student_id or not name:
            QMessageBox.warning(self, "校验提示", "学号和姓名不能为空。")
            return

        def _on_result(result):
            if result.ok:
                created = result.data or {}
                new_id = created.get("id")
                # 如果有选中人脸图片，创建后自动注册
                if new_id and self._face_image_path:
                    self._register_face_for(new_id, self._face_image_path)
                self._face_image_path = None
                self.face_path_label.setText("未选择图片")
                self.student_id_input.clear()
                self.name_input.clear()
                if checked := self.gender_group.checkedButton():
                    self.gender_group.setExclusive(False)
                    checked.setChecked(False)
                    self.gender_group.setExclusive(True)
                self.class_combo.setCurrentIndex(0)
                self._load_students()
            else:
                QMessageBox.critical(self, "错误", f"添加学生失败: {result.message}")

        worker = ApiWorker(student_service.create, student_id, name, gender, class_id)
        worker.finished.connect(_on_result)
        worker.finished.connect(worker.deleteLater)
        worker.finished.connect(lambda w=worker: self._workers.remove(w) if w in self._workers else None)
        self._workers.append(worker)
        worker.start()

    def _view_student(self, stu: Student):
        # ponytail: view as info dialog, full detail page if needed
        msg = (
            f"学号: {stu.student_no}\n"
            f"姓名: {stu.name}\n"
            f"性别: {stu.gender}\n"
            f"班级: {self._class_map.get(stu.class_id, '—')}\n"
            f"人脸注册: {'是' if stu.has_face else '否'}"
        )
        QMessageBox.information(self, f"学生: {stu.name}", msg)

    def _edit_student(self, stu: Student):
        dialog = StudentEditDialog(stu, self._class_map, self)
        if dialog.exec():
            self._load_students()

    def _delete_student(self, stu: Student):
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定删除学生「{stu.name}」（{stu.student_no}）？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        def _on_result(result):
            if result.ok:
                self._load_students()
            else:
                QMessageBox.critical(self, "错误", f"删除失败: {result.message}")

        worker = ApiWorker(student_service.delete, stu.id)
        worker.finished.connect(_on_result)
        worker.finished.connect(worker.deleteLater)
        worker.finished.connect(lambda w=worker: self._workers.remove(w) if w in self._workers else None)
        self._workers.append(worker)
        worker.start()

    # ── Face Registration ──

    def _register_face_for(self, student_id: int, image_path: str):
        """注册人脸（不弹对话框，用于创建后自动注册）。"""
        def _on_result(result):
            if not result.ok:
                QMessageBox.critical(self, "警告",
                                     f"学生已创建，但人脸注册失败: {result.message}")
            signal_bus.face_registered.emit(student_id)

        worker = ApiWorker(student_service.register_face, student_id, image_path)
        worker.finished.connect(_on_result)
        worker.finished.connect(worker.deleteLater)
        worker.finished.connect(lambda w=worker: self._workers.remove(w) if w in self._workers else None)
        self._workers.append(worker)
        worker.start()

    def _register_face(self, stu: Student):
        """选择人脸照片 → 注册 embedding。"""
        if stu.has_face:
            reply = QMessageBox.question(
                self, "重新注册人脸",
                f"「{stu.name}」已有人脸注册。是否覆盖？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        path, _ = QFileDialog.getOpenFileName(
            self, f"选择 {stu.name} 的人脸照片", "",
            "图片 (*.jpg *.jpeg *.png)",
        )
        if not path:
            return

        def _on_result(result):
            if result.ok:
                self._load_students()
                signal_bus.face_registered.emit(stu.id)
            else:
                QMessageBox.critical(self, "错误", f"人脸注册失败: {result.message}")

        worker = ApiWorker(student_service.register_face, stu.id, path)
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
