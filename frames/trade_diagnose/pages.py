# _*_ coding:utf-8 _*_
# @File  : pages.py
# @Time  : 2021-03-29 09:43
# @Author: zizle

import math
import json

from PyQt5.QtGui import QPainter, QPixmap, QIcon, QBrush, QColor, QPalette
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QTabWidget,
                             QHBoxLayout, QRadioButton, QScrollArea, QHeaderView)
from PyQt5.QtCore import Qt, pyqtSignal, QUrl, QObject, QRect
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView

from frames.trade_diagnose import threads
from frames.trade_diagnose.utils import set_table_style
from apis import LoggerApi
from utils.client import get_client_uuid_with_ini

"""
展示echarts图的类和管道
"""


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


# 导入数据页
class LoadDataWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(LoadDataWidget, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        tip_widget = QWidget(self)
        title = QLabel('欢迎使用交易诊断系统', self)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet('margin-top: 45px;font-size: 50px;color:#fff;font-weight:500')
        tip = QLabel('请先选择账单类型并导入数据', self)
        tip.setStyleSheet('margin-top: 15px;font-size: 20px;color:#222;')
        tip.setAlignment(Qt.AlignCenter)
        tip_layout = QVBoxLayout()

        tip_layout.addWidget(title)
        tip_layout.addWidget(tip)
        tip_widget.setLayout(tip_layout)
        layout.addWidget(tip_widget, alignment=Qt.AlignTop)

        selector_layout = QHBoxLayout()
        selector_layout.addStretch()
        self.daily_daily = QRadioButton(self)  # 日逐日盯市
        self.daily_daily.setText('日账单(逐日盯市)')
        self.daily_daily.setChecked(True)
        self.daily_daily.clicked.connect(lambda x: self.bill_type_changed(1))
        self.daily_bill = QRadioButton(self)  # 日逐笔对冲
        self.daily_bill.setText('日账单(逐笔对冲)')
        self.daily_bill.clicked.connect(lambda x: self.bill_type_changed(2))
        self.month_daily = QRadioButton(self)  # 月逐日盯市
        self.month_daily.setText('月账单(逐日盯市)')
        self.month_daily.clicked.connect(lambda x: self.bill_type_changed(3))
        self.month_bill = QRadioButton(self)  # 月逐笔对冲
        self.month_bill.setText('月账单(逐笔对冲)')
        self.month_bill.clicked.connect(lambda x: self.bill_type_changed(4))
        selector_layout.addWidget(self.daily_daily)
        selector_layout.addWidget(self.daily_bill)
        selector_layout.addWidget(self.month_daily)
        selector_layout.addWidget(self.month_bill)

        self.daily_bill.hide()
        self.month_daily.hide()
        self.month_bill.hide()
        self.t_label = QLabel('当前仅支持逐日盯市的日账单诊断。', self)
        self.t_label.setFixedHeight(30)
        self.t_label.setStyleSheet('color: #d0604d')
        selector_layout.addWidget(self.t_label)

        selector_layout.addStretch()
        layout.addLayout(selector_layout)

        self.load_button = QPushButton('现在导入', self)
        self.load_button.setStyleSheet('height: 30px;padding: 10px')
        self.load_button.setIcon(QIcon('media/icons/import.png'))
        layout.addWidget(self.load_button, alignment=Qt.AlignCenter | Qt.AlignTop)
        self.setLayout(layout)

        self.bill_type = 1  # 账单类型 1,2,3,4 按按钮顺序区分

    def paintEvent(self, event) -> None:
        super(LoadDataWidget, self).paintEvent(event)
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), QPixmap("media/zdbg.png"), QRect())

    def bill_type_changed(self, t):
        self.bill_type = t


