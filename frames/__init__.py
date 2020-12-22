# _*_ coding:utf-8 _*_
# ---------------------------
# Python_Version 3.6.3
# Author: zizle
# Created: 2020-05-18
# ---------------------------
import os
import json
import sys
import pickle
from PyQt5.QtWidgets import qApp, QSplashScreen
from PyQt5.QtGui import QPixmap, QFont, QImage
from PyQt5.QtCore import Qt, QSize, QUrl, QSettings, QEventLoop, QVariant
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from utils.client import get_client_uuid
from settings import ADMINISTRATOR, SERVER_API, STATIC_URL, BASE_DIR, logger

from .frameless import ClientMainApp

""" 欢迎页 """


class WelcomePage(QSplashScreen):
    def __init__(self, *args, **kwargs):
        super(WelcomePage, self).__init__(*args, *kwargs)
        self.event_loop = QEventLoop(self)
        self._bind_global_network_manager()                  # 绑定全局网络管理器

        self._get_start_image()                              # 获取开启的图片

        self._add_client_to_server()                         # 添加客户端到服务器

        self.initial_auth_file()                             # 权限验证文件初始化

    def _bind_global_network_manager(self):
        """ 绑定全局网络管理器 """
        if not hasattr(qApp, "_network"):
            network_manager = QNetworkAccessManager(self)
            setattr(qApp, "_network", network_manager)

    def _add_client_to_server(self):
        """ 新增客户端 """
        client_uuid = get_client_uuid()
        if not client_uuid:
            logger.error("GET CLIENT-UUID FAIL.")
            self.close()
            sys.exit(-1)

        client_info = {
            'client_name': '',
            'machine_uuid': client_uuid,
            'is_manager': ADMINISTRATOR
        }
        network_manager = getattr(qApp, '_network')
        url = SERVER_API + "client/"
        r = QNetworkRequest(QUrl(url))
        r.setHeader(QNetworkRequest.ContentTypeHeader, QVariant('application/json'))
        reply = network_manager.post(r, json.dumps(client_info).encode('utf-8'))
        reply.finished.connect(self.add_client_reply)
        self.event_loop.exec_()

    def add_client_reply(self):
        """ 添加客户端的信息返回了 """
        reply = self.sender()
        if reply.error():
            logger.error("New Client ERROR!{}".format(reply.error()))
            sys.exit(-1)
        data = reply.readAll().data()
        data = json.loads(data.decode("utf-8"))
        reply.deleteLater()
        # 将信息写入token
        client_uuid = data["client_uuid"]
        client_ini_path = os.path.join(BASE_DIR, "dawn/client.ini")
        token_config = QSettings(client_ini_path, QSettings.IniFormat)
        token_config.setValue("TOKEN/UUID", client_uuid)
        self.event_loop.quit()

    def _get_start_image(self):
        """ 获取开启的页面图片 """
        network_manager = getattr(qApp, "_network")
        url = STATIC_URL + "start_image_bg.png"
        reply = network_manager.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(self.start_image_reply)
        self.event_loop.exec_()

    def start_image_reply(self):
        """ 开启图片返回 """
        reply = self.sender()
        if reply.error():
            pixmap = QPixmap('media/start.png')
        else:
            start_image = QImage.fromData(reply.readAll().data())
            pixmap = QPixmap(start_image)
        reply.deleteLater()
        scaled_map = pixmap.scaled(QSize(660, 400), Qt.KeepAspectRatio)
        self.setPixmap(scaled_map)
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.setFont(font)
        self.showMessage("欢迎使用分析决策系统\n程序正在启动中...", Qt.AlignCenter, Qt.blue)
        self.event_loop.quit()

    @staticmethod
    def initial_auth_file():
        auth_filepath = os.path.join(BASE_DIR, "dawn/auth.dat")
        with open(auth_filepath, "wb") as fp:
            pickle.dump({"role": "", "auth": []}, fp)
