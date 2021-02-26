# _*_ coding:utf-8 _*_
# @File  : exchange_spider.py
# @Time  : 2020-07-22 21:00
# @Author: zizle
import json
import datetime
from PyQt5.QtWidgets import QTableWidgetItem, qApp
from PyQt5.QtNetwork import QNetworkRequest
from PyQt5.QtCore import QUrl
from .exchange_spider_ui import ExchangeSpiderUI
from spiders.czce import CZCESpider, CZCEParser
from spiders.shfe import SHFESpider, SHFEParser
from spiders.cffex import CFFEXSpider, CFFEXParser
from spiders.dce import DCESpider, DCEParser
from utils.client import get_user_token
from popup.message import InformationPopup
from settings import SERVER_API


class ExchangeSpider(ExchangeSpiderUI):
    """ 数据抓取业务 """
    _exchange_lib = {
        "cffex": "中国金融期货交易所",
        "czce": "郑州商品交易所",
        "dce": "大连商品交易所",
        "shfe": "上海期货交易所"
    }
    _actions = {
        "daily": "日交易数据",
        "rank": "日交易排名",
        "receipt": "每日仓单"
    }

    def __init__(self, *args, **kwargs):
        super(ExchangeSpider, self).__init__(*args, **kwargs)
        # 初始化未选择交易所和数据类型
        self.spider_exchange_combobox.addItem("未选择", None)
        self.parser_exchange_combobox.addItem("未选择", None)
        self.spider_data_combobox.addItem("未选择", None)
        self.parser_data_combobox.addItem("未选择", None)
        # 添加交易所和数据类型
        for exchange_name, exchange_en in self._exchange_lib.items():
            self.spider_exchange_combobox.addItem(exchange_en, exchange_name)
            self.parser_exchange_combobox.addItem(exchange_en, exchange_name)
        # 添加支持的数据类型
        for data_name, data_en in self._actions.items():
            self.spider_data_combobox.addItem(data_en, data_name)
            self.parser_data_combobox.addItem(data_en, data_name)

        # 点击抓取数据
        self.spider_start_button.clicked.connect(self.get_point_file)
        # 点击解析信号
        self.parser_start_button.clicked.connect(self.parser_point_file)
        # 点击保存的信号
        self.save_result_button.clicked.connect(self.save_parser_result)
        # 点击二次数据数据
        self.handle_button.clicked.connect(self.handle_exchange_data)

        # 关联爬取选择数据的信号
        self.spider_exchange_combobox.currentTextChanged.connect(self.change_current_spider)
        self.spider_data_combobox.currentTextChanged.connect(self.change_current_spider)
        # 管理解析数据的信号
        self.parser_exchange_combobox.currentTextChanged.connect(self.change_current_parser)
        self.parser_data_combobox.currentTextChanged.connect(self.change_current_parser)

        self.spider = None
        self.parser = None
        self.parser_result_df = None

        # self.tree_widget.selected_signal.connect(self.selected_action)  # 树控件点击事件
        # self.spider_start_button.clicked.connect(self.starting_spider_data)  # 开始抓取
        # self.parser_start_button.clicked.connect(self.starting_parser_data)  # 开始解析

    def change_current_spider(self):
        """ 选择爬虫 """
        if self.spider is not None:
            self.spider.deleteLater()
            self.spider = None
        current_exchange = self.spider_exchange_combobox.currentData()
        if current_exchange == "cffex":
            self.spider = CFFEXSpider()
        elif current_exchange == "czce":
            self.spider = CZCESpider()
        elif current_exchange == "dce":
            self.spider = DCESpider()
        elif current_exchange == "shfe":
            self.spider = SHFESpider()
        else:
            return
        self.spider.spider_finished.connect(self.spider_source_finished)

    def change_current_parser(self):
        """ 选择解析器 """
        if self.parser is not None:
            self.parser.deleteLater()
            self.parser = None
        if self.parser_result_df is not None:
            del self.parser_result_df
            self.parser_result_df = None
            self.save_result_button.setEnabled(False)
        current_exchange = self.parser_exchange_combobox.currentData()
        if current_exchange == "cffex":
            self.parser = CFFEXParser()
        elif current_exchange == "czce":
            self.parser = CZCEParser()
        elif current_exchange == "dce":
            self.parser = DCEParser()
        elif current_exchange == "shfe":
            self.parser = SHFEParser()
        else:
            return
        self.parser.parser_finished.connect(self.parser_source_finished)


    def get_point_file(self):
        """ 抓取当前数据源文件 """
        spider_data_type = self.spider_data_combobox.currentData()
        if self.spider is None or spider_data_type is None:
            self.spider_status.setText("请选择正确的交易所和数据类型再进行获取!")
            return
        self.spider_start_button.setEnabled(False)
        self.spider_start_button.update()
        status = "正在获取【" + self.spider_exchange_combobox.currentText() +\
                 "】的【" + self.spider_data_combobox.currentText() + "】的数据文件 "
        self.spider_status.setText(status)
        self.spider.set_date(self.spider_date_edit.text())
        if spider_data_type == "daily":
            self.spider.get_daily_source_file()
        elif spider_data_type == "rank":
            self.spider.get_rank_source_file()
        elif spider_data_type == "receipt":
            self.spider.get_receipt_source_file()
        else:
            pass

    def parser_point_file(self):
        """ 解析指定的数据文件 """
        self.save_result_button.setEnabled(False)
        parser_data_type = self.parser_data_combobox.currentData()
        parser_exchange_lib = self.parser_exchange_combobox.currentText()
        exchange_lib = self.parser_exchange_combobox.currentData()
        if self.parser is None or parser_data_type is None:
            self.parser_status.setText("请选择正确的交易所和数据类型再进行解析!")
            return
        self.parser_start_button.setEnabled(False)
        message = "正在解析【{}】的【{}】的数据··· ".format(parser_exchange_lib, parser_data_type)
        self.parser_status.setText(message)
        self.parser.set_date(self.parser_date_edit.text())

        if parser_data_type == "daily":  # 解析每日行情
            source_data_frame = self.parser.parser_daily_source_file()
            if source_data_frame.empty:
                return
            # 预览表格显示数据
            self.preview_parser_result(source_data_frame, exchange_lib, "daily")
            self.parser_status.setText(
                "解析{}的日行情数据完成!日期:{} = {}".format(
                    parser_exchange_lib, self.parser_date_edit.text(), int(datetime.datetime.strptime(
                        self.parser_date_edit.text(), '%Y-%m-%d').timestamp()
                    )
                )
            )
        elif parser_data_type == "rank":
            source_data_frame = self.parser.parser_rank_source_file()
            if source_data_frame.empty:
                return
            # 预览数据
            self.preview_parser_result(source_data_frame, exchange_lib, "rank")
            self.parser_status.setText(
                "解析{}的日排名数据完成!日期:{} = {}".format(
                    parser_exchange_lib, self.parser_date_edit.text(), int(datetime.datetime.strptime(
                        self.parser_date_edit.text(), '%Y-%m-%d').timestamp()
                    )
                )
            )
        # 解析的交易所
        elif parser_data_type == "receipt":
            source_data_frame = self.parser.parser_receipt_source_file()
            if source_data_frame.empty:
                return
            # 预览数据
            self.preview_parser_result(source_data_frame, exchange_lib, "receipt")
            self.parser_status.setText(
                "解析{}的仓单日报数据完成!日期:{} = {}".format(
                    parser_exchange_lib, self.parser_date_edit.text(), int(datetime.datetime.strptime(
                        self.parser_date_edit.text(), '%Y-%m-%d').timestamp()
                                                                           )
                )
            )
        else:
            pass


    # def selected_action(self, exchange, action):
    #     """ 树控件菜单点击传出信号 """
    #     self.current_exchange = exchange
    #     self.current_action = action
    #
    #     self.spider_exchange_button.setText(self._exchange_lib[exchange])
    #     self.spider_exchange_button.setIcon(QIcon("icons/" + exchange + "_logo.png"))
    #
    #     self.parser_exchange_button.setText(self._exchange_lib[exchange])
    #     self.parser_exchange_button.setIcon(QIcon("icons/" + exchange + "_logo.png"))
    #
    #     self.spider_action_button.setText(self._actions[action])
    #     self.spider_action_button.setIcon(QIcon("icons/" + action + ".png"))
    #
    #     self.parser_action_button.setText(self._actions[action])
    #     self.parser_action_button.setIcon(QIcon("icons/" + action + ".png"))
    #
    #     if self.spider is not None:
    #         self.spider.deleteLater()
    #         self.spider = None
    #     if self.parser is not None:
    #         self.parser.deleteLater()
    #         self.parser = None
    #
    #     if self.current_exchange == "czce":
    #         self.spider = CZCESpider()
    #         self.parser = CZCEParser()
    #     elif self.current_exchange == "shfe":
    #         self.spider = SHFESpider()
    #         self.parser = SHFEParser()
    #     elif self.current_exchange == "cffex":
    #         self.spider = CFFEXSpider()
    #         self.parser = CFFEXParser()
    #     elif self.current_exchange == "dce":
    #         self.spider = DCESpider()
    #         self.parser = DCEParser()
    #     else:
    #         return
    #     self.spider.spider_finished.connect(self.spider_source_finished)
    #     self.parser.parser_finished.connect(self.parser_source_finished)

    def spider_source_finished(self, message, can_reconnect):
        """ 当获取源文件爬虫结束返回的信号 """
        self.spider_status.setText(message)
        if can_reconnect:
            self.spider_start_button.setEnabled(True)

    def parser_source_finished(self, message, can_reconnect):
        """ 解析数据返回的信号 """
        self.parser_status.setText(message)
        if can_reconnect:
            self.parser_start_button.setEnabled(True)

    # def starting_spider_data(self):
    #     """ 点击开始抓取按钮 """
    #     if self.spider is None:
    #         self.spider_status.setText("爬取源数据时,软件内部发生了一个错误!")
    #         return
    #     self.spider_status.setText("开始获取【" + self._exchange_lib[self.current_exchange] + "】的【" + self._actions[self.current_action] + "】源数据.")
    #     self.spider_start_button.clicked.disconnect()
    #     current_date = self.spider_date_edit.text()
    #     self.spider.set_date(current_date)  # 设置日期
    #     if self.current_action == "daily":
    #         self.spider.get_daily_source_file()
    #     elif self.current_action == "rank":
    #         self.spider.get_rank_source_file()
    #     elif self.current_action == "receipt":
    #         self.spider.get_receipt_source_file()
    #     else:
    #         pass
    #
    # def starting_parser_data(self):
    #     if self.parser is None:
    #         self.parser_status.setText("解析源数据文件时,软件内部发生了一个错误!")
    #         return
    #     self.parser_status.setText("开始解析【" + self._exchange_lib[self.current_exchange] + "】的【" + self._actions[self.current_action] + "】源数据.")
    #     self.parser_start_button.clicked.disconnect()
    #     current_date = self.parser_date_edit.text()
    #     self.parser.set_date(current_date)
    #     if self.current_action == "daily":
    #         source_data_frame = self.parser.parser_daily_source_file()
    #         if source_data_frame.empty:
    #             self.parser_status.setText("结果【" + self._exchange_lib[self.current_exchange] + "】的【日交易行情】数据为空.")
    #             return
    #         # 保存数据到服务器数据库
    #         self.parser.save_daily_server(source_df=source_data_frame)
    #     elif self.current_action == "rank":
    #         source_data_frame = self.parser.parser_rank_source_file()
    #         if source_data_frame.empty:
    #             self.parser_status.setText("结果【" + self._exchange_lib[self.current_exchange] + "】的【日持仓排名】数据为空.")
    #             return
    #         # 保存数据到服务器数据库
    #         self.parser.save_rank_server(source_df=source_data_frame)
    #     elif self.current_action == "receipt":
    #         source_data_frame = self.parser.parser_receipt_source_file()
    #         if source_data_frame.empty:
    #             self.parser_status.setText("结果【" + self._exchange_lib[self.current_exchange] + "】的【仓单日报】数据为空.")
    #             return
    #         # 保存数据到服务器数据库
    #         self.parser.save_receipt_server(source_df=source_data_frame)
    #     else:
    #         pass

    def preview_parser_result(self, result_df, exchange_lib, data_type):
        """ 显示解析的结果 """
        # for i in result_df.itertuples():
        #     print(i)
        if data_type == "daily":
            column_labels = [
                "日期", "品种代码", "合约", "前结算", "开盘价", "最高价", "最低价", "收盘价", "结算价", "涨跌1", "涨跌2",
                "成交量", "成交额", "持仓量", "持仓变化"
            ]
            column_key = [
                "date", "variety_en", "contract", "pre_settlement", "open_price", "highest", "lowest", "close_price",
                "settlement", "zd_1", "zd_2", "trade_volume", "trade_price", "empty_volume", "increase_volume"]
            if exchange_lib == "shfe":  # 上期所没有成交额
                column_labels.remove("成交额")
                column_key.remove("trade_price")
        elif data_type == "rank":
            column_labels = [
                "日期", "品种代码", "合约", "排名", "公司1", "成交量", "成交量变化", "公司2", "买单量", "买单量变化",
                "公司3", "卖单量", "卖单量变化"]
            column_key = [
                "date", "variety_en", "contract","rank", "trade_company", "trade", "trade_increase", "long_position_company",
                "long_position", "long_position_increase", "short_position_company", "short_position",
                "short_position_increase"]
        elif data_type == "receipt":
            column_labels = ["日期", "品种代码", "仓单数量", "当日增减"]
            column_key = ["date", "variety_en", "receipt", "increase"]
        else:
            return
        # 清空表格显示数据
        preview_data = result_df.to_dict(orient='records')
        self.preview_values.clear()
        self.preview_values.setColumnCount(len(column_key))
        self.preview_values.setRowCount(len(preview_data))
        self.preview_values.setHorizontalHeaderLabels(column_labels)
        for row, row_item in enumerate(preview_data):
            for col, col_key in enumerate(column_key):
                item = QTableWidgetItem(str(row_item[col_key]))
                self.preview_values.setItem(row, col, item)
        # 将数据表存到属性
        self.parser_result_df = result_df.copy()
        self.save_result_button.setEnabled(True)

    def save_parser_result(self):
        """ 保存解析预览后的结果 """
        if self.parser_result_df is None:
            self.parser_status.setText("请先解析数据再进行保存!")
            return
        self.save_result_button.setEnabled(False)
        # 当前的数据类型
        current_data_type = self.parser_data_combobox.currentData()
        # 执行保存数据
        if current_data_type == "daily":
            self.parser.save_daily_server(self.parser_result_df)
        elif current_data_type == "rank":
            self.parser.save_rank_server(self.parser_result_df)
        elif current_data_type == "receipt":
            self.parser.save_receipt_server(self.parser_result_df)
        else:
            pass
        # 清空表
        self.preview_values.clear()
        self.preview_values.setColumnCount(0)
        self.preview_values.setRowCount(0)

    def handle_exchange_data(self):
        current_handle = self.handle_combobox.currentData()
        if current_handle == 'net_position':
            url = SERVER_API + 'rank-position/'
        elif current_handle == 'price_position':
            url = SERVER_API + 'price-position/'
        elif current_handle == 'price_index':
            url = SERVER_API + 'price-index/'
        else:
            url = ''
        self.generate_target_data(url)

    def generate_target_data(self, url):
        """ 生成目标数据 """
        if not url:
            return
        self.parser_status.setText("系统正在生处理数据,请稍后...")
        option_day = self.parser_date_edit.text().replace("-", "")
        network_manager = getattr(qApp, "_network")
        request = QNetworkRequest(QUrl(url))
        request.setRawHeader('Authorization'.encode('utf-8'), get_user_token().encode('utf-8'))
        reply = network_manager.post(request, json.dumps({"option_day": option_day}).encode("utf8"))
        reply.finished.connect(self.handle_exchange_lib_data_reply)

    def handle_exchange_lib_data_reply(self):
        """ 生成全品种净持仓返回 """
        reply = self.sender()
        if reply.error():
            p = InformationPopup("生成数据失败了:{}".format(reply.error()), self)
        else:
            data = reply.readAll().data().decode("utf8")
            data = json.loads(data)
            p = InformationPopup(data["message"], self)
            self.parser_status.setText(data["message"])
        p.exec_()
        reply.deleteLater()
