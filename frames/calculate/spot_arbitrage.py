# _*_ coding:utf-8 _*_
# @File  : variety_arbitrage.py
# @Time  : 2020-11-17 11:18
# @Author: zizle
""" 期现套利 """

import json
from PyQt5.QtWidgets import (qApp, QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QComboBox, QPushButton,
                             QTableWidget, QSplitter, QTableWidgetItem, QHeaderView)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import Qt, QMargins, QUrl, QEventLoop
from PyQt5.QtNetwork import QNetworkRequest
from channels.chart import ArbitrageChannel
from utils.constant import BLUE_STYLE_HORIZONTAL_STYLE, VERTICAL_SCROLL_STYLE
from widgets import OptionWidget, ChartViewWidget
from settings import SERVER_API


class SpotArbitrageUi(QWidget):
    TITLE_WIDGET_HEIGHT = 90

    def __init__(self, *args, **kwargs):
        super(SpotArbitrageUi, self).__init__(*args, **kwargs)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(QMargins(0, 0, 0, 0))
        main_layout.setSpacing(5)
        option_widget = OptionWidget(self)
        option_layout = QGridLayout()
        option_layout.setContentsMargins(QMargins(5, 5, 2, 5))
        option_layout.setAlignment(Qt.AlignLeft)
        title_layout = QHBoxLayout()
        page_title = QLabel("期现套利", self)
        page_title.setFixedHeight(23)
        title_layout.addWidget(page_title)
        title_layout.addStretch()
        option_layout.addLayout(title_layout, 0, 0, 1, 6)

        option_layout.addWidget(QLabel("现货:", self), 1, 0)
        self.variety_top = QComboBox(self)
        self.variety_top.setMinimumWidth(100)
        option_layout.addWidget(self.variety_top, 1, 1)

        option_layout.addWidget(QLabel("合约:", self), 2, 2)
        self.contract_top = QComboBox(self)
        self.contract_top.hide()
        option_layout.addWidget(self.contract_top, 1, 3)

        option_layout.addWidget(QLabel("期货:", self), 2, 0)
        self.variety_bottom = QComboBox(self)
        self.variety_bottom.setMinimumWidth(100)
        option_layout.addWidget(self.variety_bottom, 2, 1)

        option_layout.addWidget(QLabel("合约:", self), 2, 2)
        self.contract_bottom = QComboBox(self)
        option_layout.addWidget(self.contract_bottom, 2, 3)

        self.start_calculate_button = QPushButton("开始计算", self)
        option_layout.addWidget(self.start_calculate_button, 2, 5)

        self.three_month_button = QPushButton("近3月", self)
        setattr(self.three_month_button, "day_count", 90)
        self.three_month_button.setFocusPolicy(Qt.NoFocus)
        self.six_month_button = QPushButton("近6月", self)
        self.six_month_button.setFocusPolicy(Qt.NoFocus)
        setattr(self.six_month_button, "day_count", 180)
        self.one_year_button = QPushButton("近1年", self)
        self.one_year_button.setFocusPolicy(Qt.NoFocus)
        setattr(self.one_year_button, "day_count", 360)
        option_layout.addWidget(self.three_month_button, 2, 6)
        option_layout.addWidget(self.six_month_button, 2, 7)
        option_layout.addWidget(self.one_year_button, 2, 8)

        option_widget.setLayout(option_layout)
        option_widget.setFixedHeight(self.TITLE_WIDGET_HEIGHT)

        main_layout.addWidget(option_widget)

        # 图形与数据显示拖动区
        splitter = QSplitter(self)
        splitter.setOrientation(Qt.Vertical)
        splitter.setHandleWidth(1)

        self.contact_channel = ArbitrageChannel()  # 页面信息交互通道
        self.web_container = ChartViewWidget(data_channel=self.contact_channel,
                                             filepath='file:/html/charts/arbitrage_chart.html')
        self.web_container.setParent(self)
        splitter.addWidget(self.web_container)
        # 数据显示表
        self.view_table = QTableWidget(self)
        self.view_table.verticalHeader().hide()
        self.view_table.horizontalHeader().setMinimumSectionSize(90)
        self.view_table.setMaximumWidth(self.parent().width() * 0.8)
        self.view_table.verticalHeader().setDefaultSectionSize(20)
        self.view_table.verticalScrollBar().setStyleSheet(VERTICAL_SCROLL_STYLE)
        self.view_table.horizontalHeader().setStyleSheet(BLUE_STYLE_HORIZONTAL_STYLE)
        self.view_table.setAlternatingRowColors(True)

        splitter.addWidget(self.view_table)
        splitter.setSizes([(self.parent().height() - self.TITLE_WIDGET_HEIGHT) * 0.6,
                           (self.parent().height() - self.TITLE_WIDGET_HEIGHT) * 0.4])
        splitter.setContentsMargins(QMargins(5, 10, 5, 10))
        main_layout.addWidget(splitter)
        #
        # self.web_container = QWebEngineView(self)
        # self.web_container.load(QUrl("file:///html/charts/arbitrage_chart.html"))  # 加载页面
        # # self.web_container.setContentsMargins(QMargins(5, 5, 0, 5))
        # # 设置与页面信息交互的通道
        # channel_qt_obj = QWebChannel(self.web_container.page())  # 实例化qt信道对象,必须传入页面参数
        # self.contact_channel = ArbitrageChannel()  # 页面信息交互通道
        # self.web_container.page().setWebChannel(channel_qt_obj)
        # channel_qt_obj.registerObject("pageContactChannel", self.contact_channel)  # 信道对象注册信道，只能注册一个
        # event_loop = QEventLoop(self)  # 同步设置
        # self.web_container.loadFinished.connect(event_loop.quit) # (加载完页面才显示)
        # event_loop.exec_()
        # main_layout.addWidget(self.web_container)
        self.setLayout(main_layout)
        self.three_month_button.setCursor(Qt.PointingHandCursor)
        self.six_month_button.setCursor(Qt.PointingHandCursor)
        self.one_year_button.setCursor(Qt.PointingHandCursor)
        page_title.setObjectName("pageTitle")
        self.three_month_button.setObjectName("monthButton")
        self.six_month_button.setObjectName("monthButton")
        self.one_year_button.setObjectName("monthButton")

        option_widget.setStyleSheet(
            "#optionWidget{background-color:rgb(245,245,245)}"
            "#pageTitle{background-color:rgb(91,155,210);color:rgb(250,250,250);padding:3px 5px}"
            "#monthButton{background-color:rgb(250,250,250);border-radius: 7px;"
            "font-size:12px;color:rgb(120,120,120);padding:4px 6px}"
        )
        self.three_month_button.setStyleSheet("background-color:rgb(191,211,249);color:rgb(78,110,242)")


