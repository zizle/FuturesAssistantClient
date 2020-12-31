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
    paginator_reports_response = pyqtSignal(dict)
    date_query_reports_response = pyqtSignal(dict)
    modify_report_message_response = pyqtSignal(bool)
    delete_report_response = pyqtSignal(bool)

    def __init__(self, *args, **kwargs):
        super(ReportsAPI, self).__init__(*args, **kwargs)
        self.network_manager = getattr(qApp, '_network', None)
        if not self.network_manager:
            self.network_manager = QNetworkAccessManager(self)

    def get_paginator_reports(self, report_type: str, variety_en: str, page: int, page_size: int):
        """ 分页的形式获取报告 """
        url = QUrl(SERVER_API + 'report-file/paginator/')
        url.setQuery("report_type={}&variety_en={}&page={}&page_size={}".format(
            report_type, variety_en, page, page_size))
        reply = self.network_manager.get(QNetworkRequest(url))
        reply.finished.connect(self.paginator_reports_reply)

    def paginator_reports_reply(self):
        reply = self.sender()
        if reply.error():
            logger.error('GET-Request Paginator Of Research File Error!')
        else:
            data = json.loads(reply.readAll().data().decode('utf8'))
            self.paginator_reports_response.emit(data)
        reply.deleteLater()

    def get_date_query_reports(self, query_date: str, variety_en: str):
        """ 以日期的方式获取报告 """
        url = QUrl(SERVER_API + 'report-file/date/')
        url.setQuery("query_date={}&variety_en={}".format(query_date, variety_en))
        reply = self.network_manager.get(QNetworkRequest(url))
        reply.finished.connect(self.date_query_reports_reply)

    def date_query_reports_reply(self):
        reply = self.sender()
        if reply.error():
            logger.error('GET-Request Date Query Of Research File Error!')
        else:
            data = json.loads(reply.readAll().data().decode('utf8'))
            self.date_query_reports_response.emit(data)
        reply.deleteLater()

    def put_modify_report_message(self, report_message: dict, user_token: str):
        """ 修改某个报告的信息 """
        report_id = report_message.get('report_id', None)
        if not report_id:
            return
        url = QUrl(SERVER_API + 'report-file/{}/'.format(report_id))
        r = QNetworkRequest(url)
        r.setRawHeader('Authorization'.encode('utf8'), user_token.encode('utf8'))
        reply = self.network_manager.put(r, json.dumps(report_message).encode('utf8'))
        reply.finished.connect(self.modify_report_message_reply)

    def modify_report_message_reply(self):
        """ 修改信息返回 """
        reply = self.sender()
        if reply.error():
            logger.error('PUT-Request modify report error Qt status: {}!'.format(reply.error()))
            self.modify_report_message_response.emit(False)
        else:
            self.modify_report_message_response.emit(True)
        reply.deleteLater()

    def delete_report(self, report_id: int, user_token: str):
        """ 删除某个报告 """
        url = QUrl(SERVER_API + 'report-file/{}/'.format(report_id))
        r = QNetworkRequest(url)
        r.setRawHeader('Authorization'.encode('utf8'), user_token.encode('utf8'))
        reply = self.network_manager.deleteResource(r)
        reply.finished.connect(self.delete_report_reply)

    def delete_report_reply(self):
        """ 删除报告返回 """
        reply = self.sender()
        if reply.error():
            logger.error('DELETE-Request report error Qt status: {}'.format(reply.error()))
            self.delete_report_response.emit(False)
        else:
            self.delete_report_response.emit(True)
        reply.deleteLater()
