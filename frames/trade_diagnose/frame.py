# _*_ coding:utf-8 _*_
# @File  : frame.py
# @Time  : 2021-03-26 10:20
# @Author: zizle

import json
import math
import sys
import datetime
import time
import pandas as pd
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView

from widgets import LoadingCover

from frames.trade_diagnose.threads import HandleSourceThread


# GUI与图形窗口的通讯实例
class ChartDataObj(QObject):
    # 参数1：作图的源数据 参数2：图表配置项;
    chartSource = pyqtSignal(str, str)
    # 调整图形大小
    chartResize = pyqtSignal(int, int)  # (仅含这两个参数)


# 显示图形的QWebEngineView
class ChartEngineView(QWebEngineView):
    def __init__(self, *args, **kwargs):
        super(ChartEngineView, self).__init__(*args, **kwargs)


# 数据概览窗口（含数据导入功能）
class AllViewWidget(QMainWindow):
    load_source_sig = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(AllViewWidget, self).__init__(*args, **kwargs)
        # 工具栏
        self.tool_bar = QToolBar(self)
        self.addToolBar(Qt.TopToolBarArea, self.tool_bar)
        self.load_action = self.tool_bar.addAction('导入数据')
        self.load_action.triggered.connect(self.to_load_source)

        # 中心窗体
        self.widget = QWidget(self)
        layout = QVBoxLayout()
        self.widget.setLayout(layout)
        # 未导入数据的提示
        self.no_source_tip = QLabel('请使用上方工具栏导入待分析数据!', self)
        layout.addWidget(self.no_source_tip)
        # 数据概览表格
        self.table = QTableWidget(self)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['日期', '权益', '风险度', '净利润', '日净值', '最大本金收益率'])
        layout.addWidget(self.table)
        self.setCentralWidget(self.widget)

        # 初始化显示状态
        self.table.hide()

    def to_load_source(self):
        self.load_source_sig.emit()

    def has_source_loaded(self):
        self.no_source_tip.hide()
        self.table.show()

    def general_view_table(self, general_list):
        # 对概览数据进行显示
        # 数据对象格式
        # {'date': '日期',
        #  'profit': '权益',
        #  'degree_of_risk': '风险度',
        #  'net_profits': '净利润',
        #  'date_net_value': '日净值',
        #  'max_roe': '最大本金收益率'
        #  }
        self.table.clearContents()
        self.table.setRowCount(len(general_list))
        for row, date_item in enumerate(general_list):
            for col, key in enumerate(['date', 'profit', 'degree_of_risk', 'net_profits', 'date_net_value', 'max_roe']):
                item = QTableWidgetItem(str(date_item[key]))
                self.table.setItem(row, col, item)


# 基本数据窗口
class BaseViewWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(BaseViewWidget, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        self.title = QLabel('基本数据', self)
        self.title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title)
        self.table = QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['指标', '数值', '指标', '数值'])
        layout.addWidget(self.table)

        self.setLayout(layout)

        self.add_indicators()

    def add_indicators(self):
        indicators = [
            {'key': 'initial_equity', 'name': '期初权益'}, {'key': 'ending_equity', 'name': '期末权益'},
            {'key': 'accumulated_income', 'name': '累计入金'}, {'key': 'accumulated_cash', 'name': '累计出金'},
            {'key': 'accumulated_net', 'name': '累计净值'}, {'key': 'maxrrate', 'name': '最大回撤率'},
            {'key': 'accumulated_net_profit', 'name': '累计净利润'}, {'key': 'average_daily', 'name': '日收益率均值'},
            {'key': 'historical_maxp', 'name': '历史最大本金'}, {'key': 'maxp_profit_rate', 'name': '最大本金收益率'},
            {'key': 'max_daily_profit', 'name': '日收益率最大'}, {'key': 'min_daily_profit', 'name': '日收益率最小'},
            {'key': 'expected_annual_rate', 'name': '预计年化收益率'}, {'key': 'total_days', 'name': '总交易天数'},
            {'key': 'profit_days', 'name': '盈利天数'}, {'key': 'loss_days', 'name': '亏损天数'},
            {'key': 'wining_rate', 'name': '交易胜率'}, {'key': 'profit_loss_rate', 'name': '盈亏比'},
            {'key': 'net_profit', 'name': '手续费/净利润'}, {'key': 'average_risk', 'name': '风险度均值'},
        ]
        self.table.setRowCount(math.ceil(len(indicators) / 2))
        i = 0
        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                if col % 2 == 0:
                    item = QTableWidgetItem(indicators[i]['name'])
                    item.setData(Qt.UserRole, indicators[i]['key'])
                    self.table.setItem(row, col, item)
                    i += 1

    def show_base_data(self, base_data):
        # 显示目标数据
        # {k:v}
        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                if col % 2 == 0:
                    item = self.table.item(row, col)
                    data_key = item.data(Qt.UserRole)
                    data_item = QTableWidgetItem(str(base_data.get(data_key, '1')))
                    self.table.setItem(row, col + 1, data_item)