class SpotArbitrage(SpotArbitrageUi):
    def __init__(self, *args, **kwargs):
        super(SpotArbitrage, self).__init__(*args, **kwargs)
        self.has_contract = False  # 品种获取完毕标志
        self.has_spot = False      # 现货获取完毕标志(当两个标志共同成立的时候，请求数据)
        self.day_count = 90  # 默认为3个月
        self.network_manager = getattr(qApp, "_network")
        # 品种下拉信号
        self.variety_bottom.currentTextChanged.connect(self.bottom_variety_changed)

        # 开始计算的信号
        self.start_calculate_button.clicked.connect(self.get_arbitrage_contract_data)

        # 数据范围选择
        self.three_month_button.clicked.connect(self.day_count_selected)
        self.six_month_button.clicked.connect(self.day_count_selected)
        self.one_year_button.clicked.connect(self.day_count_selected)

        # 获取期货所有品种
        self.get_all_variety()
        # 获取现货所有品种
        self.get_all_spot_data()

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
        self.variety_bottom.clear()
        if reply.error():
            pass
        else:
            data = json.loads(reply.readAll().data().decode('utf8'))
            for group_key in data["varieties"]:
                for variety_item in data["varieties"][group_key]:
                    self.variety_bottom.addItem(variety_item["variety_name"], variety_item["variety_en"])
        reply.deleteLater()

    # def top_variety_changed(self):
    #     """ 请求品种合约 """
    #     top_variety = self.variety_top.currentData()
    #     url = SERVER_API + "{}/contract/".format(top_variety)
    #     reply = self.network_manager.get(QNetworkRequest(QUrl(url)))
    #     reply.finished.connect(self.top_contract_reply)
    #
    # def top_contract_reply(self):
    #     """ 合约返回 """
    #     self.contract_top.clear()
    #     reply = self.sender()
    #     if reply.error():
    #         pass
    #     else:
    #         data = json.loads(reply.readAll().data().decode("utf8"))
    #         for contract_item in data["contracts"]:
    #             self.contract_bottom.addItem(contract_item["contract"])
    #         self.has_contract = True
    #     reply.deleteLater()
    #     if self.has_contract and self.has_spot:
    #         self.get_arbitrage_contract_data()

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
        reply.deleteLater()

    def get_all_spot_data(self):
        """ 获取所有现货品种 """
        url = SERVER_API + "spot-variety/"
        reply = self.network_manager.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(self.all_spot_reply)

    def all_spot_reply(self):
        """ 所有现货品种返回 """
        reply = self.sender()
        self.variety_top.clear()
        if reply.error():
            pass
        else:
            data = json.loads(reply.readAll().data().decode('utf8'))
            for variety_item in data["varieties"]:
                self.variety_top.addItem(variety_item[1], variety_item[0])
            self.has_spot = True
        reply.deleteLater()
        if self.has_contract and self.has_spot:
            self.get_arbitrage_contract_data()

    def get_arbitrage_contract_data(self):
        """ 获取两个品种的数据 """
        self.start_calculate_button.setEnabled(False)
        url = SERVER_API + "arbitrage/futures-spot/"
        body_data = {
            'variety_1': self.variety_top.currentData(),
            'variety_2': self.variety_bottom.currentData(),
            'contract_1': '',
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
            self.web_container.set_chart_option(json.dumps(data["data"]), json.dumps(data["base_option"]), 'line')
            # 将数据在表格中显示
            headers = {
                'date': '日期',
                'closePrice1': '{}{}'.format(self.variety_top.currentText(), self.contract_top.currentText()),
                'closePrice2': '{}{}'.format(self.variety_top.currentText(), self.contract_bottom.currentText()),
            }
            self.view_table_show(data['data'], headers=headers)

    def view_table_show(self, values, headers):
        """ 在表格中显示数据 """
        # 将headers转为二维数组得到表头和表值的key
        header_keys = [key for key in headers.keys()]
        self.view_table.clear()
        self.view_table.setColumnCount(len(header_keys))
        self.view_table.setRowCount(len(values))
        self.view_table.setHorizontalHeaderLabels([headers[key] for key in header_keys])
        self.view_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.view_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.view_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)

        for row, row_item in enumerate(values):
            for col, col_key in enumerate(header_keys):
                item = QTableWidgetItem(str(row_item[col_key]))
                item.setTextAlignment(Qt.AlignCenter)
                self.view_table.setItem(row, col, item)
            self.view_table.setRowHeight(row, 20)
