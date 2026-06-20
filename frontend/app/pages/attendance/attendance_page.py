"""AttendancePage — 考勤记录查询（表格 + 筛选 + 统计栏）。"""
from __future__ import annotations

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (QComboBox, QDateEdit, QHBoxLayout, QLabel,
                               QPushButton, QVBoxLayout)

from app.components.course_combo import CourseCombo
from app.components.data_table import DataTable
from app.core.store import store
from app.pages.base_page import BasePage


class AttendancePage(BasePage):
    """考勤明细：日期筛选 + 课程筛选 + 表格 + 统计摘要。"""

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(16)

        title = QLabel("考勤记录")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # TODO: 筛选栏（日期范围 + 课程下拉 + 查询按钮）
        # TODO: 统计摘要标签
        # TODO: 考勤明细表格（6列）

    def bind(self):
        # TODO: 刷新时从 store 读取或请求
        pass
