"""CourseCombo — 课程下拉框组件。

在打卡页和考勤记录页复用，可绑定 store.courses 自动刷新。
"""
from __future__ import annotations

from PySide6.QtWidgets import QComboBox

from app.core.store import store


class CourseCombo(QComboBox):
    """课程下拉框，自动加载 store 中的课程列表。"""

    def __init__(self, placeholder: str = "-- 不指定课程 --", parent=None):
        super().__init__(parent)
        self._placeholder = placeholder
        self._load()
        store.courses_updated.connect(self._load)

    def _load(self):
        current = self.currentData()
        self.clear()
        self.addItem(self._placeholder, None)
        for c in store.courses:
            label = f"{c['name']}" + (f" - {c['teacher']}" if c.get("teacher") else "")
            self.addItem(label, c["id"])
        # 恢复选中
        idx = self.findData(current)
        if idx >= 0:
            self.setCurrentIndex(idx)

    def current_course_id(self) -> int | None:
        return self.currentData()
