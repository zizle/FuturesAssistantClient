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
import requests
from PyQt5.QtWidgets import qApp, QSplashScreen
from PyQt5.QtGui import QPixmap, QFont, QImage
from PyQt5.QtCore import Qt, QSize, QUrl, QSettings, QEventLoop, QVariant, QThread, pyqtSignal, QTimer
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from utils.client import get_client_uuid
from settings import ADMINISTRATOR, SERVER_API, STATIC_URL, BASE_DIR, logger

from apis.variety import VarietyAPI
from gglobal import variety

from .frameless import ClientMainApp

""" 欢迎页 """


class GetImages(QThread):
    all_reply = pyqtSignal(bool)

    def __init__(self, *args, **kwargs):
        super(GetImages, self).__init__(*args, **kwargs)
        self.is_error = False
        self.images = []

    def set_images(self, images):
        self.images = images
        # 创建缓存文件夹
        folder = os.path.join(BASE_DIR, 'cache/ADVERTISEMENT/Image/')
        if not os.path.exists(folder):
            os.makedirs(folder)

    def run(self):
        # 遍历获取数据
        for image_item in self.images:
            # print(image_item)
            try:
                r = requests.get(url=STATIC_URL + image_item['image'])
                if r.status_code != 200:
                    raise ValueError('GET IMAGE STATUS CODE: {}'.format(r.status_code))
                # 写入数据
                imagepath = os.path.join(BASE_DIR, 'cache/' + image_item['image'])
                with open(imagepath, 'wb') as f:
                    f.write(r.content)
            except Exception as e:
                logger.error('缓存广告图片文件失败!{}'.format(e))
                self.is_error = True
                continue
        self.all_reply.emit(True)


class WelcomePage(QSplashScreen):
    def __init__(self, *args, **kwargs):
        super(WelcomePage, self).__init__(*args, *kwargs)
        # self.event_loop = QEventLoop(self)
        self._bind_global_network_manager()                  # 绑定全局网络管理器

        self._get_start_image()                              # 获取开启的图片

        self._add_client_to_server()                         # 添加客户端到服务器

        self.initial_auth_file()                             # 权限验证文件初始化

        self.variety_api = VarietyAPI(self)                  # 获取系统的品种
        self.variety_api.varieties_sorted.connect(self.sys_variety_reply)

        self.get_sys_variety()                               # 获取系统品种

        # 使用requests获取广告数据以及图片信息
        self.event_loop = QEventLoop(self)
        self.images_thread = GetImages()

        # 关闭的timer
        self.exit_seconds = 10
        self.exit_timer = QTimer(self)
        self.exit_timer.timeout.connect(self.exit_timer_out)

    def exit_timer_out(self):
        if self.exit_seconds < 1:
            logger.error('获取部分资源失败,无法开启!')
            sys.exit(-1)
        else:
            self.showMessage('获取部分资源失败!{}秒后自动退出!'.format(self.exit_seconds), alignment=Qt.AlignCenter)
            self.exit_seconds -= 1

    def get_all_advertisement(self):
        """ 获取当前系统的广告信息 """
        url = SERVER_API + 'advertisement/'
        network_manager = getattr(qApp, "_network")
        reply = network_manager.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(self.get_advertisement_reply)
        self.event_loop.exec_()

    def get_advertisement_reply(self):
        reply = self.sender()
        if reply.error():
            self.showMessage('获取部分资源失败!{}后自动退出!'.format(self.exit_seconds), alignment=Qt.AlignCenter)
            self.exit_timer.start(1000)
        else:
            data = json.loads(reply.readAll().data().decode("utf-8"))
            self.start_image_thread(data['advertisements'])
        reply.deleteLater()

    def start_image_thread(self, advertisements):
        """ 开启获取图片的线程 """
        # 将数据存入缓存区文件夹,并开启线程访问数据
        ad_file = os.path.join(BASE_DIR, 'cache/advertisement.dat')
        with open(ad_file, 'wb') as adf:
            pickle.dump(advertisements, adf)
        # 开启线程请求数据
        self.images_thread.set_images(advertisements)
        self.images_thread.all_reply.connect(self.get_image_thread_finished)
        self.images_thread.finished.connect(self.images_thread.deleteLater)
        self.images_thread.start()

    def get_image_thread_finished(self):
        if self.images_thread.is_error:
            self.exit_timer.start(1000)
        else:
            self.event_loop.quit()

    def get_sys_variety(self):
        self.variety_api.get_variety_en_sorted()

    def sys_variety_reply(self, data):
        variety.set_variety(data['varieties'])

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
        # self.event_loop.exec_()

    def add_client_reply(self):
        """ 添加客户端的信息返回了 """
        reply = self.sender()
        if reply.error():
            logger.error("New Client ERROR!{}".format(reply.error()))
            # sys.exit(-1)
            self.exit_timer.start(1000)
            return
        data = reply.readAll().data()
        data = json.loads(data.decode("utf-8"))
        reply.deleteLater()
        # 将信息写入token
        client_uuid = data["client_uuid"]
        client_ini_path = os.path.join(BASE_DIR, "dawn/client.ini")
        token_config = QSettings(client_ini_path, QSettings.IniFormat)
        token_config.setValue("TOKEN/UUID", client_uuid)
        # self.event_loop.quit()

    def _get_start_image(self):
        """ 获取开启的页面图片 """
        network_manager = getattr(qApp, "_network")
        url = STATIC_URL + "start_image_bg.png"
        reply = network_manager.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(self.start_image_reply)
        # self.event_loop.exec_()

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

    @staticmethod
    def initial_auth_file():
        """ 初始化权限文件 """
        auth_filepath = os.path.join(BASE_DIR, "dawn/auth.dat")
        with open(auth_filepath, "wb") as fp:
            pickle.dump({"role": "", "auth": []}, fp)

    # 防止数据未返回点击后消失
    def mousePressEvent(self, event) -> None:
        pass
