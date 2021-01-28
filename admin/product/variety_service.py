# _*_ coding:utf-8 _*_
# @File  : variety_service.py
# @Time  : 2020-12-17 08:43
# @Author: zizle
""" 后台管理 - 产品服务 - 品种服务"""
from PyQt5.QtWidgets import QSplitter, QLabel
from PyQt5.QtCore import Qt
from .abstract import ProductServiceAdmin
from .variety import IntroductionAdmin, RuleAdmin


class VarietyServiceAdmin(ProductServiceAdmin):
    """ 主管理窗口 """
    MENUS = [
        {"id": 1, "name": "品种介绍"},
        {"id": 2, "name": "制度规则"},
    ]

    def selected_menu(self, item):
        """ 选择菜单 """
        menu_id = item.data(Qt.UserRole)
        if menu_id == 1:
            page = IntroductionAdmin(self)
        elif menu_id == 2:
            page = RuleAdmin(self)
        else:
            page = QLabel('暂未开放', self)
        self.frame_container.setCentralWidget(page)