# 数据概览窗口
class SourceViewWidget(QWidget):

    def __init__(self, *args, **kwargs):
        super(SourceViewWidget, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        # 原始数据含多个表
        self.tab = QTabWidget(self)
        self.tab.setDocumentMode(True)
        # 1原始账户表
        self.account_table = QTableWidget(self)
        self.tab.addTab(self.account_table, '资金明细')
        # 3 成交明细
        self.exchange_table = QTableWidget(self)
        self.tab.addTab(self.exchange_table, '交易明细')
        # # 2 平仓明细表
        # self.position_table = QTableWidget(self)
        # self.tab.addTab(self.position_table,  '平仓明细')

        layout.addWidget(self.tab)
        self.setLayout(layout)

        self.is_shown = False

        set_table_style([self.account_table, self.exchange_table])

    def show_source_data(self, account, trade_detail):
        if not self.is_shown:
            # 显示账户表
            self.show_account_table(account)
            # 成交明细表
            self.show_exchange_table(trade_detail)
            # 平仓明细表
            # self.show_position_table(source_data['position'])

    def show_account_table(self, account_list):
        self.account_table.clear()
        self.account_table.setRowCount(len(account_list))
        self.account_table.setColumnCount(10)
        self.account_table.setHorizontalHeaderLabels(['日期', '上日结存', '当日权益', '当日存取合计', '当日盈亏', '手续费', '当日结存', '保证金', '可用资金', '风险度'])
        for row, date_item in enumerate(account_list):
            for col, key in enumerate(['exchange_date', 'pre_rights', 'rights', 'sum_in_out', 'profit', 'charge', 'leave', 'bail', 'enabled_money', 'risk']):
                item = QTableWidgetItem(str(date_item[key]))
                # item.setBackground(QBrush(QColor(43,43,43)))
                if col == 0:
                    item.setForeground(QBrush(QColor(255,255,255)))
                else:
                    item.setForeground(QBrush(QColor(66,233,233)))
                if col == 4:
                    color = QColor(233,66,66) if float(date_item[key]) > 0 else QColor(66, 233, 66)
                    item.setForeground(QBrush(color))
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.account_table.setItem(row, col, item)

    # def show_position_table(self, position_list):
    #     self.position_table.clear()
    #     self.position_table.setRowCount(len(position_list))
    #     self.position_table.setColumnCount(7)
    #     self.position_table.setHorizontalHeaderLabels(['日期', '合约', '成交序号', '买/卖', '成交价', '手数', '平仓盈亏'])
    #     for row, date_item in enumerate(position_list):
    #         for col, key in enumerate(['close_date', 'contract', 'ex_number', 'sale_text', 'ex_price', 'hands', 'close_profit']):
    #             item = QTableWidgetItem(str(date_item[key]))
    #             item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
    #             if col == 0:
    #                 item.setForeground(QBrush(QColor(255,255,255)))
    #             elif col == 1:
    #                 item.setForeground(QBrush(QColor(245,245,2)))
    #             elif col == 6:
    #                 color = QColor(233, 66, 66) if float(date_item[key]) >= 0 else QColor(66, 233, 66)
    #                 item.setForeground(QBrush(color))
    #             else:
    #                 item.setForeground(QBrush(QColor(66, 233, 233)))
    #
    #             self.position_table.setItem(row, col, item)

    def show_exchange_table(self, exchange_list):
        self.exchange_table.clear()
        self.exchange_table.setRowCount(len(exchange_list))
        self.exchange_table.setColumnCount(9)
        self.exchange_table.setHorizontalHeaderLabels(['合约', '开仓日期', '买/卖', '开仓价', '开仓手数', '平仓日期', '平仓价', '平仓手数', '平仓盈亏'])
        for row, date_item in enumerate(exchange_list):
            for col, key in enumerate(['contract', 'open_date', 'sale_text', 'open_price', 'open_hands', 'close_date', 'close_price', 'close_hands', 'close_profit']):
                item = QTableWidgetItem(str(date_item[key]))
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                if col == 0:
                    item.setForeground(QBrush(QColor(245,245,2)))
                elif col in [1, 5]:
                    # color = QColor(233, 66, 66) if date_item[key] == '开多' else QColor(66,233,66)
                    item.setForeground(QBrush(QColor(255,255,255)))
                elif col == 8:
                    color = QColor(233, 66, 66) if date_item[key] > 0 else QColor(66, 233, 66)
                    item.setForeground(QBrush(color))
                else:
                    item.setForeground(QBrush(QColor(66, 233, 233)))

                self.exchange_table.setItem(row, col, item)

    def show_variety_table(self, variety_list):
        self.variety_table.clear()
        self.variety_table.setRowCount(len(variety_list))
        self.variety_table.setColumnCount(3)
        self.variety_table.setHorizontalHeaderLabels(['日期', '品种', '成交额'])
        for row, date_item in enumerate(variety_list):
            for col, key in enumerate(['date', 'variety', 'turnover']):
                item = QTableWidgetItem(str(date_item[key]))
                if col == 0:
                    item.setForeground(QBrush(QColor(255,255,255)))
                else:
                    item.setForeground(QBrush(QColor(66,233,233)))
                self.variety_table.setItem(row, col, item)

    def show_shmore_table(self, shmore_list):
        self.shmore_table.clear()
        self.shmore_table.setRowCount(len(shmore_list))
        self.shmore_table.setColumnCount(3)
        self.shmore_table.setHorizontalHeaderLabels(['日期', '多空', '盈亏'])
        for row, date_item in enumerate(shmore_list):
            for col, key in enumerate(['date', 'shmore', 'profit']):
                item = QTableWidgetItem(str(date_item[key]))
                if col == 0:
                    item.setForeground(QBrush(QColor(255,255,255)))
                else:
                    item.setForeground(QBrush(QColor(66,233,233)))
                self.shmore_table.setItem(row, col, item)


# 基本数据窗口
class BaseViewWidget(QScrollArea):
    finished = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(BaseViewWidget, self).__init__(*args, **kwargs)
        cw = QWidget(self)
        layout = QVBoxLayout()
        self.title = QLabel('交易诊断分析', self)
        self.title.setFixedHeight(35)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.hide()
        layout.addWidget(self.title)
        self.table = QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['指标', '数值', '指标', '数值'])
        self.table.horizontalHeader().hide()
        self.table.verticalHeader().hide()
        layout.addWidget(self.table)

        # 注释说明
        self.explain_label = QLabel(self)
        # self.explain_label.setWordWrap(True)
        layout.addWidget(self.explain_label)

        # 总结语
        self.text_label = QLabel(self)
        self.text_label.setWordWrap(True)
        self.text_label.setAlignment(Qt.AlignTop)
        self.text_label.hide()
        layout.addWidget(self.text_label)
        layout.setSpacing(0)
        cw.setLayout(layout)
        self.setWidgetResizable(True)
        self.setWidget(cw)
        self.setObjectName('area')
        cw.setObjectName('cw')
        self.text_label.setObjectName('tl')
        set_table_style([self.table])
        # self.text_label.setStyleSheet('background-color:rgb(20,20,20);color:rgb(235,118,0);padding-top:15px')
        # self.explain_label.setAttribute(Qt.WA_StyledBackground, True)
        self.explain_label.setStyleSheet('background-color:#2b2b2b;color:#bbbbbb;padding-top:15px')
        self.setStyleSheet('#area,#cw{background-color:rgb(159, 205, 254)}')

        self.thread_ = None
        self.is_shown = False

        self.table.setRowCount(13)
        self.table.setColumnCount(4)

        self.indicators_list = [
            {'nkey': '开始日期',   'nrow': 0, 'ncol': 0, 'vkey': 'ksrq', 'vrow': 0, 'vcol': 1},
            {'nkey': '结束日期',   'nrow': 0, 'ncol': 2, 'vkey': 'jsrq', 'vrow': 0, 'vcol': 3},
            {'nkey': '期初权益',   'nrow': 1, 'ncol': 0, 'vkey': 'qcqy', 'vrow': 1, 'vcol': 1},
            {'nkey': '期末权益',   'nrow': 1, 'ncol': 2, 'vkey': 'qmqy', 'vrow': 1, 'vcol': 3},
            {'nkey': '交易天数',   'nrow': 2, 'ncol': 0, 'vkey': 'qjts', 'vrow': 2, 'vcol': 1},
            {'nkey': '盈利天数',   'nrow': 2, 'ncol': 2, 'vkey': 'ylts', 'vrow': 2, 'vcol': 3},
            {'nkey': '亏损天数',   'nrow': 3, 'ncol': 0, 'vkey': 'ksts', 'vrow': 3, 'vcol': 1},
            {'nkey': '交易胜率',   'nrow': 3, 'ncol': 2, 'vkey': 'jysl', 'vrow': 3, 'vcol': 3},
            {'nkey': '累计净入金', 'nrow': 4, 'ncol': 0, 'vkey': 'ljjrj', 'vrow': 4, 'vcol': 1},
            {'nkey': '累计净值',   'nrow': 4, 'ncol': 2, 'vkey': 'ljjz', 'vrow': 4, 'vcol': 3},
            {'nkey': '交易费用', 'nrow': 5, 'ncol': 0, 'vkey': 'jyfy', 'vrow': 5, 'vcol': 1},
            {'nkey': '累计净利润', 'nrow': 5, 'ncol': 2, 'vkey': 'ljjlr', 'vrow': 5, 'vcol': 3},
            {'nkey': '盈亏比', 'nrow': 6, 'ncol': 0, 'vkey': 'ykb', 'vrow': 6, 'vcol': 1},
            {'nkey': '手续费/净利润', 'nrow': 6, 'ncol': 2, 'vkey': 'fjlrb', 'vrow': 6, 'vcol': 3},
            {'nkey': '最大回撤时点', 'nrow': 7, 'ncol': 0, 'vkey': 'zdhcsd', 'vrow': 7, 'vcol': 1},
            {'nkey': '最大回撤区间', 'nrow': 7, 'ncol': 2, 'vkey': 'zdhcqj', 'vrow': 7, 'vcol': 3},
            {'nkey': '最大日收益率', 'nrow': 8, 'ncol': 0, 'vkey': 'zdrsyl', 'vrow': 8, 'vcol': 1},
            {'nkey': '最小日收益率', 'nrow': 8, 'ncol': 2, 'vkey': 'zxrsyl', 'vrow': 8, 'vcol': 3},
            {'nkey': '日收益率均值', 'nrow': 9, 'ncol': 0, 'vkey': 'pjrsyl', 'vrow': 9, 'vcol': 1},
            {'nkey': '预计年化收益率', 'nrow': 9, 'ncol': 2, 'vkey': 'yjnhsyl', 'vrow': 9, 'vcol': 3},
            {'nkey': '最大仓位比率', 'nrow': 10, 'ncol': 0, 'vkey': 'zdcwbl', 'vrow': 10, 'vcol': 1},
            {'nkey': '最小仓位比率', 'nrow': 10, 'ncol': 2, 'vkey': 'zxcwbl', 'vrow': 10, 'vcol': 3},
            {'nkey': '平均仓位比率', 'nrow': 11, 'ncol': 0, 'vkey': 'pjcwbl', 'vrow': 11, 'vcol': 1},
            {'nkey': '空仓天数', 'nrow': 11, 'ncol': 2, 'vkey': 'kcts', 'vrow': 11, 'vcol': 3},
            {'nkey': '夏普比率', 'nrow': 12, 'ncol': 0, 'vkey': 'xpbl', 'vrow': 12, 'vcol': 1},
            {'nkey': '卡玛比率', 'nrow': 12, 'ncol': 2, 'vkey': 'kmbl', 'vrow': 12, 'vcol': 3},
        ]

        self.log_api = LoggerApi()
        self.is_logged = False

    def showEvent(self, ev) -> None:
        # 发送网络请求到服务端记录使用了本模块
        super(BaseViewWidget, self).showEvent(ev)
        if not self.is_logged:
            data = {
                'client': get_client_uuid_with_ini(),
                'error': '访问了交易诊断'
            }
            self.log_api.post(data)
            self.is_logged = True

    def clear_thread(self):
        if self.thread_:
            del self.thread_
            self.thread_ = None

    def handle_base_data(self, account, trade_detail):
        if self.is_shown:
            self.finished.emit()
            return
        self.clear_thread()
        self.thread_ = threads.HandleBaseThread(account=account, trade_detail=trade_detail, parent=self)
        self.thread_.finished.connect(self.thread_.deleteLater)
        self.thread_.handle_finished.connect(self.show_data)
        self.thread_.start()

    def show_data(self, base_data):
        self.show_base_data(base_data)
        # self.show_text(base_data)
        self.show_explain_text(base_data)
        self.finished.emit()

    def show_explain_text(self, base_data):
        explain_text = f"""
        <div style='color:#42e9e9'>
            <p>平仓盈利前五品种：<span style=color:'#dc2835'>{base_data['ylqwpz']}</span>；平仓亏损前五品种：<span style=color:'#15bc3e'>{base_data['ksqwpz']}</span></p>
            <p>交易手数前五品种：<span style=color:'#ffffff'>{base_data['shqwpz']}</span>；交易金额前五品种：<span style=color:'#ffffff'>{base_data['jeqwpz']}</span></p>
        </div>
        <div>
            <p>其中:</p>
            <p>交易天数:账户资金记录的日期总天数  盈利天数:账户资金表中当日盈亏为正的天数  亏损天数:账户资金表中当日盈亏不为正的天数</p>
            <p>交易胜率:平仓盈利的交易手数 / 总平仓手数</p>
            <p>累计净值P=P1*P2*P3.....*Pn，其中P为累计净值，Pn为当日净值；Pn=(当日权益 - 当日存取)/上日权益</p>
            <p>累计净利润：平仓交易净盈亏 - 交易费用，其中交易费用为手续费加和</p>
            <p>盈亏比：平仓交易盈利加和 / 平仓交易亏损加和 * 100%</p>
            <p>最大回撤时点：最大回撤区间开始时的时点，其中最大回撤区间为诊断的日期内的区间</p>
            <p>日收益率=当日净值Pn - 1，预计年化收益率：平均日收益率 x 250</p>
            <p>仓位比率(风险度) = 当日保证金占用 / 当日权益 * 100%</p>
            <p>空仓天数：账户中保证金占用为0的天数</p>
            <p>夏普比率：(年化收益率 - 无风险利率) / 收益率标准差; 其中无风险利率：2%</p>
            <p>卡玛比率：(年化收益率 - 无风险利率) / 最大回撤率; 其中无风险利率：2%</p>
            <p>最大回撤率:区间最高累计净值 - 当日的累计净值) / 区间最高累计净值，取最大值</p>
        </div>
        """
        self.explain_label.setText(explain_text)
        self.explain_label.setAlignment(Qt.AlignTop)

    def show_base_data(self, base_data):
        self.table.setRowCount(math.ceil(len(self.indicators_list) / 2))
        self.table.setFixedHeight(math.ceil(len(self.indicators_list) / 2) * 31)
        # 显示目标数据
        for indicator in self.indicators_list:
            item1 = QTableWidgetItem(str(indicator['nkey']))
            item1.setForeground(QBrush(QColor(66, 233, 233)))
            self.table.setItem(indicator['nrow'], indicator['ncol'], item1)
            item2 = QTableWidgetItem(str(base_data[indicator['vkey']]))
            item2.setForeground(QBrush(QColor(255, 255, 255)))
            self.table.setItem(indicator['vrow'], indicator['vcol'], item2)
            self.table.setColumnWidth(indicator['vcol'], 180)
            self.table.setRowHeight(indicator['nrow'], 31)

        self.is_shown = True

    def get_win_rate_text(self, rate, profit):  # 获取胜率分析的文字描述
        if profit > 0:
            if rate > 60:
                text = '恭喜您！胜率很高，远远高于市场的平均胜率（35%左右），您有极高的交易天赋，成熟的交易心理，希望您一直保持自己的交易风格，计划您的交易，交易您的计划。'
            elif 40 < rate <= 60:
                text = '您的胜率高于市场平均胜率（35%左右），恭喜您！您有较高的盘感，对市场的变化也相对敏感，希望您保持稳定的心态，再接再厉，创造更高的成绩。'
            elif 30 < rate <= 40:
                text = '您的胜率接近市场平均胜率（35%左右），建议您进一步加强技术分析的学习和研究，保持平稳的心态，并随时同瑞达期货各营业部客服人员沟通，了解瑞达期货推出的一些咨询服务产品和程序化交易产品，帮助您提高胜率。'
            else:
                text = '您的胜率低于市场平均胜率（35%左右），建议您暂时暂停交易，稍安勿躁。建议您努力加强技术分析的研究，并随时同瑞达期货各营业部客服人员沟通，了解瑞达期货推出的一些咨询服务产品程序化交易产品，帮助您提高胜率。'
        else:
            if rate > 60:
                text = '恭喜您！胜率很高，远远高于市场的平均胜率（35%左右），但是您的账户总体净盈亏依然亏损，这是一个极端的案例，您拥有极高的天赋，但是比较欠缺资金和仓位的管理，往往盈利的轻仓而亏损的满仓或重仓，导致整体账户亏损。'
            elif 40 < rate <= 60:
                text = '您的胜率高于市场平均胜率（35%左右），恭喜您！但是您的账户总体净盈亏依然亏损，您有较高的盘感对市场的变化也相对敏感，但比较欠缺资金和仓位的管理，往往盈利的轻仓而亏损的满仓或重仓，导致整体账户亏损。'
            elif 30 < rate <= 40:
                text = '您的胜率接近市场平均胜率（35%左右），但您的账户净盈亏依然亏损，建议您加强资金和仓位的管理，保持平稳的心态，并随时同瑞达期货各营业部客服人员沟通，了解瑞达期货推出的一些咨询服务产品和程序化交易产品，帮助您提高胜率。'
            else:
                text = '您的胜率低于市场平均胜率（35%左右），建议您暂时暂停交易，稍安勿躁。建议您努力加强技术分析的研究，并随时同瑞达期货各营业部客服人员沟通，了解瑞达期货推出的一些咨询服务产品程序化交易产品，帮助您提高胜率。'
        return text

    def get_ykfx_text(self, a, b, c):
        # a 最高获利/平均获利  b 最大亏损/平均亏损  c 单日最高亏损/单日平均亏损
        if a >= 20 or b >= 20 or c>=20:
            text = '您的最高获利或最高亏损金额远远大于平均每笔获利金额，造成了您账户资金的不稳定性，最高获利较大有可能因抓住一波趋势单或重仓单有关；最高亏损较大有可能因没有注意盘面变化、做错单未及时止损、单日重仓、或出现极端单边行情等有关，建议严格控制仓位，金字塔加码做单，同时设置好止损位。并严格执行您的交易计划。'
        elif 10<=a<20 or 10<=b<20 or 10<=c<20:
            text = '您的单笔盈亏比例在正常范围之内，建议您进一步学习一些交易的理念和技巧，制定您擅长的交易计划，并做好风险控制。'
        else:
            text = '您有非常冷静的头脑，并有很高的风险控制理念，同时拥有较好的做单思路和计划，希望您继续保持，创造更稳定的盈利。'

        return text

    def get_pjykfx_text(self, a, b, jyk):
        # a 平均盈利  b 平均亏损
        r = abs(a / b)
        if jyk > 0:
            if r >= 3:
                text = '您的资金管理和风险控制相当成功，已经达到了投资计划的目标位置。'
            elif 1 <= r <= 3:
                text = '您的计划有大部分是成功的，您的风险控制也做的相当好，建议您进一步学习技术分析，提高盈亏比，继而提高账户的盈利水平。'
            else:
                text = '您往往喜欢规避风险，一旦微小获利就立即出场，相反，亏损情况下却犹豫不决或未及时止损，但您的运气不错，盈亏比较高，建议您正确认识风险，果断止损，做好风险的管理。'
        else:
            if r >= 3:
                text = '您有较好的资金管理和风险控制，但是您的盈亏比不高，建议您加强技术分析的学习，提高盈利能力。'
            elif 1 <= r <= 3:
                text = '您的风险控制也做的比较好，但是盈亏比不高，建议您进一步学习技术分析，继而提高账户的盈利水平。'
            else:
                text = '您往往喜欢规避风险，一旦微小获利就立即出场，相反，亏损情况下却犹豫不决或未及时止损，建议您正确认识风险，果断止损，做好风险的管理。同时加强技术分析的学习，提高盈利水平。'
        return text

    def get_lxykfx_text(self, a, b):
        # a 连续盈利次数  b连续亏损次数
        if a >= 4:
            t1 = '恭喜您，您具备较强的获利能力和行情判断能力。'
        elif 2 <= a < 4:
            t1 = '您的获利能力和行情判断能力较强。'
        else:
            t1 = '您对行情的正确判断较欠缺，或者可能行情判断正确，入场或出场的点位不对导致亏损，千万不要气馁，建议您把握大的宏观局势和产业行业动态，并且学习好技术分析做好出入点位的计划。'
        if b >= 4:
            t2 = '可能与极端单边行情或者判断错行情未及时止损，或者重仓做单有关。'
        elif 2 <= b < 4:
            t2 = '您总有不服输的精神，失败之后会总结经验教训，但是请一定要注意对风险的控制和止损的重要性。'
        else:
            t2 = '您一定是上帝的宠儿，积智慧和运气与一身。'
        return [t1, t2]

    def show_text(self, base_data):  # 显示诊断结果
        class TextData(object):
            # 胜率分析
            jyk = base_data['jyk']  # 净盈亏
            jybs = int(base_data['jybs'])  # 交易笔数
            ylbs = int(base_data['ylbs'])  # 盈利笔数
            ksbs = int(base_data['ksbs'])  # 亏损笔数
            slfx = ''  # 胜率分析
            # 单笔盈亏分析
            zghl = base_data['zghl']  # 最高获利
            pjhl = base_data['pjhl']  # 平均获利
            zgks = base_data['zgks']  # 最高亏损
            pjks = base_data['pjks']  # 平均亏损
            drzgks = base_data['drzgks']  # 单日最高亏损
            drpjks = round(base_data['drpjks'], 2)  # 单日平均亏损
            ykfx = ''
            # 平均盈亏比分析
            pjykfx = ''
            # 连续盈亏次数
            lxyl = int(base_data['lxyl'])  # 连续盈利笔数
            lxks = int(base_data['lxks'])  # 连续亏损笔数
            lxykfx = ['', '']  # 连续盈亏分析


        # 胜率分析
        sl = round(TextData.ylbs * 100 / TextData.jybs, 4)
        TextData.slfx = self.get_win_rate_text(sl, TextData.jyk)

        text = f'<p style=text-indent:25px;margin-bottom:0px>' \
               f'1、胜率分析：您的账户在整个交易期间共交易<span style=color:#ccc>{TextData.jybs}</span>笔，其中获利<span style=color:#ccc>{TextData.ylbs}</span>笔，' \
               f'亏损<span style=color:#ccc>{TextData.ksbs}</span>笔，胜率为：<span style=color:#ccc>{sl}%</span>。</p>' \
               f'<p style=text-indent:25px;margin:0>{TextData.slfx}</p>'

        # 单笔盈亏分析
        a = TextData.zghl / TextData.pjhl
        b = TextData.zgks / TextData.pjks
        c = TextData.drzgks / TextData.drpjks
        TextData.ykfx = self.get_ykfx_text(a, b, c)
        text += f'<p style=text-indent:25px;margin-bottom:0px>' \
                f'2、单笔盈亏分析：您的账户单笔最高获利为<span style=color:#ccc>{TextData.zghl}</span>；而单笔最高亏损为<span style=color:#ccc>{TextData.zgks}</span>，分别是平均每笔获利的<span style=color:#ccc>{round(a, 2)}</span>倍，每笔平均亏损的<span style=color:#ccc>{round(b, 2)}</span>倍；单日最大亏损<span style=color:#ccc>{TextData.drzgks}</span>，是平均单日亏损<span style=color:#ccc>{TextData.drpjks}</span>的<span style=color:#ccc>{round(c, 2)}</span>倍。</p>' \
                f'<p style=text-indent:25px;margin:0>{TextData.ykfx}</p>'
        # 平均盈亏比分析
        TextData.pjykfx = self.get_pjykfx_text(TextData.pjhl, TextData.pjks, TextData.jyk)
        text += f'<p style=text-indent:25px;margin-bottom:0px>' \
                f'3、平均盈亏比分析：您的账户平均每笔获利<span style=color:#ccc>{TextData.pjhl}</span>，平均每笔亏损<span style=color:#ccc>{TextData.pjks}</span>,平均盈亏比（即平均每笔获利/平均每笔亏损）为<span style=color:#ccc>{round(TextData.pjhl * 100 / TextData.pjks, 2)}%</span>。</p>' \
                f'<p style=text-indent:25px;margin:0>{TextData.pjykfx}</p>'

        # 连续盈亏次数分析
        TextData.lxykfx = self.get_lxykfx_text(TextData.lxyl, TextData.lxks)
        text += f'<p style=text-indent:25px;margin-bottom:0px>' \
                f'4、连续盈亏次数分析：您的账户连续获利的最高次数是<span style=color:#ccc>{TextData.lxyl}</span>次，{TextData.lxykfx[0]}' \
                f'您的账户连续亏损的最高次数是<span style=color:#ccc>{TextData.lxks}</span>次，{TextData.lxykfx[1]}</p>'

        # 说明
        text += f'<p style=text-indent:25px;margin-bottom:0px>' \
                f'说明：该分析系统仅从客户客观交易的数据统计而得，所提建议具有一定的主观性，并非完全客观，不当之处，敬请见谅！</p>'

        self.text_label.setText(text)


