# _*_ coding:utf-8 _*_
# @File  : variety_calculate.py
# @Time  : 2020-11-17 09:33
# @Author: zizle

""" 品种计算 """
import os
import json

from PyQt5.QtWidgets import qApp, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QGraphicsDropShadowEffect, \
    QStackedWidget, QScrollArea, QLabel, QFrame
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtNetwork import QNetworkRequest, QNetworkAccessManager
from PyQt5.QtCore import Qt, QUrl, QMargins
from PyQt5.QtGui import QColor
from settings import SERVER_API, BASE_DIR
from widgets import OptionWidget, GridWidget
from frames.calculate import variety_calculate_widgets as VCW


class VarietyButton(QPushButton):
    """ 选择品种的按钮 """
    def __init__(self, *args, **kwargs):
        super(VarietyButton, self).__init__(*args, **kwargs)
        self.setObjectName('varietyBtn')
        self.setFixedSize(66, 22)
        self.setCursor(Qt.PointingHandCursor)
        # self.setCheckable(True)
        self.setStyleSheet(
            "#varietyBtn{border:1px solid rgb(160,160,170)}"
            "#varietyBtn:hover{color:rgb(250,250,250);background-color:rgb(65,99,161)}"
            # "#varietyBtn:checked{background-color:rgb(0,164,172);color:rgb(250,250,250)}"
        )


