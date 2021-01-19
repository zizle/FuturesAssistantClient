# _*_ coding:utf-8 _*_
# @File  : maintain.py
# @Time  : 2021-01-19 09:46
# @Author: zizle

# 顾问服务的后台管理
import json

from PyQt5.QtWidgets import (qApp, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTextBrowser, QMessageBox,
                             QFrame)
from PyQt5.QtCore import QMargins, Qt, QUrl
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest

from widgets import OptionWidget, RichTextEdit
from utils.client import get_user_token
from settings import SERVER_API


class ConsultantMaintain(QWidget):
    consultant_type = None

    def __init__(self, *args, **kwargs):
        super(ConsultantMaintain, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        # 操作框
        option_widget = OptionWidget(self)
        option_layout = QHBoxLayout()
        self.show_button = QPushButton('查看当前', self)
        self.create_button = QPushButton('修改内容', self)
        self.title_edit = QLineEdit(self)
        self.title_edit.setPlaceholderText('在这里输入标题')
        self.title_edit.hide()
        option_layout.addWidget(self.show_button)
        option_layout.addWidget(self.create_button)
        option_layout.addWidget(self.title_edit)
        option_layout.addStretch()
        option_widget.setLayout(option_layout)
        layout.addWidget(option_widget)

        # 显示QTextBrowser当前的和一个编辑RichText新的
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(QMargins(8, 5, 8, 5))
        self.text_browser = QTextBrowser(self)
        self.text_browser.setFrameShape(QFrame.NoFrame)
        content_layout.addWidget(self.text_browser)

        self.rich_edit = RichTextEdit()
        self.rich_edit.setParent(self)
        self.rich_edit.hide()
        content_layout.addWidget(self.rich_edit)

        self.confirm_button = QPushButton('确定', self)
        self.confirm_button.hide()
        content_layout.addWidget(self.confirm_button, alignment=Qt.AlignRight)

        layout.addLayout(content_layout)
        self.setLayout(layout)

        """ 业务部分 """
        self.network_manager = getattr(qApp, '_network', QNetworkAccessManager(self))
        self.create_button.clicked.connect(self.to_create_new_article)
        self.show_button.clicked.connect(self.to_show_current_article)
        self.confirm_button.clicked.connect(self.confirm_create_article)

        self.get_current_article()

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

    def to_create_new_article(self):
        """ 新建一个文章 """
        self.rich_edit.setHtml(self.text_browser.toHtml())
        self.rich_edit.show()
        self.confirm_button.show()
        self.text_browser.hide()

    def to_show_current_article(self):
        """ 显示当前文章 """
        self.text_browser.show()
        self.rich_edit.hide()
        self.confirm_button.hide()
        self.rich_edit.clear()

    def confirm_create_article(self):
        """ 确定创建文章 """
        content = self.rich_edit.toHtml()
        data = {
            'user_token': get_user_token(raw=True),
            'article_type': self.consultant_type,
            'content': content
        }
        url = SERVER_API + 'consultant/article/{}/'.format(self.consultant_type)
        request = QNetworkRequest(QUrl(url))
        reply = self.network_manager.post(request, json.dumps(data).encode('utf8'))
        reply.finished.connect(self.create_article_reply)

    def create_article_reply(self):
        reply = self.sender()
        if reply.error():
            QMessageBox.information(self, '失败', '创建失败了!')
        else:
            QMessageBox.information(self, '失败', '创建成功!')
            self.rich_edit.clear()
        reply.deleteLater()


# 人才培养
class PersonTrain(ConsultantMaintain):
    consultant_type = 'person'


# 部门组建
class OrganizationCreated(ConsultantMaintain):
    consultant_type = 'organization'


# 制度考核
class ExamineChecked(ConsultantMaintain):
    consultant_type = 'examine'

