"""BasePage — 所有页面的基类。

提供统一的生命周期方法 on_enter/on_leave 和刷新协议。
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget


class BasePage(QWidget):
    """页面基类。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setup_ui()
        self.bind()

    def setup_ui(self):
        """子类覆写：构建本页面的 UI。"""
        pass

    def bind(self):
        """子类覆写：连接信号/槽。"""
        pass

    def on_enter(self, **kwargs):
        """页面成为当前页时调用（由 Router 触发）。"""
        self.refresh()

    def refresh(self):
        """刷新页面数据。子类覆写。"""
        pass
