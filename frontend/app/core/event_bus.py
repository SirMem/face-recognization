"""SignalBus — 全局信号总线。

用于解耦组件间通信。任何组件都可以 emit 或 connect
到这里的信号，无需持有对方引用。
"""
from __future__ import annotations

from PySide6.QtCore import QObject, Signal


class SignalBus(QObject):
    """应用级全局信号总线（单例）。"""
    # 认证
    login_success = Signal(dict)
    logout = Signal()

    # 导航
    navigate_requested = Signal(str)   # page_name

    # 数据变更 — 用于触发页面刷新
    student_created = Signal()
    student_deleted = Signal()
    face_registered = Signal(int)      # student_id
    course_created = Signal()
    course_deleted = Signal()
    checkin_completed = Signal(dict)   # recognize result

    _instance: SignalBus | None = None

    def __new__(cls) -> SignalBus:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        super().__init__()
        self._initialized = True


# 全局单例
signal_bus = SignalBus()