class VarietyCalculate(QWidget):
    GROUP = None

    def __init__(self, *args, **kwargs):
        super(VarietyCalculate, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        self.option_widget = OptionWidget(self)
        self.variety_widget = GridWidget(self)
        option_layout = QVBoxLayout()
        option_layout.addWidget(self.variety_widget)
        self.option_widget.setLayout(option_layout)
        layout.addWidget(self.option_widget, alignment=Qt.AlignTop)

        self.calculate_widget = QScrollArea(self)
        self.calculate_widget.setWidgetResizable(True)
        self.calculate_widget.setFrameShape(QFrame.NoFrame)
        layout.addWidget(self.calculate_widget)

        self.network_manager = getattr(qApp, '_network', QNetworkAccessManager(self))
        self.get_current_varieties()
        self.setLayout(layout)

    def get_current_varieties(self):
        if not self.GROUP:
            return
        url = SERVER_API + 'variety/?group={}'.format(self.GROUP)
        reply = self.network_manager.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(self.group_variety_reply)

    def group_variety_reply(self):
        """ 获取到组下的品种 """
        reply = self.sender()
        if reply.error():
            pass
        else:
            data = reply.readAll().data().decode("utf8")
            data = json.loads(data)
            self.set_variety_widget(data['varieties'])

    def set_variety_widget(self, varieties):
        widgets_list = []
        for variety_item in varieties:
            if variety_item['variety_en'] not in self.include_variety():
                continue
            button = VarietyButton(variety_item['variety_name'])  # 不要设置parent父控件
            setattr(button, 'variety_en', variety_item['variety_en'])
            button.clicked.connect(self.selected_variety)
            widgets_list.append(button)
        self.variety_widget.set_widgets(66, widgets_list)
        # 初始化计算控件
        if len(widgets_list) > 0:
            variety_en = getattr(widgets_list[0], 'variety_en', None)
            if variety_en:
                self.set_calculate_widget(variety_en)

    def set_calculate_widget(self, variety_en):
        if not getattr(VCW, variety_en, None):
            c_widget = QLabel('该品种还没有计算公式!')
            c_widget.setAlignment(Qt.AlignCenter)
            c_widget.setStyleSheet('font-size:20px;color:#ff6433;font-weight:bold')
        else:
            c_widget = getattr(VCW, variety_en)()
        self.calculate_widget.setWidget(c_widget)

    def selected_variety(self):
        btn = self.sender()
        variety_en = getattr(btn, 'variety_en')
        self.set_calculate_widget(variety_en)

    def include_variety(self):
        return []


class FinanceCalculate(VarietyCalculate):
    GROUP = 'finance'

    def include_variety(self):
        return ['GZ']


class FarmCalculate(VarietyCalculate):
    GROUP = 'farm'

    def include_variety(self):
        return ['A', 'AP', 'C', 'CF', 'CJ', 'JD', 'P', 'LH', 'PM', 'RS', 'SR']


class ChemicalCalculate(VarietyCalculate):
    GROUP = 'chemical'

    def include_variety(self):
        return ['EB', 'EG', 'FU', 'PF', 'PG', 'SC', 'SP', 'L', 'MA', 'PP', 'RU', 'TA', 'V']


class MetalCalculate(VarietyCalculate):
    GROUP = 'metal'

    def include_variety(self):
        return ['AL', 'CU', 'HC', 'NI', 'PB', 'RB', 'SF', 'SM', 'SN', 'SS', 'J', 'I', 'ZN']


# class TitleOptionWidget(QWidget):
#     def __init__(self, *args, **kwargs):
#         super(TitleOptionWidget, self).__init__(*args, **kwargs)
#         self.setAttribute(Qt.WA_StyledBackground, True)  # 必须设置,如果不设置将导致子控件产生阴影
#         shadow = QGraphicsDropShadowEffect(self)
#         shadow.setOffset(0, 1)
#         shadow.setColor(QColor(100, 100, 100))
#         shadow.setBlurRadius(5)
#         self.setGraphicsEffect(shadow)
#         self.setObjectName("optionWidget")
#         self.setStyleSheet("#optionWidget{background-color:rgb(245,245,245)}")
#
#
# class VarietyCalculateUI(QWidget):
#     def __init__(self, *args, **kwargs):
#         super(VarietyCalculateUI, self).__init__(*args, **kwargs)
#         layout = QVBoxLayout()
#         layout.setContentsMargins(QMargins(0, 0, 0, 0))
#         layout.setSpacing(5)
#         option_layout = QHBoxLayout()
#         option_layout.setContentsMargins(QMargins(5, 5, 2, 5))
#         self.variety_group_combobox = QComboBox(self)
#         option_layout.addWidget(self.variety_group_combobox)
#
#         self.variety_combobox = QComboBox(self)
#         option_layout.addWidget(self.variety_combobox)
#
#         self.enter_button = QPushButton("确定", self)
#         option_layout.addWidget(self.enter_button)
#         option_layout.addStretch()
#
#         title_option_widget = TitleOptionWidget(self)
#         title_option_widget.setLayout(option_layout)
#         title_option_widget.setFixedHeight(42)
#         layout.addWidget(title_option_widget)
#
#         content_layout = QVBoxLayout()
#         self.variety_stacked = QStackedWidget(self)
#         self.formula_area = QScrollArea(self)
#         content_layout.addWidget(self.variety_stacked, alignment=Qt.AlignTop)
#         content_layout.addWidget(self.formula_area)
#
#         layout.addLayout(content_layout)
#         # self.web_container = QWebEngineView(self)
#         # layout.addWidget(self.web_container)
#         self.setLayout(layout)
#
#
# class VarietyCalculate(VarietyCalculateUI):
#     def __init__(self, *args, **kwargs):
#         super(VarietyCalculate, self).__init__(*args, **kwargs)
#         self.network_manger = getattr(qApp, "_network")
#         self.variety_group_combobox.currentTextChanged.connect(self.get_group_variety)
#         # 添加品种分组
#         for group_item in [
#             {"group_id": "finance", "group_name": "金融股指"},
#             {"group_id": "farm", "group_name": "农副产品"},
#             {"group_id": "chemical", "group_name": "能源化工"},
#             {"group_id": "metal", "group_name": "金属产业"},
#         ]:
#             self.variety_group_combobox.addItem(group_item["group_name"], group_item["group_id"])
#
#         self.enter_button.clicked.connect(self.enter_variety_calculate)
#
#     def get_group_variety(self):
#         """ 获取组下品种 """
#
#         current_group = self.variety_group_combobox.currentData()
#         url = SERVER_API + 'variety/?group={}'.format(current_group)
#         reply = self.network_manger.get(QNetworkRequest(QUrl(url)))
#         reply.finished.connect(self.group_variety_reply)
#
#     def group_variety_reply(self):
#         """ 获取到组下的品种 """
#         reply = self.sender()
#         self.variety_combobox.clear()
#         if reply.error():
#             pass
#         else:
#             data = reply.readAll().data().decode("utf8")
#             data = json.loads(data)
#             for variety_item in data["varieties"]:
#                 self.variety_combobox.addItem(variety_item["variety_name"], variety_item["variety_en"])
#             self.variety_combobox.setMinimumWidth(100)
#         reply.deleteLater()
#
#
#
#     def enter_variety_calculate(self):
#         """ 当前品种改变 """
#         current_variety = self.variety_combobox.currentData()
#         if not current_variety:
#             return
#         # 显示对应的计算公式界面
#         file_path = os.path.join(BASE_DIR, 'classini/formulas.json')
#         with open(file_path, "r", encoding="utf-8") as f:
#             support_list = json.load(f)
#         if current_variety in support_list:
#             page_file = "file:///pages/formulas/variety/calculate_{}.html".format(current_variety)
#         else:
#             page_file = "file:///pages/formulas/variety/no_found.html"
#         self.web_container.load(QUrl(page_file))
