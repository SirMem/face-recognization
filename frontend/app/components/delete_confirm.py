"""DeleteConfirm — 通用删除确认弹窗。"""
from __future__ import annotations

from PySide6.QtWidgets import QMessageBox


def confirm_delete(parent, title: str = "确认删除", message: str = "确定删除？此操作不可撤销。") -> bool:
    """显示删除确认对话框。返回 True=用户确认删除。"""
    reply = QMessageBox.question(
        parent, title, message,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
    )
    return reply == QMessageBox.StandardButton.Yes