# 交易分析 - 手数金额
class HandsPriceWidget(QScrollArea):
    finished = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(HandsPriceWidget, self).__init__(*args, **kwargs)
        cw = QWidget(self)  # center widget

        layout = QVBoxLayout()
        self.chart = ChartEngineView(self)
        self.chart.setMinimumHeight(300)
        # 加载图形页面html
        self.chart.page().load(QUrl('file:///html/charts/handPrice.html'))
        # 设置与页面信息交互的通道
        channel_qt_obj = QWebChannel(self.chart.page())  # 实例化qt信道对象,必须传入页面参数
        self.contact_channel = ChartDataObj(self)  # 页面信息交互通道
        self.chart.page().setWebChannel(channel_qt_obj)
        channel_qt_obj.registerObject("pageContactChannel", self.contact_channel)  # 信道对象注册信道,只能注册一个

        layout.addWidget(self.chart)

        cw.setLayout(layout)
        self.setWidgetResizable(True)
        self.setWidget(cw)
        self.setStyleSheet("QScrollArea{background-color:#ffffff}")
        self.viewport().setStyleSheet("background-color:#ffffff")

        self.thread_ = None
        self.is_shown = False

    def resizeEvent(self, event):
        super(HandsPriceWidget, self).resizeEvent(event)
        self.contact_channel.chartResize.emit(self.chart.width() -50, self.chart.height())

    def clear_thread(self):
        if self.thread_:
            del self.thread_
            self.thread_ = None

    def handle_data(self, trade_detail):
        if self.is_shown:
            self.finished.emit()
            return
        self.clear_thread()
        self.thread_ = threads.HandlePriceHandsThread(trade_detail, parent=self)
        self.thread_.finished.connect(self.thread_.deleteLater)
        self.thread_.handle_finished.connect(self.data_show)
        self.thread_.start()

    def data_show(self, data):
        # 传入数据到页面显示图形
        self.contact_channel.chartSource.emit(json.dumps(data), '')
        self.finished.emit()


