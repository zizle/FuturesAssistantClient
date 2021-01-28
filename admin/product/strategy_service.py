# _*_ coding:utf-8 _*_
# @File  : strategy_service.py
# @Time  : 2020-12-17 08:43
# @Author: zizle
""" 后台管理 - 产品服务 -策略服务"""
from PyQt5.QtWidgets import QWidget, QSplitter, QMainWindow, QLabel
from PyQt5.QtCore import Qt
from .abstract import ProductServiceAdmin
from .strategy import ExchangeStrategy, PlanFileAdmin


class StrategyServiceAdmin(ProductServiceAdmin):
    MENUS = [
        {"id": 1, "name": "交易策略"},
        {"id": 2, "name": "方案管理"},
    ]

    def selected_menu(self, item):
        """ 选择菜单 """
        menu_id = item.data(Qt.UserRole)
        if menu_id == 1:
            page = ExchangeStrategy(self)
        elif menu_id == 2:
            page = QLabel('到产品服务 - 资讯服务 - 报告管理 中进行维护!', self)
            page.setAlignment(Qt.AlignCenter)
        else:
            page = QLabel('暂未开放', self)
        self.frame_container.setCentralWidget(page)