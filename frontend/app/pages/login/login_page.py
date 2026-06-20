"""LoginPage — 管理员登录页。"""
from __future__ import annotations

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import QLabel, QLineEdit, QPushButton, QVBoxLayout

from app.pages.base_page import BasePage
from app.services.auth_service import auth_service
from app.core.event_bus import signal_bus


class LoginWorker(QThread):
    """后台线程执行登录，避免阻塞 UI。"""
    finished = Signal(object)

    def __init__(self, username: str, password: str):
        super().__init__()
        self.username = username
        self.password = password

    def run(self):
        result = auth_service.login(self.username, self.password)
        self.finished.emit(result)


class LoginPage(BasePage):
    """全屏居中的登录卡片。"""

    def __init__(self, on_login_success=None, parent=None):
        self._on_login_success = on_login_success
        super().__init__(parent)

    def setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # TODO: 登录卡片布局
        # - 品牌 Logo + 标题
        # - 用户名输入框
        # - 密码输入框
        # - 登录按钮
        # - 状态提示文字

    def bind(self):
        # TODO: 连接信号
        pass