# 交易分析 - 日内隔夜交易
class PassNightWidget(QScrollArea):
    finished = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(PassNightWidget, self).__init__(*args, **kwargs)
        cw = QWidget(self)  # center widget

        layout = QVBoxLayout()
        self.chart = ChartEngineView(self)
        self.chart.setMinimumHeight(300)
        # 加载图形页面html
        self.chart.page().load(QUrl('file:///html/charts/passNight.html'))
        # 设置与页面信息交互的通道
        channel_qt_obj = QWebChannel(self.chart.page())  # 实例化qt信道对象,必须传入页面参数
        self.contact_channel = ChartDataObj(self)  # 页面信息交互通道
        self.chart.page().setWebChannel(channel_qt_obj)
        channel_qt_obj.registerObject("pageContactChannel", self.contact_channel)  # 信道对象注册信道,只能注册一个

        layout.addWidget(self.chart)

        cw.setLayout(layout)
        self.setWidgetResizable(True)
        self.setWidget(cw)
        self.setStyleSheet("QScrollArea{background-color:#ffffff}")
        self.viewport().setStyleSheet("background-color:#ffffff")

        self.thread_ = None
        self.is_shown = False

    def resizeEvent(self, event):
        super(PassNightWidget, self).resizeEvent(event)
        self.contact_channel.chartResize.emit(self.chart.width() - 50, 300)

    def clear_thread(self):
        if self.thread_:
            del self.thread_
            self.thread_ = None

    def handle_data(self, trade_detail):
        if self.is_shown:
            self.finished.emit()
            return
        self.clear_thread()
        self.thread_ = threads.HandlePassNightThread(trade_detail, parent=self)
        self.thread_.finished.connect(self.thread_.deleteLater)
        self.thread_.handle_finished.connect(self.data_show)
        self.thread_.start()

    def data_show(self, data):
        # 传入数据到页面显示图形
        self.contact_channel.chartSource.emit(json.dumps(data), '')
        self.finished.emit()


