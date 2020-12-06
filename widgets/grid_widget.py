# _*_ coding:utf-8 _*_
# @File  : grid_widget.py
# @Time  : 2020-12-04 10:59
# @Author: zizle
""" 以grid布局自适应宽度放置控件的控件 """

from PyQt5.QtWidgets import QWidget, QGridLayout, QVBoxLayout
from PyQt5.QtCore import Qt, QMargins


class GridWidget(QWidget):
    def __init__(self, *args, **kwargs):
        """
        传入控件列表,自适应宽度布局控件
        :param widget_width: 控件的宽度
        :param widgets_list: 待布局的按钮{}对象列表
        :param signal_key: 点击传出的信号的key
        :param args:
        :param kwargs:
        """
        super(GridWidget, self).__init__(*args, **kwargs)
        layout = QGridLayout()
        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        layout.setSpacing(3)
        self.setLayout(layout)
        self.widgets_list = None
        self.widget_width = None

    def set_widgets(self, widget_width: int, widgets_list: list):
        self.widgets_list = widgets_list
        self.widget_width = widget_width
        self.show_widgets()

    def show_widgets(self):
        if not self.widgets_list or not self.widget_width:
            return
        row_index = col_index = 0
        col_count = self.parent().width() // (self.widget_width + 6)
        for widget in self.widgets_list:
            widget.setParent(self)
            if col_index >= col_count:
                col_index = 0
                row_index += 1
            self.layout().addWidget(widget, row_index, col_index)
            col_index += 1

    def resizeEvent(self, event):
        super(GridWidget, self).resizeEvent(event)
        self.show_widgets()
