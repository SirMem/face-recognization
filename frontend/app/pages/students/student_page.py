"""StudentPage — 学生管理（CRUD + 人脸注册）。"""
from __future__ import annotations

from PySide6.QtWidgets import (QComboBox, QHBoxLayout, QLabel, QLineEdit,
                               QPushButton, QVBoxLayout)

from app.components.data_table import DataTable
from app.pages.base_page import BasePage


class StudentPage(BasePage):
    """学生列表 + 添加表单 + 删除 + 人脸注册入口。"""

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("学生管理")
        title.setObjectName("pageTitle")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        # TODO: 添加表单（FormCard + 输入框 + 添加按钮）
        # TODO: 学生表格（6列：学号/姓名/性别/班级/人脸状态/操作）

    def bind(self):
        # TODO: 连接信号
        pass
