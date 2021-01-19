# _*_ coding:utf-8 _*_
# @File  : consultant_service.py
# @Time  : 2020-12-17 08:40
# @Author: zizle
""" 后台管理 - 产品服务 - 顾问服务"""
from PyQt5.QtWidgets import QLabel

from .abstract import ProductServiceAdmin, Qt
from .consultant import PersonTrain, OrganizationCreated, ExamineChecked


class ConsultantServiceAdmin(ProductServiceAdmin):
    MENUS = [
        {"id": 1, "name": "人才培养"},
        {"id": 2, "name": "部门组建"},
        {"id": 3, "name": "制度考核"},
    ]

    def selected_menu(self, item):
        """ 选择菜单 """
        menu_id = item.data(Qt.UserRole)
        if menu_id == 1:
            page = PersonTrain(self)
        elif menu_id == 2:
            page = OrganizationCreated(self)
        elif menu_id == 3:
            page = ExamineChecked(self)
        else:
            page = QLabel('暂未开放', self)
        self.frame_container.setCentralWidget(page)
