# _*_ coding:utf-8 _*_
# @File  : advertisement.py
# @Time  : 2020-10-13 15:10
# @Author: zizle
""" 弹窗显示广告的信息 """

from PyQt5.QtWidgets import QDialog, qApp, QVBoxLayout, QLabel, QScrollArea, QFrame
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtNetwork import QNetworkRequest
from PyQt5.QtCore import Qt, QUrl, QMargins


# 显示图片的弹窗
class ImagePopup(QDialog):
    def __init__(self, url, *args, **kwargs):
        super(ImagePopup, self).__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.url = url
        layout = QVBoxLayout()
        self.image_label = QLabel(self)
        layout.addWidget(self.image_label)
        self.setLayout(layout)
        self.resize(800, 400)
        self.image_label.setFixedSize(800, 400)
        self.get_image()

    def get_image(self):
        network_manager = getattr(qApp, "_network")
        reply = network_manager.get(QNetworkRequest(QUrl(self.url)))
        reply.finished.connect(self.image_reply)

    def image_reply(self):
        reply = self.sender()
        if reply.error():
            pass
        else:
            image = QImage.fromData(reply.readAll().data())
            self.image_label.setPixmap(QPixmap(image))
            self.image_label.setScaledContents(True)
        reply.deleteLater()


# 显示内容的弹窗
class TextPopup(QDialog):
    def __init__(self, message, *args, **kwargs):
        super(TextPopup, self).__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_DeleteOnClose)
        layout = QVBoxLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        self.scroll_area = QScrollArea(self)
        self.text_label = QLabel(self)
        self.text_label.setContentsMargins(QMargins(30, 10, 30, 10))
        self.text_label.setAlignment(Qt.AlignTop)
        self.text_label.setText(message)
        self.text_label.setWordWrap(True)
        self.text_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.scroll_area.setWidget(self.text_label)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)

        layout.addWidget(self.scroll_area)
        layout.addStretch()
        self.setLayout(layout)
        self.resize(600, 350)
