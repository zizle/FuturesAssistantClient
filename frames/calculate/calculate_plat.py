# _*_ coding:utf-8 _*_
# @File  : calculate_plat.py
# @Time  : 2020-11-16 14:58
# @Author: zizle
from PyQt5.QtWidgets import QTreeWidgetItem, QTreeWidget, QWidget, QHBoxLayout, QSplitter, QMainWindow, QLabel
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt
from gglobal import rate
from apis.caculate_plat import ExchangeRateAPI
from .variety_calculate import FinanceCalculate, FarmCalculate, ChemicalCalculate, MetalCalculate
from .variety_arbitrage import VarietyArbitrage
from .duration_arbitrage import DurationArbitrage
from .spot_arbitrage import SpotArbitrage
from .correlation import CorrelationWidget
from .unit_transform import UnitTransform


class MenuTreeWidget(QTreeWidget):
    def __init__(self, *args, **kwargs):
        super(MenuTreeWidget, self).__init__(*args, **kwargs)
        self.header().hide()
        self.setFocusPolicy(Qt.NoFocus)
        self.setColumnCount(1)
        self.setIndentation(0)
        self.setObjectName('menuTree')
        self.setStyleSheet("#menuTree{border:none;border-right: 1px solid rgba(50,50,50,100)}"
                           "#menuTree::item:hover{color:rgb(0,164,172);}"
                           "#menuTree::item{height:28px;}"
                           )

    def mouseDoubleClickEvent(self, event, *args, **kwargs):
        event.accept()


class CalculatePlatUi(QWidget):
    def __init__(self, *args, **kwargs):
        super(CalculatePlatUi, self).__init__(*args, **kwargs)
        layout = QHBoxLayout()
        layout.setContentsMargins(2,2,2,2)
        main_splitter = QSplitter(self)
        self.menu_tree = MenuTreeWidget(self)
        main_splitter.addWidget(self.menu_tree)
        main_splitter.setHandleWidth(1)
        self.frame_loader = QMainWindow(self)
        main_splitter.addWidget(self.frame_loader)
        main_splitter.setSizes([self.width() * 0.18, self.width() * 0.82])
        layout.addWidget(main_splitter)
        self.setLayout(layout)
        self.menu_tree.setFocusPolicy(Qt.NoFocus)
        self.menu_tree.setObjectName("menuTree")
        self.setStyleSheet("#menuTree{border:none;border-right: 1px solid rgba(50,50,50,100)}"
                           "#menuTree::item:hover{background-color:rgba(0,255,0,50)}"
                           "#menuTree::item:selected{background-color:rgba(255,0,0,100)}"
                           "#menuTree::item{height:28px;}"
                           )


class CalculatePlat(CalculatePlatUi):
    def __init__(self, *args, **kwargs):
        super(CalculatePlat, self).__init__(*args, **kwargs)
        menus = [
            {"id": 1, "name": "套利计算", "icon": "media/icons/arbitrage.png", "children": [
                {"id": "1_1", "name": "跨品种套利", "icon": "media/icons/point.png"},
                {"id": "1_2", "name": "跨期套利", "icon": "media/icons/point.png"},
                {"id": "1_3", "name": "期现套利", "icon": "media/icons/point.png"},
            ]},
            {"id": 2, "name": "品种计算", "icon": "media/icons/arbitrage.png", "children": [
                {"id": "2_1", "name": "金融股指", "icon": "media/icons/point.png"},
                {"id": "2_2", "name": "农副产品", "icon": "media/icons/point.png"},
                {"id": "2_3", "name": "能源化工", "icon": "media/icons/point.png"},
                {"id": "2_4", "name": "金属产业", "icon": "media/icons/point.png"},
            ]},
            # {"id": 2, "name": "套保计算", "children": None},
            # {"id": 3, "name": "交割计算", "children": None},

            {"id": 4, "name": "其他计算", "icon": "media/icons/arbitrage_others.png", "children": [
                {"id": '4_1', "name": "单位换算", "icon": "media/icons/point.png", "children": None},
                {"id": '4_2', "name": "相关性计算", "icon": "media/icons/point.png", "children": None},
            ]},
        ]
        bold_font = QFont()
        bold_font.setBold(True)
        for menu_item in menus:
            top_level_item = QTreeWidgetItem(self.menu_tree)
            top_level_item.setText(0, menu_item["name"])
            setattr(top_level_item, "menu_id", menu_item["id"])
            top_level_item.setIcon(0, QIcon(menu_item['icon']))
            top_level_item.setFont(0, bold_font)
            # 添加子菜单
            self.menu_tree.addTopLevelItem(top_level_item)
            if menu_item["children"] is not None:
                for children_item in menu_item["children"]:
                    child = QTreeWidgetItem(top_level_item)
                    child.setText(0, children_item["name"])
                    setattr(child, "menu_id", children_item["id"])
                    child.setIcon(0, QIcon(children_item['icon']))
                    top_level_item.addChild(child)

        self.menu_tree.expandAll()
        # 按钮菜单点击事件
        self.menu_tree.itemClicked.connect(self.user_selected_menu)

        self.rate_api = ExchangeRateAPI(self)
        self.rate_api.exchange_rate_reply.connect(self.set_exchange_rate_data)
        self.rate_api.get_exchange_rate()

    def set_exchange_rate_data(self, data):
        """ 设置汇率数据 """
        rate.set_exchange_rate(data['rates'])
        self.set_default_page()

    def set_default_page(self):
        page = FinanceCalculate(self)
        self.frame_loader.setCentralWidget(page)

    def user_selected_menu(self, item):
        """ 用户选择菜单 """
        if not item.parent() and item.childCount():  # 点击父级展开
            item.setExpanded(not item.isExpanded())
            return
        menu_id = getattr(item, "menu_id")
        if menu_id == "1_1":  # 跨品种套利
            page = VarietyArbitrage(self)
        elif menu_id == "1_2":  # 跨期套利
            page = DurationArbitrage(self)
        elif menu_id == "1_3":  # 期现套利
            page = SpotArbitrage(self)
        elif menu_id == '2_1':
            page = FinanceCalculate(self)
        elif menu_id == '2_2':
            page = FarmCalculate(self)
        elif menu_id == '2_3':
            page = ChemicalCalculate(self)
        elif menu_id == '2_4':
            page = MetalCalculate(self)
        elif menu_id == '4_1':
            page = UnitTransform(self)
        elif menu_id == '4_2':
            page = CorrelationWidget(self)
        else:
            page = QLabel('暂未开放', self)
        self.frame_loader.setCentralWidget(page)

