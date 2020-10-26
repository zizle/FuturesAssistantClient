# _*_ coding:utf-8 _*_
# @File  : password.py
# @Time  : 2020-10-26 13:04
# @Author: zizle
import json
from PyQt5.QtWidgets import qApp, QDialog, QLabel, QLineEdit, QGridLayout, QPushButton
from PyQt5.QtCore import QMargins, Qt, QUrl, QEventLoop, pyqtSignal
from PyQt5.QtNetwork import QNetworkRequest, QNetworkReply
from utils.client import get_user_token
from .message import InformationPopup
from settings import SERVER_API


class EditPasswordPopup(QDialog):
    """ 修改密码的弹窗 """
    re_login = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(EditPasswordPopup, self).__init__(*args, **kwargs)
        self.event_loop = QEventLoop(self)
        layout = QGridLayout()
        layout.setContentsMargins(QMargins(20, 30, 20, 20))
        layout.setSpacing(20)
        layout.addWidget(QLabel("原密码:", self), 0, 0)
        self.old_password = QLineEdit(self)
        self.old_password.setEchoMode(QLineEdit.Password)
        self.old_password.setPlaceholderText("输入旧密码")
        layout.addWidget(self.old_password, 0, 1)

        layout.addWidget(QLabel("新密码:", self), 1, 0)
        self.new_password = QLineEdit(self)
        self.new_password.setEchoMode(QLineEdit.Password)
        self.new_password.setPlaceholderText("输入新密码")
        layout.addWidget(self.new_password, 1, 1)

        layout.addWidget(QLabel("确认密码:", self), 2, 0)
        self.confirm_password = QLineEdit(self)
        self.confirm_password.setEchoMode(QLineEdit.Password)
        self.confirm_password.setPlaceholderText("再次确认密码")
        layout.addWidget(self.confirm_password, 2, 1)

        self.confirm_button = QPushButton("确认修改", self)
        self.confirm_button.setFixedWidth(100)
        self.confirm_button.clicked.connect(self.confirm_modify_password)
        layout.addWidget(self.confirm_button, 3, 1, alignment=Qt.AlignRight)

        self.setLayout(layout)
        self.setFixedSize(400, 200)
        self.setWindowTitle("密码修改")

    def confirm_modify_password(self):
        """ 提交修改密码 """
        old_password = self.old_password.text()
        new_password = self.new_password.text()
        confirm_password = self.confirm_password.text()
        # 对比两次输入的密码
        if new_password != confirm_password:
            p = InformationPopup("两次输入密码不一致!", self)
            p.exec_()
            return
        # 验证密码长度
        if len(new_password) < 6 or len(new_password) > 20:
            p = InformationPopup("密码需为6-20位的长度!", self)
            p.exec_()
            return
        # 提交修改密码
        self.modify_password(old_password, new_password, confirm_password)

    def modify_password(self, old_password, new_password, confirm_password):
        body = {
            "old_password": old_password,
            "new_password": new_password,
            "confirm_password": confirm_password
        }
        network_manger = getattr(qApp, "_network")
        url = SERVER_API + "modify-password/"
        request = QNetworkRequest(QUrl(url))
        request.setRawHeader("Authorization".encode("utf-8"), get_user_token().encode("utf-8"))
        reply = network_manger.post(request, json.dumps(body).encode("utf-8"))
        reply.finished.connect(self.modify_password_reply)
        self.event_loop.exec_()

    def modify_password_reply(self):
        """ 修改密码返回 """
        reply = self.sender()
        self.event_loop.quit()
        if reply.error() == QNetworkReply.AuthenticationRequiredError:
            message = "用户验证错误!修改密码失败!"
        elif reply.error() == QNetworkReply.ProtocolInvalidOperationError:
            message = "两次输入密码不一致!"
        elif reply.error() == QNetworkReply.UnknownContentError:
            message = "原密码错误!"
        else:
            message = "修改密码成功!请重新登录!"
        reply.deleteLater()
        p = InformationPopup(message, self)
        p.exec_()
        self.re_login.emit()
        self.close()


