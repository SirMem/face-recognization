"""StatCard — 统计卡片组件。

用于 Dashboard 展示数值类指标：总考勤、出勤、迟到、缺勤。
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout

from app.components import BaseWidget


class StatCard(BaseWidget):
    """统计卡片：图标 + 数值 + 标签。"""

    def __init__(self, label: str = "", value: str | int = "--", icon_text: str = "", accent: str = "", parent=None):
        self._label = label
        self._value = value
        self._icon_text = icon_text
        self._accent = accent
        super().__init__(parent)

    def setup_ui(self):
        self.setFixedHeight(120)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)

        # 图标
        self.icon_lbl = QLabel(self._icon_text)
        self.icon_lbl.setFixedSize(40, 40)
        self.icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.icon_lbl)

        # 文字
        text_col = QVBoxLayout()
        text_col.setSpacing(4)
        self.value_lbl = QLabel(str(self._value))
        self.value_lbl.setObjectName("statValue")
        text_col.addWidget(self.value_lbl)

        self.label_lbl = QLabel(self._label)
        self.label_lbl.setObjectName("statLabel")
        text_col.addWidget(self.label_lbl)

        layout.addLayout(text_col)
        layout.addStretch()

    def update_value(self, value: str | int):
        self.value_lbl.setText(str(value))
