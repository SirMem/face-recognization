"""CheckinPage — 人脸打卡页面，对齐 Figma 设计。"""
from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.pages.base_page import BasePage

# ── Figma colors ──────────────────────────────────────────────────────────
_BG = "#f9f9ff"
_TEXT_PRIMARY = "#091c35"
_TEXT_SECONDARY = "#5c5f60"
_TEXT_MUTED = "#737685"
_BORDER = "#c3c6d6"
_BRAND = "#003d9b"
_BRAND_LIGHT = "#dfe8ff"
_WHITE = "#ffffff"
_VIEWPORT_BG = "#091c35"
_DARK_BORDER = "#737685"
_GRID_COLOR = "#ffffff"
_BTN_SECONDARY_TEXT = "#434654"


class CameraTimer(QLabel):
    """左上角 timer 显示 00:00:00"""

    def __init__(self, parent=None):
        super().__init__("00:00:00", parent)
        self.setStyleSheet(f"color: {_TEXT_SECONDARY}; font-family: 'JetBrains Mono'; font-size: 13px;")
        self._sec = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)

    def start(self):
        self._sec = 0
        self._timer.start(1000)

    def stop(self):
        self._timer.stop()
        self.setText("00:00:00")

    def _tick(self):
        self._sec += 1
        m, s = divmod(self._sec, 60)
        h, m = divmod(m, 60)
        self.setText(f"{h:02d}:{m:02d}:{s:02d}")


