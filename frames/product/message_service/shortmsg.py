# _*_ coding:utf-8 _*_
# @File  : shortmsg.py
# @Time  : 2020-12-22 14:04
# @Author: zizle

""" 短信通 """

from PyQt5.QtWidgets import (QScrollArea, QFrame, QWidget, QVBoxLayout, QHBoxLayout, QDateEdit, QLabel, QGridLayout)
from PyQt5.QtGui import QPalette, QFont, QColor, QPainter, QBrush, QPen
from PyQt5.QtCore import QDate, QTimeLine, QMargins, Qt, QRectF, QLineF, QTimer

from widgets import OptionWidget
from utils.constant import VERTICAL_SCROLL_STYLE
from apis.product import ShortMsgAPI


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

    def paintEvent(self, event):
        super(AreaWidget, self).paintEvent(event)
        painter = QPainter(self)
        painter.setPen(QPen(QColor(160, 160, 160), 3))
        line = QLineF(27, 0, 27, self.height())
        painter.drawLine(line)


class ShortMessage(QWidget):
    WEEKS = {
        1: '星期一', 2: '星期二', 3: '星期三', 4: '星期四', 5: '星期五', 6: '星期六', 7: '星期日'
    }

    def __init__(self, *args, **kwargs):
        super(ShortMessage, self).__init__(*args, **kwargs)
        """ UI部分 """
        layout = QVBoxLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        option_layout = QHBoxLayout()
        option_widget = OptionWidget(self)
        option_widget.enter_signal.connect(self.enter_option_widget)
        option_widget.leave_signal.connect(self.leave_option_widget)
        self.date_edit = QDateEdit(self)
        current_date = QDate.currentDate()
        self.date_edit.setDate(current_date)
        self.date_edit.setDisplayFormat('yyyy-MM-dd')
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setFixedWidth(100)

        option_layout.addWidget(self.date_edit)

        # 显示星期
        font = QFont()
        font.setBold(True)
        font.setPointSize(13)
        week = self.WEEKS.get(current_date.dayOfWeek(), '')
        self.week_label = QLabel(week, self)
        self.week_label.setFixedWidth(60)
        self.week_label.setFont(font)
        option_layout.addWidget(self.week_label)

        self.message_label = QLabel('数据持续更新中', option_widget)
        self.message_label.setFixedSize(140, 20)
        p = self.message_label.palette()
        p.setColor(QPalette.WindowText, Qt.red)
        self.message_label.setPalette(p)
        self.message_label.move(180, 10)

        option_layout.addStretch()

        option_widget.setLayout(option_layout)

        option_widget.setFixedHeight(40)

        layout.addWidget(option_widget)

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
        self.timeline = QTimeLine(10000, self)  # 实例化一个时间轴，持续时间为5秒
        self.timeline.setFrameRange(180, 340)  # 设置帧率范围，该值表示在规定的时间内将要执行多少帧
        self.timeline.frameChanged.connect(self.set_message_label_position)  # 帧数变化时发出信号
        self.timeline.setLoopCount(0)  # 传入0代表无限循环运行.传入正整数会运行相应次数，传入负数不运行
        self.timeline.start()  # 启动动画
        # 当前时间
        self.request_start_time = self.date_edit.date().toString('yyyy-MM-ddT00:00:00')
        self.short_msg_api = ShortMsgAPI(self)
        self.short_msg_api.short_messages_reply.connect(self.short_message_reply)

        self.get_message()

        # 重新选择日期
        self.date_edit.dateChanged.connect(self.query_date_changed)

        # 定时获取数据
        self.interval_get_timer = QTimer(self)
        self.interval_get_timer.timeout.connect(self.get_message)
        self.interval_get_timer.start(30000)

    def set_message_label_position(self, frame):
        self.message_label.move(frame, 10)
        if frame <= 181:
            self.timeline.setFrameRange(180, 340)
        elif frame >= 339:
            self.timeline.setFrameRange(340, 180)
        else:
            pass

    def enter_option_widget(self):
        self.timeline.setPaused(True)

    def leave_option_widget(self):
        self.timeline.setPaused(False)

    def query_date_changed(self, date):
        """ 日期改变 """
        self.request_start_time = date.toString('yyyy-MM-ddT00:00:00')
        self.week_label.setText(self.WEEKS.get(date.dayOfWeek(), ''))
        # 删除原来的widget
        self.content_widget.deleteLater()
        self.content_widget = AreaWidget(self)
        self.content_scroll_area.setWidget(self.content_widget)
        # 请求数据
        self.get_message()
        if date == QDate.currentDate():
            self.message_label.show()
            if not self.interval_get_timer.isActive():
                self.interval_get_timer.start(30000)
        else:
            self.message_label.hide()
            if self.interval_get_timer.isActive():
                self.interval_get_timer.stop()

    def get_message(self):
        """ 请求新的短信通 """
        self.short_msg_api.get_time_quantum_short_message(start_time=self.request_start_time)

    def short_message_reply(self, data):
        """ 数据返回 """
        # 显示数据
        for msg_item in data['short_messages']:
            m = ShortMsgContentWidget(time_str=msg_item['time_str'], content_str=msg_item['content'], parent=self)
            self.content_widget.layout().insertWidget(0, m)

        self.content_widget.layout().addStretch()

        if len(data['short_messages']) > 0:
            item = data['short_messages'][-1]
            self.request_start_time = item['create_time']

