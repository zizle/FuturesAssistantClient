# _*_ coding:utf-8 _*_
# @File  : calculate_plat.py
# @Time  : 2020-11-16 14:58
# @Author: zizle
from PyQt5.QtWidgets import QTreeWidgetItem, QLabel
from .calculate_plat_ui import CalculatePlatUi
from .variety_calculate import VarietyCalculate
from .variety_arbitrage import VarietyArbitrage
from .duration_arbitrage import DurationArbitrage
from .spot_arbitrage import SpotArbitrage
from .correlation import CorrelationWidget


class CalculatePlat(CalculatePlatUi):
    def __init__(self, *args, **kwargs):
        super(CalculatePlat, self).__init__(*args, **kwargs)
        menus = [
            {"id": 1, "name": "套利计算", "children": [
                {"id": "1_1", "name": "跨品种套利"},
                {"id": "1_2", "name": "跨期套利"},
                {"id": "1_3", "name": "期现套利"},
            ]},
            # {"id": 2, "name": "套保计算", "children": None},
            # {"id": 3, "name": "交割计算", "children": None},

            {"id": 4, "name": "其他计算", "children": [
                {"id": '4_1', "name": "品种计算", "children": None},
                {"id": '4_2', "name": "相关性计算", "children": None},
            ]},
        ]

        for menu_item in menus:
            top_level_item = QTreeWidgetItem(self.menu_tree)
            top_level_item.setText(0, menu_item["name"])
            setattr(top_level_item, "menu_id", menu_item["id"])
            # 添加子菜单
            if menu_item["children"] is not None:
                for children_item in menu_item["children"]:
                    child = QTreeWidgetItem(top_level_item)
                    child.setText(0, children_item["name"])
                    setattr(child, "menu_id", children_item["id"])
                    top_level_item.addChild(child)
            self.menu_tree.addTopLevelItem(top_level_item)

        # 按钮菜单点击事件
        self.menu_tree.itemClicked.connect(self.user_selected_menu)

    def user_selected_menu(self, item):
        """ 用户选择菜单 """
        try:
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
            elif menu_id == "4_1":
                page = VarietyCalculate(self)
            elif menu_id == '4_2':
                page = CorrelationWidget(self)
            else:
                return
            self.frame_loader.setCentralWidget(page)
        except Exception as e:
            print(e)
