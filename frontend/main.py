"""VisionAttend — 人脸识别考勤系统 PySide6 前端入口。"""
from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.core.theme import theme_manager
from app.core.router import Router
from app.core.event_bus import signal_bus
from app.pages.dashboard.dashboard_page import DashboardPage
from app.pages.checkin.checkin_page import CheckinPage
from app.pages.attendance.attendance_page import AttendancePage
from app.pages.students.student_page import StudentPage
from app.pages.courses.course_page import CoursePage


class BrandHeader(QFrame):
    """左侧品牌栏 — VisionAttend + ADMIN TERMINAL"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(64)
        self.setObjectName("brandHeader")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 10, 24, 11)

        logo = QLabel("V")
        logo.setObjectName("brandLogo")
        logo.setFixedSize(32, 32)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)

        col = QVBoxLayout()
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(0)
        title = QLabel("VisionAttend")
        title.setObjectName("brandTitle")
        subtitle = QLabel("ADMIN TERMINAL")
        subtitle.setObjectName("brandSubtitle")
        col.addWidget(title)
        col.addWidget(subtitle)
        layout.addLayout(col)
        layout.addStretch()


class Sidebar(QFrame):
    """左侧导航栏 260px"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(260)
        self.setObjectName("sidebar")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Brand
        layout.addWidget(BrandHeader())

        # Nav tabs
        nav = QFrame()
        nav.setObjectName("navContainer")
        nav_layout = QVBoxLayout(nav)
        nav_layout.setContentsMargins(8, 16, 8, 16)
        nav_layout.setSpacing(4)

        self._nav_btns: dict[str, QPushButton] = {}
        for name in ["Dashboard", "Check-in", "Records", "Students", "Courses"]:
            btn = QPushButton(name)
            btn.setObjectName("navButton")
            btn.setProperty("active", name == "Dashboard")
            btn.setFixedHeight(44)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            self._nav_btns[name] = btn
            nav_layout.addWidget(btn)
        nav_layout.addStretch()
        layout.addWidget(nav, 1)

        # Footer profile
        footer = QFrame()
        footer.setObjectName("sidebarFooter")
        footer.setFixedHeight(90)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(16, 17, 16, 16)

        avatar = QLabel("AU")
        avatar.setObjectName("userAvatar")
        avatar.setFixedSize(32, 32)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_layout.addWidget(avatar)

        col = QVBoxLayout()
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(0)
        uname = QLabel("Admin User")
        uname.setObjectName("userName")
        urole = QLabel("System Administrator")
        urole.setObjectName("userRole")
        col.addWidget(uname)
        col.addWidget(urole)
        footer_layout.addLayout(col)
        footer_layout.addStretch()

        layout.addWidget(footer)

    def set_active(self, name: str):
        for k, btn in self._nav_btns.items():
            active = k == name
            btn.setProperty("active", active)
            btn.style().unpolish(btn)
            btn.style().polish(btn)


