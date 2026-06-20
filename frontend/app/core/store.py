"""AppStore — 全局状态管理。

类似 Redux 的中心化 Store，但基于 QObject + Signal。
页面只需 connect 到对应信号即可响应状态变化。

使用方式：
    store = AppStore()
    store.stats_updated.connect(self._on_stats_changed)
    store.update_stats(data)
"""
from __future__ import annotations

from PySide6.QtCore import QObject, Signal


class AppStore(QObject):
    """全局应用状态（单例）。"""
    # ── 认证 ──
    auth_changed = Signal(object)      # user dict | None
    token_changed = Signal(str)        # access_token

    # ── 数据 ──
    stats_updated = Signal(dict)       # 考勤统计数据
    courses_updated = Signal(list)     # 课程列表

    _instance: AppStore | None = None

    def __new__(cls) -> AppStore:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        super().__init__()
        self._initialized = True
        # 状态
        self._user: dict | None = None
        self._token: str | None = None
        self._stats: dict = {}
        self._courses: list = []

    # ── Auth ──
    @property
    def user(self) -> dict | None:
        return self._user

    @user.setter
    def user(self, value: dict | None):
        self._user = value
        self.auth_changed.emit(value)

    @property
    def token(self) -> str | None:
        return self._token

    @token.setter
    def token(self, value: str | None):
        self._token = value
        self.token_changed.emit(value)

    @property
    def is_authenticated(self) -> bool:
        return self._token is not None

    # ── Stats ──
    @property
    def stats(self) -> dict:
        return self._stats

    def update_stats(self, stats: dict):
        self._stats = stats
        self.stats_updated.emit(stats)

    # ── Courses ──
    @property
    def courses(self) -> list:
        return self._courses

    def update_courses(self, courses: list):
        self._courses = courses
        self.courses_updated.emit(courses)


# 全局单例
store = AppStore()
