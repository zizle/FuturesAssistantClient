# _*_ coding:utf-8 _*_
# @File  : exchange_query.py
# @Time  : 2020-07-23 15:46
# @Author: zizle

""" 交易所数据查询 """

import pandas as pd
import json
from PyQt5.QtWidgets import (qApp, QTableWidgetItem, QWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QSplitter,
                             QTableWidget, QGridLayout, QDateEdit, QPushButton, QHBoxLayout, QMainWindow, QLabel, QFrame)
from PyQt5.QtCore import Qt, QTimer, QUrl, QMargins, QDate, QTime
from PyQt5.QtGui import QIcon, QFont, QBrush, QColor
from PyQt5.QtNetwork import QNetworkRequest
from .exchange_query_ui import ExchangeQueryUI
from widgets import TreeWidget, OptionWidget, GridWidget, LoadingCover
from utils.constant import VARIETY_ZH, HORIZONTAL_SCROLL_STYLE, VERTICAL_SCROLL_STYLE, HORIZONTAL_HEADER_STYLE
from settings import SERVER_API


class ExchangeQuery1(ExchangeQueryUI):
    """ 查询数据的业务 """
    _exchange_lib = {
        "cffex": "中国金融期货交易所",
        "shfe": "上海期货交易所",
        "czce": "郑州商品交易所",
        "dce": "大连商品交易所"
    }
    _actions = {
        "daily": "日交易数据",
        "rank": "日交易排名",
        "receipt": "每日仓单"
    }

    def __init__(self, *args, **kwargs):
        super(ExchangeQuery, self).__init__(*args, **kwargs)

        self.current_exchange = None
        self.current_action = None

        self.tip_timer = QTimer(self)  # 显示查询中文字
        self.tip_timer.timeout.connect(self.animation_tip_text)

        self.exchange_tree.selected_signal.connect(self.selected_action)  # 树控件点击事件
        self.exchange_tree.unselected_signal.connect(self.unselected_any)  # 没有选择项目
        # self.query_button.clicked.connect(self.query_target_data)            # 查询合约详情数据
        self.query_button.hide()  # (20200925关闭,由控件默认查询)
        self.query_variety_sum_button.clicked.connect(self.query_variety_sum)  # 查询品种合计数

    def keyPressEvent(self, event):
        """ Ctrl + C复制表格内容 """
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_C:
            # 获取表格的选中行
            selected_ranges = self.show_table.selectedRanges()[0]
            text_str = ""
            # 行
            for row in range(selected_ranges.topRow(), selected_ranges.bottomRow() + 1):
                row_str = ""
                # 列
                for col in range(selected_ranges.leftColumn(), selected_ranges.rightColumn() + 1):
                    item = self.show_table.item(row, col)
                    row_str += item.text() + '\t'
                text_str += row_str + '\n'
            clipboard = qApp.clipboard()
            clipboard.setText(text_str)

    def is_allow_query(self):
        """ 是否允许查询判断函数 """
        self.tip_label.show()
        if self.current_exchange is None or self.current_action is None:
            self.tip_label.setText("左侧选择想要查询的数据类别再进行查询.")
            return False
        else:
            self.tip_label.setText("正在查询相关数据 ")
            return True

    def animation_tip_text(self):
        """ 动态展示查询文字提示 """
        tips = self.tip_label.text()
        tip_points = tips.split(' ')[1]
        if len(tip_points) > 2:
            self.tip_label.setText("正在查询相关数据 ")
        else:
            self.tip_label.setText("正在查询相关数据 " + "·" * (len(tip_points) + 1))

    def selected_action(self, exchange, action):
        """ 目录树点击信号 """
        self.current_exchange = exchange
        self.current_action = action
        if self.current_action == "rank":
            self.rank_select.show()
        else:
            self.rank_select.hide()
        # 默认进行详情数据的查询
        self.query_target_data()

    def unselected_any(self):
        """ 没有选择项目 """
        self.current_exchange = None
        self.current_action = None

    def query_target_data(self):
        """ 点击确定查询合约详情目标数据 """
        if not self.is_allow_query():
            return
        self.tip_timer.start(400)
        # 清除table
        self.show_table.clear()
        self.show_table.setRowCount(0)
        self.show_table.setColumnCount(0)
        # 查询数据进行展示
        current_date = self.query_date_edit.text()
        # app = QApplication.instance()
        network_manger = getattr(qApp, "_network")

        url = SERVER_API + "exchange/" + self.current_exchange + "/" + self.current_action + "/?date=" + current_date
        request = QNetworkRequest(QUrl(url))
        reply = network_manger.get(request)
        reply.finished.connect(self.query_result_reply)

    def query_variety_sum(self):
        """ 查询各品种的合计数 """
        if not self.is_allow_query():
            return
        # 清除table
        self.tip_timer.start(400)
        self.show_table.clear()
        self.show_table.setRowCount(0)
        self.show_table.setColumnCount(0)
        # 查询数据进行展示
        current_date = self.query_date_edit.text()
        # app = QApplication.instance()
        network_manger = getattr(qApp, "_network")

        url = SERVER_API + "exchange/" + self.current_exchange + "/" + self.current_action + "/variety-sum/?date=" + current_date
        if self.rank_select.isEnabled():
            url += "&rank=" + str(self.rank_select.value())
        request = QNetworkRequest(QUrl(url))
        reply = network_manger.get(request)
        reply.finished.connect(self.query_result_reply)

    def query_result_reply(self):
        """ 请求数据返回结果 """
        reply = self.sender()
        if reply.error():
            self.tip_label.setText("失败:{}".format(reply.error()))
            return
        data = reply.readAll().data()
        data = json.loads(data.decode("utf-8"))
        reply.deleteLater()
        self.show_table_fill_contents(data['content_keys'], data["result"])  # 数据表显示数据
        self.tip_timer.stop()
        self.tip_label.setText("查询成功!")

    def show_table_fill_contents(self, headers, contents):
        """ 查询到的数据填到表格中 """
        self.show_table.setColumnCount(len(headers))
        self.show_table.setRowCount(len(contents))
        headers_keys = list()
        headers_labels = list()
        for key, value in headers.items():
            headers_keys.append(key)
            headers_labels.append(value)
        self.show_table.setHorizontalHeaderLabels(headers_labels)
        for row, row_item in enumerate(contents):
            self.show_table.setRowHeight(row, 20)
            for col, value_key in enumerate(headers_keys):
                item = QTableWidgetItem(str(row_item[value_key]))
                item.setTextAlignment(Qt.AlignCenter)
                self.show_table.setItem(row, col, item)


