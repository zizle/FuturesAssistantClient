# _*_ coding:utf-8 _*_
# @File  : caculate_plat.py
# @Time  : 2021-01-25 11:05
# @Author: zizle

# 计算平台部分APi
import json
from PyQt5.QtWidgets import qApp
from PyQt5.QtNetwork import QNetworkRequest, QNetworkAccessManager
from PyQt5.QtCore import QObject, pyqtSignal, QUrl
from settings import SERVER_API, logger


class ExchangeRateAPI(QObject):
    exchange_rate_reply = pyqtSignal(dict)

    def __init__(self, *args, **kwargs):
        super(ExchangeRateAPI, self).__init__(*args, **kwargs)
        self.network_manger = getattr(qApp, '_network', QNetworkAccessManager(self))

    def get_exchange_rate(self):
        url = SERVER_API + 'datalib/exchange-rate/'
        reply = self.network_manger.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(self.get_rate_reply)

    def get_rate_reply(self):
        reply = self.sender()
        if reply.error():
            logger.error('GET-Request exchange_rate Error:{}'.format(reply.error()))
        else:
            data = json.loads(reply.readAll().data().decode('utf8'))
            self.exchange_rate_reply.emit(data)
        reply.deleteLater()


class CorrelationAPI(QObject):
    correlation_reply = pyqtSignal(dict)

    def __init__(self, *args, **kwargs):
        super(CorrelationAPI, self).__init__(*args, **kwargs)
        self.network_manger = getattr(qApp, '_network', QNetworkAccessManager(self))

    def get_correlations(self, st, et):
        # 请求相关性计算的数据，st=开始日期,et=结束日期
        url = SERVER_API + 'correlation/?ts={}&es={}'.format(st, et)
        reply = self.network_manger.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(self.correlation_data_reply)

    def correlation_data_reply(self):
        reply = self.sender()
        if reply.error():
            logger.error('GET-Request Correlation Data Error:{}'.format(reply.error()))
        else:
            data = json.loads(reply.readAll().data().decode('utf8'))
            self.correlation_reply.emit(data)
        reply.deleteLater()

