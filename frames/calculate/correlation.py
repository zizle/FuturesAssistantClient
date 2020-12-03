# _*_ coding:utf-8 _*_
# @File  : correlation.py
# @Time  : 2020-12-03 16:54
# @Author: zizle

""" 相关性计算 """

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt


class CorrelationWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(CorrelationWidget, self).__init__(*args, **kwargs)
        """ UI部分 """
        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel('暂未开放', self, alignment=Qt.AlignCenter))
        self.setLayout(main_layout)

        """ 业务部分 """
