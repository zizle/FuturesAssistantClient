# _*_ coding:utf-8 _*_
# @File  : weekly_report.py
# @Time  : 2020-10-15 11:28
# @Author: zizle
import json
from PyQt5.QtWidgets import qApp
from PyQt5.QtNetwork import QNetworkRequest
from PyQt5.QtCore import QUrl
from .abstract_report import ReportAbstract
from settings import SERVER_API


class WeeklyReport(ReportAbstract):
    def __init__(self, *args, **kwargs):
        super(WeeklyReport, self).__init__(*args, **kwargs)
        self.set_page_name("研究周报")
        # 获取初始页报告
        self.get_current_page_report(report_type="weekly", current_page=1)
        # 品种下拉框选择
        self.variety_combobox.currentIndexChanged.connect(self.query_current_report)
        # 点击页码的事件
        self.paginator.clicked.connect(self.query_current_page)

    def query_current_report(self):
        # 点击查询得先重置当前页码
        self.paginator.setCurrentPage(1)
        self.get_current_page_report(report_type="weekly", current_page=1)

    def query_current_page(self):
        self.get_current_page_report(report_type="weekly")
