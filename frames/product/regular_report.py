# _*_ coding:utf-8 _*_
# @File  : regular_report.py
# @Time  : 2020-10-27 13:16
# @Author: zizle
import json
from PyQt5.QtWidgets import qApp, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from widgets.pdf_shower import PDFContentPopup
from .regular_report_ui import RegularReportUI
from settings import SERVER_API, STATIC_URL


class RegularReport(RegularReportUI):
    def __init__(self, *args, **kwargs):
        super(RegularReport, self).__init__(*args, **kwargs)
        self.network_manager = getattr(qApp, "_network")
        if not self.network_manager:
            self.network_manager = QNetworkAccessManager(self)
        self.variety_combobox.addItem("全部", "0")
        for report_type in [
            {"name": "收盘日评", "type_id": "daily"},
            {"name": "每周报告", "type_id": "weekly"},
            {"name": "月度报告", "type_id": "monthly"},
            {"name": "年度报告", "type_id": "annual"},
        ]:
            self.report_combobox.addItem(report_type["name"], report_type["type_id"])

        self.query_button.clicked.connect(self.query_reports)

        self.paginator.clicked.connect(self.get_current_report)

        self.report_table.cellClicked.connect(self.view_detail_report)

        self.get_all_variety()
        self.get_current_report()

    def get_all_variety(self):
        """ 获取所有品种 """
        url = SERVER_API + "variety/all/"
        reply = self.network_manager.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(self.all_variety_reply)

    def all_variety_reply(self):
        """ 获取品种返回 """
        reply = self.sender()
        if reply.error():
            pass
        else:
            data = json.loads(reply.readAll().data().decode("utf-8"))
            for group_name, group_varieties in data["varieties"].items():
                for variety_item in group_varieties:
                    self.variety_combobox.addItem(variety_item["variety_name"], variety_item["variety_en"])
        reply.deleteLater()

    def query_reports(self):
        self.paginator.setCurrentPage(1)
        self.get_current_report()

    def get_current_report(self, current_page=None):
        """ 分页获取当前报告 """
        if current_page is None:
            current_page = self.paginator.get_current_page()
        report_type = self.report_combobox.currentData()
        current_variety = self.variety_combobox.currentData()
        url = SERVER_API + "report-file/paginator/?report_type={}&variety_en={}&page={}&page_size=22".format(report_type, current_variety, current_page)
        reply = self.network_manager.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(self.report_information_reply)

    def report_information_reply(self):
        """ 报告数据返回 """
        reply = self.sender()
        if reply.error():
            pass
        else:
            data = json.loads(reply.readAll().data().decode("utf-8"))
            self.paginator.setTotalPages(data["total_page"])
            self.show_report_information(data["reports"])
        reply.deleteLater()

    def show_report_information(self, reports):
        """ 显示报告 """
        self.report_table.clear()
        header_keys = ["variety_zh", "title", "type_text", "date"]
        self.report_table.setColumnCount(len(header_keys))
        self.report_table.setHorizontalHeaderLabels(["相关品种", "标题", "报告类型", "日期"])
        self.report_table.setRowCount(len(reports))
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        if len(reports) >= 20:
            self.report_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        else:
            self.report_table.verticalHeader().setSectionResizeMode(QHeaderView.Interactive)
        for row, row_item in enumerate(reports):
            for col, col_key in enumerate(header_keys):
                item = QTableWidgetItem(str(row_item[col_key]))
                if col == 0:
                    item.setData(Qt.UserRole, row_item["filepath"])
                item.setTextAlignment(Qt.AlignCenter)
                self.report_table.setItem(row, col, item)

    def view_detail_report(self, row, col):
        """ 查看报告内容 """
        item = self.report_table.item(row, 0)
        title = self.report_table.item(row, 1).text()
        file_url = STATIC_URL + item.data(Qt.UserRole)
        p = PDFContentPopup(file=file_url, title=title, parent=self)
        p.exec_()
