# _*_ coding:utf-8 _*_
# @File  : weekly_index.py
# @Time  : 2020-12-24 09:37
# @Author: zizle

""" 周度持仓指数变化 """


import json
import datetime
import pandas as pd
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QDateEdit, QLabel, QPushButton, QSplitter,
                             QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QFileDialog)
from PyQt5.QtCore import QDate, Qt, QMargins, QObject, pyqtSignal
from xlsxwriter.exceptions import FileCreateError
from widgets import OptionWidget, ChartViewWidget
from popup.message import InformationPopup
from apis.position import PositionAPI
from utils.constant import VERTICAL_SCROLL_STYLE, BLUE_STYLE_HORIZONTAL_STYLE
from utils.characters import full_width_to_half_width
from utils.client import set_weekly_exclude_variety, get_weekly_exclude_variety


# 图形数据交互
class ChartChannel(QObject):
    chartSource = pyqtSignal(str, str, str)
    chartResize = pyqtSignal(int, int)


class WeeklyPositionPrice(QWidget):
    """ 周度持仓指数变化窗口 """
    def __init__(self, *args, **kwargs):
        super(WeeklyPositionPrice, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        option_widget = OptionWidget(self)
        option_layout = QHBoxLayout()
        option_layout.addWidget(QLabel('日期:', self))
        self.date_edit = QDateEdit(self)
        current_date = QDate.currentDate()
        self.date_edit.setDate(current_date)
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setMaximumDate(current_date)
        self.date_edit.setMinimumDate(current_date.addMonths(-1))  # 支持一个月内变动
        option_layout.addWidget(self.date_edit)

        self.query_button = QPushButton('查询', self)
        option_layout.addWidget(self.query_button)

        # 数据导出
        self.export_table = QPushButton('数据导出', self)
        option_layout.addWidget(self.export_table)

        option_layout.addStretch()

        # 屏蔽品种
        option_layout.addWidget(QLabel('屏蔽品种(中横线间隔):', self))
        self.exclude_variety = QLineEdit(self)
        self.exclude_variety.setToolTip('输入想要去除的品种交易代码,以 - 间隔')
        option_layout.addWidget(self.exclude_variety)

        option_widget.setFixedHeight(45)
        option_widget.setLayout(option_layout)

        layout.addWidget(option_widget)
        # 图形展示区
        splitter = QSplitter(self)
        splitter.setOrientation(Qt.Vertical)
        # 数据交互通道
        self.channel = ChartChannel()
        self.chart_view = ChartViewWidget(self.channel, 'file:/html/charts/weekly_position.html', self)
        splitter.addWidget(self.chart_view)
        # 表格展示区
        self.table = QTableWidget(self)
        self.table.verticalHeader().hide()
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setStyleSheet(BLUE_STYLE_HORIZONTAL_STYLE)
        self.table.verticalScrollBar().setStyleSheet(VERTICAL_SCROLL_STYLE)
        splitter.addWidget(self.table)
        splitter.setSizes([self.parent().height() * 0.7, self.parent().height() * 0.3])

        layout.addWidget(splitter)

        self.setLayout(layout)

        """ 逻辑部分 """
        # 设置初始化的屏蔽持仓品种
        self.exclude_variety.setText(get_weekly_exclude_variety())

        self.query_api = PositionAPI(self)
        self.query_api.weekly_increase_data.connect(self.weekly_increase_reply)

        self.date_edit.dateChanged.connect(self.get_current_data)

        self.chart_view.page().loadFinished.connect(self.chart_page_loaded)

        self.query_button.clicked.connect(self.get_current_data)  # 查询

        self.export_table.clicked.connect(self.export_table_data)  # 导出数据

    def read_table_data(self):
        header_list = []
        value_list = []
        for header_col in range(self.table.columnCount()):
            header_list.append(
                self.table.horizontalHeaderItem(header_col).text()
            )
        for row in range(self.table.rowCount()):
            row_list = []
            for col in range(self.table.columnCount()):
                item_value = self.table.item(row, col).text()
                try:
                    value = datetime.datetime.strptime(item_value, '%Y%m%d') if col == 0 else float(
                        self.table.item(row, col).text().replace(',', ''))
                except ValueError:
                    value = item_value
                row_list.append(value)
            value_list.append(row_list)
        return pd.DataFrame(value_list, columns=header_list)

    def export_table_data(self):
        """ 导出数据 """
        table_df = self.read_table_data()
        filepath, _ = QFileDialog.getSaveFileName(self, '保存文件', '周度持仓变化幅度表', 'EXCEL文件(*.xlsx *.xls)')
        if filepath:
            # 3 导出数据
            writer = pd.ExcelWriter(filepath, engine='xlsxwriter', datetime_format='YYYY-MM-DD')
            # 多级表头默认会出现一个空行,需改pandas源码,这里不做处理
            table_df.to_excel(writer, sheet_name='品种周度变化', encoding='utf8', index=False,
                              merge_cells=False)
            work_sheets = writer.sheets['品种周度变化']
            book_obj = writer.book
            format_obj = book_obj.add_format({'font_name': 'Arial', 'font_size': 9})
            work_sheets.set_column('A:G', 17, cell_format=format_obj)
            try:
                writer.save()
            except FileCreateError:
                p = InformationPopup('请关闭打开的文件再进行替换保存!', self)
                p.exec_()

    def chart_page_loaded(self):
        self.get_current_data()

    def get_current_data(self):
        """ 获取数据 """
        self.table.clear()
        set_weekly_exclude_variety(self.exclude_variety.text().strip())  # 保存本次使用的屏蔽品种
        exclude_variety = (full_width_to_half_width(self.exclude_variety.text())).upper()
        self.query_api.get_weekly_increase(
            query_date=self.date_edit.date().toString('yyyyMMdd'), exclude_variety=exclude_variety)

    def weekly_increase_reply(self, data):
        """ 周度数据返回了 """
        last_date = datetime.datetime.strptime(data['last_date'], '%Y%m%d')
        current_date = datetime.datetime.strptime(data['current_date'], '%Y%m%d')
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            '品种', last_date.strftime('%Y.%m.%d') + '持仓', current_date.strftime('%Y.%m.%d') + '持仓', '持仓涨跌%',
            last_date.strftime('%Y.%m.%d') + '指数', current_date.strftime('%Y.%m.%d') + '指数', '权重指数涨跌%'])
        self.table_show_data(data['data'])

        base_option = {
            'title': '国内商品期货(指数)一周持仓变化及涨跌幅统计',
            'subtext': '{}-{}'.format(last_date.strftime('%m.%d'), current_date.strftime('%m.%d'))
        }
        self.show_charts(data['data'], base_option)

    def table_show_data(self, records):
        # 在表格显示
        self.table.setRowCount(len(records))
        for row, row_item in enumerate(records):
            item0 = QTableWidgetItem(row_item['variety_name'])
            item0.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 0, item0)
            item1 = QTableWidgetItem(format(row_item['l_position'], ','))
            item1.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 1, item1)
            item2 = QTableWidgetItem(format(row_item['c_position'], ','))
            item2.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 2, item2)
            item3 = QTableWidgetItem('%.2f' % (row_item['position_increase'] * 100))
            item3.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 3, item3)

            item4 = QTableWidgetItem(format(row_item['l_price'], ','))
            item4.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 4, item4)
            item5 = QTableWidgetItem(format(row_item['c_price'], ','))
            item5.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 5, item5)
            item6 = QTableWidgetItem('%.2f' % (row_item['wp_increase'] * 100))
            item6.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 6, item6)

            self.table.setRowHeight(row, 24)

    def show_charts(self, source_data, base_option):
        """ 显示图形 """
        self.chart_view.set_chart_option(json.dumps(source_data), json.dumps(base_option), '')

