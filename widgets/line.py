# _*_ coding:utf-8 _*_
# @File  : line.py
# @Time  : 2020-12-18 13:50
# @Author: zizle
from PyQt5.QtWidgets import QFrame
from PyQt5.QtCore import Qt


class HorizontalSepLine(QFrame):
    def __init__(self, *args):
        super(HorizontalSepLine, self).__init__(*args)
        self.setLineWidth(2)
        self.setFrameStyle(QFrame.HLine | QFrame.Plain)
        self.setStyleSheet('color:rgb(228,228,228)')


class VerticalSepLine(QFrame):
    def __init__(self, *args):
        super(VerticalSepLine, self).__init__(*args)
        self.setLineWidth(2)
        self.setFrameStyle(QFrame.VLine | QFrame.Plain)
        self.setStyleSheet('color:rgb(228,228,228)')
