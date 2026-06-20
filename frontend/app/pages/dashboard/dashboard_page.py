"""DashboardPage — 考勤总览首页。"""
from __future__ import annotations

from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QVBoxLayout

from app.components.action_card import ActionCard
from app.components.stat_card import StatCard
from app.core.store import store
from app.pages.base_page import BasePage


class DashboardPage(BasePage):
    """考勤总览：统计卡片 + 快捷入口 + 图表区域。"""

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(20)

        # 标题
        title = QLabel("考勤总览")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # 统计卡片 (2×2 网格)
        cards = QGridLayout()
        cards.setSpacing(16)

        self.card_total = StatCard("总考勤次数", "--", "📅", "#4fc3f7")
        self.card_present = StatCard("出勤", "--", "✅", "#22c55e")
        self.card_late = StatCard("迟到", "--", "⏰", "#f59e0b")
        self.card_absent = StatCard("缺勤", "--", "❌", "#ef4444")

        cards.addWidget(self.card_total, 0, 0)
        cards.addWidget(self.card_present, 0, 1)
        cards.addWidget(self.card_late, 1, 0)
        cards.addWidget(self.card_absent, 1, 1)
        layout.addLayout(cards)

        # TODO: 图表区域（pyqtgraph 环形图或柱状图）
        # TODO: 快捷入口（ActionCard ×3）

    def bind(self):
        store.stats_updated.connect(self._on_stats_updated)

    def refresh(self):
        # 由 on_enter 触发，从 store 读取 stats 或重新请求
        pass

    def _on_stats_updated(self, stats: dict):
        self.card_total.update_value(stats.get("total", 0))
        self.card_present.update_value(stats.get("present", 0))
        self.card_late.update_value(stats.get("late", 0))
        self.card_absent.update_value(stats.get("absent", 0))
