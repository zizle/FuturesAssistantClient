# _*_ coding:utf-8 _*_
# @File  : user_center_ui.py
# @Time  : 2020-08-28 16:25
# @Author: zizle
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QGridLayout, QPushButton, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, QSize, QMargins, QRect
from PyQt5.QtGui import QPainter, QPixmap, QPalette, QBrush, QColor


class BaseInfoWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(BaseInfoWidget, self).__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_StyledBackground, True)
        # 基本信息布局
        info_layout = QGridLayout()
        info_layout.setContentsMargins(QMargins(10, 28, 10, 28))
        info_layout.addWidget(QLabel("客户端号:", self), 0, 0)
        self.client_code = QLabel(self)
        self.client_code.setTextInteractionFlags(Qt.TextSelectableByMouse)
        info_layout.addWidget(self.client_code, 0, 1)

        info_layout.addWidget(QLabel("用户号:", self), 0, 2)
        self.user_code = QLabel(self)
        self.user_code.setTextInteractionFlags(Qt.TextSelectableByMouse)
        info_layout.addWidget(self.user_code, 0, 3)

        info_layout.addWidget(QLabel("今日在线:", self), 1, 0)
        self.today_online = QLabel(self)
        self.today_online.setToolTip("时长每连续使用2分钟记录一次")
        info_layout.addWidget(self.today_online, 1, 1)

        info_layout.addWidget(QLabel("累计在线:", self), 1, 2)
        self.online_seconds = QLabel(self)
        info_layout.addWidget(self.online_seconds, 1, 3)

        self.setLayout(info_layout)

        self.setObjectName("infoWidget")
        # 设置阴影
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setOffset(0, 0)
        shadow.setColor(QColor(100, 100, 100))
        shadow.setBlurRadius(8)
        self.setGraphicsEffect(shadow)
        self.setObjectName("moduleWidget")
        self.client_code.setObjectName("clientCode")
        self.user_code.setObjectName("userCode")
        self.setStyleSheet(
            "#infoWidget{background-color:rgb(250,250,250)}"
            "#clientCode{color:rgb(23,130,230)}"
            "#userCode{color:rgb(23,130,230)}"
        )

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(230, 230, 230, 150))

    # def enterEvent(self, event):
    #     effect = self.graphicsEffect()
    #     effect.setOffset(1, 1)
    #     self.setGraphicsEffect(effect)
    #
    # def leaveEvent(self, event):
    #     effect = self.graphicsEffect()
    #     effect.setOffset(0, 0)
    #     self.setGraphicsEffect(effect)


class ModifyPasswordWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(ModifyPasswordWidget, self).__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_StyledBackground, True)
        layout = QGridLayout()
        layout.setContentsMargins(QMargins(20, 30, 20, 20))
        layout.setSpacing(20)
        layout.addWidget(QLabel("旧密码:", self), 0, 0)
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
        self.confirm_button.setFixedWidth(200)
        layout.addWidget(self.confirm_button, 3, 1, alignment=Qt.AlignRight)

        self.setLayout(layout)

        # 设置阴影
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setOffset(0, 0)
        shadow.setColor(QColor(100, 100, 100))
        shadow.setBlurRadius(8)
        self.setGraphicsEffect(shadow)
        self.setObjectName("passwordWidget")
        self.setStyleSheet(
            "#passwordWidget{background-color:rgb(250,250,250}"
        )

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(130, 230, 230, 150))


class UserCenterUI(QWidget):
    def __init__(self, *args, **kwargs):
        super(UserCenterUI, self).__init__(*args, **kwargs)
        main_layout = QGridLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(20)

        # self.avatar = CAvatar(size=QSize(180, 180))
        # self.avatar.setParent(self)
        # self.avatar.setToolTip("点击修改头像")
        # main_layout.addWidget(self.avatar, 0, 0)

        self.info_widget = BaseInfoWidget(self)
        main_layout.addWidget(self.info_widget, 0, 1)

        # 修改密码控件
        self.modify_password_widget = ModifyPasswordWidget(self)
        main_layout.addWidget(self.modify_password_widget, 1, 1)

        self.setLayout(main_layout)
        self.info_widget.setFixedSize(550, 120)
        self.modify_password_widget.setFixedWidth(550)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), QPixmap("media/home_bg.png"), QRect())
