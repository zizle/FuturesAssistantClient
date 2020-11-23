# _*_ coding:utf-8 _*_
# @File  : password.py
# @Time  : 2020-10-26 13:04
# @Author: zizle
import re
import json
from PyQt5.QtWidgets import qApp, QDialog, QLabel, QLineEdit, QGridLayout, QPushButton
from PyQt5.QtCore import QMargins, Qt, QUrl, QEventLoop, pyqtSignal, QTimer
from PyQt5.QtNetwork import QNetworkRequest, QNetworkReply
from popup.message import InformationPopup
from utils.client import get_user_token
from .message import InformationPopup
from settings import SERVER_API


class ResetPasswordPopup(QDialog):
    def __init__(self, user_phone, *args, **kwargs):
        super(ResetPasswordPopup, self).__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.email_timer = QTimer(self)  # 倒计时发送邮箱验证码
        self.email_timer.timeout.connect(self.refresh_email_seconds)
        layout = QGridLayout()
        layout.setContentsMargins(QMargins(20, 30, 20, 20))
        layout.setSpacing(20)
        layout.addWidget(QLabel("验证码:", self), 1, 0)
        self.verify_code = QLineEdit(self)
        self.verify_code.setPlaceholderText("已向您预留邮箱中发送验证码")
        self.verify_code.setMinimumWidth(230)
        layout.addWidget(self.verify_code, 1, 1)
        self.verify_button = QPushButton("发送", self)
        self.verify_button.clicked.connect(self.send_email_to_user)
        layout.addWidget(self.verify_button, 1, 2, alignment=Qt.AlignRight)

        layout.addWidget(QLabel("手机号:", self), 0, 0)
        self.phone_edit = QLineEdit(self)
        self.phone_edit.setPlaceholderText("登录用的手机号")
        self.phone_edit.setText(user_phone)
        layout.addWidget(self.phone_edit, 0, 1, 1, 2)

        layout.addWidget(QLabel("新密码:", self), 2, 0)
        self.new_password = QLineEdit(self)
        self.new_password.setEchoMode(QLineEdit.Password)
        self.new_password.setPlaceholderText("输入新密码")
        layout.addWidget(self.new_password, 2, 1, 1, 2)

        layout.addWidget(QLabel("确认密码:", self), 3, 0)
        self.confirm_password = QLineEdit(self)
        self.confirm_password.setEchoMode(QLineEdit.Password)
        self.confirm_password.setPlaceholderText("再次确认密码")
        layout.addWidget(self.confirm_password, 3, 1, 1, 2)

        self.confirm_button = QPushButton("确认修改", self)
        self.confirm_button.setFixedWidth(100)
        self.confirm_button.clicked.connect(self.confirm_reset_password)
        layout.addWidget(self.confirm_button, 4, 2, alignment=Qt.AlignRight)

        self.setLayout(layout)
        self.setFixedSize(440, 300)
        self.setWindowTitle("重置密码")
        self.setLayout(layout)

        self.send_email_to_user()

    def refresh_email_code(self):
        reply = self.sender()
        if reply.error():
            pass
        else:
            data = json.loads(reply.readAll().data().decode("utf-8"))
            if data["status"] != 200:
                p = InformationPopup(data["message"], self)
                p.exec_()
            else:
                # 后端请求发送验证码
                self.verify_button.setText("60秒重发")
                self.verify_button.setEnabled(False)
                if not self.email_timer.isActive():
                    self.email_timer.start(1000)
        reply.deleteLater()

    def send_email_to_user(self):
        """ 请求发送验证码给用户 """
        user_phone = self.phone_edit.text()
        if not re.match(r'^[1][3-9][0-9]{9}$', user_phone):
            p = InformationPopup("手机号格式有误!", self)
            p.exec_()
            return
        network_manager = getattr(qApp, "_network")
        url = SERVER_API + "email-code/?phone={}".format(user_phone)
        reply = network_manager.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(self.refresh_email_code)

    def refresh_email_seconds(self):
        """ 倒计时发送邮箱验证码 """
        text = self.verify_button.text()
        seconds = int(text[:2])
        if seconds - 1 > 0:
            new_text = "%02d秒重发" % (seconds - 1)
            self.verify_button.setText(new_text)
        else:
            if self.email_timer.isActive():
                self.email_timer.stop()
            self.verify_button.setText("发送")
            self.verify_button.setEnabled(True)

    def confirm_reset_password(self):
        """ 确定重置密码 """
        body = {
            "email_code": self.verify_code.text(),
            "user_phone": self.phone_edit.text(),
            "new_password": self.new_password.text(),
            "confirm_password": self.confirm_password.text()
        }
        if body["new_password"] != body["confirm_password"]:
            p = InformationPopup("两次输入密码不一致!", self)
            p.exec_()
            return
        if len(body["new_password"]) < 6 or len(body["new_password"]) > 20:
            p = InformationPopup("密码长度为6-20位的组合!", self)
            p.exec_()
            return
        network_manager = getattr(qApp, "_network")
        url = SERVER_API + "reset-password/email/"
        reply = network_manager.post(QNetworkRequest(QUrl(url)), json.dumps(body).encode("utf-8"))
        reply.finished.connect(self.reset_password_reply)

    def reset_password_reply(self):
        """ 重置密码返回 """
        reply = self.sender()
        if reply.error():
            p = InformationPopup("重置密码失败!", self)
            p.exec_()
        else:
            p = InformationPopup("重置密码成功,前往登录!", self)
            p.exec_()
            self.close()
        reply.deleteLater()


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


