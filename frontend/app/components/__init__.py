"""BaseWidget — 所有可复用组件的基类。

采用"三方法模式"：setup_ui() + connect_signals() + apply_theme()
子类只需覆写需要的方法。
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QWidget

from app.core.theme import theme_manager
from app.core.event_bus import signal_bus


class BaseWidget(QFrame):
    """组件基类，自动连接主题变化信号。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setup_ui()
        self.connect_signals()
        theme_manager.theme_changed.connect(self.on_theme_changed)

    def setup_ui(self):
        """子类覆写：构建 UI 布局。"""
        pass

    def connect_signals(self):
        """子类覆写：连接信号/槽。"""
        pass

    def on_theme_changed(self, mode: str):
        """主题变化时刷新样式。"""
        self.style().unpolish(self)
        self.style().polish(self)
