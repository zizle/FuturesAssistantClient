# _*_ coding:utf-8 _*_
# @File  : widget.py
# @Time  : 2020-12-03 17:47
# @Author: zizle
from PyQt5.QtWidgets import QWidget, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor


class OptionWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(OptionWidget, self).__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_StyledBackground, True)  # 必须设置,如果不设置将导致子控件产生阴影
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setOffset(0, 1)
        shadow.setColor(QColor(100, 100, 100))
        shadow.setBlurRadius(5)
        self.setGraphicsEffect(shadow)
        self.setObjectName("optionWidget")
        self.setStyleSheet("#optionWidget{background-color:rgb(245,245,245)}")

    def enterEvent(self, event):
        effect = self.graphicsEffect()
        effect.setOffset(1, 2)
        self.setGraphicsEffect(effect)

    def leaveEvent(self, event):
        effect = self.graphicsEffect()
        effect.setOffset(0, 1)
        self.setGraphicsEffect(effect)