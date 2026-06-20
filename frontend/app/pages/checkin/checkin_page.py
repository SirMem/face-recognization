"""CheckinPage — 人脸打卡页面。"""
from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from app.components.course_combo import CourseCombo
from app.pages.base_page import BasePage


class CheckinPage(BasePage):
    """摄像头实时画面 + 拍照识别 + 结果展示。"""

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(16)

        title = QLabel("人脸打卡")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        content = QHBoxLayout()
        content.setSpacing(24)

        # TODO: 左—摄像头面板 (CameraWidget)
        # - 实时画面
        # - 启动/关闭摄像头按钮
        # - 拍照识别按钮

        # TODO: 右—结果面板
        # - 识别结果图标
        # - 学生姓名/学号/时间/置信度
        # - 课程下拉选择框

        layout.addLayout(content)

    def bind(self):
        # TODO: 连接信号
        pass
