"""DashboardPage — 考勤总览页，对齐 Figma 设计。"""
from __future__ import annotations

from PySide6.QtCore import QThread, Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

import pyqtgraph as pg

from app.pages.base_page import BasePage
from app.services.attendance_service import attendance_service
from app.core.store import store
from app.core.event_bus import signal_bus

# ── Figma colors ──────────────────────────────────────────────────────────
_BG = "#f9f9ff"
_TEXT_PRIMARY = "#091c35"
_TEXT_SECONDARY = "#5c5f60"
_BORDER = "#c3c6d6"
_BRAND = "#003d9b"
_GREEN = "#006e1c"
_GREEN_BG = "#c4f8c9"
_RED = "#ba1a1a"
_RED_BG = "#ffdad6"
_ORANGE = "#934b00"
_ORANGE_BG = "#ffdbb9"
_BLUE_BG = "#dae2ff"
_WHITE = "#ffffff"
_CHART_ABSENT = "#c3c6d6"


# ═════════════════════════════════════════════════════════════════════════
#  Worker — 后台取 Dashboard 数据
# ═════════════════════════════════════════════════════════════════════════

class DashboardWorker(QThread):
    finished = Signal(object)

    def run(self):
        try:
            result = attendance_service.get_dashboard()
        except Exception as e:
            result = type("R", (), {"ok": False, "data": None, "message": str(e)})()
        self.finished.emit(result)


# ═════════════════════════════════════════════════════════════════════════
#  Stat card — 单张统计卡片
# ═════════════════════════════════════════════════════════════════════════

