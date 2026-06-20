"""FormCard — 表单卡片容器组件。

用于学生管理、课程管理等页面的添加/编辑表单区域。
"""
from __future__ import annotations

from PySide6.QtWidgets import QFrame, QHBoxLayout


class FormCard(QFrame):
    """带边框和背景的表单容器。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("formCard")
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(16, 12, 16, 12)
        self._layout.setSpacing(12)

    def add_widget(self, widget):
        self._layout.addWidget(widget)

    def add_stretch(self):
        self._layout.addStretch()
