# _*_ coding:utf-8 _*_
# @File  : message_service.py
# @Time  : 2020-12-17 08:34
# @Author: zizle

""" 后台管理 - 产品服务 - 资讯服务"""
from .abstract import ProductServiceAdmin, Qt
from .message.shortmsg import ShortMsgAdmin
from .message.report import ReportFileAdmin


class MessageServiceAdmin(ProductServiceAdmin):
    MENUS = [
        {"id": 1, "name": "短信通"},
        {"id": 2, "name": "报告管理"},
        {"id": 3, "name": "市场路演"},
        {"id": 4, "name": "技术解盘"},
    ]

    def selected_menu(self, item):
        """ 选择菜单 """
        menu_id = item.data(Qt.UserRole)
        print(menu_id)
        if menu_id == 1:
            page = ShortMsgAdmin(self)
        elif menu_id == 2:
            page = ReportFileAdmin(self)
        else:
            return
        self.frame_container.setCentralWidget(page)

