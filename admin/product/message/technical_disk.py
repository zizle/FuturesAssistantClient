# _*_ coding:utf-8 _*_
# @File  : technical_disk.py
# @Time  : 2020-12-23 09:08
# @Author: zizle

""" 技术解盘 """

from PyQt5.QtCore import QMargins, QDate
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QDateEdit, QLabel, QPushButton, QTableWidget, QFrame
from widgets import OptionWidget


class TechnicalDiskAdmin(QWidget):
    """ 技术解盘管理 """

    def __init__(self, *args, **kwargs):
        super(TechnicalDiskAdmin, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        option_widget = OptionWidget(self)
        option_layout = QHBoxLayout()
        option_layout.addWidget(QLabel('日期:', self))
        self.date_edit = QDateEdit(self)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat('yyyy-MM-dd')
        self.date_edit.setCalendarPopup(True)
        option_layout.addWidget(self.date_edit)

        self.query_button = QPushButton('查询', self)
        option_layout.addWidget(self.query_button)

        self.create_button = QPushButton('新建', self)
        option_layout.addWidget(self.create_button)

        option_layout.addStretch()

        option_widget.setLayout(option_layout)

        option_widget.setFixedHeight(45)
        layout.addWidget(option_widget)

        content = QWidget(self)
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(QMargins(5, 0, 5, 5))

        self.table = QTableWidget(self)
        self.table.setShowGrid(False)
        self.table.setFrameShape(QFrame.NoFrame)
        content_layout.addWidget(self.table)

        content.setLayout(content_layout)

        layout.addWidget(content)

        self.setLayout(layout)

        """ 逻辑部分 """



