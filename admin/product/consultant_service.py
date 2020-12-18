# _*_ coding:utf-8 _*_
# @File  : consultant_service.py
# @Time  : 2020-12-17 08:40
# @Author: zizle
""" 后台管理 - 产品服务 - 顾问服务"""
from .abstract import ProductServiceAdmin, Qt


class ConsultantServiceAdmin(ProductServiceAdmin):
    MENUS = []

    def selected_menu(self, item):
        """ 选择菜单 """
        menu_id = item.data(Qt.UserRole)
        print(menu_id)