class StatCard(QFrame):
    def __init__(
        self,
        label: str,
        value: str,
        icon_bg: str,
        icon_text: str,
        subtitle: str = "",
        trend: str = "",
        trend_color: str = "",
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("statCard")
        self.setStyleSheet(f"""
            #statCard {{
                background: {_BG};
                border: 1px solid {_BORDER};
                border-radius: 8px;
            }}
        """)
        self.setFixedSize(221, 129)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(0)

        # Row 1: label + icon
        row1 = QHBoxLayout()
        row1.setContentsMargins(0, 0, 0, 0)
        row1.setSpacing(4)
        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {_TEXT_SECONDARY}; font-size: 12px; font-weight: 700; letter-spacing: 0.6px;")
        row1.addWidget(lbl)
        row1.addStretch()

        icon_frame = QFrame()
        icon_frame.setFixedSize(22, 22)
        icon_frame.setStyleSheet(f"""
            background: {icon_bg};
            border-radius: 6px;
        """)
        icon_lbl = QLabel(icon_text)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet(f"color: {icon_bg == _GREEN_BG and _GREEN or icon_bg == _RED_BG and _RED or icon_bg == _ORANGE_BG and _ORANGE or _BRAND}; font-size: 10px;")
        icon_layout = QVBoxLayout(icon_frame)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.addWidget(icon_lbl)
        row1.addWidget(icon_frame)
        layout.addLayout(row1)
        layout.addSpacing(7)

        # Value — store reference
        self._value_lbl = QLabel(value)
        self._value_lbl.setStyleSheet(f"color: {_TEXT_PRIMARY}; font-size: 32px; font-weight: 700; letter-spacing: -0.64px;")
        layout.addWidget(self._value_lbl)
        layout.addSpacing(7)

        # Subtitle / trend — store reference
        self._sub_lbl = QLabel(trend or subtitle)
        self._sub_lbl.setStyleSheet(f"color: {trend_color or _TEXT_SECONDARY}; font-size: 12px;")
        layout.addWidget(self._sub_lbl)

    def set_data(self, value: str, trend: str = "", trend_color: str = ""):
        self._value_lbl.setText(str(value))
        if trend:
            self._sub_lbl.setText(trend)
            self._sub_lbl.setStyleSheet(f"color: {trend_color}; font-size: 12px;")


# ═════════════════════════════════════════════════════════════════════════
#  Quick Action Card
# ═════════════════════════════════════════════════════════════════════════

class QuickActionCard(QFrame):
    clicked = Signal()

    def __init__(self, icon_char: str, title: str, desc: str, parent=None):
        super().__init__(parent)
        self.setObjectName("actionCard")
        self.setStyleSheet(f"""
            #actionCard {{
                background: {_BG};
                border: 1px solid {_BORDER};
                border-radius: 8px;
            }}
            #actionCard:hover {{
                background: #f0f3ff;
            }}
        """)
        self.setFixedHeight(82)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        icon = QFrame()
        icon.setFixedSize(48, 48)
        icon.setStyleSheet(f"background: #dfe8ff; border-radius: 4px;")
        icon_lbl = QLabel(icon_char)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet(f"color: {_BRAND}; font-size: 18px;")
        icon_layout = QVBoxLayout(icon)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.addWidget(icon_lbl)
        layout.addWidget(icon)

        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(2)
        t = QLabel(title)
        t.setStyleSheet(f"color: {_TEXT_PRIMARY}; font-size: 16px; font-weight: 600;")
        text_col.addWidget(t)
        d = QLabel(desc)
        d.setStyleSheet(f"color: {_TEXT_SECONDARY}; font-size: 16px;")
        text_col.addWidget(d)
        layout.addLayout(text_col)
        layout.addStretch()

        chevron = QLabel("›")
        chevron.setStyleSheet(f"color: {_BORDER}; font-size: 18px;")
        layout.addWidget(chevron)

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


# ═════════════════════════════════════════════════════════════════════════
#  Dashboard Page
# ═════════════════════════════════════════════════════════════════════════

class DashboardPage(BasePage):
    """考勤总览页 — 与 Figma "Main Content Area" 设计一致。"""

    def __init__(self, parent=None):
        self._worker: DashboardWorker | None = None
        self._closing = False
        super().__init__(parent)

    def setup_ui(self):
        self.setObjectName("dashboardPage")
        self.setStyleSheet(f"background: transparent;")

        root = QVBoxLayout(self)
        root.setContentsMargins(32, 64, 32, 0)
        root.setSpacing(0)

        # ════════════════════════════════════════════════
        #  Page Header
        # ════════════════════════════════════════════════
        header = QFrame()
        header.setObjectName("dashPageHeader")
        header.setFixedHeight(68)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        left_col = QVBoxLayout()
        left_col.setContentsMargins(0, 0, 0, 0)
        left_col.setSpacing(0)

        title = QLabel("总览")
        title.setStyleSheet(f"color: {_TEXT_PRIMARY}; font-size: 32px; font-weight: 700; letter-spacing: -0.64px;")
        left_col.addWidget(title)

        subtitle = QLabel("今日考勤概览与快捷操作。")
        subtitle.setStyleSheet(f"color: {_TEXT_SECONDARY}; font-size: 16px;")
        left_col.addWidget(subtitle)
        header_layout.addLayout(left_col)
        header_layout.addStretch()

        # Export Report button
        export_btn = QPushButton("  导出报告")
        export_btn.setObjectName("exportBtn")
        export_btn.setStyleSheet(f"""
            #exportBtn {{
                background: {_BG};
                border: 1px solid {_BORDER};
                border-radius: 4px;
                color: {_TEXT_PRIMARY};
                font-size: 16px;
                padding: 8px 16px;
            }}
            #exportBtn:hover {{ background: #f0f3ff; }}
        """)
        export_btn.setFixedHeight(42)
        export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        header_layout.addWidget(export_btn)
        header_layout.addSpacing(12)

        # New Session button
        new_btn = QPushButton("  新建考勤")
        new_btn.setObjectName("newSessionBtn")
        new_btn.setStyleSheet(f"""
            #newSessionBtn {{
                background: {_BRAND};
                border: none;
                border-radius: 4px;
                color: {_WHITE};
                font-size: 16px;
                font-weight: 600;
                padding: 9px 16px;
            }}
            #newSessionBtn:hover {{ background: #002b6a; }}
        """)
        new_btn.setFixedHeight(42)
        new_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        header_layout.addWidget(new_btn)

        root.addWidget(header)
        root.addSpacing(24)

        # ════════════════════════════════════════════════
        #  Stats Cards Row
        # ════════════════════════════════════════════════
        cards_row = QHBoxLayout()
        cards_row.setContentsMargins(0, 0, 0, 0)
        cards_row.setSpacing(24)

        self.card_total = StatCard("总应到", "—", "#dae2ff", "✦", subtitle="所有活跃课程")
        self.card_present = StatCard("已签到", "—", _GREEN_BG, "✓")
        self.card_late = StatCard("迟到", "—", _ORANGE_BG, "!", subtitle="待处理")
        self.card_absent = StatCard("缺勤", "—", _RED_BG, "✕")

        cards_row.addWidget(self.card_total)
        cards_row.addWidget(self.card_present)
        cards_row.addWidget(self.card_late)
        cards_row.addWidget(self.card_absent)
        root.addLayout(cards_row)
        root.addSpacing(24)

        # ════════════════════════════════════════════════
        #  Bento Grid: Left (Chart) + Right (Actions)
        # ════════════════════════════════════════════════
        bento = QHBoxLayout()
        bento.setContentsMargins(0, 0, 0, 0)
        bento.setSpacing(24)

        # ── Left: Chart / Summary ──
        chart_card = QFrame()
        chart_card.setObjectName("chartCard")
        chart_card.setStyleSheet(f"""
            #chartCard {{
                background: {_BG};
                border: 1px solid {_BORDER};
                border-radius: 8px;
            }}
        """)
        chart_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        chart_card.setFixedHeight(426)

        chart_layout = QVBoxLayout(chart_card)
        chart_layout.setContentsMargins(24, 24, 24, 24)
        chart_layout.setSpacing(0)

        # Chart header
        chart_header = QHBoxLayout()
        chart_header.setContentsMargins(0, 0, 0, 0)
        chart_header.addWidget(QLabel("出勤率概览"))
        chart_header_item = chart_header.itemAt(0)
        chart_header_item.widget().setStyleSheet(f"color: {_TEXT_PRIMARY}; font-size: 20px; font-weight: 600;")
        chart_header.addStretch()
        # Legend
        legend = QHBoxLayout()
        legend.setSpacing(8)
        for color, text in [(_BRAND, "已签到"), (_CHART_ABSENT, "缺勤")]:
            dot = QLabel(f"●  {text}")
            dot.setStyleSheet(f"color: {color}; font-size: 12px;")
            legend.addWidget(dot)
        chart_header.addLayout(legend)
        chart_layout.addLayout(chart_header)

        subtitle2 = QLabel("每日实时趋势")
        subtitle2.setStyleSheet(f"color: {_TEXT_SECONDARY}; font-size: 16px;")
        chart_layout.addWidget(subtitle2)
        chart_layout.addSpacing(24)

        # Chart area with overlay
        chart_container = QFrame()
        chart_container.setStyleSheet(f"background: transparent;")
        chart_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        chart_stack = QVBoxLayout(chart_container)
        chart_stack.setContentsMargins(0, 0, 0, 0)
        chart_stack.setSpacing(0)

        # pyqtgraph plot
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground(None)
        self.plot_widget.getAxis("left").setStyle(showValues=False)
        self.plot_widget.getAxis("bottom").setStyle(showValues=True)
        self.plot_widget.getAxis("left").setPen(_BORDER)
        self.plot_widget.getAxis("bottom").setPen(_BORDER)
        self.plot_widget.showGrid(y=True, alpha=0.3)

        self.bars_present: list = []
        self.bars_absent: list = []

        chart_stack.addWidget(self.plot_widget, 1)

        # Overlay: large percentage centered
        pct_overlay = QWidget()
        pct_overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        pct_overlay.setStyleSheet("background: transparent;")
        pct_layout = QVBoxLayout(pct_overlay)
        pct_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        pct_row = QHBoxLayout()
        pct_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pct_value = QLabel("—")
        self.pct_value.setStyleSheet(f"color: {_BRAND}; font-size: 64px; font-weight: 700;")
        pct_row.addWidget(self.pct_value)
        self.pct_sign = QLabel("%")
        self.pct_sign.setStyleSheet(f"color: {_BRAND}; font-size: 32px; font-weight: 700;")
        pct_row.addWidget(self.pct_sign)
        pct_layout.addLayout(pct_row)

        self.pct_label = QLabel("当前出勤率")
        self.pct_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pct_label.setStyleSheet(f"color: {_TEXT_SECONDARY}; font-size: 12px; font-weight: 700; letter-spacing: 1.2px;")
        pct_layout.addWidget(self.pct_label)

        # Overlay on chart using QStackedLayout approach — simpler: put percentage below chart
        chart_stack.addWidget(pct_overlay)

        chart_layout.addWidget(chart_container, 1)

        bento.addWidget(chart_card, 2)

        # ── Right: Quick Entry ──
        quick_col = QVBoxLayout()
        quick_col.setContentsMargins(0, 0, 0, 0)
        quick_col.setSpacing(0)

        quick_title = QLabel("快捷入口")
        quick_title.setStyleSheet(f"color: {_TEXT_PRIMARY}; font-size: 20px; font-weight: 600;")
        quick_col.addWidget(quick_title)
        quick_col.addSpacing(24)

        self.action_face = QuickActionCard("📷", "人脸打卡", "启动摄像头进行人脸识别打卡")
        self.action_student = QuickActionCard("👤", "学生管理", "注册或编辑学生信息")
        self.action_records = QuickActionCard("📋", "考勤记录", "查看历史考勤数据")

        quick_col.addWidget(self.action_face)
        quick_col.addSpacing(8)
        quick_col.addWidget(self.action_student)
        quick_col.addSpacing(8)
        quick_col.addWidget(self.action_records)
        quick_col.addStretch()

        quick_card = QFrame()
        quick_card.setStyleSheet("background: transparent;")
        quick_card.setLayout(quick_col)
        quick_card.setFixedWidth(303)
        bento.addWidget(quick_card, 1)

        root.addLayout(bento)
        root.addStretch(1)

    # ═══════════════════════════════════════════════════════════════════
    #  Data
    # ═══════════════════════════════════════════════════════════════════

    def bind(self):
        self.action_face.clicked.connect(lambda: signal_bus.navigate_requested.emit("checkin"))
        self.action_student.clicked.connect(lambda: signal_bus.navigate_requested.emit("students"))
        self.action_records.clicked.connect(lambda: signal_bus.navigate_requested.emit("attendance"))

    def refresh(self):
        self._fetch()

    def _fetch(self):
        if self._worker and self._worker.isRunning():
            return
        w = DashboardWorker()
        w.finished.connect(self._handle_data)
        w.finished.connect(w.deleteLater)
        self._worker = w
        w.start()

    def _handle_data(self, result):
        self._worker = None
        if not result.ok:
            return

        d = result.data or {}
        today_total = d.get("total_expected", 0)
        present = d.get("present", 0)
        late = d.get("late", 0)
        absent = d.get("absent", 0)
        rate = d.get("rate", 0)
        present_trend = d.get("present_trend")
        absent_trend = d.get("absent_trend")
        series = d.get("daily_series", [])

        self.card_total.set_data(str(today_total))
        self.card_present.set_data(str(present), trend=present_trend or "", trend_color=_GREEN)
        self.card_late.set_data(str(late))
        self.card_absent.set_data(str(absent), trend=absent_trend or "", trend_color=_RED)

        # Percentage overlay
        self.pct_value.setText(f"{rate:.1f}")

        # Chart
        self._update_chart(series)

    def _update_chart(self, series: list):
        self.plot_widget.clear()
        if not series:
            return

        x = list(range(len(series)))
        labels = [s["date"][-5:] for s in series]  # MM-DD

        present_vals = [s["present"] for s in series]
        absent_vals = [s["absent"] for s in series]
        width = 0.3

        # Present bars
        bars_p = pg.BarGraphItem(
            x=[i - width / 2 for i in x],
            height=present_vals,
            width=width,
            brush=_BRAND,
        )
        # Absent bars
        bars_a = pg.BarGraphItem(
            x=[i + width / 2 for i in x],
            height=absent_vals,
            width=width,
            brush=_CHART_ABSENT,
        )
        self.plot_widget.addItem(bars_p)
        self.plot_widget.addItem(bars_a)

        # Axis
        axis = self.plot_widget.getAxis("bottom")
        axis.setTicks([list(enumerate(labels))])

    def closeEvent(self, event):
        self._closing = True
        if self._worker and self._worker.isRunning():
            try:
                self._worker.finished.disconnect(self._handle_data)
            except RuntimeError:
                pass
            self._worker.wait()
        super().closeEvent(event)