# 交易分析 - 交易费用
class ExchangeChargeWidget(QScrollArea):
    finished = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(ExchangeChargeWidget, self).__init__(*args, **kwargs)
        cw = QWidget(self)  # center widget

        layout = QVBoxLayout()
        self.chart = ChartEngineView(self)
        self.chart.setMinimumHeight(300)
        # 加载图形页面html
        self.chart.page().load(QUrl('file:///html/charts/exchangeCharge.html'))
        # 设置与页面信息交互的通道
        channel_qt_obj = QWebChannel(self.chart.page())  # 实例化qt信道对象,必须传入页面参数
        self.contact_channel = ChartDataObj(self)  # 页面信息交互通道
        self.chart.page().setWebChannel(channel_qt_obj)
        channel_qt_obj.registerObject("pageContactChannel", self.contact_channel)  # 信道对象注册信道,只能注册一个

        layout.addWidget(self.chart)

        cw.setLayout(layout)
        self.setWidgetResizable(True)
        self.setWidget(cw)
        self.setStyleSheet("QScrollArea{background-color:#ffffff}")
        self.viewport().setStyleSheet("background-color:#ffffff")

        self.thread_ = None
        self.is_shown = False

    def resizeEvent(self, event):
        super(ExchangeChargeWidget, self).resizeEvent(event)
        self.contact_channel.chartResize.emit(self.chart.width() - 50, 420)

    def clear_thread(self):
        if self.thread_:
            del self.thread_
            self.thread_ = None

    def handle_data(self, account_data):
        if self.is_shown:
            self.finished.emit()
            return
        self.clear_thread()
        self.thread_ = threads.HandleExChargeThread(account_data, parent=self)
        self.thread_.finished.connect(self.thread_.deleteLater)
        self.thread_.handle_finished.connect(self.data_show)
        self.thread_.start()

    def data_show(self, data):
        # 传入数据到页面显示图形
        self.contact_channel.chartSource.emit(json.dumps(data), '')
        self.finished.emit()

