# _*_ coding:utf-8 _*_
# @File  : regular_report_ui.py
# @Time  : 2020-10-27 13:13
# @Author: zizle
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, QComboBox, QTableWidget, QHeaderView, QFrame,
                             QAbstractItemView, QPushButton)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QBrush, QColor
from utils.constant import VERTICAL_SCROLL_STYLE, HORIZONTAL_SCROLL_STYLE, HORIZONTAL_HEADER_STYLE
from widgets.paginator import Paginator


class ReportTable(QTableWidget):
    def __init__(self, *args, **kwargs):
        super(ReportTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()
        self.setEditTriggers(QHeaderView.NoEditTriggers)
        self.setFrameShape(QFrame.NoFrame)
        self.setFocusPolicy(Qt.NoFocus)
        self.setAlternatingRowColors(True)
        # 不能选中
        self.setSelectionMode(QAbstractItemView.NoSelection)
        # 背景透明
        table_palette = self.palette()
        table_palette.setBrush(QPalette.Base, QBrush(QColor(255, 255, 255, 0)))
        self.setPalette(table_palette)
        self.setCursor(Qt.PointingHandCursor)
        self.verticalScrollBar().setStyleSheet(VERTICAL_SCROLL_STYLE)
        self.horizontalScrollBar().setStyleSheet(HORIZONTAL_SCROLL_STYLE)

        # 设置鼠标进入整行颜色变化
        self.setMouseTracking(True)
        self.mouse_last_row = -1
        self.last_row_background = None
        self.itemEntered.connect(self.mouse_enter_item)

        self.horizontalHeader().setStyleSheet(HORIZONTAL_HEADER_STYLE)

    def mouse_enter_item(self, item):
        current_row = self.row(item)
        # 改变当前行的颜色
        for col in range(self.columnCount()):
            self.item(current_row, col).setForeground(QBrush(QColor(248, 121, 27)))
            self.item(current_row, col).setBackground(QBrush(QColor(220, 220, 220)))
        # 恢复离开行的颜色
        self.recover_row_color()
        self.mouse_last_row = current_row

    def recover_row_color(self):
        if self.mouse_last_row >= 0:
            for col in range(self.columnCount()):
                self.item(self.mouse_last_row, col).setForeground(QBrush(QColor(0, 0, 0)))
                self.item(self.mouse_last_row, col).setBackground(QBrush(QColor(245, 245, 245, 0)))  # 透明

    def leaveEvent(self, *args, **kwargs):
        """ 鼠标离开事件 """
        # 将最后记录行颜色变为原来的样子,且修改记录行为-1
        self.recover_row_color()
        self.mouse_last_row = -1


class RegularReportUI(QWidget):
    def __init__(self, *args, **kwargs):
        super(RegularReportUI, self).__init__(*args, **kwargs)
        main_layout = QVBoxLayout()
        opts_layout = QHBoxLayout()
        opts_layout.addWidget(QLabel("报告类型:", self))
        self.report_combobox = QComboBox(self)
        opts_layout.addWidget(self.report_combobox)

        opts_layout.addWidget(QLabel("相关品种:", self))
        self.variety_combobox = QComboBox(self)
        self.variety_combobox.setMinimumWidth(100)
        opts_layout.addWidget(self.variety_combobox)

        self.query_button = QPushButton("查询", self)
        opts_layout.addWidget(self.query_button)

        opts_layout.addStretch()
        self.paginator = Paginator()
        self.paginator.setParent(self)
        opts_layout.addWidget(self.paginator)
        main_layout.addLayout(opts_layout)
        # 表格
        self.report_table = ReportTable(self)
        main_layout.addWidget(self.report_table)

        self.setLayout(main_layout)
