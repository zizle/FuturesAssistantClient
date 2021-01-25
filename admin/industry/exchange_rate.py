# _*_ coding:utf-8 _*_
# @File  : exchange_rate.py
# @Time  : 2021-01-22 14:07
# @Author: zizle

# 汇率数据的爬取
import json
import random
import datetime

from PyQt5.QtWidgets import qApp, QWidget, QVBoxLayout, QHBoxLayout, QDateEdit, QPushButton, QTableWidget, \
    QTableWidgetItem
from PyQt5.QtCore import Qt, QDate, QMargins, QUrl
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest

from popup.message import InformationPopup
from widgets import OptionWidget
from settings import USER_AGENTS


class ExchangeRateAdmin(QWidget):
    SPIDER_URL = "http://www.chinamoney.com.cn/ags/ms/cm-u-bk-ccpr/CcprHisNew?startDate={}&endDate={}&currency=USD/CNY,EUR/CNY,100JPY/CNY,HKD/CNY,GBP/CNY,AUD/CNY,NZD/CNY,SGD/CNY,CHF/CNY,CAD/CNY,CNY/MYR,CNY/RUB,CNY/ZAR,CNY/KRW,CNY/AED,CNY/SAR,CNY/HUF,CNY/PLN,CNY/DKK,CNY/SEK,CNY/NOK,CNY/TRRY,CNY/MXXN,CNY/THB&pageNum=1&pageSize=10"

    def __init__(self, *args, **kwargs):
        super(ExchangeRateAdmin, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0,))
        option_widget = OptionWidget(self)
        option_layout = QHBoxLayout()
        self.search_date = QDateEdit(self)
        self.search_date.setDate(QDate.currentDate())
        self.search_date.setDisplayFormat('yyyy-MM-dd')
        self.query_button = QPushButton('查询', self)
        self.save_button = QPushButton('保存', self)
        option_layout.addWidget(self.search_date)
        option_layout.addWidget(self.query_button)
        option_layout.addWidget(self.save_button)
        option_layout.addStretch()
        option_widget.setFixedHeight(40)
        option_widget.setLayout(option_layout)
        content_layout = QVBoxLayout()
        self.table = QTableWidget(self)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['日期', '汇率名称', '汇率值'])
        content_layout.addWidget(self.table)

        layout.addWidget(option_widget)
        layout.addLayout(content_layout)
        self.setLayout(layout)

        self.query_button.clicked.connect(self.query_exchange_rate)
        self.save_button.clicked.connect(self.save_exchange_rate)
        self.network_manager = getattr(qApp, '_network', QNetworkAccessManager(self))
        self.current_data = []

    def query_exchange_rate(self):
        current_date = self.search_date.text()
        if not current_date:
            return
        url = self.SPIDER_URL.format(current_date, current_date)
        req = QNetworkRequest(QUrl(url))
        req.setHeader(QNetworkRequest.UserAgentHeader, random.choice(USER_AGENTS).encode('utf8'))
        reply = self.network_manager.get(req)
        reply.finished.connect(self.exchange_rate_reply)

    def exchange_rate_reply(self):
        reply = self.sender()
        if reply.error():
            p = InformationPopup('获取数据失败!{}'.format(reply.error()))
            p.exec_()
        else:
            data = json.loads(reply.readAll().data().decode('utf8'))
            try:
                self.show_table(data)
            except Exception as e:
                print(e)
        reply.deleteLater()

    def show_table(self, data):
        # 处理显示数据
        head = data['head']
        records = data['records']
        data = data['data']
        if head['rep_code'] != '200':
            p = InformationPopup('网站响应错误!{}'.format(head['rep_code']), self)
            p.exec_()
            return
        # 验证日期
        if data['startDate'] != data['endDate']:
            p = InformationPopup('数据日期超出一天！', self)
            p.exec_()
            return
        create_date = data['startDate']
        table_header = data['searchlist']
        if len(records) > 1:
            p = InformationPopup('响应数据长度超出一天！', self)
            p.exec_()
            return
        table_values = records[0]['values']
        # 整理显示数据
        result = list(zip(table_header, table_values))
        final_data = []
        for item in result:
            final_data.append(
                {
                    'rate_date': create_date,
                    'rate_name': item[0],
                    'rate': item[1]
                }
            )
        print(final_data)
        self.current_data = final_data
        self.table.setRowCount(len(self.current_data))
        for row, row_item in enumerate(self.current_data):
            for col, key in enumerate(['rate_date', 'rate_name', 'rate']):
                item = QTableWidgetItem(row_item[key])
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

    def save_exchange_rate(self):
        # 保存数据
        if len(self.current_data) < 1:
            p = InformationPopup('还没获取数据!', self)
            p.exec_()
            return
        # 发起后端保存请求












