"""DataTable — 通用表格组件。

封装 QTableWidget 的常见配置：列头、交替色、只读、选中行。
"""
from __future__ import annotations

from PySide6.QtWidgets import QHeaderView, QTableWidget


class DataTable(QTableWidget):
    """通用数据表格，统一表格样式和行为。"""

    def __init__(self, columns: list[str], parent=None):
        super().__init__(parent)
        self.setColumnCount(len(columns))
        self.setHorizontalHeaderLabels(columns)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)
        self.setObjectName("dataTable")

    def set_data(self, rows: list[list[str]]):
        """批量填充数据。rows 是二维列表。"""
        self.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                self.setItem(r, c, QTableWidgetItem(str(val)))
