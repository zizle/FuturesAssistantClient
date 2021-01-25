# _*_ coding:utf-8 _*_
# @File  : plan_file.py
# @Time  : 2021-01-20 10:46
# @Author: zizle

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFormLayout, QLineEdit, QTableWidget)
from widgets import OptionWidget, FilePathLineEdit
from PyQt5.QtCore import QMargins, Qt
from gglobal import variety


class CreateWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(CreateWidget, self).__init__(*args, **kwargs)
        layout = QFormLayout()
        self.file_edit = FilePathLineEdit(self)
        self.title_edit = QLineEdit(self)

        layout.addRow("文件:", self.file_edit)
        layout.addRow("标题:", self.title_edit)
        self.setLayout(layout)


class PlanFileAdmin(QWidget):
    def __init__(self, *args, **kwargs):
        super(PlanFileAdmin, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        option_widget = OptionWidget(self)
        option_layout = QHBoxLayout()
        self.manager_button = QPushButton('管理', self)
        self.create_button = QPushButton('新建', self)
        option_layout.addWidget(self.manager_button)
        option_layout.addWidget(self.create_button)
        option_layout.addStretch()
        option_widget.setLayout(option_layout)
        layout.addWidget(option_widget)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(8, 5, 8, 5)
        self.table = QTableWidget(self)
        content_layout.addWidget(self.table)
        self.create_widget = CreateWidget(self)
        content_layout.addWidget(self.create_widget)
        layout.addLayout(content_layout)
        self.setLayout(layout)
