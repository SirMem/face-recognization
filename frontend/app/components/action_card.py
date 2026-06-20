"""ActionCard — 操作卡片组件。

用于 Dashboard 的快捷入口：人脸打卡、学生管理、考勤记录。
点击后导航到对应页面。
"""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout

from app.components import BaseWidget


class ActionCard(BaseWidget):
    """操作卡片：图标 + 标题 + 描述 + 点击信号。"""
    clicked = Signal()

    def __init__(self, title: str = "", description: str = "", icon_text: str = "", parent=None):
        self._title = title
        self._description = description
        self._icon_text = icon_text
        super().__init__(parent)

    def setup_ui(self):
        self.setFixedHeight(100)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)

        icon = QLabel(self._icon_text)
        icon.setFixedSize(36, 36)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon)

        text = QVBoxLayout()
        text.setSpacing(4)
        t = QLabel(self._title)
        t.setObjectName("actionTitle")
        text.addWidget(t)
        d = QLabel(self._description)
        d.setObjectName("actionDesc")
        d.setWordWrap(True)
        text.addWidget(d)
        layout.addLayout(text)
        layout.addStretch()

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)
