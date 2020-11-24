# _*_ coding:utf-8 _*_
# @File  : variety_arbitrage.py
# @Time  : 2020-11-17 11:18
# @Author: zizle
""" 跨期套利 """

import json
from PyQt5.QtWidgets import (qApp, QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QComboBox,
                             QGraphicsDropShadowEffect, QPushButton)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import Qt, QMargins, QUrl, QEventLoop
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


class DurationArbitrageUi(QWidget):
    def __init__(self, *args, **kwargs):
        super(DurationArbitrageUi, self).__init__(*args, **kwargs)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(QMargins(0, 0, 0, 0))
        main_layout.setSpacing(5)
        option_widget = OptionWidget(self)
        option_layout = QGridLayout()
        option_layout.setContentsMargins(QMargins(5, 5, 2, 5))
        option_layout.setAlignment(Qt.AlignLeft)
        title_layout = QHBoxLayout()
        page_title = QLabel("跨期套利", self)
        page_title.setFixedHeight(23)
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

        # 隐藏品种2
        # option_layout.addWidget(QLabel("品种:", self), 2, 0)
        self.variety_bottom = QComboBox(self)
        self.variety_bottom.setMinimumWidth(100)
        self.variety_bottom.hide()
        option_layout.addWidget(self.variety_bottom, 2, 1)

        option_layout.addWidget(QLabel("合约:", self), 2, 2)
        self.contract_bottom = QComboBox(self)
        option_layout.addWidget(self.contract_bottom, 2, 3)

        self.start_calculate_button = QPushButton("开始计算", self)
        option_layout.addWidget(self.start_calculate_button, 2, 5)

        self.three_month_button = QPushButton("近3月", self)
        setattr(self.three_month_button, "day_count", 90)
        self.six_month_button = QPushButton("近6月", self)
        setattr(self.six_month_button, "day_count", 180)
        self.one_year_button = QPushButton("近1年", self)
        setattr(self.one_year_button, "day_count", 360)
        option_layout.addWidget(self.three_month_button, 2, 6)
        option_layout.addWidget(self.six_month_button, 2, 7)
        option_layout.addWidget(self.one_year_button, 2, 8)

        option_widget.setLayout(option_layout)
        option_widget.setFixedHeight(90)

        main_layout.addWidget(option_widget)

        self.web_container = QWebEngineView(self)
        self.web_container.load(QUrl("file:///html/charts/arbitrage_chart.html"))  # 加载页面
        # self.web_container.setContentsMargins(QMargins(5, 5, 0, 5))
        # 设置与页面信息交互的通道
        channel_qt_obj = QWebChannel(self.web_container.page())  # 实例化qt信道对象,必须传入页面参数
        self.contact_channel = ArbitrageChannel()  # 页面信息交互通道
        self.web_container.page().setWebChannel(channel_qt_obj)
        channel_qt_obj.registerObject("pageContactChannel", self.contact_channel)  # 信道对象注册信道，只能注册一个
        event_loop = QEventLoop(self)  # 同步加载页面
        self.web_container.loadFinished.connect(event_loop.quit)
        event_loop.exec_()
        main_layout.addWidget(self.web_container)
        self.setLayout(main_layout)

        page_title.setObjectName("pageTitle")
        self.initial_styles()

    def initial_styles(self):
        self.three_month_button.setObjectName("monthButton")
        self.six_month_button.setObjectName("monthButton")
        self.one_year_button.setObjectName("monthButton")
        self.three_month_button.setCursor(Qt.PointingHandCursor)
        self.six_month_button.setCursor(Qt.PointingHandCursor)
        self.one_year_button.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(
            "#pageTitle{background-color:rgb(91,155,210);color:rgb(250,250,250);padding:3px 5px}"
            "#monthButton{background-color:rgb(250,250,250);border-radius: 7px;"
            "font-size:12px;color:rgb(120,120,120);padding:4px 6px}"
        )
        self.three_month_button.setStyleSheet("background-color:rgb(191,211,249);color:rgb(78,110,242)")


class DurationArbitrage(DurationArbitrageUi):
    def __init__(self, *args, **kwargs):
        super(DurationArbitrage, self).__init__(*args, **kwargs)
        self.day_count = 90  # 默认为3个月
        self.network_manager = getattr(qApp, "_network")
        # 品种下拉信号
        self.variety_top.currentTextChanged.connect(self.top_variety_changed)
        # 获取所有品种
        self.get_all_variety()
        # 品种下拉信号
        # self.variety_bottom.currentTextChanged.connect(self.bottom_variety_changed)
        # 开始计算的信号
        self.start_calculate_button.clicked.connect(self.get_arbitrage_contract_data)

        # 数据范围选择
        self.three_month_button.clicked.connect(self.day_count_selected)
        self.six_month_button.clicked.connect(self.day_count_selected)
        self.one_year_button.clicked.connect(self.day_count_selected)

    def day_count_selected(self):
        button = self.sender()
        day_count = getattr(button, "day_count")
        if day_count:
            self.change_button_style(day_count)
            self.day_count = day_count
        self.get_arbitrage_contract_data()

    def change_button_style(self, day_count):
        if day_count <= 90:
            self.three_month_button.setStyleSheet("background-color:rgb(191,211,249);color:rgb(78,110,242)")
            self.six_month_button.setStyleSheet("background-color:rgb(250,250,250);color:rgb(120,120,120)")
            self.one_year_button.setStyleSheet("background-color:rgb(250,250,250);color:rgb(120,120,120)")
        elif day_count <= 180:
            self.six_month_button.setStyleSheet("background-color:rgb(191,211,249);color:rgb(78,110,242)")
            self.three_month_button.setStyleSheet("background-color:rgb(250,250,250);color:rgb(120,120,120)")
            self.one_year_button.setStyleSheet("background-color:rgb(250,250,250);color:rgb(120,120,120)")
        else:
            self.one_year_button.setStyleSheet("background-color:rgb(191,211,249);color:rgb(78,110,242)")
            self.three_month_button.setStyleSheet("background-color:rgb(250,250,250);color:rgb(120,120,120)")
            self.six_month_button.setStyleSheet("background-color:rgb(250,250,250);color:rgb(120,120,120)")

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
        self.contract_bottom.clear()
        reply = self.sender()
        if reply.error():
            pass
        else:
            data = json.loads(reply.readAll().data().decode("utf8"))
            for contract_item in data["contracts"]:
                self.contract_top.addItem(contract_item["contract"])
                self.contract_bottom.addItem(contract_item["contract"])
            # 将合约设置为第二个
            if self.contract_bottom.count() >= 1:
                self.contract_bottom.setCurrentIndex(1)
        reply.deleteLater()
        self.get_arbitrage_contract_data()

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
            'variety_2': self.variety_top.currentData(),
            'contract_1': self.contract_top.currentText(),
            'contract_2': self.contract_bottom.currentText(),
            'day_count': self.day_count
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
            # 将数据传入界面出图
            self.contact_channel.chartSource.emit(json.dumps(data["data"]), json.dumps(data["base_option"]))









