"""ThemeManager — 设计 Token + 主题切换系统。

职责：
1. 持有所有语义化 Token（颜色、间距、字号、圆角）
2. 应用 QPalette + 模板化 QSS 实现亮/暗切换
3. 切换时 emit 信号通知全局 Widget 刷新
"""
from __future__ import annotations

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QColor, QPalette


# ── Design Tokens ──────────────────────────────────────────────────────

COLORS_LIGHT = {
    "primary": "#003d9b",
    "primary_hover": "#002f7a",
    "primary_light": "#e8efff",
    "surface_page": "#f9f9ff",
    "surface_card": "#ffffff",
    "surface_sidebar": "#ffffff",
    "text_primary": "#1e293b",
    "text_secondary": "#64748b",
    "text_disabled": "#94a3b8",
    "text_on_primary": "#ffffff",
    "success": "#22c55e",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "info": "#3b82f6",
    "border": "#c3c6d6",
    "border_focus": "#003d9b",
    "status_present": "#22c55e",
    "status_late": "#f59e0b",
    "status_absent": "#ef4444",
}

COLORS_DARK = {
    "primary": "#60a5fa",
    "primary_hover": "#3b82f6",
    "primary_light": "#1e3a5f",
    "surface_page": "#0f172a",
    "surface_card": "#1e293b",
    "surface_sidebar": "#1e293b",
    "text_primary": "#f1f5f9",
    "text_secondary": "#94a3b8",
    "text_disabled": "#64748b",
    "text_on_primary": "#ffffff",
    "success": "#4ade80",
    "warning": "#fbbf24",
    "danger": "#f87171",
    "info": "#60a5fa",
    "border": "#334155",
    "border_focus": "#60a5fa",
    "status_present": "#4ade80",
    "status_late": "#fbbf24",
    "status_absent": "#f87171",
}

SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 16,
    "lg": 24,
    "xl": 32,
    "xxl": 48,
}

FONT = {
    "family": "Inter",
    "family_mono": "JetBrains Mono",
    "size_xs": 10,
    "size_sm": 12,
    "size_md": 14,
    "size_lg": 16,
    "size_xl": 20,
    "size_2xl": 32,
    "size_3xl": 48,
    "weight_regular": 400,
    "weight_semibold": 600,
    "weight_bold": 700,
}

RADIUS = {
    "sm": 4,
    "md": 6,
    "lg": 8,
    "xl": 12,
}


class ThemeManager(QObject):
    """全局主题管理器（单例）。"""
    theme_changed = Signal(str)  # "light" | "dark"

    _instance: ThemeManager | None = None

    def __new__(cls) -> ThemeManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        super().__init__()
        self._initialized = True
        self._mode: str = "dark"

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def colors(self) -> dict:
        return COLORS_DARK if self._mode == "dark" else COLORS_LIGHT

    @property
    def spacing(self) -> dict:
        return SPACING

    @property
    def font(self) -> dict:
        return FONT

    @property
    def radius(self) -> dict:
        return RADIUS

    def apply(self, app, mode: str = "dark"):
        """应用主题到 QApplication。"""
        self._mode = mode
        colors = self.colors

        # ── QPalette ──
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(colors["surface_page"]))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(colors["text_primary"]))
        palette.setColor(QPalette.ColorRole.Base, QColor(colors["surface_card"]))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(colors["surface_sidebar"]))
        palette.setColor(QPalette.ColorRole.Text, QColor(colors["text_primary"]))
        palette.setColor(QPalette.ColorRole.Button, QColor(colors["primary"]))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(colors["text_on_primary"]))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(colors["primary"]))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(colors["text_on_primary"]))
        palette.setColor(QPalette.ColorRole.Link, QColor(colors["primary"]))
        app.setPalette(palette)

        # ── QSS ──
        self._apply_qss(app)

        self.theme_changed.emit(mode)

    def _apply_qss(self, app):
        """从模板读取 QSS 并替换占位符。"""
        import os
        qss_path = os.path.join(os.path.dirname(__file__), "..", "..", "resources", "styles", "base.qss")
        qss_path = os.path.normpath(qss_path)
        if not os.path.exists(qss_path):
            return
        with open(qss_path, "r", encoding="utf-8") as f:
            template = f.read()
        # 合并所有 Token
        ctx = {}
        ctx.update(self.colors)
        ctx.update({f"spacing_{k}": v for k, v in self.spacing.items()})
        ctx.update({f"font_size_{k}": v for k, v in self.font.items() if k.startswith("size_")})
        ctx.update({f"radius_{k}": v for k, v in self.radius.items()})
        app.setStyleSheet(template.format(**ctx))

    def switch_to(self, mode: str):
        """便捷方法：直接切换。"""
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            self.apply(app, mode)


# 全局单例
theme_manager = ThemeManager()