# 盈亏分析 - 净值图
class NetValueWidget(QScrollArea):
    finished = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(NetValueWidget, self).__init__(*args, **kwargs)
        cw = QWidget(self)  # center widget

        layout = QVBoxLayout()
        self.chart = ChartEngineView(self)
        self.chart.setFixedHeight(420)
        # 加载图形页面html
        self.chart.page().load(QUrl('file:///html/charts/netValue.html'))
        # 设置与页面信息交互的通道
        channel_qt_obj = QWebChannel(self.chart.page())  # 实例化qt信道对象,必须传入页面参数
        self.contact_channel = ChartDataObj(self)  # 页面信息交互通道
        self.chart.page().setWebChannel(channel_qt_obj)
        channel_qt_obj.registerObject("pageContactChannel", self.contact_channel)  # 信道对象注册信道,只能注册一个

        # self.table = QTableWidget(self)

        layout.addWidget(self.chart)
        layout.addStretch()
        # layout.addWidget(self.table)

        cw.setLayout(layout)
        self.setWidgetResizable(True)
        self.setWidget(cw)
        self.setStyleSheet("QScrollArea{background-color:#ffffff}")
        self.viewport().setStyleSheet("background-color:#ffffff")

        self.thread_ = None
        self.is_shown = False

    def resizeEvent(self, event):
        super(NetValueWidget, self).resizeEvent(event)
        self.contact_channel.chartResize.emit(self.chart.width() - 50, 420)

    def clear_thread(self):
        if self.thread_:
            del self.thread_
            self.thread_ = None

    def handle_data(self, account_data):
        if self.is_shown:
            self.finished.emit()
            return
        self.clear_thread()
        self.thread_ = threads.HandleNetValueThread(account_data, parent=self)
        self.thread_.finished.connect(self.thread_.deleteLater)
        self.thread_.handle_finished.connect(self.data_show)
        self.thread_.start()

    def data_show(self, data):
        # 传入数据到页面显示图形
        self.contact_channel.chartSource.emit(json.dumps(data), '')
        self.finished.emit()