# 最大本金收益率窗口，上面是折线图，下面是数据表
class MaxPrincipalProfitRate(QWidget):
    def __init__(self, *args, **kwargs):
        super(MaxPrincipalProfitRate, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        self.chart = ChartEngineView(self)
        self.chart.setMaximumHeight(430)
        layout.addWidget(self.chart)
        self.table = QTableWidget(self)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(['日期', '最大本金收益率'])
        layout.addWidget(self.table)
        self.setLayout(layout)

        # 加载图形页面html
        self.chart.page().load(QUrl('file:///html/charts/mppr.html'))
        # 设置与页面信息交互的通道
        channel_qt_obj = QWebChannel(self.chart.page())  # 实例化qt信道对象,必须传入页面参数
        self.contact_channel = ChartDataObj(self)  # 页面信息交互通道
        self.chart.page().setWebChannel(channel_qt_obj)
        channel_qt_obj.registerObject("pageContactChannel", self.contact_channel)  # 信道对象注册信道,只能注册一个

    def resizeEvent(self, event):
        super(MaxPrincipalProfitRate, self).resizeEvent(event)
        self.contact_channel.chartResize.emit(self.chart.width() - 50, self.chart.height())

    def show_data(self, data):
        # 显示数据
        # print(data)
        self.table.setRowCount(len(data))
        x_data, y_data = [], []
        for row, item in enumerate(data):
            x_data.append(item['date'])
            y_data.append(float(item['max_roe'].replace('%', '')))
            # 显示到表格上
            item1 = QTableWidgetItem(str(item['date']))
            self.table.setItem(row, 0, item1)
            item2 = QTableWidgetItem(str(item['max_roe']))
            self.table.setItem(row, 1, item2)
        source_data = {
            'x_data': x_data,
            'y_data': y_data
        }
        self.contact_channel.chartSource.emit(json.dumps(source_data), json.dumps({}))




class S(QWidget):
    def __init__(self, *args, **kwargs):
        super(S, self).__init__(*args, **kwargs)
        self.resize(1000, 600)
        layout = QHBoxLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        layout.setSpacing(1)
        self.splitter = QSplitter(self)
        # 左侧是个list
        self.left_list = QListWidget(self)
        self.left_list.setMinimumWidth(100)
        self.left_list.setMaximumWidth(250)
        # 右侧是个显示窗
        self.stacked = QStackedWidget(self)

        self.splitter.addWidget(self.left_list)
        self.splitter.addWidget(self.stacked)
        self.splitter.setHandleWidth(2)

        # 添加菜单目录，添加各窗口
        # 数据概览
        self.left_list.addItem(QListWidgetItem('数据概览', self.left_list))
        self.all_view = AllViewWidget(self)
        self.all_view.load_source_sig.connect(self.load_data_source)
        self.stacked.addWidget(self.all_view)
        # 基本数据
        self.left_list.addItem(QListWidgetItem('基本数据', self.left_list))
        self.base_view = BaseViewWidget(self)
        self.stacked.addWidget(self.base_view)
        # 最大本金收益率
        self.left_list.addItem(QListWidgetItem('最大本金收益率', self.left_list))
        self.mppr_view = MaxPrincipalProfitRate(self)
        self.stacked.addWidget(self.mppr_view)

        # 弹窗处理数据的提示
        self.tip_popup = LoadingCover(self)
        self.tip_popup.hide()

        layout.addWidget(self.splitter)
        self.setLayout(layout)

        # 处理原始数据的线程
        self.handle_thread = None
        self.has_data = False
        self.source_data = None
        self.base_data = {}
        self.left_list.clicked.connect(self.change_left_menu)

    def change_left_menu(self, index):
        menu_row = index.row()
        if menu_row > 0 and not self.has_data:
            QMessageBox.information(self, '错误', '需先导入原始数据才能进行分析!')
            return
        if menu_row == 1:  # 展示基本数据
            self.base_view.show_base_data(self.base_data)
        elif menu_row == 2:  # 最大本金收益率
            self.mppr_view.show_data(self.source_data)
        else:
            pass
        self.stacked.setCurrentIndex(menu_row)

    def resizeEvent(self, event):
        super(S, self).resizeEvent(event)
        self.tip_popup.resize(self.width(), self.height())

    def load_data_source(self):
        print('导入待分析的原始数据')
        self.tip_popup.show(text='正在处理数据')
        # 数据处理需使用线程处理完成，然后信号返回数据
        if self.handle_thread:
            self.handle_thread = None
        self.handle_thread = HandleSourceThread(self)
        self.handle_thread.handle_finished.connect(self.source_has_handle_finished)
        self.handle_thread.finished.connect(self.handle_thread.deleteLater)
        self.handle_thread.start()

    def source_has_handle_finished(self, source):
        # 线程处理数据返回
        self.all_view.has_source_loaded()
        self.source_data = source
        self.all_view.general_view_table(self.source_data)  # 目标源数据
        self.base_data = {
            'initial_equity': 213562,
            'ending_equity': 254265,
            'accumulated_income': 165165,
            'accumulated_cash': 15454,
            'accumulated_net': 12645,
            'maxrrate': '68%',
            'accumulated_net_profit': 23645,
            'average_daily': '10%',
            'historical_maxp': 25668,
            'maxp_profit_rate': '21%',
            'max_daily_profit': 4210,
            'min_daily_profit': 109,
            'expected_annual_rate': '12%',
            'total_days': 182,
            'profit_days': 102,
            'loss_days': 80,
            'wining_rate': '54%',
            'profit_loss_rate': '23%',
            'net_profit': '80%',
            'average_risk': '67%'

        }  # 基础数据
        self.has_data = True
        self.tip_popup.hide()
