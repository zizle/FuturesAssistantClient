# _*_ coding:utf-8 _*_
# @File  : exchange_strategy.py
# @Time  : 2021-01-20 09:46
# @Author: zizle


from PyQt5.QtWidgets import (QScrollArea, QFrame, QWidget, QVBoxLayout, QHBoxLayout, QDateEdit, QLabel, QGridLayout)
from PyQt5.QtGui import QPalette, QFont, QColor, QPainter, QBrush, QPen
from PyQt5.QtCore import QDate, QTimeLine, QMargins, Qt, QRectF, QLineF, QTimer

from utils.constant import VERTICAL_SCROLL_STYLE
from apis.product import ExchangeStrategyAPI


class CirclePoint(QLabel):
    """ 时间轴上的点 """
    def __init__(self, *args, **kwargs):
        super(CirclePoint, self).__init__(*args, **kwargs)
        self.setFixedSize(14, 14)

    def paintEvent(self, event):
        super(CirclePoint, self).paintEvent(event)
        painter = QPainter(self)

        painter.setPen(Qt.NoPen)

        painter.setBrush(QBrush(QColor(160, 160, 160)))
        rect = QRectF(0, 0, 14, 14)
        painter.drawEllipse(rect)

        painter.setBrush(QBrush(Qt.red))
        rect = QRectF(3.5, 3.5, 7, 7)
        painter.drawEllipse(rect)


class MsgTextLabel(QLabel):
    """ 显示内容的QLabel """
    # def __init__(self, *args, **kwargs):
    #     super(MsgTextLabel, self).__init__(*args, **kwargs)

    def enterEvent(self, event):
        super(MsgTextLabel, self).enterEvent(event)
        self.setStyleSheet('background-color:rgb(200,200,200);border-radius:5px')

    def leaveEvent(self, event):
        super(MsgTextLabel, self).leaveEvent(event)
        self.setStyleSheet('background-color:rgb(245,245,245);border-radius:5px')


class ShortMsgContentWidget(QWidget):
    """ 每个短讯的内容块(总) """
    def __init__(self, time_str: str, content_str: str, *args, **kwargs):
        super(ShortMsgContentWidget, self).__init__(*args, **kwargs)
        layout = QGridLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(CirclePoint(self), 0, 0)
        time_label = QLabel(time_str, self)
        time_font = QFont()
        time_font.setBold(True)
        time_font.setPointSize(13)
        p = time_label.palette()
        p.setColor(QPalette.WindowText, Qt.red)
        time_label.setPalette(p)
        time_label.setFont(time_font)
        layout.addWidget(time_label, 0, 1)
        c = MsgTextLabel(content_str, self)
        c.setStyleSheet('background-color:rgb(245,245,245);border-radius:5px')
        c.setContentsMargins(QMargins(8, 0, 8, 2))
        c.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        c.setWordWrap(True)
        layout.addWidget(c, 1, 1)
        self.setLayout(layout)


class AreaWidget(QWidget):
    """ 置于滚动区域的widget """

    def __init__(self, *args, **kwargs):
        super(AreaWidget, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        layout.setContentsMargins(QMargins(20, 0, 10, 5))
        layout.setSpacing(25)
        self.setLayout(layout)

    # def paintEvent(self, event):
    #     super(AreaWidget, self).paintEvent(event)
    #     painter = QPainter(self)
    #     painter.setPen(QPen(QColor(160, 160, 160), 3))
    #     line = QLineF(27, 0, 27, self.height())
    #     painter.drawLine(line)


class ExchangeStrategy(QWidget):

    def __init__(self, *args, **kwargs):
        super(ExchangeStrategy, self).__init__(*args, **kwargs)
        """ UI部分 """
        layout = QVBoxLayout()
        layout.setContentsMargins(QMargins(0, 20, 0, 0))

        self.content_scroll_area = QScrollArea(self)
        self.content_scroll_area.setFrameShape(QFrame.NoFrame)
        self.content_scroll_area.setBackgroundRole(QPalette.Light)
        self.content_scroll_area.verticalScrollBar().setStyleSheet(VERTICAL_SCROLL_STYLE)

        layout.addWidget(self.content_scroll_area)

        # 内容控件
        self.content_widget = AreaWidget(self)
        self.content_scroll_area.setWidget(self.content_widget)
        # self.content_widget.setFixedWidth(self.parent().width())
        self.content_scroll_area.setWidgetResizable(True)

        self.setLayout(layout)
        """ 逻辑部分 """
        self.strategy_api = ExchangeStrategyAPI(self)
        self.strategy_api.strategy_reply.connect(self.strategy_reply)

        self.get_strategy()

    def get_strategy(self):
        """ 请求新的投顾策略"""
        self.strategy_api.get_strategy()

    def strategy_reply(self, data):
        """ 数据返回 """
        # 显示数据
        for msg_item in data['strategy']:
            content = "<div style='text-indent:30px;line-height:28px;'>{}</div>".format(msg_item['content'])
            m = ShortMsgContentWidget(time_str=msg_item['create_time'], content_str=content, parent=self)
            self.content_widget.layout().addWidget(m)
        self.content_widget.layout().addStretch()



