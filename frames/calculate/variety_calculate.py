# _*_ coding:utf-8 _*_
# @File  : variety_calculate.py
# @Time  : 2020-11-17 09:33
# @Author: zizle

""" 品种计算 """
import os
import json
from PyQt5.QtWidgets import qApp, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QGraphicsDropShadowEffect
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtNetwork import QNetworkRequest
from PyQt5.QtCore import Qt, QUrl, QMargins
from PyQt5.QtGui import QColor
from settings import SERVER_API, BASE_DIR


class TitleOptionWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(TitleOptionWidget, self).__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_StyledBackground, True)  # 必须设置,如果不设置将导致子控件产生阴影
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setOffset(0, 1)
        shadow.setColor(QColor(100, 100, 100))
        shadow.setBlurRadius(5)
        self.setGraphicsEffect(shadow)
        self.setObjectName("optionWidget")
        self.setStyleSheet("#optionWidget{background-color:rgb(245,245,245)}")


class VarietyCalculateUI(QWidget):
    def __init__(self, *args, **kwargs):
        super(VarietyCalculateUI, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        layout.setSpacing(5)
        option_layout = QHBoxLayout()
        option_layout.setContentsMargins(QMargins(5, 5, 2, 5))
        self.variety_group_combobox = QComboBox(self)
        option_layout.addWidget(self.variety_group_combobox)

        self.variety_combobox = QComboBox(self)
        option_layout.addWidget(self.variety_combobox)

        self.enter_button = QPushButton("确定", self)
        option_layout.addWidget(self.enter_button)
        option_layout.addStretch()

        title_option_widget = TitleOptionWidget(self)
        title_option_widget.setLayout(option_layout)

        layout.addWidget(title_option_widget)
        self.web_container = QWebEngineView(self)
        layout.addWidget(self.web_container)
        self.setLayout(layout)


class VarietyCalculate(VarietyCalculateUI):
    def __init__(self, *args, **kwargs):
        super(VarietyCalculate, self).__init__(*args, **kwargs)
        self.network_manger = getattr(qApp, "_network")
        self.variety_group_combobox.currentTextChanged.connect(self.get_group_variety)
        # 添加品种分组
        for group_item in [
            {"group_id": "finance", "group_name": "金融股指"},
            {"group_id": "farm", "group_name": "农副产品"},
            {"group_id": "chemical", "group_name": "能源化工"},
            {"group_id": "metal", "group_name": "金属产业"},
        ]:
            self.variety_group_combobox.addItem(group_item["group_name"], group_item["group_id"])

        self.enter_button.clicked.connect(self.enter_variety_calculate)

    def get_group_variety(self):
        """ 获取组下品种 """

        current_group = self.variety_group_combobox.currentData()
        url = SERVER_API + 'variety/?group={}'.format(current_group)
        reply = self.network_manger.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(self.group_variety_reply)

    def group_variety_reply(self):
        """ 获取到组下的品种 """
        reply = self.sender()
        self.variety_combobox.clear()
        if reply.error():
            pass
        else:
            data = reply.readAll().data().decode("utf8")
            data = json.loads(data)
            for variety_item in data["varieties"]:
                self.variety_combobox.addItem(variety_item["variety_name"], variety_item["variety_en"])
            self.variety_combobox.setMinimumWidth(100)
        reply.deleteLater()

    def enter_variety_calculate(self):
        """ 当前品种改变 """
        current_variety = self.variety_combobox.currentData()
        if not current_variety:
            return
        # 显示对应的计算公式界面
        file_path = os.path.join(BASE_DIR, 'classini/formulas.json')
        with open(file_path, "r", encoding="utf-8") as f:
            support_list = json.load(f)
        if current_variety in support_list:
            page_file = "file:///pages/formulas/variety/calculate_{}.html".format(current_variety)
        else:
            page_file = "file:///pages/formulas/variety/no_found.html"
        self.web_container.load(QUrl(page_file))
