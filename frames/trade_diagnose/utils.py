# _*_ coding:utf-8 _*_
# @File  : utils.py
# @Time  : 2021-03-30 16:50
# @Author: zizle
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QFont
from PyQt5.QtWidgets import QFrame


def set_table_style(table_list):
    font = QFont()
    font.setPointSize(10)
    for table in table_list:
        table.horizontalHeader().setDefaultSectionSize(128)
        table.setFont(font)
        table.setFrameShape(QFrame.NoFrame)
        table.setFocusPolicy(Qt.NoFocus)
        table.verticalHeader().hide()
        table.setBackgroundRole(QPalette.Foreground)
        table.setStyleSheet('background-color:#2b2b2b')
        table.verticalScrollBar().setStyleSheet('background-color:#fff')
        table.horizontalScrollBar().setStyleSheet('background-color:#fff')
        table.horizontalHeader().setStyleSheet(
            "QHeaderView::section{background-color: #a0cfcf;"
            "border:1px solid rgb(60,60,60);border-left:none;"
            "min-height:25px;min-width:40px;font-weight:bold;color:#0000ff};"
        )