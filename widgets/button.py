# _*_ coding:utf-8 _*_
# @File  : button.py
# @Time  : 2020-12-03 13:15
# @Author: zizle
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon


class OperateButton(QPushButton):
    """ 表格操作按钮 """
    def __init__(self, icon_path, hover_icon_path, *args):
        super(OperateButton, self).__init__(*args)
        self.icon_path = icon_path
        self.hover_icon_path = hover_icon_path
        self.setCursor(Qt.PointingHandCursor)
        self.setIcon(QIcon(self.icon_path))
        self.setObjectName("operateButton")
        self.setStyleSheet("#operateButton{border:none}#operateButton:hover{color:#d81e06}")

    def enterEvent(self, *args, **kwargs):
        self.setIcon(QIcon(self.hover_icon_path))

    def leaveEvent(self, *args, **kwargs):
        self.setIcon(QIcon(self.icon_path))