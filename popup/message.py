# _*_ coding:utf-8 _*_
# ---------------------------
# Python_Version 3.6.3
# Author: zizle
# Created: 2020-09-09
# ---------------------------

""" 自定义消息弹窗 """
from PyQt5.QtWidgets import QWidget, QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSignal, QMargins


class WarningPopup(QDialog):
    confirm_operate = pyqtSignal(dict)

    def __init__(self, message, *args):
        super(WarningPopup, self).__init__(*args)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle("警告")
        self.setFixedWidth(230)
        main_layout = QVBoxLayout()
        message_layout = QHBoxLayout()
        message_layout.setSpacing(5)
        icon_label = QLabel(self)
        icon_label.setFixedSize(50, 50)
        icon_label.setPixmap(QPixmap("media/icons/warning.png"))
        icon_label.setScaledContents(True)
        message_layout.addWidget(icon_label, alignment=Qt.AlignLeft)
        message = "<div style=text-indent:24px;font-size:12px;line-height:18px;>" + message + "</div>"
        message_label = QLabel(message, self)
        message_label.setMinimumWidth(155)

        message_label.setWordWrap(True)
        message_layout.addWidget(message_label)
        main_layout.addLayout(message_layout)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        cancel_button = QPushButton("取消", self)
        cancel_button.clicked.connect(self.close)
        button_layout.addWidget(cancel_button)

        confirm_button = QPushButton("确定", self)
        confirm_button.clicked.connect(self.make_sure_confirm_operate)
        button_layout.addWidget(confirm_button)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
        self.data = dict()

    def set_data(self, data):
        """ 设置发出信号带的数据 """
        self.data.update(data)

    def make_sure_confirm_operate(self):
        self.confirm_operate.emit(self.data)
        self.close()


class ExitAppPopup(QDialog):
    confirm_operate = pyqtSignal()

    def __init__(self, message, *args):
        super(ExitAppPopup, self).__init__(*args)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle("提示")
        self.setFixedWidth(230)
        main_layout = QVBoxLayout()
        message_layout = QHBoxLayout()
        message_layout.setSpacing(5)
        icon_label = QLabel(self)
        icon_label.setFixedSize(50, 50)
        icon_label.setPixmap(QPixmap("media/icons/exit_app.png"))
        icon_label.setScaledContents(True)
        message_layout.addWidget(icon_label, alignment=Qt.AlignLeft)
        message = "<div style=text-indent:24px;font-size:12px;line-height:18px;>" + message + "</div>"
        message_label = QLabel(message, self)
        message_label.setMinimumWidth(155)

        message_label.setWordWrap(True)
        message_layout.addWidget(message_label)
        main_layout.addLayout(message_layout)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        cancel_button = QPushButton("取消", self)
        cancel_button.clicked.connect(self.close)
        button_layout.addWidget(cancel_button)

        confirm_button = QPushButton("确定", self)
        confirm_button.clicked.connect(self.make_sure_confirm_operate)
        button_layout.addWidget(confirm_button)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def make_sure_confirm_operate(self):
        self.confirm_operate.emit()
        self.close()


class InformationPopup(QDialog):
    def __init__(self, message, *args, **kwargs):
        super(InformationPopup, self).__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle("提示")
        self.setFixedWidth(230)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(QMargins(1, 0, 1, 0))
        message_layout = QHBoxLayout()
        message_layout.setContentsMargins(8, 5, 8, 5)
        message_layout.setSpacing(5)
        icon_label = QLabel(self)
        icon_label.setFixedSize(50, 50)
        icon_label.setPixmap(QPixmap("media/icons/information.png"))
        icon_label.setScaledContents(True)
        message_layout.addWidget(icon_label, alignment=Qt.AlignLeft)
        message = "<div style=text-indent:24px;line-height:25px;>" + message + "</div>"
        message_label = QLabel(message, self)
        message_label.setMinimumWidth(155)
        message_label.setWordWrap(True)
        message_layout.addWidget(message_label)
        main_layout.addLayout(message_layout)

        h_line = QFrame(self)
        h_line.setLineWidth(1)
        h_line.setContentsMargins(QMargins(0,0,0,0))
        h_line.setFrameStyle(QFrame.HLine | QFrame.Plain)
        main_layout.addWidget(h_line)
        h_line.setObjectName("sepLine")

        buttons_widget = QWidget(self)
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(QMargins(8, 8, 8, 8))
        buttons_widget.setObjectName("buttonWidget")
        confirm_button = QPushButton("确定", self)
        confirm_button.clicked.connect(self.close)
        buttons_layout.addWidget(confirm_button, alignment=Qt.AlignBottom | Qt.AlignRight)
        buttons_widget.setLayout(buttons_layout)
        main_layout.addWidget(buttons_widget)
        self.setLayout(main_layout)
        self.setObjectName("informationPopup")
        self.setStyleSheet("#informationPopup{background-color:rgb(255,255,255)}"
                           "#buttonWidget{background-color:rgb(240,240,240)}"
                           "#sepLine{color:rgb(230,230,230)}")



