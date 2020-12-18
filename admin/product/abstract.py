# _*_ coding:utf-8 _*_
# @File  : abstract.py
# @Time  : 2020-12-18 13:30
# @Author: zizle

from PyQt5.QtCore import QMargins
from PyQt5.QtWidgets import QWidget, QSplitter, QMainWindow, QHBoxLayout, QListWidgetItem
from PyQt5.QtCore import Qt
from widgets import ListWidget


class ProductServiceAdmin(QWidget):
    """ 主管理窗口 """
    MENUS = []

    def __init__(self, *args):
        super(ProductServiceAdmin, self).__init__(*args)
        layout = QHBoxLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        splitter = QSplitter(self)
        # 左侧菜单
        self.menu_list = ListWidget(self)
        splitter.addWidget(self.menu_list)
        # 右侧显示容器
        self.frame_container = QMainWindow(self)
        splitter.addWidget(self.frame_container)
        splitter.setSizes([self.parent().width() * 0.18, self.parent().width() * 0.82])
        layout.addWidget(splitter)
        self.setLayout(layout)

        self.add_admin_menus()

        self.menu_list.itemClicked.connect(self.selected_menu)

    def add_admin_menus(self):
        """ 添加菜单 """
        for menu_item in self.MENUS:
            item = QListWidgetItem(menu_item['name'])
            item.setData(Qt.UserRole, menu_item["id"])
            self.menu_list.addItem(item)

    def selected_menu(self, item):
        """ 选择菜单 """
        pass