""" UI类 """


class VarietyButton(QPushButton):
    """ 选择品种的按钮 """
    def __init__(self, *args, **kwargs):
        super(VarietyButton, self).__init__(*args, **kwargs)
        self.setObjectName('varietyBtn')
        self.setFixedSize(66, 22)
        self.setCursor(Qt.PointingHandCursor)
        # self.setCheckable(True)
        self.setStyleSheet(
            "#varietyBtn{border:1px solid rgb(160,160,170)}"
            "#varietyBtn:hover{color:rgb(250,250,250);background-color:rgb(65,99,161)}"
            # "#varietyBtn:checked{background-color:rgb(0,164,172);color:rgb(250,250,250)}"
        )


class ExchangeDataShow(QWidget):
    """ 查询交易所数据操作页面 """

    def __init__(self, exchange, data_type='daily', *args, **kwargs):
        super(ExchangeDataShow, self).__init__(*args, **kwargs)
        """ UI部分 """
        # 操作头
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(QMargins(0, 0, 0, 0))
        option_widget = OptionWidget(self)
        option_layout = QVBoxLayout()
        query_layout = QHBoxLayout()
        # 日期编辑
        initialize_date = QDate.currentDate()
        if QTime.currentTime() < QTime(15, 50, 00):  # 小于15:50分时默认为前一天
            initialize_date = initialize_date.addDays(-1)
        while initialize_date.dayOfWeek() > 5:  # 当为周末时往前推日期
            initialize_date = initialize_date.addDays(-1)
        self.query_date_edit = QDateEdit(initialize_date, self)
        self.query_date_edit.setCalendarPopup(True)
        self.query_date_edit.setDisplayFormat("yyyy-MM-dd")
        query_layout.addWidget(self.query_date_edit)
        # 查询按钮
        self.query_button = QPushButton('查询', self)
        query_layout.addWidget(self.query_button)
        query_layout.addStretch()
        option_layout.addLayout(query_layout)
        # 品种显示
        self.variety_widget = GridWidget(self)
        option_layout.addWidget(self.variety_widget)

        option_widget.setLayout(option_layout)

        main_layout.addWidget(option_widget)

        # 显示框
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(QMargins(5, 5, 5, 5))
        self.data_table = QTableWidget(self)
        self.data_table.verticalHeader().hide()
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setFrameShape(QFrame.NoFrame)
        self.data_table.horizontalHeader().setStyleSheet(HORIZONTAL_HEADER_STYLE)
        self.data_table.horizontalScrollBar().setStyleSheet(HORIZONTAL_SCROLL_STYLE)
        self.data_table.verticalScrollBar().setStyleSheet(VERTICAL_SCROLL_STYLE)
        content_layout.addWidget(self.data_table)
        main_layout.addLayout(content_layout)

        self.setLayout(main_layout)
        self.data_table.setObjectName('dataTable')
        self.setStyleSheet(
            "#dataTable{selection-color:rgb(80,100,200);selection-background-color:rgb(220,220,220);"
            "alternate-background-color:rgb(242,242,242);gridline-color:rgb(60,60,60)}"
        )
        self.loading_cover = LoadingCover(self)
        self.loading_cover.resize(self.parent().width(), self.parent().height())
        self.loading_cover.hide()

        """ 逻辑部分 """
        self.current_exchange = exchange
        self.data_type = data_type

        self.network_manger = getattr(qApp, '_network')
        # 获取品种
        self.get_variety_with_current_exchange()
        # 查询
        self.query_button.clicked.connect(self.get_current_variety_data)
        
    def resizeEvent(self, event):
        super(ExchangeDataShow, self).resizeEvent(event)
        self.loading_cover.resize(self.parent().width(), self.parent().height())

    def get_variety_with_current_exchange(self):
        """ 查询当前交易所的所有品种 """
        if self.current_exchange is None:
            return
        url = SERVER_API + 'exchange-variety/?exchange={}&is_real=1'.format(self.current_exchange)
        reply = self.network_manger.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(self.exchange_variety_reply)

    def exchange_variety_reply(self):
        reply = self.sender()
        if reply.error():
            varieties = []
        else:
            data = json.loads(reply.readAll().data().decode('utf8'))
            varieties = data['varieties']
        reply.deleteLater()
        widgets_list = []
        for variety_item in varieties:
            button = VarietyButton(variety_item['variety_name'])  # 不要设置parent父控件
            setattr(button, 'variety_en', variety_item['variety_en'])
            button.clicked.connect(self.selected_variety)
            widgets_list.append(button)
        self.variety_widget.set_widgets(66, widgets_list)

    def selected_variety(self):
        """ 选择当前交易所某个品种 """
        button = self.sender()
        variety_en = getattr(button, 'variety_en')
        self.get_current_variety_data(variety=variety_en)

    def get_current_variety_data(self, variety):
        """ 获取当前的数据 """
        self.loading_cover.show('正在获取数据')
        self.data_table.clear()
        self.data_table.setRowCount(0)
        self.data_table.setColumnCount(0)
        url = SERVER_API + 'exchange/{}/{}/?date={}'.format(self.current_exchange, self.data_type,
                                                            self.query_date_edit.text())
        if variety:
            url += '&variety={}'.format(variety)

        reply = self.network_manger.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(self.current_data_reply)

    def current_data_reply(self):
        """ 当前数据返回 """
        reply = self.sender()
        if reply.error():
            pass
        else:
            data = json.loads(reply.readAll().data().decode('utf8'))
            if self.data_type == 'daily':
                self.table_show_daily_content(data['content_keys'], data['result'])
            if self.data_type == 'rank':
                self.table_show_rank_content(data['content_keys'], data['result'])
        reply.deleteLater()
        self.loading_cover.hide()

    def table_show_daily_content(self, content_key: dict, content_values: list):
        """ 显示数据 """
        columns = list(content_key.keys())
        # 填表
        column_count = len(columns)
        self.data_table.setColumnCount(column_count)
        # 设置表头
        self.data_table.setHorizontalHeaderLabels([content_key[key] for key in columns])
        # 显示数据
        current_variety = ''  # 品种头
        # 计算成交量和持仓量和变化
        for row_item in content_values:
            row = self.data_table.rowCount()
            if current_variety != row_item['variety_en']:  # 显示商品名称
                self.data_table.insertRow(row)  # 添加一行显示名称
                self.data_table.setSpan(row, 0, 1, column_count)  # 合并单元格
                item = QTableWidgetItem(str(row_item['variety_zh']))
                item.setBackground(QBrush(QColor(255, 245, 187)))
                self.data_table.setItem(row, 0, item)
                current_variety = row_item['variety_en']
                row += 1
            self.data_table.insertRow(row)  # 添加一行开始显示数据
            for col, col_key in enumerate(columns):
                item = QTableWidgetItem(str(row_item[col_key]))
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.data_table.setItem(row, col, item)

    def table_show_rank_content(self, content_key: dict, content_values: list):
        columns = list(content_key.keys())
        # 填表
        column_count = len(columns)
        self.data_table.setColumnCount(column_count)
        # 设置表头
        self.data_table.setHorizontalHeaderLabels([content_key[key] for key in columns])
        # 显示数据
        current_contract = ''  # 品种头
        # 计算成交量和持仓量和变化
        for row_item in content_values:
            row = self.data_table.rowCount()
            if current_contract != row_item['contract']:  # 显示商品名称
                self.data_table.insertRow(row)  # 添加一行显示名称
                self.data_table.setSpan(row, 0, 1, column_count)  # 合并单元格
                contract_text = '{} {}'.format(row_item['variety_zh'], row_item['contract'])
                item = QTableWidgetItem(contract_text)
                item.setBackground(QBrush(QColor(255, 245, 187)))
                self.data_table.setItem(row, 0, item)
                current_contract = row_item['contract']
                row += 1
            self.data_table.insertRow(row)  # 添加一行开始显示数据
            for col, col_key in enumerate(columns):
                item = QTableWidgetItem(str(row_item[col_key]))
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.data_table.setItem(row, col, item)


