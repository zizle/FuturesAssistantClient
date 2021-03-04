# _*_ coding:utf-8 _*_
# @File  : correlation.py
# @Time  : 2020-12-03 16:54
# @Author: zizle

""" 相关性计算 """

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QTableWidget, QDateEdit
from PyQt5.QtCore import Qt, QMargins, QDate

from widgets import OptionWidget


class CorrelationWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(CorrelationWidget, self).__init__(*args, **kwargs)
        """ UI部分 """
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(QMargins(0, 0, 0, 0))
        opts_layout = QHBoxLayout()
        option_widget = OptionWidget(self)

        self.three_month = QPushButton('近3月', self)
        self.six_month = QPushButton('近6月', self)
        self.one_year = QPushButton('近1年', self)
        opts_layout.addWidget(self.three_month)
        opts_layout.addWidget(self.six_month)
        opts_layout.addWidget(self.one_year)

        self.custom_time = QPushButton('自定义', self)
        opts_layout.addWidget(self.custom_time)

        c_date = QDate().currentDate()
        e_date = QDate(c_date.year() - 1, c_date.month(), c_date.day())
        self.start_date = QDateEdit(self)
        self.start_date.setDate(e_date)
        self.start_date.setDisplayFormat('yyyy-MM-dd')
        self.start_date.setCalendarPopup(True)
        self.start_date.setEnabled(False)

        self.end_date = QDateEdit(self)
        self.end_date.setDisplayFormat('yyyy-MM-dd')
        self.end_date.setDate(c_date)
        self.end_date.setCalendarPopup(True)
        self.end_date.setEnabled(False)

        opts_layout.addWidget(self.start_date)
        opts_layout.addWidget(QLabel(' - ', self))
        opts_layout.addWidget(self.end_date)

        opts_layout.addStretch()

        option_widget.setLayout(opts_layout)
        option_widget.setFixedHeight(45)
        main_layout.addWidget(option_widget)

        self.corr_table = QTableWidget(self)
        main_layout.addWidget(self.corr_table)

        m = QLabel('暂未开放', self)
        m.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(m)
        option_widget.hide()
        self.corr_table.hide()
        self.setLayout(main_layout)

        """ 业务部分 """
        self.start_date_str = None
        self.end_date_str = None
        self.three_month.clicked.connect(lambda: self.set_date_range(3))
        self.six_month.clicked.connect(lambda: self.set_date_range(6))
        self.one_year.clicked.connect(lambda: self.set_date_range(12))

        self.custom_time.clicked.connect(self.set_custom_date_range)

        self.three_month.click()

    def set_date_range(self, month):
        # 设置起始日期
        print(month)
        self.start_date.setEnabled(False)
        self.end_date.setEnabled(False)

    def set_custom_date_range(self):
        self.start_date.setEnabled(True)
        self.end_date.setEnabled(True)

    def get_correlation_data(self):
        pass