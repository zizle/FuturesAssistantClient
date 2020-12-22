# _*_ coding:utf-8 _*_
# @File  : message_service.py
# @Time  : 2020-12-22 14:17
# @Author: zizle
import json
from PyQt5.QtCore import QObject, pyqtSignal, QUrl
from PyQt5.QtWidgets import qApp
from PyQt5.QtNetwork import QNetworkRequest, QNetworkAccessManager
from settings import SERVER_API, logger


""" 短讯通API """


class ShortMsgAPI(QObject):
    short_messages_reply = pyqtSignal(dict)

    def __init__(self, *args, **kwargs):
        super(ShortMsgAPI, self).__init__(*args, **kwargs)
        self.network_manager = getattr(qApp, '_network', None)
        if not self.network_manager:
            self.network_manager = QNetworkAccessManager(self)

    def get_time_quantum_short_message(self, start_time: str):
        """ 获取最新时间段内的短讯息 """
        url = SERVER_API + "short-message/?start_time={}".format(start_time)
        reply = self.network_manager.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(self.latest_short_message_reply)

    def latest_short_message_reply(self):
        reply = self.sender()
        if reply.error():
            logger.error('GET-Request time_quantum_short_message ERROR!')
        else:
            data = json.loads(reply.readAll().data().decode("utf-8"))
            self.short_messages_reply.emit(data)
        reply.deleteLater()


""" 报告的API """


class ReportsAPI(QObject):
    reports_reply_signal = pyqtSignal(dict)

    def __init__(self, *args, **kwargs):
        super(ReportsAPI, self).__init__(*args, **kwargs)
        self.network_manager = getattr(qApp, '_network', None)
        if not self.network_manager:
            self.network_manager = QNetworkAccessManager(self)

    def get_paginator_reports(self, report_type: str, variety_en: str, page: int, page_size: int):
        """ 获取报告 """
        url = QUrl(SERVER_API + 'report-file/paginator/')
        url.setQuery("report_type={}&variety_en={}&page={}&page_size={}".format(
            report_type, variety_en, page, page_size))
        reply = self.network_manager.get(QNetworkRequest(url))
        reply.finished.connect(self.reports_reply)

    def reports_reply(self):
        reply = self.sender()
        if reply.error():
            logger.error('GET-Request variety with en sorted ERROR!')
        else:
            data = json.loads(reply.readAll().data().decode('utf8'))
            self.reports_reply_signal.emit(data)
        reply.deleteLater()

