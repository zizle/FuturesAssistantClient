# _*_ coding:utf-8 _*_
# @File  : widget.py
# @Time  : 2020-12-03 17:47
# @Author: zizle
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QWidget, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, QUrl, pyqtSignal
from PyQt5.QtGui import QColor


class OptionWidget(QWidget):
    enter_signal = pyqtSignal()
    leave_signal = pyqtSignal()

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
        super(OptionWidget, self).enterEvent(event)
        effect = self.graphicsEffect()
        effect.setOffset(1, 2)
        self.setGraphicsEffect(effect)
        self.enter_signal.emit()

    def leaveEvent(self, event):
        super(OptionWidget, self).leaveEvent(event)
        effect = self.graphicsEffect()
        effect.setOffset(0, 1)
        self.setGraphicsEffect(effect)
        self.leave_signal.emit()


class ChartViewWidget(QWebEngineView):
    def __init__(self, data_channel, filepath: str, *args, **kwargs):
        super(ChartViewWidget, self).__init__(*args, **kwargs)
        data_channel.setParent(self)
        # 加载图形容器
        self.page().load(QUrl(filepath))  # 加载页面
        # 设置与页面信息交互的通道
        channel_qt_obj = QWebChannel(self.page())  # 实例化qt信道对象,必须传入页面参数
        self.contact_channel = data_channel  # 页面信息交互通道
        self.page().setWebChannel(channel_qt_obj)
        channel_qt_obj.registerObject("pageContactChannel", self.contact_channel)  # 信道对象注册信道,只能注册一个

    def resizeEvent(self, event):
        super(ChartViewWidget, self).resizeEvent(event)
        self.resize_chart()

    def set_chart_option(self, source_data, base_option, chart_type):
        """ 传入数据设置图形 """
        self.contact_channel.chartSource.emit(source_data, base_option, chart_type)
        self.resize_chart()

    def resize_chart(self):
        self.contact_channel.chartResize.emit(self.width(), self.height())

