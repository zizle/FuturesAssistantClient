# _*_ coding:utf-8 _*_
# @File  : daily_report.py
# @Time  : 2020-10-15 09:37
# @Author: zizle
from .abstract_report import ReportAbstract


class DailyReport(ReportAbstract):
    def __init__(self, *args, **kwargs):
        super(DailyReport, self).__init__(*args, **kwargs)
        # 设置页面名称
        self.set_page_name("收盘评论")
        # 获取初始页报告
        self.get_current_page_report(report_type=1, current_page=1)
        # 品种下拉框选择
        self.variety_combobox.currentIndexChanged.connect(self.query_current_report)
        # 点击页码的事件
        self.paginator.clicked.connect(self.query_current_page)

    def query_current_report(self):
        # 点击查询得先重置当前页码
        self.paginator.setCurrentPage(1)
        self.get_current_page_report(report_type=1, current_page=1)

    def query_current_page(self):
        self.get_current_page_report(report_type=1)


