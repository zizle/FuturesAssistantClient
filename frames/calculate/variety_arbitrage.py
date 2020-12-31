# _*_ coding:utf-8 _*_
# @File  : variety_arbitrage.py
# @Time  : 2020-11-17 11:18
# @Author: zizle
""" 跨品种套利 """
import json

from PyQt5.QtWidgets import (qApp, QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QComboBox, QPushButton,
                             QSpinBox, QSplitter, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt, QMargins, QUrl
from PyQt5.QtNetwork import QNetworkRequest
from channels.chart import ArbitrageChannel
from widgets import OptionWidget, ChartViewWidget
from utils.date_handler import generate_date_with_limit
from utils.client import get_previous_variety, set_previous_variety
from utils.constant import HORIZONTAL_SCROLL_STYLE, VERTICAL_SCROLL_STYLE, BLUE_STYLE_HORIZONTAL_STYLE
from settings import SERVER_API


class VarietyArbitrageUi(QWidget):
    TITLE_WIDGET_HEIGHT = 120

    def __init__(self, *args, **kwargs):
        super(VarietyArbitrageUi, self).__init__(*args, **kwargs)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(QMargins(0, 0, 0, 0))
        main_layout.setSpacing(5)
        option_widget = OptionWidget(self)
        option_layout = QGridLayout()
        option_layout.setContentsMargins(QMargins(5, 5, 2, 5))
        option_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        title_layout = QHBoxLayout()
        page_title = QLabel("跨品种套利", self)
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

        # 记录最近使用的2个品种1
        self.previous_label1 = QLabel('最近使用:', self)
        option_layout.addWidget(self.previous_label1, 1, 8)
        self.previous_variety1 = QPushButton(self)
        setattr(self.previous_variety1, 'top', True)
        self.previous_variety1.setCursor(Qt.PointingHandCursor)
        self.previous_variety2 = QPushButton(self)
        setattr(self.previous_variety2, 'top', True)
        self.previous_variety2.setCursor(Qt.PointingHandCursor)
        option_layout.addWidget(self.previous_variety1, 1, 9)
        option_layout.addWidget(self.previous_variety2, 1, 10)

        option_layout.addWidget(QLabel("品种:", self), 2, 0)
        self.variety_bottom = QComboBox(self)
        self.variety_bottom.setMinimumWidth(100)
        option_layout.addWidget(self.variety_bottom, 2, 1)

        option_layout.addWidget(QLabel("合约:", self), 2, 2)
        self.contract_bottom = QComboBox(self)
        option_layout.addWidget(self.contract_bottom, 2, 3)

        self.start_calculate_button = QPushButton("开始计算", self)
        option_layout.addWidget(self.start_calculate_button, 2, 4)

        self.three_month_button = QPushButton("近3月", self)
        setattr(self.three_month_button, "day_count", 90)
        self.three_month_button.setFocusPolicy(Qt.NoFocus)
        self.six_month_button = QPushButton("近6月", self)
        self.six_month_button.setFocusPolicy(Qt.NoFocus)
        setattr(self.six_month_button, "day_count", 180)
        self.one_year_button = QPushButton("近1年", self)
        self.one_year_button.setFocusPolicy(Qt.NoFocus)
        setattr(self.one_year_button, "day_count", 360)
        option_layout.addWidget(self.three_month_button, 2, 5)
        option_layout.addWidget(self.six_month_button, 2, 6)
        option_layout.addWidget(self.one_year_button, 2, 7)

        # 记录最近使用的2个品种2
        self.previous_label2 = QLabel('最近使用:', self)
        option_layout.addWidget(self.previous_label2, 2, 8)
        self.previous_variety3 = QPushButton(self)
        setattr(self.previous_variety3, 'top', False)
        self.previous_variety3.setCursor(Qt.PointingHandCursor)
        self.previous_variety4 = QPushButton(self)
        setattr(self.previous_variety4, 'top', False)
        self.previous_variety4.setCursor(Qt.PointingHandCursor)
        option_layout.addWidget(self.previous_variety3, 2, 9)
        option_layout.addWidget(self.previous_variety4, 2, 10)

        self.last_year_count = QSpinBox(self)
        self.last_year_count.setPrefix("近 ")
        self.last_year_count.setSuffix(" 年")
        self.last_year_count.setMinimum(2)
        self.last_year_count.setMaximum(5)
        self.last_year_count.setValue(3)
        option_layout.addWidget(self.last_year_count, 3, 3)
        self.year_arbitrage_button = QPushButton('季节价差', self)
        option_layout.addWidget(self.year_arbitrage_button, 3, 4)

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

        page_title.setObjectName("pageTitle")
        self.previous_label1.hide()
        self.previous_label2.hide()
        self.previous_variety1.hide()
        self.previous_variety2.hide()
        self.previous_variety3.hide()
        self.previous_variety4.hide()
        self.three_month_button.setCursor(Qt.PointingHandCursor)
        self.six_month_button.setCursor(Qt.PointingHandCursor)
        self.one_year_button.setCursor(Qt.PointingHandCursor)
        self.previous_label1.setObjectName('previousLabel')
        self.previous_label2.setObjectName('previousLabel')
        self.previous_variety1.setObjectName('previousVariety')
        self.previous_variety2.setObjectName('previousVariety')
        self.previous_variety3.setObjectName('previousVariety')
        self.previous_variety4.setObjectName('previousVariety')
        self.three_month_button.setObjectName("monthButton")
        self.six_month_button.setObjectName("monthButton")
        self.one_year_button.setObjectName("monthButton")
        option_widget.setStyleSheet(
            "#optionWidget{background-color:rgb(245,245,245)}"
            "#pageTitle{background-color:rgb(91,155,210);color:rgb(250,250,250);padding:3px 5px}"
            "#monthButton{background-color:rgb(250,250,250);border-radius:7px;"
            "font-size:12px;color:rgb(120,120,120);padding:4px 6px}"
            "#previousLabel{font-size:12px;color:rgb(20,50,210)}"
            "#previousVariety{font-size:12px;border-radius:5px;color:rgb(250,250,250);padding:4px 6px;"
            "background-color:rgb(191,211,249)}"
        )
        self.three_month_button.setStyleSheet("background-color:rgb(191,211,249);color:rgb(78,110,242)")
        self.view_table.setObjectName('viewTable')
        self.view_table.setStyleSheet(
            "#viewTable{selection-color:rgb(80,100,200);selection-background-color:rgb(220,220,220);"
            "alternate-background-color:rgb(242,242,242);gridline-color:rgb(60,60,60)}"
        )


class VarietyArbitrage(VarietyArbitrageUi):
    def __init__(self, *args, **kwargs):
        super(VarietyArbitrage, self).__init__(*args, **kwargs)
        self.has_top_contract = False  # 合约获取完毕标志
        self.has_bottom_contract = False  # 当两个合约都获取完毕才请求数据
        self.previous_variety_filename = 'VARIETYARBITRAGE'

        # 读取用户最近使用的品种
        self.read_previous_variety()

        self.day_count = 90  # 默认为3个月
        self.network_manager = getattr(qApp, "_network")
        # 品种下拉信号
        self.variety_top.currentTextChanged.connect(self.top_variety_changed)
        # 获取所有品种
        self.get_all_variety()

        # 品种下拉信号
        self.variety_bottom.currentTextChanged.connect(self.bottom_variety_changed)
        # 开始计算的信号
        self.start_calculate_button.clicked.connect(self.get_arbitrage_contract_data)
        # 数据范围选择
        self.three_month_button.clicked.connect(self.day_count_selected)
        self.six_month_button.clicked.connect(self.day_count_selected)
        self.one_year_button.clicked.connect(self.day_count_selected)

        # 季节价差
        self.year_arbitrage_button.clicked.connect(self.get_season_arbitrage_data)

        # 点击最近使用的品种
        self.previous_variety1.clicked.connect(self.previous_variety_clicked)
        self.previous_variety2.clicked.connect(self.previous_variety_clicked)
        self.previous_variety3.clicked.connect(self.previous_variety_clicked)
        self.previous_variety4.clicked.connect(self.previous_variety_clicked)

    def previous_variety_clicked(self):
        """ 点击最近使用的品种 """
        button = self.sender()
        # variety_en = getattr(button, 'variety_en')
        variety_name = button.text()  # 也是源于下拉框,正常不会出错
        is_top = getattr(button, 'top')
        if is_top:
            self.variety_top.setCurrentText(variety_name)
        else:
            self.variety_bottom.setCurrentText(variety_name)

    def read_previous_variety(self):
        """ 读取用户最近使用的品种 """
        values = get_previous_variety('VARIETYARBITRAGE')
        previous_en1, previous_name1 = values['top'][0].get('variety_en'), values['top'][0].get('variety_name')
        previous_en2, previous_name2 = values['top'][1].get('variety_en'), values['top'][1].get('variety_name')
        previous_en3, previous_name3 = values['bottom'][0].get('variety_en'), values['bottom'][0].get('variety_name')
        previous_en4, previous_name4 = values['bottom'][1].get('variety_en'), values['bottom'][1].get('variety_name')
        if previous_en1 and previous_name1:
            self.show_previous_variety(self.previous_variety1, previous_en1, previous_name1)
            self.previous_label1.show()
            if previous_en2 and previous_name2:
                self.show_previous_variety(self.previous_variety2, previous_en2, previous_name2)
        if previous_en3 and previous_name3:
            self.previous_label2.show()
            self.previous_variety3.setText(previous_name3)
            self.show_previous_variety(self.previous_variety3, previous_en3, previous_name3)
            if previous_en4 and previous_name4:
                self.show_previous_variety(self.previous_variety4, previous_en4, previous_name4)

    @staticmethod
    def show_previous_variety(button, variety_en, variety_name):
        """ 显示 """
        button.setText(variety_name)
        setattr(button, 'variety_en', variety_en)
        button.show()

    def save_previous_variety(self):
        """ 保存最近使用品种 """
        v1_en, v1_name = self.variety_top.currentData(), self.variety_top.currentText()
        v2_en, v2_name = self.variety_bottom.currentData(), self.variety_bottom.currentText()
        set_previous_variety(self.previous_variety_filename, v1_name, v1_en, 'top')
        set_previous_variety(self.previous_variety_filename, v2_name, v2_en, 'bottom')

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
            all_variety = data["varieties"]
            for group_key in all_variety:
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
            self.has_top_contract = True
        reply.deleteLater()
        # if self.has_top_contract and self.has_bottom_contract:
        #     self.get_arbitrage_contract_data()

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
            # 将合约设置为第二个
            if self.contract_bottom.count() >= 1:
                self.contract_bottom.setCurrentIndex(1)
            self.has_bottom_contract = True
        reply.deleteLater()

    def get_arbitrage_contract_data(self):
        """ 获取两个品种的数据 """
        self.start_calculate_button.setEnabled(False)
        url = SERVER_API + "arbitrage/variety/"
        body_data = {
            'variety_1': self.variety_top.currentData(),
            'variety_2': self.variety_bottom.currentData(),
            'contract_1': self.contract_top.currentText(),
            'contract_2': self.contract_bottom.currentText(),
            'day_count': self.day_count
        }
        # 保存最近使用的品种
        self.save_previous_variety()
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
            # 将数据传入界面出图(参数1:数据源,参数2:基本信息;参数3:图形类型)
            self.web_container.set_chart_option(json.dumps(data["data"]), json.dumps(data["base_option"]), 'line')
            # 将数据在表格中显示
            headers = {
                'date': '日期',
                'closePrice1': '{}{}'.format(self.variety_top.currentText(), self.contract_top.currentText()),
                'closePrice2': '{}{}'.format(self.variety_bottom.currentText(), self.contract_bottom.currentText()),
            }
            self.view_table_show(data['data'], headers=headers)

        self.read_previous_variety()

    def get_season_arbitrage_data(self):
        """ 获取季节价差的数据 """
        self.year_arbitrage_button.setEnabled(False)
        v1 = self.variety_top.currentData()
        v2 = self.variety_bottom.currentData()
        c1 = self.contract_top.currentText()
        c2 = self.contract_bottom.currentText()
        year_count = self.last_year_count.value()
        if not all([v1, v2, c1, c2]):
            return
        # 保存最近使用
        self.save_previous_variety()
        url = SERVER_API + 'arbitrage/contract-season/?v1={}&v2={}&c1={}&c2={}&year_count={}'.format(v1, v2, c1, c2, year_count)
        reply = self.network_manager.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(self.season_arbitrage_data_reply)

    def season_arbitrage_data_reply(self):
        """ 季节价差图表的数据返回了 """
        reply = self.sender()
        if reply.error():
            pass
        else:
            data = json.loads(reply.readAll().data().decode('utf8'))
            self.show_arbitrage_charts(data['data'], data['date_limit'])
        self.year_arbitrage_button.setEnabled(True)
        reply.deleteLater()
        self.read_previous_variety()

    def show_arbitrage_charts(self, source_data, date_limit):
        """ 显示季节性图形 """
        variety1 = self.variety_top.currentText()
        variety2 = self.variety_bottom.currentText()
        if variety1 == variety2:
            title = '{}历史价差走势'.format(variety1)
        else:
            title = '{}与{}历史价差走势'.format(variety1, variety2)
        base_option = {
            'title': title,
            'x_axis': generate_date_with_limit(date_limit[0], date_limit[1])
        }
        # 将数据传入界面出图(参数1:数据源,参数2:基本信息;参数3:图形类型)
        self.web_container.set_chart_option(json.dumps(source_data), json.dumps(base_option), 'season')
        self.clear_view_table()

    def clear_view_table(self):
        """ 清除表格数据 """
        self.view_table.clear()
        self.view_table.setRowCount(0)
        self.view_table.setColumnCount(0)

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










