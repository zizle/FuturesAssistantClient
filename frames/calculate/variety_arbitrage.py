# _*_ coding:utf-8 _*_
# @File  : variety_arbitrage.py
# @Time  : 2020-11-17 11:18
# @Author: zizle
""" 跨品种套利 """
import json
from PyQt5.QtWidgets import (qApp, QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QComboBox,
                             QGraphicsDropShadowEffect, QPushButton)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import Qt, QMargins, QUrl
from PyQt5.QtGui import QColor
from PyQt5.QtNetwork import QNetworkRequest
from channels.chart import ArbitrageChannel
from settings import SERVER_API


class OptionWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(OptionWidget, self).__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_StyledBackground, True)  # 必须设置,如果不设置将导致子控件产生阴影
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setOffset(0, 1)
        shadow.setColor(QColor(100, 100, 100))
        shadow.setBlurRadius(5)
        self.setGraphicsEffect(shadow)
        self.setObjectName("optionWidget")
        self.setStyleSheet("#optionWidget{background-color:rgb(245,245,245)}")


class VarietyArbitrageUi(QWidget):
    def __init__(self, *args, **kwargs):
        super(VarietyArbitrageUi, self).__init__(*args, **kwargs)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(QMargins(0, 0, 0, 0))
        main_layout.setSpacing(5)
        option_widget = OptionWidget(self)
        option_layout = QGridLayout()
        option_layout.setContentsMargins(QMargins(5, 5, 2, 5))
        option_layout.setAlignment(Qt.AlignLeft)
        title_layout = QHBoxLayout()
        page_title = QLabel("跨品种套利", self)
        title_layout.addWidget(page_title)
        title_layout.addStretch()
        option_layout.addLayout(title_layout, 0, 0, 1, 6)

        option_layout.addWidget(QLabel("品种:", self), 1, 0)
        self.variety_top = QComboBox(self)
        self.variety_top.setMinimumWidth(100)
        option_layout.addWidget(self.variety_top, 1, 1)

        option_layout.addWidget(QLabel("合约:", self), 1, 2)
        self.contract_top = QComboBox(self)
        option_layout.addWidget(self.contract_top, 1, 3)

        option_layout.addWidget(QLabel("品种:", self), 2, 0)
        self.variety_bottom = QComboBox(self)
        self.variety_bottom.setMinimumWidth(100)
        option_layout.addWidget(self.variety_bottom, 2, 1)

        option_layout.addWidget(QLabel("合约:", self), 2, 2)
        self.contract_bottom = QComboBox(self)
        option_layout.addWidget(self.contract_bottom, 2, 3)

        self.start_calculate_button = QPushButton("开始计算", self)
        option_layout.addWidget(self.start_calculate_button, 2, 5)

        option_widget.setLayout(option_layout)

        main_layout.addWidget(option_widget)

        self.web_container = QWebEngineView(self)
        self.web_container.load(QUrl("file:///html/charts/arbitrage_chart.html"))  # 加载页面
        # self.web_container.setContentsMargins(QMargins(5, 5, 0, 5))
        # 设置与页面信息交互的通道
        channel_qt_obj = QWebChannel(self.web_container.page())  # 实例化qt信道对象,必须传入页面参数
        self.contact_channel = ArbitrageChannel()  # 页面信息交互通道
        self.web_container.page().setWebChannel(channel_qt_obj)
        channel_qt_obj.registerObject("pageContactChannel", self.contact_channel)  # 信道对象注册信道，只能注册一个

        main_layout.addWidget(self.web_container)
        self.setLayout(main_layout)

        page_title.setObjectName("pageTitle")
        self.setStyleSheet(
            "#pageTitle{background-color:rgb(91,155,210);color:rgb(250,250,250);padding:3px 5px}"
        )


class VarietyArbitrage(VarietyArbitrageUi):
    def __init__(self, *args, **kwargs):
        super(VarietyArbitrage, self).__init__(*args, **kwargs)
        self.network_manager = getattr(qApp, "_network")
        # 品种下拉信号
        self.variety_top.currentTextChanged.connect(self.top_variety_changed)
        # 获取所有品种
        self.get_all_variety()
        # 品种下拉信号
        self.variety_bottom.currentTextChanged.connect(self.bottom_variety_changed)
        # 开始计算的信号
        self.start_calculate_button.clicked.connect(self.get_arbitrage_contract_data)

    def get_all_variety(self):
        url = SERVER_API + "variety/all/?is_real=1"
        reply = self.network_manager.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(self.all_variety_reply)

    def all_variety_reply(self):
        reply = self.sender()
        self.variety_top.clear()
        self.variety_bottom.clear()
        if reply.error():
            pass
        else:
            data = json.loads(reply.readAll().data().decode('utf8'))
            for group_key in data["varieties"]:
                for variety_item in data["varieties"][group_key]:
                    self.variety_top.addItem(variety_item["variety_name"], variety_item["variety_en"])
                    self.variety_bottom.addItem(variety_item["variety_name"], variety_item["variety_en"])
        reply.deleteLater()

    def top_variety_changed(self):
        """ 请求品种合约 """
        top_variety = self.variety_top.currentData()
        url = SERVER_API + "{}/contract/".format(top_variety)
        reply = self.network_manager.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(self.top_contract_reply)

    def top_contract_reply(self):
        """ 合约返回 """
        self.contract_top.clear()
        reply = self.sender()
        if reply.error():
            pass
        else:
            data = json.loads(reply.readAll().data().decode("utf8"))
            for contract_item in data["contracts"]:
                self.contract_top.addItem(contract_item["contract"])

    def bottom_variety_changed(self):
        """ 请求品种合约 """
        bottom_variety = self.variety_bottom.currentData()
        url = SERVER_API + "{}/contract/".format(bottom_variety)
        reply = self.network_manager.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(self.bottom_contract_reply)

    def bottom_contract_reply(self):
        self.contract_bottom.clear()
        reply = self.sender()
        if reply.error():
            pass
        else:
            data = json.loads(reply.readAll().data().decode("utf8"))
            for contract_item in data["contracts"]:
                self.contract_bottom.addItem(contract_item["contract"])

    def get_arbitrage_contract_data(self):
        """ 获取两个品种的数据 """
        self.start_calculate_button.setEnabled(False)
        url = SERVER_API + "arbitrage/variety/"
        body_data = {
            'variety_1': self.variety_top.currentData(),
            'variety_2': self.variety_bottom.currentData(),
            'contract_1': self.contract_top.currentText(),
            'contract_2': self.contract_bottom.currentText()
        }
        reply = self.network_manager.post(QNetworkRequest(QUrl(url)), json.dumps(body_data).encode("utf8"))
        reply.finished.connect(self.arbitrage_contract_reply)

    def arbitrage_contract_reply(self):
        """ 获取套利计算的数据返回了 """
        self.start_calculate_button.setEnabled(True)
        reply = self.sender()
        if reply.error():
            pass
        else:
            data = json.loads(reply.readAll().data().decode("utf8"))
            print(data)
            # 将数据传入界面出图
            try:
                self.contact_channel.chartSource.emit(json.dumps(data["data"]), json.dumps(data["base_option"]))
            except Exception as e:
                print(e)









