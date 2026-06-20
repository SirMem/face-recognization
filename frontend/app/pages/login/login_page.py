"""LoginPage — 管理员登录页。"""
from __future__ import annotations

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

from app.core.event_bus import signal_bus
from app.core.store import store
from app.core.theme import COLORS_LIGHT, FONT
from app.pages.base_page import BasePage
from app.services.api_client import ApiClient, ApiResult
from app.services.auth_service import auth_service


class LoginWorker(QThread):
    """后台线程执行登录，避免阻塞 UI。"""
    result_ready = Signal(object)

    def __init__(self, username: str, password: str):
        super().__init__()
        self.username = username
        self.password = password

    def run(self):
        try:
            result = ApiClient(auth_service.base_url)._request(
                "POST",
                "/auth/login",
                json={"username": self.username, "password": self.password},
                timeout=3,
            )
            result = ApiClient._handle(result)
        except Exception:
            result = ApiResult(ok=False, message="登录失败，请稍后重试")
        self.result_ready.emit(result)


class LoginPage(BasePage):
    """全屏居中的登录卡片。"""

    def __init__(self, on_login_success=None, parent=None):
        self._on_login_success = on_login_success
        self._worker: LoginWorker | None = None
        self._closing = False
        super().__init__(parent)

    def setup_ui(self):
        colors = COLORS_LIGHT
        accent = colors["primary_hover"]  # selected Figma node uses the darker brand token

        self.setWindowTitle("VisionAttend Admin Terminal")
        self.setObjectName("loginPage")
        self.setMinimumSize(720, 560)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(24)
        outer.addStretch(1)

        card = QFrame()
        card.setObjectName("loginCard")
        card.setFixedWidth(440)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        accent_bar = QFrame()
        accent_bar.setObjectName("loginAccent")
        accent_bar.setFixedHeight(4)
        card_layout.addWidget(accent_bar)

        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(32, 28, 32, 32)
        body_layout.setSpacing(0)

        logo = QLabel("VA")
        logo.setObjectName("loginLogo")
        logo.setFixedSize(64, 64)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        body_layout.addWidget(logo, alignment=Qt.AlignmentFlag.AlignHCenter)
        body_layout.addSpacing(16)

        title = QLabel("VisionAttend")
        title.setObjectName("loginTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        body_layout.addWidget(title)

        subtitle = QLabel("Admin Terminal")
        subtitle.setObjectName("loginSubtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        body_layout.addWidget(subtitle)
        body_layout.addSpacing(24)

        self.username_input = self._input_field(body_layout, "Username", "Enter administrator ID", "👤")
        body_layout.addSpacing(16)
        self.password_input = self._input_field(body_layout, "Password", "••••••••", "🔒", password=True)
        body_layout.addSpacing(24)

        self.login_btn = QPushButton("Login to Terminal  →")
        self.login_btn.setObjectName("loginSubmit")
        self.login_btn.setFixedHeight(40)
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        body_layout.addWidget(self.login_btn)

        self.status_lbl = QLabel("")
        self.status_lbl.setObjectName("loginStatus")
        self.status_lbl.setTextFormat(Qt.TextFormat.PlainText)
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_lbl.setWordWrap(True)
        self.status_lbl.hide()
        body_layout.addSpacing(8)
        body_layout.addWidget(self.status_lbl)

        card_layout.addWidget(body)
        outer.addWidget(card, alignment=Qt.AlignmentFlag.AlignHCenter)
        outer.addStretch(1)

        self.setStyleSheet(f"""
            #loginPage {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {colors['surface_card']}, stop: 1 {colors['surface_container_low']});
            }}
            #loginCard {{
                background: {colors['surface_card']};
                border: 1px solid #c3c6d6;
                border-radius: 8px;
            }}
            #loginAccent {{
                background: {accent};
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }}
            #loginLogo {{
                background: #e7eeff;
                border: 1px solid #dfe8ff;
                border-radius: 8px;
                color: {accent};
                font-size: 20px;
                font-weight: 700;
            }}
            #loginTitle {{
                color: {accent};
                font-family: {FONT['family']};
                font-size: 24px;
                font-weight: 700;
            }}
            #loginSubtitle {{
                color: #5c5f60;
                font-size: 14px;
            }}
            #loginLabel {{
                color: #091c35;
                font-size: 14px;
                font-weight: 600;
            }}
            #inputShell {{
                background: {colors['surface_page']};
                border: 1px solid #c3c6d6;
                border-radius: 4px;
            }}
            #inputIcon {{
                color: #737685;
                font-size: 14px;
            }}
            QLineEdit#loginInput {{
                background: transparent;
                border: none;
                color: #091c35;
                padding: 0;
                font-size: 14px;
            }}
            QLineEdit#loginInput:focus {{
                border: none;
            }}
            #loginSubmit {{
                background: {accent};
                border: none;
                border-radius: 4px;
                color: {colors['text_on_primary']};
                font-size: 14px;
                font-weight: 600;
            }}
            #loginSubmit:hover {{ background: {colors['primary']}; }}
            #loginSubmit:disabled {{
                background: #c3c6d6;
                color: #737685;
            }}
            #loginStatus {{
                color: {colors['danger']};
                font-size: 12px;
            }}
            #loginStatus[ok="true"] {{ color: {colors['success']}; }}
        """)

    def _input_field(self, parent_layout: QVBoxLayout, label: str, placeholder: str, icon: str, *, password: bool = False) -> QLineEdit:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)

        label_lbl = QLabel(label)
        label_lbl.setObjectName("loginLabel")
        row.addWidget(label_lbl)
        row.addStretch(1)
        parent_layout.addLayout(row)
        parent_layout.addSpacing(4)

        shell = QFrame()
        shell.setObjectName("inputShell")
        shell.setFixedHeight(40)
        shell_layout = QHBoxLayout(shell)
        shell_layout.setContentsMargins(12, 0, 12, 0)
        shell_layout.setSpacing(12)

        icon_lbl = QLabel(icon)
        icon_lbl.setObjectName("inputIcon")
        icon_lbl.setFixedWidth(16)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        shell_layout.addWidget(icon_lbl)

        field = QLineEdit()
        field.setObjectName("loginInput")
        field.setPlaceholderText(placeholder)
        if password:
            field.setEchoMode(QLineEdit.EchoMode.Password)
        shell_layout.addWidget(field)
        parent_layout.addWidget(shell)
        return field

    def bind(self):
        self.login_btn.clicked.connect(self._login)
        self.username_input.returnPressed.connect(self.password_input.setFocus)
        self.password_input.returnPressed.connect(self._login)

    def refresh(self):
        pass

    def _login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        if not username or not password:
            self._set_status("请输入用户名和密码")
            return

        self._set_busy(True)
        self._set_status("正在登录...", ok=True)
        worker = LoginWorker(username, password)
        worker.result_ready.connect(self._handle_result)
        worker.finished.connect(worker.deleteLater)
        worker.finished.connect(self._worker_finished)
        self._worker = worker
        worker.start()

    def _handle_result(self, result):
        if self._closing:
            return
        self._set_busy(False)
        if result.ok:
            data = result.data if isinstance(result.data, dict) else {}
            token = data.get("access_token")
            if not token:
                self._set_status("登录响应缺少令牌")
                return
            store.token = token
            store.user = data.get("user")
            auth_service.set_token(token)
            self._set_status("登录成功", ok=True)
            signal_bus.login_success.emit(data)
            if self._on_login_success:
                self._on_login_success(data)
            return

        self._set_status(result.message or "登录失败")
        self.password_input.selectAll()
        self.password_input.setFocus()

    def _set_busy(self, busy: bool):
        self.username_input.setDisabled(busy)
        self.password_input.setDisabled(busy)
        self.login_btn.setDisabled(busy)
        self.login_btn.setText("Logging in..." if busy else "Login to Terminal  →")

    def _worker_finished(self):
        self._worker = None

    def closeEvent(self, event):
        self._closing = True
        if self._worker and self._worker.isRunning():
            try:
                self._worker.result_ready.disconnect(self._handle_result)
            except RuntimeError:
                pass
            self._worker.wait()
        super().closeEvent(event)

    def _set_status(self, text: str, *, ok: bool = False):
        self.status_lbl.setText(text)
        self.status_lbl.setProperty("ok", ok)
        self.status_lbl.style().unpolish(self.status_lbl)
        self.status_lbl.style().polish(self.status_lbl)
        self.status_lbl.setVisible(bool(text))