class VarietyProfitWidget(QScrollArea):
    finished = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(VarietyProfitWidget, self).__init__(*args, **kwargs)
        cw = QWidget(self)  # center widget

        layout = QVBoxLayout()
        self.chart = ChartEngineView(self)
        self.chart.setMinimumHeight(300)
        # 加载图形页面html
        self.chart.page().load(QUrl('file:///html/charts/varietyProfit.html'))
        # 设置与页面信息交互的通道
        channel_qt_obj = QWebChannel(self.chart.page())  # 实例化qt信道对象,必须传入页面参数
        self.contact_channel = ChartDataObj(self)  # 页面信息交互通道
        self.chart.page().setWebChannel(channel_qt_obj)
        channel_qt_obj.registerObject("pageContactChannel", self.contact_channel)  # 信道对象注册信道,只能注册一个

        layout.addWidget(self.chart)

        cw.setLayout(layout)
        self.setWidgetResizable(True)
        self.setWidget(cw)
        self.setStyleSheet("QScrollArea{background-color:#ffffff}")
        self.viewport().setStyleSheet("background-color:#ffffff")

        self.thread_ = None
        self.is_shown = False

    def resizeEvent(self, event):
        super(VarietyProfitWidget, self).resizeEvent(event)
        self.contact_channel.chartResize.emit(self.chart.width() - 50, 300)

    def clear_thread(self):
        if self.thread_:
            del self.thread_
            self.thread_ = None

    def handle_data(self, trade_detail):
        if self.is_shown:
            self.finished.emit()
            return
        self.clear_thread()
        self.thread_ = threads.HandleVarietyProfitThread(trade_detail, parent=self)
        self.thread_.finished.connect(self.thread_.deleteLater)
        self.thread_.handle_finished.connect(self.data_show)
        self.thread_.start()

    def data_show(self, data):
        # 传入数据到页面显示图形
        self.contact_channel.chartSource.emit(json.dumps(data), '')
        self.finished.emit()


