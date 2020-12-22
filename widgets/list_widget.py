# _*_ coding:utf-8 _*_
# @File  : list_widget.py
# @Time  : 2020-12-18 13:17
# @Author: zizle
from PyQt5.QtWidgets import QListWidget


class ListWidget(QListWidget):
    def __init__(self, *args, **kwargs):
        super(ListWidget, self).__init__(*args, **kwargs)
