"""CheckinPage — 人脸打卡页面（上传图片识别模式）。"""
from __future__ import annotations

from PySide6.QtCore import QThread, Qt, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
)

from app.pages.base_page import BasePage
from app.services.face_service import face_service

# ── Figma colors ──────────────────────────────────────────────────────────
_BG = "#f9f9ff"
_TEXT_PRIMARY = "#091c35"
_TEXT_SECONDARY = "#5c5f60"
_TEXT_MUTED = "#737685"
_BORDER = "#c3c6d6"
_BRAND = "#003d9b"
_BRAND_LIGHT = "#dfe8ff"
_WHITE = "#ffffff"
_BTN_SECONDARY_TEXT = "#434654"


class RecognitionResults(QFrame):
    """右侧识别结果面板"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("recognitionPanel")
        self.setStyleSheet(f"""
            #recognitionPanel {{
                background: {_WHITE};
                border: 1px solid {_BORDER};
                border-radius: 8px;
            }}
        """)
        self.setFixedWidth(303)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Heading
        heading_frame = QFrame()
        heading_frame.setObjectName("recogHeading")
        heading_frame.setStyleSheet(f"border-bottom: 1px solid {_BORDER};")
        heading_layout = QHBoxLayout(heading_frame)
        heading_layout.setContentsMargins(16, 16, 16, 16)

        heading = QLabel("识别结果")
        heading.setStyleSheet(f"color: {_TEXT_PRIMARY}; font-size: 20px; font-weight: 600;")
        heading_layout.addWidget(heading)
        heading_layout.addStretch()

        layout.addWidget(heading_frame)

        # Result area
        self.result_area = QFrame()
        result_layout = QVBoxLayout(self.result_area)
        result_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        result_layout.setContentsMargins(16, 40, 16, 40)

        icon = QLabel("👤")
        icon.setStyleSheet("font-size: 48px;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        result_layout.addWidget(icon)
        result_layout.addSpacing(16)

        self.result_title = QLabel("等待识别...")
        self.result_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_title.setStyleSheet(f"color: {_TEXT_PRIMARY}; font-size: 24px; font-weight: 600;")
        result_layout.addWidget(self.result_title)
        result_layout.addSpacing(8)

        self.result_desc = QLabel("选择人脸照片\n开始识别。")
        self.result_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_desc.setStyleSheet(f"color: {_TEXT_SECONDARY}; font-size: 14px; line-height: 20px;")
        result_layout.addWidget(self.result_desc)

        layout.addWidget(self.result_area, 1)

        # Recent section
        recent_frame = QFrame()
        recent_frame.setObjectName("recentSection")
        recent_frame.setStyleSheet(f"border-top: 1px solid {_BORDER};")

        recent_layout = QVBoxLayout(recent_frame)
        recent_layout.setContentsMargins(16, 12, 16, 16)

        recent_label = QLabel("最近扫描")
        recent_label.setStyleSheet(f"color: {_TEXT_SECONDARY}; font-size: 12px; font-weight: 700; letter-spacing: 0.6px;")
        recent_layout.addWidget(recent_label)
        recent_layout.addSpacing(8)

        self.scan_time = QLabel("--:--:--")
        self.scan_time.setStyleSheet(f"color: {_TEXT_MUTED}; font-family: 'JetBrains Mono'; font-size: 13px;")
        recent_layout.addWidget(self.scan_time)

        self.scan_name = QLabel("等待数据...")
        self.scan_name.setStyleSheet(f"color: {_TEXT_MUTED}; font-size: 13px;")
        recent_layout.addWidget(self.scan_name)

        layout.addWidget(recent_frame)


# ── Worker — 后台识别 ──────────────────────────────────────────────────

class CheckinWorker(QThread):
    finished = Signal(object)

    def __init__(self, fn, params=None):
        super().__init__()
        self._fn = fn
        self._params = params

    def run(self):
        try:
            result = self._fn(self._params) if self._params else self._fn()
        except Exception as e:
            result = type("R", (), {"ok": False, "data": None, "message": str(e)})()
        self.finished.emit(result)


# ═══════════════════════════════════════════════════════════════════════════

class CheckinPage(BasePage):
    """人脸打卡页 — 上传图片 → API 识别 → 展示结果。"""

    def __init__(self, parent=None):
        self._workers: list[QThread] = []
        super().__init__(parent)

    def setup_ui(self):
        self.setObjectName("checkinPage")
        self.setStyleSheet("background: transparent;")

        root = QVBoxLayout(self)
        root.setContentsMargins(32, 32, 32, 32)
        root.setSpacing(24)

        # ── Header ──
        header = QFrame()
        header.setFixedHeight(68)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(0, 0, 0, 0)

        left = QVBoxLayout()
        left.setContentsMargins(0, 0, 0, 0)
        left.setSpacing(0)
        title = QLabel("人脸打卡")
        title.setStyleSheet(f"color: {_TEXT_PRIMARY}; font-size: 32px; font-weight: 700; letter-spacing: -0.64px;")
        left.addWidget(title)
        subtitle = QLabel("上传人脸照片进行生物识别打卡。")
        subtitle.setStyleSheet(f"color: {_TEXT_SECONDARY}; font-size: 16px;")
        left.addWidget(subtitle)
        h_layout.addLayout(left)
        h_layout.addStretch()

        root.addWidget(header)

        # ── Bento: Upload zone (left) + Results (right) ──
        bento = QHBoxLayout()
        bento.setContentsMargins(0, 0, 0, 0)
        bento.setSpacing(24)

        # ── Left: Upload area ──
        upload_card = QFrame()
        upload_card.setObjectName("uploadCard")
        upload_card.setStyleSheet(f"""
            #uploadCard {{
                background: {_WHITE};
                border: 1px solid {_BORDER};
                border-radius: 8px;
            }}
        """)
        upload_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        upload_card.setMinimumHeight(300)

        upload_layout = QVBoxLayout(upload_card)
        upload_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        upload_layout.setContentsMargins(40, 40, 40, 40)

        upload_icon = QLabel("📷")
        upload_icon.setStyleSheet("font-size: 56px;")
        upload_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        upload_layout.addWidget(upload_icon)

        upload_layout.addSpacing(16)

        self.status_label = QLabel("选择人脸照片进行打卡")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(f"color: {_TEXT_MUTED}; font-size: 15px;")
        upload_layout.addWidget(self.status_label)

        upload_layout.addSpacing(24)

        self.upload_btn = QPushButton("  选择图片并识别")
        self.upload_btn.setObjectName("uploadBtn")
        self.upload_btn.setStyleSheet(f"""
            #uploadBtn {{
                background: {_BRAND};
                border: none;
                border-radius: 4px;
                color: {_WHITE};
                font-size: 14px;
                font-weight: 600;
                padding: 10px 24px;
            }}
            #uploadBtn:hover {{ background: #002b6a; }}
            #uploadBtn:disabled {{ background: #a0a0a0; }}
        """)
        self.upload_btn.setFixedHeight(40)
        self.upload_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        upload_layout.addWidget(self.upload_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        bento.addWidget(upload_card, 2)

        # ── Right: Results ──
        self.recognition_panel = RecognitionResults()
        bento.addWidget(self.recognition_panel, 1)

        root.addLayout(bento)
        root.addStretch(1)

    def bind(self):
        self.upload_btn.clicked.connect(self._capture)

    def _capture(self):
        """选择图片 → API 识别 → 更新结果面板。"""
        path, _ = QFileDialog.getOpenFileName(
            self, "选择人脸照片", "",
            "图片 (*.jpg *.jpeg *.png *.bmp *.webp)",
        )
        if not path:
            return
        self.upload_btn.setEnabled(False)
        self.upload_btn.setText("  识别中…")
        self.status_label.setText("处理中…")

        # ponytail: reads full file into memory, fine for single images
        with open(path, "rb") as f:
            image_data = f.read()
        w = CheckinWorker(face_service.recognize, image_data)
        w.finished.connect(self._handle_recognition)
        w.finished.connect(w.deleteLater)
        self._workers.append(w)
        w.start()

    def _handle_recognition(self, result):
        self._workers = [w for w in self._workers if not w.isFinished()]
        self.upload_btn.setEnabled(True)
        self.upload_btn.setText("  选择图片并识别")

        if not result.ok:
            self.status_label.setText(result.message or "识别失败")
            self.recognition_panel.result_title.setText("识别失败")
            self.recognition_panel.result_desc.setText(result.message or "请重试")
            return

        data = result.data or {}
        panel = self.recognition_panel

        if data.get("is_match"):
            panel.result_title.setText(data["student_name"])
            panel.result_desc.setText(
                f"学号 #{data['student_no']}\n"
                f"置信度: {float(data.get('confidence', 0)) * 100:.1f}%"
            )
            from datetime import datetime
            raw = data.get("checkin_time", "")
            try:
                dt = datetime.fromisoformat(raw)
                panel.scan_time.setText(dt.strftime("%H:%M:%S"))
            except Exception:
                panel.scan_time.setText(raw)
            panel.scan_name.setText(data["student_name"])
            self.status_label.setText("✓ 识别成功")
        else:
            panel.result_title.setText("未匹配")
            panel.result_desc.setText(data.get("message", "未找到匹配人脸"))
            self.status_label.setText("未找到匹配")
