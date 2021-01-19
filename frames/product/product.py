# _*_ coding:utf-8 _*_
# @File  : product.py
# @Time  : 2020-09-15 11:01
# @Author: zizle
""" 产品服务主页面 """

from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout, QSplitter, QMainWindow, QTreeWidgetItem
from PyQt5.QtCore import Qt, QMargins
from PyQt5.QtGui import QFont, QIcon
from widgets import TreeWidget
from .message_service import ShortMessage, RegularReport, SpecialReport, ResearchReport, TechnicalDisk
from .consultant import PersonTrain, Organization, Examine


class ProductPage(QWidget):
    def __init__(self, *args, **kwargs):
        super(ProductPage, self).__init__(*args, **kwargs)
        """ UI部分 """
        layout = QHBoxLayout()
        layout.setContentsMargins(QMargins(0, 0, 2, 2))
        main_splitter = QSplitter(self)
        # 左侧菜单
        self.menu_tree = TreeWidget(self)
        main_splitter.addWidget(self.menu_tree)
        # 右侧显示窗口
        self.right_frame = QMainWindow(self)
        main_splitter.addWidget(self.right_frame)

        main_splitter.setSizes([self.parent().width() * 0.18, self.parent().width() * 0.82])

        main_splitter.setHandleWidth(1)
        layout.addWidget(main_splitter)
        self.setLayout(layout)

        """ 逻辑部分 """
        self.add_menus()
        # 按钮菜单点击事件
        self.menu_tree.itemClicked.connect(self.user_selected_menu)

    def add_menus(self):
        # 添加左侧菜单
        menus = [
            {"menu_id": "1", "menu_name": "资讯服务", "icon": "media/icons/product/message.png", "children": [
                {"menu_id": "1_1", "menu_name": "短信通", "icon": "media/icons/point.png"},
                {"menu_id": "1_2", "menu_name": "定期报告", "icon": "media/icons/point.png"},
                {"menu_id": "1_3", "menu_name": "专题研究", "icon": "media/icons/point.png"},
                {"menu_id": "1_4", "menu_name": "调研报告", "icon": "media/icons/point.png"},
                {"menu_id": "1_5", "menu_name": "市场路演", "icon": "media/icons/point.png"},
                {"menu_id": "1_6", "menu_name": "技术解盘", "icon": "media/icons/point.png"}
            ]},
            {"menu_id": "2", "menu_name": "顾问服务", "icon": "media/icons/product/consultant.png","children": [
                {"menu_id": "2_1", "menu_name": "人才培养", "icon": "media/icons/point.png"},
                {"menu_id": "2_2", "menu_name": "部门组建", "icon": "media/icons/point.png"},
                {"menu_id": "2_3", "menu_name": "制度考核", "icon": "media/icons/point.png"}
            ]},
            {"menu_id": "3", "menu_name": "策略服务", "icon": "media/icons/product/strategy.png", "children": [
                {"menu_id": "3_1", "menu_name": "交易策略", "icon": "media/icons/point.png"},
                {"menu_id": "3_2", "menu_name": "投资方案", "icon": "media/icons/point.png"},
                {"menu_id": "3_3", "menu_name": "套保方案", "icon": "media/icons/point.png"},
            ]},
            {"menu_id": "4", "menu_name": "品种基础", "icon": "media/icons/product/variety.png", "children": [
                {"menu_id": "4_1", "menu_name": "品种介绍", "icon": "media/icons/point.png"},
                {"menu_id": "4_2", "menu_name": "制度规则", "icon": "media/icons/point.png"}
            ]},

        ]
        bold_font = QFont()
        bold_font.setBold(True)
        for menu_item in menus:
            top_item = QTreeWidgetItem(self.menu_tree)
            top_item.setText(0, menu_item['menu_name'])
            setattr(top_item, 'menu_id', menu_item['menu_id'])
            top_item.setIcon(0, QIcon(menu_item['icon']))
            top_item.setFont(0, bold_font)
            self.menu_tree.addTopLevelItem(top_item)
            for children_item in menu_item["children"]:
                child = QTreeWidgetItem(top_item)
                setattr(child, 'menu_id', children_item['menu_id'])
                child.setText(0, children_item['menu_name'])
                child.setIcon(0, QIcon(children_item['icon']))
                top_item.addChild(child)

    def user_selected_menu(self, item):
        if not item.parent() and item.childCount():  # 点击父级展开
            item.setExpanded(not item.isExpanded())
            return
        menu_id = getattr(item, "menu_id")
        menu_text = item.text(0)
        if menu_id == "1_1":  # 短信通
            page = ShortMessage(self)
        elif menu_id == "1_2":
            page = RegularReport(self)
        elif menu_id == "1_3":
            page = SpecialReport(self)
        elif menu_id == "1_4":
            page = ResearchReport(self)
        elif menu_id == "1_6":
            page = TechnicalDisk(self)
        elif menu_id == '2_1':
            try:
                page = PersonTrain(self)
            except Exception as e:
                print(e)
        elif menu_id == '2_2':
            page = Organization(self)
        elif menu_id == '2_3':
            page = Examine(self)
        else:
            page = QLabel("「" + menu_text + "」正在研发中···\n更多资讯请访问【首页】查看.")
            page.setStyleSheet('font-size:16px;font-weight:bold;color:rgb(230,50,50)')
            page.setAlignment(Qt.AlignCenter)
        self.right_frame.setCentralWidget(page)
