# _*_ coding:utf-8 _*_
# @File  : strategy_service.py
# @Time  : 2021-01-20 09:53
# @Author: zizle

# 策略服务的API
import json
from PyQt5.QtWidgets import qApp
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt5.QtCore import QObject, pyqtSignal, QUrl

from utils.client import get_user_token
from settings import SERVER_API, logger

""" 交易策略API """


class ExchangeStrategyAPI(QObject):
    strategy_reply = pyqtSignal(dict)

    def __init__(self, *args, **kwargs):
        super(ExchangeStrategyAPI, self).__init__(*args, **kwargs)
        self.network_manager = getattr(qApp, '_network', None)
        if not self.network_manager:
            self.network_manager = QNetworkAccessManager(self)

    def get_strategy(self):
        """ 请求交易策略 """
        url = QUrl(SERVER_API + 'consultant/strategy/')
        url.setQuery('admin=0&user_token={}'.format(get_user_token(raw=True)))
        reply = self.network_manager.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(self.get_strategy_reply)

    def get_strategy_reply(self):
        reply = self.sender()
        if reply.error():
            logger.error('GET-Request get_strategy ERROR!')
        else:
            data = json.loads(reply.readAll().data().decode("utf-8"))
            self.strategy_reply.emit(data)
        reply.deleteLater()
