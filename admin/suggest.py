# _*_ coding:utf-8 _*_
# @File  : suggest.py
# @Time  : 2021-02-22 10:35
# @Author: zizle

# 意见建议后台查看
import json

from PyQt5.QtWidgets import qApp, QWidget, QScrollArea, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtNetwork import QNetworkRequest, QNetworkAccessManager
from PyQt5.QtCore import QUrl, Qt
from settings import SERVER_API


class SuggestWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(SuggestWidget, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        t_layout = QHBoxLayout()
        self.title = QLabel(self)
        self.user = QLabel(self)
        self.title.setObjectName('title')
        self.user.setObjectName('user')
        t_layout.addWidget(self.title)
        t_layout.addWidget(self.user)
        self.links = QLabel(self)
        self.links.setObjectName('links')
        t_layout.addWidget(self.links)
        t_layout.addStretch()
        self.content = QLabel(self)
        self.content.setWordWrap(True)
        layout.addLayout(t_layout)
        layout.addWidget(self.content)
        self.setStyleSheet('#title,#user{color:rgb(233,66,66);font-weight:700}')
        self.setLayout(layout)

    def set_title(self, t, u):
        self.title.setText(t)
        self.user.setText(u)

    def set_content(self, c):
        self.content.setText(c)

    def set_links(self, c):
        self.links.setText('联系方式:' + str(c))


class SuggestAdmin(QScrollArea):
    def __init__(self, *args, **kwargs):
        super(SuggestAdmin, self).__init__(*args, **kwargs)
        self.widget = QWidget(self)
        self.setWidget(self.widget)
        self.setWidgetResizable(True)
        self.network_manager = getattr(qApp, '_network', QNetworkAccessManager(self))
        self.get_suggestions()

    def get_suggestions(self):
        url = SERVER_API + 'suggest/'
        reply = self.network_manager.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(self.suggest_reply)

    def suggest_reply(self):
        reply = self.sender()
        if reply.error():
            pass
        else:
            data = json.loads(reply.readAll().data().decode('utf8'))
            self.show_suggestions(data['suggestions'])
        reply.deleteLater()

    def show_suggestions(self, suggestions):
        if not suggestions:
            s_content = QLabel('还没有收到建议!', self)
            s_content.setAlignment(Qt.AlignCenter)
            s_content.setStyleSheet('color:red')
            self.setWidget(s_content)
            return
        # 显示建议内容
        content_layout = QVBoxLayout()
        for suggest_item in suggestions:
            s = SuggestWidget(self)
            s.set_title(suggest_item['create_time'], suggest_item['username'])
            s.set_links(suggest_item['links'])
            s.set_content(suggest_item['content'])
            content_layout.addWidget(s)
        content_layout.addStretch()
        self.widget.setLayout(content_layout)
