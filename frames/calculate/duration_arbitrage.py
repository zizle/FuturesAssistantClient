# _*_ coding:utf-8 _*_
# @File  : variety_arbitrage.py
# @Time  : 2020-11-17 11:18
# @Author: zizle
""" 跨期套利 """

import json
from PyQt5.QtWidgets import (qApp, QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QComboBox, QPushButton,
                             QSplitter, QTableWidget, QHeaderView, QTableWidgetItem)

from PyQt5.QtCore import Qt, QMargins, QUrl
from PyQt5.QtNetwork import QNetworkRequest
from channels.chart import ArbitrageChannel
from popup.message import InformationPopup
from utils.constant import VERTICAL_SCROLL_STYLE, BLUE_STYLE_HORIZONTAL_STYLE
from widgets import OptionWidget, ChartViewWidget
from settings import SERVER_API


class DurationArbitrageUi(QWidget):
    TITLE_WIDGET_HEIGHT = 90

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
        self.three_month_button.setFocusPolicy(Qt.NoFocus)
        self.six_month_button = QPushButton("近6月", self)
        setattr(self.six_month_button, "day_count", 180)
        self.six_month_button.setFocusPolicy(Qt.NoFocus)
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
        self.view_table.setObjectName('viewTable')
        self.view_table.setStyleSheet(
            "#viewTable{selection-color:rgb(80,100,200);selection-background-color:rgb(220,220,220);"
            "alternate-background-color:rgb(242,242,242);gridline-color:rgb(60,60,60)}"
        )


class DurationArbitrage(DurationArbitrageUi):
    def __init__(self, *args, **kwargs):
        super(DurationArbitrage, self).__init__(*args, **kwargs)
        self.day_count = 90  # 默认为3个月
        self.page_load_finished = False  # 是否初始化请求数据
        self.web_container.page().loadFinished.connect(self.loadpage_finished)
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

    def loadpage_finished(self):
        self.page_load_finished = True

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
        if self.page_load_finished:
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
        if not self.page_load_finished:
            p = InformationPopup('资源加载出错!', self)
            p.exec_()
            return
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







