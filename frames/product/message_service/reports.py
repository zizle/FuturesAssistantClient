# _*_ coding:utf-8 _*_
# @File  : reports.py
# @Time  : 2020-12-22 17:43
# @Author: zizle
""" 报告 """
from PyQt5.QtGui import QBrush, QColor, QPalette
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QPushButton, QTableWidget, QFrame, \
    QTableWidgetItem, QHeaderView, QAbstractItemView
from PyQt5.QtCore import Qt, QMargins

from settings import STATIC_URL
from widgets import OptionWidget, Paginator, PDFContentPopup
from apis.variety import VarietyAPI
from apis.product import ReportsAPI
from utils.constant import VERTICAL_SCROLL_STYLE, HORIZONTAL_SCROLL_STYLE, HORIZONTAL_STYLE_NO_GRID, HORIZONTAL_HEADER_STYLE


class ReportTable(QTableWidget):
    def __init__(self, *args, **kwargs):
        super(ReportTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()
        self.setEditTriggers(QHeaderView.NoEditTriggers)
        self.setFrameShape(QFrame.NoFrame)
        self.setFocusPolicy(Qt.NoFocus)
        self.setAlternatingRowColors(True)
        # 不能选中
        self.setSelectionMode(QAbstractItemView.NoSelection)
        # 背景透明
        table_palette = self.palette()
        table_palette.setBrush(QPalette.Base, QBrush(QColor(255, 255, 255, 0)))
        self.setPalette(table_palette)
        self.setCursor(Qt.PointingHandCursor)
        self.verticalScrollBar().setStyleSheet(VERTICAL_SCROLL_STYLE)
        self.horizontalScrollBar().setStyleSheet(HORIZONTAL_SCROLL_STYLE)

        # 设置鼠标进入整行颜色变化
        self.setMouseTracking(True)
        self.mouse_last_row = -1
        self.last_row_background = None
        self.itemEntered.connect(self.mouse_enter_item)

        self.horizontalHeader().setStyleSheet(HORIZONTAL_HEADER_STYLE)

        self.cellClicked.connect(self.view_detail_report)

    def mouse_enter_item(self, item):
        current_row = self.row(item)
        # 改变当前行的颜色
        for col in range(self.columnCount()):
            self.item(current_row, col).setForeground(QBrush(QColor(248, 121, 27)))
            self.item(current_row, col).setBackground(QBrush(QColor(220, 220, 220)))
        # 恢复离开行的颜色
        self.recover_row_color()
        self.mouse_last_row = current_row

    def recover_row_color(self):
        if self.mouse_last_row >= 0:
            for col in range(self.columnCount()):
                self.item(self.mouse_last_row, col).setForeground(QBrush(QColor(0, 0, 0)))
                self.item(self.mouse_last_row, col).setBackground(QBrush(QColor(245, 245, 245, 0)))  # 透明

    def leaveEvent(self, *args, **kwargs):
        """ 鼠标离开事件 """
        # 将最后记录行颜色变为原来的样子,且修改记录行为-1
        self.recover_row_color()
        self.mouse_last_row = -1

    def show_report_contents(self, reports, header_keys):
        self.clearContents()
        self.setRowCount(len(reports))
        for row, row_item in enumerate(reports):
            for col, col_key in enumerate(header_keys):
                item = QTableWidgetItem(str(row_item[col_key]))
                if col == 0:
                    item.setData(Qt.UserRole, row_item["filepath"])
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, col, item)

            self.setRowHeight(row, 28)

    def view_detail_report(self, row, col):
        """ 查看报告内容 """
        item = self.item(row, 0)
        title = self.item(row, 1).text()
        file_url = STATIC_URL + item.data(Qt.UserRole)
        p = PDFContentPopup(file=file_url, title=title, parent=self)
        p.exec_()


