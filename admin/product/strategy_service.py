# _*_ coding:utf-8 _*_
# @File  : strategy_service.py
# @Time  : 2020-12-17 08:43
# @Author: zizle
""" 后台管理 - 产品服务 -策略服务"""
from PyQt5.QtWidgets import QWidget, QSplitter, QMainWindow
from widgets import TreeWidget


class MessageService(QSplitter):
    """ 主管理窗口 """
    def __init__(self, *args):
        super(MessageService, self).__init__(*args)