"""CoursePage — 课程管理（CRUD）。"""
from __future__ import annotations

from PySide6.QtWidgets import (QHBoxLayout, QLabel, QLineEdit, QPushButton,
                               QVBoxLayout)

from app.components.data_table import DataTable
from app.pages.base_page import BasePage


class CoursePage(BasePage):
    """课程列表 + 添加表单 + 删除。"""

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(16)

        title = QLabel("课程管理")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # TODO: 添加表单（FormCard + 课程名称/教师/时间 + 添加按钮）
        # TODO: 课程表格（4列：课程名称/授课教师/上课时间/操作）

    def bind(self):
        # TODO: 连接信号
        pass
