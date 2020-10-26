# _*_ coding:utf-8 _*_
# @File  : user_center.py
# @Time  : 2020-08-28 16:26
# @Author: zizle
import json
from PyQt5.QtWidgets import qApp
from PyQt5.QtNetwork import QNetworkRequest, QNetworkReply
from PyQt5.QtCore import QUrl, pyqtSignal
from .user_center_ui import UserCenterUI
from utils.client import get_client_uuid_with_ini, get_user_token
from popup.message import InformationPopup
from settings import SERVER_API


class UserCenter(UserCenterUI):
    reset_password_signal = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(UserCenter, self).__init__(*args, **kwargs)
        self.info_widget.client_code.setText(get_client_uuid_with_ini())

        self.get_user_information()

        # 确认修改密码
        self.modify_password_widget.confirm_button.clicked.connect(self.modify_password)


    def get_user_information(self):
        """ 获取用户信息 """
        network_manager = getattr(qApp, "_network")
        url = SERVER_API + "user/info/"
        request = QNetworkRequest(QUrl(url))
        request.setRawHeader("Authorization".encode("utf-8"), get_user_token().encode("utf-8"))
        reply = network_manager.get(request)
        reply.finished.connect(self.user_information_reply)

    def user_information_reply(self):
        """ 获取用户基本信息在线时长返回 """
        reply = self.sender()
        if reply.error():
            pass
        else:
            data = json.loads(reply.readAll().data().decode("utf-8"))
            user_info = data["user"]
            self.info_widget.user_code.setText(user_info["user_code"])
            self.info_widget.today_online.setText("{}分钟".format(user_info["today_online"]))
            self.info_widget.online_seconds.setText("{}分钟".format(user_info["total_online"]))
        reply.deleteLater()

    def modify_password(self):
        old_password = self.modify_password_widget.old_password.text()
        new_password = self.modify_password_widget.new_password.text()
        confirm_password = self.modify_password_widget.confirm_password.text()
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

    def modify_password_reply(self):
        """ 修改密码返回 """
        reply = self.sender()
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
        self.reset_password_signal.emit()
