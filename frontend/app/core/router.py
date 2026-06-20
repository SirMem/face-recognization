"""Router — 页面路由（QStackedWidget 上层的导航控制）。

用法：
    router = Router(stack_widget)
    router.register("dashboard", DashboardPage)
    router.navigate("dashboard")
"""
from __future__ import annotations

from collections import deque

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QStackedWidget


class Router(QObject):
    """管理 QStackedWidget 的页面注册、导航和历史。"""
    page_changed = Signal(str)  # 当前页面名称

    def __init__(self, stack: QStackedWidget, parent=None):
        super().__init__(parent)
        self._stack = stack
        self._pages: dict[str, object] = {}
        self._history: deque[str] = deque(maxlen=20)

    def register(self, name: str, page_widget, **kwargs):
        """注册一个页面（name 作为路由标识）。"""
        from PySide6.QtWidgets import QWidget
        if isinstance(page_widget, type):
            page_widget = page_widget(**kwargs)
        self._stack.addWidget(page_widget)
        self._pages[name] = page_widget

    def navigate(self, name: str, **kwargs):
        """跳转到指定页面。"""
        widget = self._pages.get(name)
        if widget is None:
            raise KeyError(f"Route '{name}' not registered")
        self._stack.setCurrentWidget(widget)
        self._history.append(name)
        self.page_changed.emit(name)
        # 触发页面生命周期
        if hasattr(widget, "on_enter"):
            widget.on_enter(**kwargs)

    def go_back(self) -> str | None:
        """返回上一页。"""
        if len(self._history) < 2:
            return None
        self._history.pop()  # 当前页
        prev = self._history[-1]
        self.navigate(prev)
        return prev

    @property
    def current(self) -> str | None:
        if not self._history:
            return None
        return self._history[-1]

    @property
    def pages(self) -> dict[str, object]:
        return self._pages
