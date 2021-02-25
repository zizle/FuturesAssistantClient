# _*_ coding:utf-8 _*_
# @File  : czce_receipt.py
# @Time  : 2021-02-25 17:01
# @Author: zizle


# 郑商所的仓单爬虫

import os
import datetime
import random
import requests
from pandas import read_html
from PyQt5.QtWidgets import qApp
from PyQt5.QtNetwork import QNetworkRequest, QNetworkAccessManager
from PyQt5.QtCore import QObject, QUrl, pyqtSignal, QFile
from settings import USER_AGENTS, LOCAL_SPIDER_SRC


class CZCEReceiptSpider(QObject):
    spider_status = pyqtSignal(str, bool)
    parser_status = pyqtSignal(str, bool)

    def __init__(self, *args, **kwargs):
        super(CZCEReceiptSpider, self).__init__(*args, **kwargs)
        self.network_manager = getattr(qApp, '_network', QNetworkAccessManager(self))
        self.date = None

    def set_date(self, date):
        self.date = datetime.datetime.strptime(date, '%Y-%m-%d')

    def get_receipt_html(self):
        if not self.date:
            raise ValueError("date error. Please use `set_date` function to set date")
        url = "http://www.czce.com.cn/cn/DFSStaticFiles/Future/{}/{}/FutureDataWhsheet.htm".format(self.date.year,
                                                                                                   self.date.strftime(
                                                                                                       '%Y%m%d'))
        r = requests.get(url)
        save_path = os.path.join(LOCAL_SPIDER_SRC, 'czce/receipt/{}.html'.format(self.date.strftime("%Y-%m-%d")))
        with open(save_path, 'wb') as f:
            f.write(r.content)
        self.spider_status.emit('爬取郑商所{}HTML仓单文件成功!'.format(self.date.strftime("%Y-%m-%d")), True)

    def receipt_html_reply(self):
        reply = self.sender()
        if reply.error():
            self.spider_status.emit("获取郑商所{}的仓单源数据失败".format(self.date.strftime("%Y-%m-%d")), True)
        else:
            # 保存数据
            save_path = os.path.join(LOCAL_SPIDER_SRC, 'czce/receipt/{}.html'.format(self.date.strftime("%Y-%m-%d")))
            file_data = reply.readAll()
            file_obj = QFile(save_path)
            is_open = file_obj.open(QFile.WriteOnly)
            if is_open:
                file_obj.write(file_data)
                file_obj.close()
            self.spider_status.emit("获取郑商所{}每日仓单数据源文件成功!".format(self.date.strftime("%Y-%m-%d")), False)
        reply.deleteLater()

    def parser_receipts(self):

        # url = "http://www.czce.com.cn/cn/DFSStaticFiles/Future/{}/{}/FutureDataWhsheet.htm".format(self.date.year,
        #                                                                                            self.date.strftime(
        #                                                                                                '%Y%m%d'))
        # dfs = read_html(url)
        # for df in dfs:
        #     print(df)
        #
        # print(len(dfs))
        # 解析仓单数据文件
        file_path = os.path.join(LOCAL_SPIDER_SRC, "czce/receipt/{}.html".format(self.date.strftime("%Y-%m-%d")))
        if not os.path.exists(file_path):
            self.parser_status.emit("没有发现郑商所{}的仓单日报源文件,请先抓取数据!".format(self.date.strftime("%Y-%m-%d")), True)
            return
        html_dfs = read_html(file_path)  # 解析每个dfs,获取品种和对应的仓单数据情况
        for df in html_dfs:
            print(df)


