# _*_ coding:utf-8 _*_
# @File  : position.py
# @Time  : 2020-12-23 15:16
# @Author: zizle

""" 与持仓,净持仓有关的API """
import json
from PyQt5.QtCore import QObject, pyqtSignal, QUrl
from PyQt5.QtWidgets import qApp
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from settings import SERVER_API, logger


class PositionAPI(QObject):
    weekly_increase_data = pyqtSignal(dict)

    def __init__(self, *args, **kwargs):
        super(PositionAPI, self).__init__(*args, **kwargs)
        self.network_manager = getattr(qApp, '_network', None)
        if not self.network_manager:
            self.network_manager = QNetworkAccessManager(self)

    def get_weekly_increase(self, query_date: str, exclude_variety: str):
        """ 获取周度涨跌幅数据 """
        url = QUrl(SERVER_API + 'position-weight-price/')
        url.setQuery("date={}&exclude={}".format(query_date, exclude_variety))
        reply = self.network_manager.get(QNetworkRequest(url))
        reply.finished.connect(self.weekly_increase_reply)

    def weekly_increase_reply(self):
        """ 周度涨跌数据返回"""
        reply = self.sender()
        if reply.error():
            logger.error('GET-Request Weekly Increase Data Error!')
        else:
            data = json.loads(reply.readAll().data().decode('utf8'))
            self.weekly_increase_data.emit(data)
        reply.deleteLater()