class MultiReport(QWidget):
    """ 报告显示窗口 """
    REPORT_TYPE = None

    def __init__(self, *args, **kwargs):
        super(MultiReport, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        layout.setSpacing(5)
        option_widget = OptionWidget(self)
        option_layout = QHBoxLayout()
        self.type_label = QLabel('类型', self)
        option_layout.addWidget(self.type_label)

        self.report_combobox = QComboBox(self)
        option_layout.addWidget(self.report_combobox)

        option_layout.addWidget(QLabel('相关品种:', self))

        self.variety_combobox = QComboBox(self)
        self.variety_combobox.setMinimumWidth(100)
        option_layout.addWidget(self.variety_combobox)

        self.query_button = QPushButton('查询', self)
        option_layout.addWidget(self.query_button)

        option_layout.addStretch()

        self.paginator = Paginator()
        self.paginator.setParent(self)
        option_layout.addWidget(self.paginator)

        option_widget.setLayout(option_layout)
        option_widget.setFixedHeight(45)
        layout.addWidget(option_widget)

        self.report_table = ReportTable(self)
        self.report_table.setColumnCount(4)
        self.report_table.setHorizontalHeaderLabels(['相关品种', '标题', '类型', '日期'])
        self.report_table.setShowGrid(False)
        self.report_table.horizontalHeader().setStyleSheet(HORIZONTAL_STYLE_NO_GRID)
        self.report_table.horizontalHeader().setDefaultSectionSize(150)
        self.report_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        layout.addWidget(self.report_table)
        self.setLayout(layout)

        # 报告的API
        self.report_api = ReportsAPI(self)
        self.report_api.reports_reply_signal.connect(self.reports_reply)

        # 品种的API
        self.variety_api = VarietyAPI(self)
        self.variety_api.varieties_sorted.connect(self.varieties_reply)
        self.variety_api.get_variety_en_sorted()

        # 查询事件
        self.query_button.clicked.connect(self.get_current_reports)
        # 页码变化
        self.paginator.clicked.connect(self.get_current_reports)

        # 类型变化
        self.report_combobox.currentTextChanged.connect(self.current_report_type_changed)

        # 品种变化
        self.variety_combobox.currentTextChanged.connect(self.current_variety_changed)

    def varieties_reply(self, data):
        """ 品种返回 """
        self.variety_combobox.clear()
        self.variety_combobox.addItem('全部', '0')
        for v_item in data['varieties']:
            self.variety_combobox.addItem(v_item['variety_name'], v_item['variety_en'])

    def reset_paginator_pages(self):
        """ 重置翻页器 """
        self.paginator.setCurrentPage(1)
        self.paginator.setTotalPages(1)

    def current_variety_changed(self):
        """ 品种变化 """
        if self.report_combobox.currentData() is None:
            return
        self.reset_paginator_pages()
        self.get_current_reports()

    def current_report_type_changed(self):
        """ 类型变化 """
        print(self.variety_combobox.currentData())
        if self.variety_combobox.currentData() is None:
            return
        self.REPORT_TYPE = self.report_combobox.currentData()
        self.reset_paginator_pages()
        self.get_current_reports()

    def get_current_reports(self):
        self.report_api.get_paginator_reports(report_type=self.REPORT_TYPE, variety_en=self.variety_combobox.currentData(),
                                              page=self.paginator.current_page, page_size=30)

    def reports_reply(self, data):
        """ 报告数据返回 """
        header_keys = ['variety_zh', 'title', 'type_text', 'date']
        self.report_table.show_report_contents(data['reports'], header_keys)

        self.paginator.setCurrentPage(data['page'])
        self.paginator.setTotalPages(data['total_page'])


class RegularReport(MultiReport):
    """ 定期报告 """
    def __init__(self, *args, **kwargs):
        super(RegularReport, self).__init__(*args, **kwargs)
        # 添加类型
        for item in [
            {'name': '收盘日评', 'en': 'daily'}, {'name': '每周报告', 'en': 'weekly'}, {'name': '月度报告', 'en': 'monthly'},
            {'name': '年度报告', 'en': 'annual'},
        ]:
            self.report_combobox.addItem(item['name'], item['en'])

        self.REPORT_TYPE = 'daily'


class SpecialReport(MultiReport):
    """ 专题研究 """
    REPORT_TYPE = 'special'

    def __init__(self, *args, **kwargs):
        super(SpecialReport, self).__init__(*args, **kwargs)
        self.type_label.hide()
        self.report_combobox.hide()


class ResearchReport(MultiReport):
    """ 调研报告 """
    REPORT_TYPE = 'research'

    def __init__(self, *args, **kwargs):
        super(ResearchReport, self).__init__(*args, **kwargs)
        self.type_label.hide()
        self.report_combobox.hide()

