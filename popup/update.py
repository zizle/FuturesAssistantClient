# _*_ coding:utf-8 _*_
# @File  : update.py
# @Time  : 2020-09-14 11:13
# @Author: zizle

""" 新版本更新弹窗 """
from PyQt5.QtWidgets import QDialog, QVBoxLayout,QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal


class NewVersionPopup(QDialog):
    to_update = pyqtSignal()

    def __init__(self, message, *args, **kwargs):
        super(NewVersionPopup, self).__init__(*args, *kwargs)
        self.setWindowFlags(self.windowFlags() | Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint)
        self.setMinimumWidth(320)
        self.force = False
        self.setAttribute(Qt.WA_DeleteOnClose)
        main_layout = QVBoxLayout()
        self.setWindowTitle("新版本")
        label = QLabel(message, self)
        main_layout.addWidget(label)
        self.ignore_button = QPushButton("本次忽略", self)
        self.ignore_button.clicked.connect(self.close)
        self.update_button = QPushButton("立即更新", self)
        self.update_button.clicked.connect(self.to_update_page)
        self.update_button.setFocus()
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.ignore_button)
        button_layout.addWidget(self.update_button)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def to_update_page(self):
        self.hide()
        self.to_update.emit()
        self.close()
        
    def closeEvent(self, event):
        if self.force:
            event.ignore()
        else:
            super(NewVersionPopup, self).closeEvent(event)

    def set_force(self):
        """ 设置强制更新 """
        self.force = True
        self.ignore_button.hide()