class TopHeader(QFrame):
    """顶部顶栏 64px — 只保留 Logout（右对齐）"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(64)
        self.setObjectName("topHeader")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(32, 0, 32, 0)
        layout.addStretch(1)

        self.logout_btn = QPushButton("Logout")
        self.logout_btn.setObjectName("logoutBtn")
        self.logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.logout_btn)


class MainWindow(QWidget):
    """主窗口 — 侧栏(260) + 顶栏(64) + 内容区"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("VisionAttend - 人脸识别考勤系统")
        self.setMinimumSize(1280, 800)
        self.setObjectName("mainWindow")

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Left sidebar
        self.sidebar = Sidebar()
        root.addWidget(self.sidebar)

        # Right area: header + content
        right = QVBoxLayout()
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(0)

        self.header = TopHeader()
        right.addWidget(self.header)

        self.content = QStackedWidget()
        self.content.setObjectName("mainContent")
        right.addWidget(self.content, 1)

        root.addLayout(right, 1)

        # ── Router ──
        self._router = Router(self.content)
        self._router.register("dashboard", DashboardPage)
        self._router.register("checkin", CheckinPage)
        self._router.register("attendance", AttendancePage)
        self._router.register("students", StudentPage)
        self._router.register("courses", CoursePage)

        # Map sidebar label → route name
        _route_map = {
            "Dashboard": "dashboard",
            "Check-in": "checkin",
            "Records": "attendance",
            "Students": "students",
            "Courses": "courses",
        }
        # Reverse: route → sidebar label — built from the map above
        _label_of = {v: k for k, v in _route_map.items()}

        # ── Wire sidebar nav buttons ──
        for label, route in _route_map.items():
            btn = self.sidebar._nav_btns[label]
            btn.clicked.connect(lambda _r=route: self._router.navigate(_r))

        # ── Highlight active nav on route change ──
        self._router.page_changed.connect(
            lambda name: self.sidebar.set_active(_label_of.get(name, name))
        )

        # ── Global navigate signal → router ──
        signal_bus.navigate_requested.connect(self._router.navigate)

        # ── Logout → back to login ──
        self.header.logout_btn.clicked.connect(self._logout)

        # ── Start on dashboard ──
        self._router.navigate("dashboard")

        self._apply_styles()

    def _logout(self):
        from app.pages.login.login_page import LoginPage
        self.close()
        w = LoginPage(
            lambda data: (
                w.close(),
                MainWindow().show(),
            )
        )
        w.resize(600, 480)
        w.show()

    def _apply_styles(self):
        self.setStyleSheet("""
            #mainWindow {
                background: #ffffff;
            }
            #sidebar {
                background: #ffffff;
                border-right: 1px solid #c3c6d6;
            }
            #brandHeader {
                border-bottom: 1px solid #c3c6d6;
            }
            #brandLogo {
                background: #003d9b;
                border-radius: 2px;
                color: #ffffff;
                font-size: 16px;
                font-weight: 700;
            }
            #brandTitle {
                color: #003d9b;
                font-size: 20px;
                font-weight: 700;
                letter-spacing: -0.5px;
            }
            #brandSubtitle {
                color: #5c5f60;
                font-family: 'JetBrains Mono';
                font-size: 10px;
                letter-spacing: 0.5px;
            }
            #navButton {
                background: transparent;
                border: 1px solid transparent;
                border-radius: 4px;
                color: #5c5f60;
                font-size: 16px;
                font-weight: 400;
                padding: 10px 12px;
                text-align: left;
            }
            #navButton:hover {
                background: #dae2ff;
                color: #003d9b;
            }
            #navButton[active="true"] {
                background: #dae2ff;
                border: 1px solid #003d9b;
                color: #003d9b;
                font-weight: 700;
            }
            #sidebarFooter {
                border-top: 1px solid #c3c6d6;
            }
            #userAvatar {
                background: #495a81;
                border-radius: 12px;
                color: #ffffff;
                font-size: 16px;
            }
            #userName {
                color: #091c35;
                font-size: 16px;
                font-weight: 600;
            }
            #userRole {
                color: #5c5f60;
                font-family: 'JetBrains Mono';
                font-size: 11px;
            }
            #topHeader {
                background: #f9f9ff;
                border-bottom: 1px solid #c3c6d6;
            }
            #logoutBtn {
                background: #003d9b1a;
                border: none;
                border-radius: 4px;
                color: #003d9b;
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 0.6px;
                padding: 8px 16px;
            }
            #logoutBtn:hover {
                background: #003d9b33;
            }
            #mainContent {
                background: #f9f9ff;
            }
        """)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("VisionAttend")

    theme_manager.apply(app, "dark")

    from app.pages.login.login_page import LoginPage

    main_window: MainWindow | None = None

    def on_login_success(_login_data):
        nonlocal main_window
        login_window.close()
        main_window = MainWindow()
        main_window.show()

    login_window = LoginPage(on_login_success)
    login_window.resize(600, 480)
    login_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