class CFFEXDataShow(ExchangeDataShow):
    pass


class CZCEDataShow(ExchangeDataShow):
    pass


class DCEDataShow(ExchangeDataShow):
    pass


class SHFEDataShow(ExchangeDataShow):
    pass


class ExchangeQuery(QWidget):
    """ 交易所数据查询主页面 """

    def __init__(self, *args, **kwargs):
        super(ExchangeQuery, self).__init__(*args, **kwargs)
        """ UI部分 """
        layout = QVBoxLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        splitter = QSplitter(self)

        # 左侧菜单
        self.tree_menu = TreeWidget(self)
        splitter.addWidget(self.tree_menu)

        # 右侧
        self.right_widget = QMainWindow(self)

        splitter.addWidget(self.right_widget)
        splitter.setHandleWidth(1)
        self.tree_menu.setMinimumWidth(220)
        splitter.setSizes([self.parent().width() * 0.18, self.parent().width() * 0.82])
        layout.addWidget(splitter)

        self.setLayout(layout)

        self.current_exchange = None

        # 添加菜单
        self.add_list_menu()

        # 左侧菜单点击事件
        self.tree_menu.itemClicked.connect(self.left_menu_selected)

    def add_list_menu(self):
        """ 添加左侧菜单 """
        lib = [
            {
                "id": "cffex", "name": "中国金融期货交易所", "logo": "media/icons/cffex_logo.png",
                "children": [
                    {"id": "daily", "name": "日交易数据", "logo": "media/icons/point.png"},
                    {"id": "rank", "name": "持仓排名", "logo": "media/icons/point.png"},
                ]
            },
            {
                "id": "czce", "name": "郑州商品交易所", "logo": "media/icons/czce_logo.png",
                "children": [
                    {"id": "daily", "name": "日交易数据", "logo": "media/icons/point.png"},
                    {"id": "rank", "name": "持仓排名", "logo": "media/icons/point.png"},
                ]
            },
            {
                "id": "dce", "name": "大连商品交易所", "logo": "media/icons/dce_logo.png",
                "children": [
                    {"id": "daily", "name": "日交易数据", "logo": "media/icons/point.png"},
                    {"id": "rank", "name": "持仓排名", "logo": "media/icons/point.png"},
                ]
            },
            {
                "id": "shfe", "name": "上海期货交易所", "logo": "media/icons/shfe_logo.png",
                "children": [
                    {"id": "daily", "name": "日交易数据", "logo": "media/icons/point.png"},
                    {"id": "rank", "name": "持仓排名", "logo": "media/icons/point.png"},
                ]
            },
        ]
        bold_font = QFont()
        bold_font.setBold(True)
        for item in lib:
            tree_item = QTreeWidgetItem()
            tree_item.setText(0, item["name"])
            setattr(tree_item, "id", item["id"])
            # tree_item.setTextAlignment(0, Qt.AlignRight | Qt.AlignVCenter)
            tree_item.setIcon(0, QIcon(item["logo"]))
            tree_item.setFont(0, bold_font)
            self.tree_menu.addTopLevelItem(tree_item)
            for child_item in item["children"]:
                child = QTreeWidgetItem(tree_item)
                child.setText(0, child_item["name"])
                setattr(child, "id", child_item["id"])
                child.setIcon(0, QIcon(child_item["logo"]))
                # child.setTextAlignment(0, Qt.AlignRight | Qt.AlignVCenter)
                tree_item.addChild(child)

    def left_menu_selected(self, tree_item):
        """ 选择左侧菜单 """
        if tree_item.childCount():
            if tree_item.isExpanded():
                tree_item.setExpanded(False)
                # tree_item.setIcon(0, QIcon("icons/arrow_right.png"))
            else:
                tree_item.setExpanded(True)
                # tree_item.setIcon(0, QIcon("icons/arrow_bottom.png"))
            parent_id = getattr(tree_item, "id")
            self.current_exchange = parent_id
            # 请求交易所的所有品种
            # self.get_variety_with_current_exchange()
            # 显示界面
            self.set_data_show_page(parent_id, 'daily')  # 默认查询日行情数据
        elif tree_item.parent():
            item_id = getattr(tree_item, "id")
            parent_id = getattr(tree_item.parent(), "id")
            if parent_id != self.current_exchange:
                self.current_exchange = parent_id
                # 请求交易所的所有品种
                # self.get_variety_with_current_exchange()
            # 获取当前交易所当前类型的所有品种所有数据
            # 显示界面
            self.set_data_show_page(parent_id, item_id)
        else:
            pass

    def set_data_show_page(self, exchange, data_type):
        """ 设置哪个交易所的页面 """
        if not self.current_exchange:
            return
        if exchange == 'cffex':
            page = CFFEXDataShow('cffex', data_type, self)
        elif exchange == 'czce':
            page = CZCEDataShow('czce', data_type, self)
        elif exchange == 'dce':
            page = DCEDataShow('dce', data_type, self)
        elif exchange == 'shfe':
            page = SHFEDataShow('shfe', data_type, self)
        else:
            page = QLabel('暂未开放', self)
        self.right_widget.setCentralWidget(page)
