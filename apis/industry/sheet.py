# _*_ coding:utf-8 _*_
# @File  : sheet.py
# @Time  : 2021-02-05 11:29
# @Author: zizle

# 与用户表格相关的API
import json

from PyQt5.QtWidgets import qApp
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QUrl
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest

from settings import SERVER_API, logger


class SheetAPI(QObject):
    sheet_last_reply = pyqtSignal(dict)

    def __init__(self, *args, **kwargs):
        super(SheetAPI, self).__init__(*args, **kwargs)
        self.network_manager = getattr(qApp, '_network', None)
        if not self.network_manager:
            self.network_manager = QNetworkAccessManager(self)

    def get_sheet_last(self, sheet_id: int):
        url = SERVER_API + 'sheet/{}/record/last/'.format(sheet_id)
        reply = self.network_manager.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(self.sheet_record_last_reply)

    def sheet_record_last_reply(self):
        reply = self.sender()
        if reply.error():
            logger.error('GET-Request Sheet last record!Error:{}'.format(reply.error()))
        else:
            data = json.loads(reply.readAll().data().decode('utf8'))
            self.sheet_last_reply.emit(data)
        reply.deleteLater()

    def save_sheet_new_data(self, sheet_id: int, data: dict):
        url = SERVER_API + 'sheet/{}/record/last/'.format(sheet_id)