class StatusMessage(QFrame):
    """居中提示文案"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(595, 670)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon = QLabel("📷")
        icon.setStyleSheet(f"font-size: 42px; color: {_TEXT_MUTED};")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon)
        layout.addSpacing(16)

        self.msg = QLabel("Click 'Start Camera' to begin")
        self.msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.msg.setStyleSheet(f"color: {_TEXT_MUTED}; font-family: 'JetBrains Mono'; font-size: 13px;")
        layout.addWidget(self.msg)


class CameraViewport(QFrame):
    """左侧摄像头区域"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("cameraViewport")
        self.setStyleSheet(f"""
            #cameraViewport {{
                background: {_VIEWPORT_BG};
                border: 1px solid {_DARK_BORDER};
                border-radius: 4px;
            }}
        """)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumHeight(400)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(17, 17, 17, 17)
        layout.setSpacing(0)

        # Top bar: offline badge + timer
        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)

        badge_frame = QFrame()
        badge_frame.setObjectName("cameraBadge")
        badge_layout = QHBoxLayout(badge_frame)
        badge_layout.setContentsMargins(8, 1, 8, 1)
        badge_layout.setSpacing(8)

        dot = QLabel("●")
        dot.setStyleSheet(f"color: {_TEXT_SECONDARY}; font-size: 10px;")
        badge_layout.addWidget(dot)

        self.status_text = QLabel("CAMERA OFFLINE")
        self.status_text.setStyleSheet(f"color: {_TEXT_SECONDARY}; font-size: 12px; font-weight: 700; letter-spacing: 1.2px;")
        badge_layout.addWidget(self.status_text)

        top.addWidget(badge_frame)
        top.addStretch()

        self.timer = CameraTimer()
        top.addWidget(self.timer)

        layout.addLayout(top)

        # Center viewport area
        viewport = QFrame()
        viewport.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        vp_layout = QVBoxLayout(viewport)
        vp_layout.setContentsMargins(0, 0, 0, 0)

        # Overlay reticle grid
        reticle = QFrame()
        reticle.setFixedSize(595, 670)
        reticle.setStyleSheet("""
            background: transparent;
            border: none;
        """)
        reticle.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        rl = QVBoxLayout(reticle)
        rl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Center square
        center = QFrame()
        center.setFixedSize(256, 256)
        center.setStyleSheet(f"border: 1px solid {_GRID_COLOR}; border-radius: 4px; background: transparent;")
        rl.addWidget(center, alignment=Qt.AlignmentFlag.AlignCenter)

        # Status overlay
        self.status_overlay = StatusMessage()
        vp_layout.addWidget(self.status_overlay, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(viewport, 1)

        # Bottom: Controls
        controls = QFrame()
        controls.setFixedHeight(50)
        ctrl_layout = QHBoxLayout(controls)
        ctrl_layout.setContentsMargins(0, 0, 0, 0)

        self.start_btn = QPushButton("  Start Camera")
        self.start_btn.setObjectName("startCamBtn")
        self.start_btn.setStyleSheet(f"""
            #startCamBtn {{
                background: {_BRAND};
                border: none;
                border-radius: 4px;
                color: {_WHITE};
                font-size: 14px;
                font-weight: 600;
                padding: 10px 24px;
            }}
            #startCamBtn:hover {{ background: #002b6a; }}
        """)
        self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ctrl_layout.addWidget(self.start_btn)
        ctrl_layout.addStretch()

        self.capture_btn = QPushButton("  Capture & Recognize")
        self.capture_btn.setObjectName("captureBtn")
        self.capture_btn.setStyleSheet(f"""
            #captureBtn {{
                background: transparent;
                border: 1px solid {_BORDER};
                border-radius: 4px;
                color: {_BTN_SECONDARY_TEXT};
                font-size: 14px;
                font-weight: 600;
                padding: 9px 24px;
            }}
            #captureBtn:hover {{ background: {_BRAND_LIGHT}; }}
        """)
        self.capture_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ctrl_layout.addWidget(self.capture_btn)

        layout.addWidget(controls)


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

        heading = QLabel("Live Feed")
        heading.setStyleSheet(f"color: {_TEXT_PRIMARY}; font-size: 20px; font-weight: 600;")
        heading_layout.addWidget(heading)
        heading_layout.addStretch()

        refresh_dot = QLabel("⟳")
        refresh_dot.setStyleSheet(f"color: {_TEXT_MUTED}; font-size: 14px;")
        heading_layout.addWidget(refresh_dot)

        layout.addWidget(heading_frame)

        # Initial state area
        initial = QFrame()
        initial_layout = QVBoxLayout(initial)
        initial_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        initial_layout.setContentsMargins(16, 40, 16, 40)

        icon = QLabel("👤")
        icon.setStyleSheet("font-size: 48px;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        initial_layout.addWidget(icon)
        initial_layout.addSpacing(16)

        self.result_title = QLabel("Waiting for\nrecognition...")
        self.result_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_title.setStyleSheet(f"color: {_TEXT_PRIMARY}; font-size: 24px; font-weight: 600;")
        initial_layout.addWidget(self.result_title)
        initial_layout.addSpacing(8)

        self.result_desc = QLabel("Position subject within the frame and\ninitiate capture to process biometric\ndata.")
        self.result_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_desc.setStyleSheet(f"color: {_TEXT_SECONDARY}; font-size: 14px; line-height: 20px;")
        initial_layout.addWidget(self.result_desc)

        layout.addWidget(initial, 1)

        # Recent scans section
        recent_frame = QFrame()
        recent_frame.setObjectName("recentSection")
        recent_frame.setStyleSheet(f"border-top: 1px solid {_BORDER};")

        recent_layout = QVBoxLayout(recent_frame)
        recent_layout.setContentsMargins(16, 12, 16, 16)

        recent_label = QLabel("RECENT SCANS")
        recent_label.setStyleSheet(f"color: {_TEXT_SECONDARY}; font-size: 12px; font-weight: 700; letter-spacing: 0.6px;")
        recent_layout.addWidget(recent_label)
        recent_layout.addSpacing(8)

        scan_time = QLabel("--:--:--")
        scan_time.setStyleSheet(f"color: {_TEXT_MUTED}; font-family: 'JetBrains Mono'; font-size: 13px;")
        recent_layout.addWidget(scan_time)

        scan_name = QLabel("Awaiting data...")
        scan_name.setStyleSheet(f"color: {_TEXT_MUTED}; font-size: 13px;")
        recent_layout.addWidget(scan_name)

        layout.addWidget(recent_frame)


class CheckinPage(BasePage):
    """人脸打卡页 — 左摄像头 + 右识别结果，对齐 Figma。"""

    def setup_ui(self):
        self.setObjectName("checkinPage")
        self.setStyleSheet("background: transparent;")

        root = QVBoxLayout(self)
        root.setContentsMargins(32, 32, 32, 0)
        root.setSpacing(0)

        # ── Header ──
        header = QFrame()
        header.setFixedHeight(68)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        left_col = QVBoxLayout()
        left_col.setContentsMargins(0, 0, 0, 0)
        left_col.setSpacing(0)

        title = QLabel("Face Check-in")
        title.setStyleSheet(f"color: {_TEXT_PRIMARY}; font-size: 32px; font-weight: 700; letter-spacing: -0.64px;")
        left_col.addWidget(title)

        subtitle = QLabel("Real-time biometric attendance capture.")
        subtitle.setStyleSheet(f"color: {_TEXT_SECONDARY}; font-size: 16px;")
        left_col.addWidget(subtitle)
        header_layout.addLayout(left_col)
        header_layout.addStretch()

        # Course selector
        course_selector = QFrame()
        course_selector.setObjectName("courseSelector")
        course_selector.setStyleSheet(f"""
            #courseSelector {{
                background: {_WHITE};
                border: 1px solid {_BORDER};
                border-radius: 4px;
            }}
        """)
        cs_layout = QHBoxLayout(course_selector)
        cs_layout.setContentsMargins(16, 10, 40, 10)
        cs_layout.setSpacing(8)

        self.course_label = QLabel("CS101: Intro to Computer Science")
        self.course_label.setStyleSheet(f"color: {_TEXT_PRIMARY}; font-size: 14px;")
        cs_layout.addWidget(self.course_label)

        chevron = QLabel("▼")
        chevron.setStyleSheet(f"color: {_TEXT_SECONDARY}; font-size: 10px;")
        cs_layout.addWidget(chevron)

        header_layout.addWidget(course_selector)
        header_layout.addSpacing(12)

        # Logout button
        logout_btn = QPushButton("Logout")
        logout_btn.setObjectName("logoutInline")
        logout_btn.setStyleSheet(f"""
            #logoutInline {{
                background: transparent;
                border: 1px solid {_BORDER};
                border-radius: 4px;
                color: {_TEXT_SECONDARY};
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 0.6px;
                padding: 8px 16px;
            }}
            #logoutInline:hover {{ background: {_BRAND_LIGHT}; }}
        """)
        logout_btn.setFixedHeight(34)
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.clicked.connect(self._logout)
        header_layout.addWidget(logout_btn)

        root.addWidget(header)
        root.addSpacing(24)

        # ── Bento: Camera + Results ──
        bento = QHBoxLayout()
        bento.setContentsMargins(0, 0, 0, 0)
        bento.setSpacing(24)

        self.camera_viewport = CameraViewport()
        bento.addWidget(self.camera_viewport, 2)

        self.recognition_panel = RecognitionResults()
        bento.addWidget(self.recognition_panel, 1)

        root.addLayout(bento)
        root.addStretch(1)

    def bind(self):
        self.camera_viewport.start_btn.clicked.connect(self._toggle_camera)
        self.camera_viewport.capture_btn.clicked.connect(self._capture)

    def _toggle_camera(self):
        btn = self.camera_viewport.start_btn
        if btn.text().strip() == "Start Camera":
            btn.setText("  Stop Camera")
            btn.setStyleSheet(f"""
                #startCamBtn {{
                    background: #ba1a1a;
                    border: none;
                    border-radius: 4px;
                    color: {_WHITE};
                    font-size: 14px;
                    font-weight: 600;
                    padding: 10px 24px;
                }}
                #startCamBtn:hover {{ background: #8f1313; }}
            """)
            self.camera_viewport.status_text.setText("CAMERA ACTIVE")
            self.camera_viewport.status_text.setStyleSheet("color: #22c55e; font-size: 12px; font-weight: 700; letter-spacing: 1.2px;")
            self.camera_viewport.status_overlay.msg.setText("Live feed active")
            self.camera_viewport.timer.start()
        else:
            btn.setText("  Start Camera")
            btn.setStyleSheet(f"""
                #startCamBtn {{
                    background: {_BRAND};
                    border: none;
                    border-radius: 4px;
                    color: {_WHITE};
                    font-size: 14px;
                    font-weight: 600;
                    padding: 10px 24px;
                }}
                #startCamBtn:hover {{ background: #002b6a; }}
            """)
            self.camera_viewport.status_text.setText("CAMERA OFFLINE")
            self.camera_viewport.status_text.setStyleSheet(f"color: {_TEXT_SECONDARY}; font-size: 12px; font-weight: 700; letter-spacing: 1.2px;")
            self.camera_viewport.status_overlay.msg.setText("Click 'Start Camera' to begin")
            self.camera_viewport.timer.stop()

    def _capture(self):
        # TODO: wire real capture → update recognition panel
        pass

    def _logout(self):
        from app.core.event_bus import signal_bus
        from app.core.store import store
        store.token = ""
        store.user = None
        signal_bus.logout.emit()
