# _*_ coding:utf-8 _*_
# ---------------------------
# Python_Version 3.6.3
# Author: zizle
# Created: 2020-05-18
# ---------------------------
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QDialog, QLabel, QGridLayout, QPushButton, QDesktopWidget, QVBoxLayout
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QPixmap


# 提示信息
class InformationPopup(QDialog):
    def __init__(self, title='提示', message='在这里设置提示信息', *args, **kwargs):
        super(InformationPopup, self).__init__(*args, **kwargs)
        layout = QGridLayout()
        self.setWindowTitle(title)
        ico_label = QLabel()
        ico_label.setFixedSize(48,48)
        pix = QPixmap('media/tips/information.png')
        ico_label.setPixmap(pix)
        ico_label.setScaledContents(True)
        layout.addWidget(ico_label, 0, 0)
        layout.addWidget(QLabel(message, styleSheet='color:rgb(10,10,10);font-weight:bold'), 0, 1)
        layout.addWidget(QPushButton('确定', clicked=self.close, cursor=Qt.PointingHandCursor), 1, 1)
        self.setLayout(layout)
        self.setMaximumWidth(320)
        self.setStyleSheet("""
        QPushButton{
            border: none;
            font-size:14px;
            background-color: rgb(74,115,134);
            padding:5px;
            color:rgb(254,254,254)
        }
        """)
        self.setAttribute(Qt.WA_DeleteOnClose)


class WebPopup(QDialog):
    def __init__(self, *args, **kwargs):
        super(WebPopup, self).__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_DeleteOnClose)
        lt = QVBoxLayout(self)
        lt.setContentsMargins(0, 0, 0, 0)
        self.web = QWebEngineView(self)
        lt.addWidget(self.web)
        self.setLayout(lt)
        available_size = QDesktopWidget().availableGeometry()  # 用户的桌面信息,来改变自身窗体大小
        available_width, available_height = available_size.width(), available_size.height()
        self.resize(available_width * 0.7, available_height * 0.72)

    def load_page(self, url):
        self.web.load(QUrl(url))