class RiskControlWidget(QScrollArea):
    finished = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(RiskControlWidget, self).__init__(*args, **kwargs)
        cw = QWidget(self)  # center widget

        layout = QVBoxLayout()
        self.chart = ChartEngineView(self)
        self.chart.setMinimumHeight(300)
        # 加载图形页面html
        self.chart.page().load(QUrl('file:///html/charts/riskControl.html'))
        # 设置与页面信息交互的通道
        channel_qt_obj = QWebChannel(self.chart.page())  # 实例化qt信道对象,必须传入页面参数
        self.contact_channel = ChartDataObj(self)  # 页面信息交互通道
        self.chart.page().setWebChannel(channel_qt_obj)
        channel_qt_obj.registerObject("pageContactChannel", self.contact_channel)  # 信道对象注册信道,只能注册一个

        layout.addWidget(self.chart)

        cw.setLayout(layout)
        self.setWidgetResizable(True)
        self.setWidget(cw)
        self.setStyleSheet("QScrollArea{background-color:#ffffff}")
        self.viewport().setStyleSheet("background-color:#ffffff")

        self.thread_ = None
        self.is_shown = False

    def resizeEvent(self, event):
        super(RiskControlWidget, self).resizeEvent(event)
        self.contact_channel.chartResize.emit(self.chart.width() - 50, 300)

    def clear_thread(self):
        if self.thread_:
            del self.thread_
            self.thread_ = None

    def handle_data(self, account, trade_detail):
        if self.is_shown:
            self.finished.emit()
            return
        self.clear_thread()
        self.thread_ = threads.HandleRiskControlThread(account, trade_detail, parent=self)
        self.thread_.finished.connect(self.thread_.deleteLater)
        self.thread_.handle_finished.connect(self.data_show)
        self.thread_.start()

    def data_show(self, data):
        # 传入数据到页面显示图形
        self.contact_channel.chartSource.emit(json.dumps(data), '')
        self.finished.emit()