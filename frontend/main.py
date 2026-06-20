"""VisionAttend — 人脸识别考勤系统 PySide6 前端入口。"""
from __future__ import annotations

import os
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from app.core.theme import theme_manager
from app.core.router import Router
from app.core.store import store
from app.core.event_bus import signal_bus
from app.pages.dashboard.dashboard_page import DashboardPage
from app.pages.login.login_page import LoginPage


class MainWindow(QWidget):
    """主窗口：NavigationInterface + QStackedWidget。

    使用 qfluentwidgets 的 NavigationInterface 实现侧栏导航。
    页面向导通过 Router 管理。
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("VisionAttend - 人脸识别考勤系统")
        self.setMinimumSize(1280, 800)
        self.setObjectName("mainWindow")

        # 布局
        # TODO: NavigationInterface + QStackedWidget
        # - 参考 qfluentwidgets 的 FluentWindow 或自定义实现
        # - 注册 5 个导航项（Dashboard / Check-in / Records / Students / Courses）
        # - 底部用户信息

    def _init_navigation(self):
        # TODO: 使用 NavigationInterface 添加导航项
        pass

    def _init_routes(self):
        # TODO: Router.register("dashboard", DashboardPage)
        # TODO: Router.register("checkin", CheckinPage)
        # TODO: Router.register("attendance", AttendancePage)
        # TODO: Router.register("students", StudentPage)
        # TODO: Router.register("courses", CoursePage)
        pass


def main():
    # 高 DPI 支持
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("VisionAttend")

    # 应用主题
    theme_manager.apply(app, "dark")

    # 登录 → 主窗口流程
    def on_login_success(login_data):
        login_window.close()
        main_window = MainWindow()
        main_window.show()

    login_window = LoginPage(on_login_success)
    login_window.resize(600, 480)
    login_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
