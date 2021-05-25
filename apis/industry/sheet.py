# _*_ coding:utf-8 _*_
# @File  : sheet.py
# @Time  : 2021-02-05 11:29
# @Author: zizle

# 与用户表格相关的API
import json

import requests
from PyQt5.QtWidgets import qApp
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QUrl, QThread
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest

from settings import SERVER_API, logger
from utils.client import get_user_token


class SheetAPI(QObject):
    sheet_last_reply = pyqtSignal(dict)
    add_record_reply = pyqtSignal(bool)

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

    def save_sheet_new_data(self, sheet_id: int, data: list):
        url = SERVER_API + 'sheet/{}/record/add/'.format(sheet_id)
        r = QNetworkRequest(QUrl(url))
        r.setRawHeader('Authorization'.encode('utf8'), get_user_token().encode('utf8'))
        r.setHeader(QNetworkRequest.ContentTypeHeader, 'application/json')
        reply = self.network_manager.post(r, json.dumps(data).encode('utf8'))
        reply.finished.connect(self.add_reply)

    def add_reply(self):
        reply = self.sender()
        if reply.error():
            logger.error('POST-Request add sheet record Error:{}'.format(reply.error()))
            self.add_record_reply.emit(False)
        else:
            self.add_record_reply.emit(True)
        reply.deleteLater()


class SwapSheetSorted(QThread):
    def __init__(self, *args, **kwargs):
        super(SwapSheetSorted, self).__init__(*args, **kwargs)
        self.body_data = {}

    def set_body_data(self, data):
        self.body_data = data

    def run(self):
        try:
            requests.put(SERVER_API + "sheet/suffix/", json=self.body_data)
        except Exception as e:
            logger.error(f'用户交换数据表排序错误{e}')


class UpdateSheetRows(QThread):
    update_signal = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(UpdateSheetRows, self).__init__(*args, **kwargs)
        self.update_rows = []
        self.sheet_id = 0

    def set_sheet_id(self, sid):
        self.sheet_id = sid

    def set_rows(self, rows):
        self.update_rows = rows

    def run(self):
        if not self.sheet_id:
            return
        try:
            r = requests.put(SERVER_API + f'sheet/{self.sheet_id}/update/', json=self.update_rows)
        except Exception as e:
            self.update_signal.emit(f'数据有误,更新失败!\n{e}')
        else:
            self.update_signal.emit('数据更新成功!')
            

class GetChartSheetColumns(QThread):  # 获取图形对应的列名称
    columns_reply = pyqtSignal(dict)

    def __init__(self, *args, **kwargs):
        super(GetChartSheetColumns, self).__init__(*args, **kwargs)
        self.sheet_id = 0
        self.chart_id = 0

    def set_sheet_id(self, sid: int, cid: int):
        self.sheet_id = sid
        self.chart_id = cid

    def run(self):
        if self.sheet_id < 1:
            return
        try:
            r = requests.get(SERVER_API + f'chart/sheet-headers/?sid={self.sheet_id}&cid={self.chart_id}')
            result = r.json()
        except Exception as e:
            logger('获取图形对应表的列数据失败{}'.format(e))
        else:
            self.columns_reply.emit(result)

