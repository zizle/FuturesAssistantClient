# _*_ coding:utf-8 _*_
# @File  : variety.py
# @Time  : 2020-12-22 13:34
# @Author: zizle
""" 品种相关网络请求 """
import json
from PyQt5.QtCore import QObject, pyqtSignal, QUrl
from PyQt5.QtWidgets import qApp
from PyQt5.QtNetwork import QNetworkRequest, QNetworkAccessManager

from settings import SERVER_API, logger


class VarietyAPI(QObject):
    varieties_sorted = pyqtSignal(dict)
    upload_intro_reply = pyqtSignal(dict)

    def __init__(self, *args, **kwargs):
        super(VarietyAPI, self).__init__(*args, **kwargs)
        self.network_manager = getattr(qApp, '_network', None)
        if not self.network_manager:
            self.network_manager = QNetworkAccessManager(self)

    def get_variety_en_sorted(self):
        """ 获取所有品种以交易代码排序 """
        url = SERVER_API + 'variety-en-sorted/?is_real=2'
        reply = self.network_manager.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(self.variety_reply)

    def variety_reply(self):
        reply = self.sender()
        if reply.error():
            logger.error('GET-Request variety ERROR!')
        else:
            data = json.loads(reply.readAll().data().decode('utf8'))
            self.varieties_sorted.emit(data)
        reply.deleteLater()

    def upload_variety_intro_file(self, variety_en, multipart_data):
        """ 上传品种介绍文件 """
        url = SERVER_API + 'variety/{}/intro/'.format(variety_en)
        reply = self.network_manager.post(QNetworkRequest(QUrl(url)), multipart_data)
        reply.finished.connect(self.upload_reply)
        multipart_data.setParent(reply)

    def upload_reply(self):
        reply = self.sender()
        if reply.error():
            self.upload_intro_reply.emit({'message': '上传失败!'})
        else:
            self.upload_intro_reply.emit({'message': '上传成功!'})
        reply.deleteLater()
