# _*_ coding:utf-8 _*_
# @File  : correlation.py
# @Time  : 2020-12-03 16:54
# @Author: zizle

""" 相关性计算 """

import datetime
import json

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QTableWidget, QDateEdit, \
    QMessageBox, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt, QMargins, QDate
from widgets import OptionWidget, ChartViewWidget
from channels.chart import ArbitrageChannel
from apis.caculate_plat import CorrelationAPI


class CorrelationWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(CorrelationWidget, self).__init__(*args, **kwargs)
        """ UI部分 """
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(QMargins(0, 0, 0, 0))
        opts_layout = QHBoxLayout()
        option_widget = OptionWidget(self)

        self.three_month = QPushButton('近3月', self)
        self.six_month = QPushButton('近6月', self)
        self.one_year = QPushButton('近1年', self)
        opts_layout.addWidget(self.three_month)
        opts_layout.addWidget(self.six_month)
        opts_layout.addWidget(self.one_year)

        self.custom_time = QPushButton('自定义', self)
        opts_layout.addWidget(self.custom_time)

        c_date = QDate().currentDate()
        e_date = QDate(c_date.year() - 1, c_date.month(), c_date.day())
        self.start_date = QDateEdit(self)
        self.start_date.setDate(e_date)
        self.start_date.setDisplayFormat('yyyy-MM-dd')
        self.start_date.setCalendarPopup(True)
        self.start_date.setEnabled(False)

        self.end_date = QDateEdit(self)
        self.end_date.setDisplayFormat('yyyy-MM-dd')
        self.end_date.setDate(c_date)
        self.end_date.setCalendarPopup(True)
        self.end_date.setEnabled(False)

        opts_layout.addWidget(self.start_date)
        opts_layout.addWidget(QLabel(' - ', self))
        opts_layout.addWidget(self.end_date)

        tips_label = QLabel('颜色越浅,负相关越大!颜色越深,正相关越大!可通过滑条调整显示的数据.', self)
        tips_label.setStyleSheet('color:rgb(233,66,66);font-size:12px')
        opts_layout.addWidget(tips_label)
        opts_layout.addStretch()

        option_widget.setLayout(opts_layout)
        option_widget.setFixedHeight(45)
        main_layout.addWidget(option_widget)

        self.chart_channel = ArbitrageChannel(self)
        self.chart_view = ChartViewWidget(self.chart_channel, 'file:/html/charts/correlation.html', self)

        self.chart_view.setContextMenuPolicy(Qt.NoContextMenu)
        # self.corr_table = QTableWidget(self)
        # main_layout.addWidget(self.corr_table)

        self.chart_view.hide()
        main_layout.addWidget(self.chart_view)

        self.loading_label = QLabel('Loading···', self)
        self.loading_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.loading_label)
        self.setLayout(main_layout)

        """ 业务部分 """
        self.correlation_api = CorrelationAPI(self)
        self.correlation_api.correlation_reply.connect(self.correlation_data_reply)

        self.start_date_str = None
        self.end_date_str = None
        self.three_month.clicked.connect(lambda: self.set_date_range(3))
        self.six_month.clicked.connect(lambda: self.set_date_range(6))
        self.one_year.clicked.connect(lambda: self.set_date_range(12))

        self.custom_time.clicked.connect(self.set_custom_date_range)

        self.start_date.dateChanged.connect(self.set_custom_dates)
        self.end_date.dateChanged.connect(self.set_custom_dates)

        self.chart_view.loadFinished.connect(self.chart_container_loaded)

    def chart_container_loaded(self, load):
        if load:
            self.three_month.click()

    def set_date_range(self, month):
        btn = self.sender()
        btn.setEnabled(False)
        if month == 3:
            self.six_month.setEnabled(True)
            self.one_year.setEnabled(True)
        elif month == 6:
            self.three_month.setEnabled(True)
            self.one_year.setEnabled(True)
        elif month == 12:
            self.three_month.setEnabled(True)
            self.six_month.setEnabled(True)
        else:
            pass
        self.custom_time.setEnabled(True)
        # 设置起始日期
        self.start_date.setEnabled(False)
        self.end_date.setEnabled(False)
        current_date = datetime.datetime.now()
        start = current_date + datetime.timedelta(days=-(month * 30))
        self.start_date_str = start.strftime('%Y-%m-%d')
        self.end_date_str = current_date.strftime('%Y-%m-%d')
        self.get_correlation_data()

    def set_custom_date_range(self):
        self.start_date.setEnabled(True)
        self.end_date.setEnabled(True)
        self.custom_time.setEnabled(False)
        self.three_month.setEnabled(True)
        self.six_month.setEnabled(True)
        self.one_year.setEnabled(True)

    def set_custom_dates(self):
        s, e = '', ''
        if self.start_date.isEnabled():
            s = self.start_date.text()
        if self.end_date.isEnabled():
            e = self.end_date.text()
        if e > s:
            self.start_date_str = s
            self.end_date_str = e
            self.get_correlation_data()
        else:
            QMessageBox.information(self, '错误', '开始日期需小于结束日期')

    def get_correlation_data(self):
        if not self.start_date_str or not self.end_date_str:
            return
        self.chart_view.hide()
        self.loading_label.show()
        self.correlation_api.get_correlations(self.start_date_str, self.end_date_str)

    def correlation_data_reply(self, data):
        # 填充数据到表格中
        sources = {
            'columns': data.get('columns', []),
            'index': data.get('index', []),
            'correlation': data.get('correlation', [])
        }
        self.chart_view.set_chart_option(source_data=json.dumps(sources), base_option="{}", chart_type='heatmap')
        self.loading_label.hide()
        self.chart_view.show()

        # self.corr_table.setRowCount(len(index))
        # self.corr_table.setColumnCount(len(columns))
        # self.corr_table.setHorizontalHeaderLabels(columns)
        # self.corr_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        # self.corr_table.setVerticalHeaderLabels(index)
        # for row, row_item in enumerate(correlation):
        #     self.corr_table.setRowHeight(row, 22)
        #     for col, col_item in enumerate(row_item):
        #         item = QTableWidgetItem(str(col_item))
        #         item.setTextAlignment(Qt.AlignCenter)
        #         self.corr_table.setItem(row, col, item)

