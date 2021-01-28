# _*_ coding:utf-8 _*_
# @File  : consultant.py
# @Time  : 2021-01-19 14:11
# @Author: zizle

import json

from PyQt5.QtGui import QPixmap, QPalette
from PyQt5.QtWidgets import qApp, QWidget, QVBoxLayout, QTextBrowser, QFrame, QScrollArea, QLabel, QHBoxLayout
from PyQt5.QtNetwork import QNetworkRequest, QNetworkAccessManager
from PyQt5.QtCore import QUrl
from settings import SERVER_API


class ConsultantWidget(QScrollArea):
    consultant_type = None

    def __init__(self, *args, **kwargs):
        super(ConsultantWidget, self).__init__(*args, **kwargs)
        self.setFrameShape(QFrame.NoFrame)

        widget = QWidget(self)
        layout = QHBoxLayout()

        # 显示文字
        self.text_browser = QTextBrowser(self)
        self.text_browser.setFrameShape(QFrame.NoFrame)
        layout.addWidget(self.text_browser)

        # 显示图片
        self.image_label = QLabel(self)
        layout.addWidget(self.image_label)

        self.setLayout(layout)

        self.setObjectName('scroll')
        self.setBackgroundRole(QPalette.Base)

        self.setWidget(widget)
        self.setWidgetResizable(True)

        self.network_manager = getattr(qApp, '_network', QNetworkAccessManager(self))

        self.set_image()
        self.get_current_article()

    def set_image(self):
        if self.consultant_type is None:
            return
        file = 'media/product/{}.jpg'.format(self.consultant_type)
        self.image_label.setPixmap(QPixmap(file))
        self.image_label.setScaledContents(True)

    def get_current_article(self):
        """ 获取当前文章内容 """
        if self.consultant_type is None:
            return
        url = SERVER_API + 'consultant/article/{}/'.format(self.consultant_type)
        reply = self.network_manager.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(self.current_article_reply)

    def current_article_reply(self):
        """ 当前模块的文章返回了 """
        reply = self.sender()
        if reply.error():
            pass
        else:
            data = json.loads(reply.readAll().data().decode('utf8'))
            article = data['article']
            if article:
                self.text_browser.setText(article['content'])
        reply.deleteLater()


class PersonTrain(ConsultantWidget):
    consultant_type = 'person'


class Organization(ConsultantWidget):
    consultant_type = 'organization'


# 风险管理
class RiskManager(ConsultantWidget):
    consultant_type = 'riskmanager'


# 场外期权
class OTCOption(ConsultantWidget):
    consultant_type = 'otcoption'


# 保险+期货
class SafeFutures(ConsultantWidget):
    consultant_type = 'safefutures'

# 制度考核废弃了
# class Examine(ConsultantWidget):
#     consultant_type = 'examine'


