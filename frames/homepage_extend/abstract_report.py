# _*_ coding:utf-8 _*_
# @File  : abstract_report.py
# @Time  : 2020-10-15 11:28
# @Author: zizle

""" 各种报告的UI """
import json
from PyQt5.QtWidgets import (qApp, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QHeaderView, QTableWidgetItem)
from PyQt5.QtCore import Qt, QRect, QUrl, QMargins
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtNetwork import QNetworkRequest
from widgets import Paginator, PDFContentPopup
from settings import STATIC_URL, SERVER_API, ADMINISTRATOR

from frames.product.message_service import ReportTable


class ReportAbstract(QWidget):
    def __init__(self, *args, **kwargs):
        super(ReportAbstract, self).__init__(*args, **kwargs)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(QMargins(58, 28, 58, 28))

        # 操作的控制控件
        title_widget = QWidget(self)
        title_widget.setMinimumWidth(1080)  # 与显示的table一样宽
        title_layout = QVBoxLayout()
        title_layout.setContentsMargins(QMargins(0, 0, 0, 0))
        self.page_name = QLabel(self)
        title_layout.addWidget(self.page_name, alignment=Qt.AlignLeft)

        opts_layout = QHBoxLayout()
        opts_layout.addWidget(QLabel("品种:", self))
        # self.date_edit = QDateEdit(self)
        # self.date_edit.setDisplayFormat("yyyy-MM-dd")
        # self.date_edit.setCalendarPopup(True)
        # current_hour = QTime.currentTime().hour()
        # current_date = QDate.currentDate() if current_hour >= 16 else QDate.currentDate().addDays(-1)
        # self.date_edit.setDate(current_date)
        # opts_layout.addWidget(self.date_edit)
        self.variety_combobox = QComboBox(self)
        self.variety_combobox.addItem("全部", "0")
        self.variety_combobox.setFixedWidth(100)
        opts_layout.addWidget(self.variety_combobox)
        opts_layout.addStretch()
        # 分页器
        self.paginator = Paginator(parent=self)
        opts_layout.addWidget(self.paginator)

        title_layout.addLayout(opts_layout)

        title_widget.setLayout(title_layout)

        main_layout.addWidget(title_widget)

        self.report_table = ReportTable(self)
        self.report_table.setMinimumWidth(1080)
        main_layout.addWidget(self.report_table)
        self.setLayout(main_layout)
        self.page_name.setObjectName("pageName")
        self.setStyleSheet(
            "#pageName{color:rgb(233,66,66);font-style:italic;font-size:25px}"
        )
        self.get_all_variety()  # 获取所有品种
        # # 点击事件
        # self.report_table.cellClicked.connect(self.view_detail_report)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), QPixmap("media/beijing.jpg"), QRect())

    def get_all_variety(self):
        """ 获取系统中所有的品种 """
        url = SERVER_API + "variety/all/"
        network_manager = getattr(qApp, "_network")
        reply = network_manager.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(self.all_variety_reply)

    def all_variety_reply(self):
        """ 获取所有品种返回 """
        reply = self.sender()
        if reply.error():
            pass
        else:
            data = json.loads(reply.readAll().data().decode("utf-8"))
            for group_name, group_varieties in data["varieties"].items():
                for variety_item in group_varieties:
                    self.variety_combobox.addItem(variety_item["variety_name"], variety_item["variety_en"])
        reply.deleteLater()

    def get_current_page_report(self, report_type, current_page=None):
        """ 获取当前页的报告"""
        if current_page is None:
            current_page = self.paginator.get_current_page()
        variety_en = self.variety_combobox.currentData()
        url = SERVER_API + "report-file/paginator/?report_type={}&variety_en={}&page={}&page_size=22".format(report_type, variety_en, current_page)
        network_manager = getattr(qApp, "_network")
        reply = network_manager.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(self.current_report_reply)

    def current_report_reply(self):
        """ 当前报告返回 """
        reply = self.sender()
        if reply.error():
            pass
        else:
            data = json.loads(reply.readAll().data().decode("utf-8"))
            self.paginator.setTotalPages(data["total_page"])
            self.show_report_content(data["reports"])
        reply.deleteLater()

    def set_page_name(self, name: str):
        self.page_name.setText(name)

    def show_report_content(self, reports):
        """ 显示报告 """
        self.report_table.setColumnCount(5)
        self.report_table.setHorizontalHeaderLabels(['相关品种', '标题', '类型', '日期', '阅读'])
        header_keys = ["variety_zh", "title", "type_text", "file_date", "reading"]
        self.report_table.horizontalHeader().setDefaultSectionSize(150)
        self.report_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        if not ADMINISTRATOR:
            self.report_table.horizontalHeader().setSectionHidden(4, True)
        self.report_table.show_report_contents(reports, header_keys)

