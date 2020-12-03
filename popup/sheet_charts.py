# _*_ coding:utf-8 _*_
# @File  : sheet_charts.py
# @Time  : 2020-09-08 10:19
# @Author: zizle

""" 表的图形弹窗 """
import json
import pandas as pd
from PyQt5.QtWidgets import (qApp, QWidget,QTableWidget, QTableWidgetItem, QSplitter, QDialog, QVBoxLayout, QDesktopWidget, QAbstractItemView,
                             QHeaderView, QTextEdit, QPushButton, QMessageBox, QComboBox, QLabel, QLineEdit, QGridLayout)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QIcon, QIntValidator
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtNetwork import QNetworkRequest
from PyQt5.QtWebChannel import QWebChannel
from channels.chart import ChartOptionChannel
from utils.client import get_user_token
from settings import SERVER_API, logger


# 显示一张表的所有图形和源数据
class SheetChartsPopup(QDialog):
    def __init__(self, sheet_id: int, is_own: int, *args, **kwargs):
        super(SheetChartsPopup, self).__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.sheet_id = sheet_id

        # 初始化大小
        available_size = QDesktopWidget().availableGeometry()  # 用户的桌面信息,来改变自身窗体大小
        available_width, available_height = available_size.width(), available_size.height()
        self.resize(available_width * 0.66, available_height * 0.72)

        main_layout = QVBoxLayout()
        main_splitter = QSplitter(self)
        main_splitter.setOrientation(Qt.Vertical)

        self.chart_container = QWebEngineView(self)
        user_token = get_user_token().split(' ')[1]
        charts_url = SERVER_API + "sheet/{}/chart/?is_own={}&token={}".format(self.sheet_id, is_own, user_token)
        self.chart_container.load(QUrl(charts_url))
        main_splitter.addWidget(self.chart_container)

        self.sheet_table = QTableWidget(self)
        self.sheet_table.verticalHeader().hide()
        self.sheet_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        main_splitter.addWidget(self.sheet_table)
        main_splitter.setSizes([available_height * 0.43, available_height * 0.3])  # 初始化大小

        main_layout.addWidget(main_splitter)
        self.setLayout(main_layout)

        self.sheet_table.horizontalHeader().setStyleSheet(
            "QHeaderView::section{background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,"
            "stop:0 #bbbbbb, stop: 0.5 #eeeeee,stop: 0.6 #eeeeee, stop:1 #bbbbbb);"
            "border:1px solid rgb(201,202,202);border-left:none;"
            "min-height:25px;min-width:40px;font-weight:bold;font-size:13px};"
        )

        self._get_sheet_values()

    def _get_sheet_values(self):
        """ 获取表格原始数据 """
        network_manager = getattr(qApp, "_network")
        url = SERVER_API + "sheet/{}/".format(self.sheet_id)
        reply = network_manager.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(self.sheet_values_reply)

    def sheet_values_reply(self):
        """ 获取到数据表数据 """
        reply = self.sender()
        if reply.error():
            logger.error("用户获取数据表源数据失败:{}".format(reply.error()))
        else:
            data = reply.readAll().data()
            data = json.loads(data.decode("utf-8"))
            # 使用pandas处理数据到弹窗表格中
            self.handler_sheet_values(data["sheet_values"])

    def handler_sheet_values(self, values):
        """ pandas处理数据到弹窗相应参数中 """
        value_df = pd.DataFrame(values)
        sheet_headers = value_df.iloc[:1].to_numpy().tolist()[0]  # 取表头
        sheet_headers.pop(0)  # 删掉id列
        col_index_list = ["id", ]
        for i, header_item in enumerate(sheet_headers):  # 根据表头生成数据选择项
            col_index_list.append("column_{}".format(i))
        sheet_headers.insert(0, "编号")
        self.sheet_table.setColumnCount(len(sheet_headers))
        self.sheet_table.setHorizontalHeaderLabels(sheet_headers)
        self.sheet_table.horizontalHeader().setDefaultSectionSize(150)
        self.sheet_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.sheet_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)

        table_show_df = value_df.iloc[1:]
        table_show_df = table_show_df.sort_values(by="column_0")
        table_show_df.reset_index(inplace=True)  # 重置索引,让排序生效(赋予row正确的值)
        self.sheet_table.setRowCount(table_show_df.shape[0])
        for row, row_item in table_show_df.iterrows():  # 遍历数据(填入表格显示)
            for col, col_key in enumerate(col_index_list):
                item = QTableWidgetItem(str(row_item[col_key]))
                item.setTextAlignment(Qt.AlignCenter)
                self.sheet_table.setItem(row, col, item)


class DeciphermentPopup(QWidget):
    """ 编辑解说的弹窗 """
    def __init__(self, chart_id, *args, **kwargs):
        super(DeciphermentPopup, self).__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowFlag(Qt.Dialog)
        self.setWindowTitle("解读图形")
        self.resize(380, 200)
        self.chart_id = chart_id
        main_layout = QVBoxLayout()
        self.decipherment_edit = QTextEdit(self)
        main_layout.addWidget(self.decipherment_edit)
        commit_button = QPushButton("确定", self)
        commit_button.clicked.connect(self.commit_current_decipherment)
        main_layout.addWidget(commit_button, alignment=Qt.AlignRight)
        self.setLayout(main_layout)

        self._get_chart_base_information()

    def _get_chart_base_information(self):
        """ 获取图形的基本信息 """
        network_manager = getattr(qApp, "_network")
        url = SERVER_API + "chart/{}/".format(self.chart_id)
        reply = network_manager.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(self.base_information_reply)

    def base_information_reply(self):
        """ 获取基本信息返回 """
        reply = self.sender()
        if reply.error():
            self.decipherment_edit.setPlaceholderText("获取信息失败了......")
        else:
            data = reply.readAll().data()
            data = json.loads(data.decode("utf-8"))
            chart_info = data["data"]
            self.decipherment_edit.setText(chart_info["decipherment"])
        reply.deleteLater()

    def commit_current_decipherment(self):
        """ 上传当前的图形解读 """
        decipherment = self.decipherment_edit.toPlainText()
        body = {
            "decipherment": decipherment
        }

        network_manager = getattr(qApp, "_network")
        url = SERVER_API + "chart-decipherment/{}/".format(self.chart_id)
        reply = network_manager.put(QNetworkRequest(QUrl(url)), json.dumps(body).encode("utf-8"))
        reply.finished.connect(self.commit_decipherment_reply)

    def commit_decipherment_reply(self):
        """ 修改解读返回 """
        reply = self.sender()
        if not reply.error():
            QMessageBox.information(self, "成功", "修改成功!")
        self.close()


class ChartPopup(QWidget):
    """ 显示某个图形 """
    def __init__(self, chart_id, *args, **kwargs):
        super(ChartPopup, self).__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowFlag(Qt.Dialog)
        self.setWindowIcon(QIcon("media/icons/win_chart.png"))
        self.resize(680, 380)
        self.chart_id = chart_id
        main_layout = QVBoxLayout()
        self.chart_container = QWebEngineView(self)
        self.chart_container.load(QUrl("file:///html/charts/custom_chart.html"))

        # 设置与页面信息交互的通道
        channel_qt_obj = QWebChannel(self.chart_container.page())  # 实例化qt信道对象,必须传入页面参数
        self.contact_channel = ChartOptionChannel()  # 页面信息交互通道
        self.chart_container.page().setWebChannel(channel_qt_obj)
        channel_qt_obj.registerObject("pageContactChannel", self.contact_channel)  # 信道对象注册信道，只能注册一个

        main_layout.addWidget(self.chart_container)
        self.setLayout(main_layout)
        self.chart_container.loadFinished.connect(self._get_chart_option_values)

    def _get_chart_option_values(self):
        """ 获取图形的配置和数据 """
        network_manager = getattr(qApp, "_network")
        url = SERVER_API + "chart-option/{}/".format(self.chart_id)
        reply = network_manager.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(self.chart_option_values_reply)

    def chart_option_values_reply(self):
        """ 获取图形的配置和数据返回 """
        reply = self.sender()
        if reply.error():
            logger.error("用户获取单个图形配置和数据错误:{}".format(reply.error()))
        else:
            data = reply.readAll().data()
            data = json.loads(data.decode("utf-8"))
            chart_type = data["chart_type"]
            base_option = data["base_option"]
            chart_values = data["chart_values"]
            sheet_headers = data["sheet_headers"]
            self.contact_channel.chartSource.emit(
                chart_type, json.dumps(base_option), json.dumps(chart_values), json.dumps(sheet_headers)
            )
        reply.deleteLater()


# 调整某个已设置的图形配置
class EditChartOptionPopup(QDialog):
    def __init__(self, chart_id, *args, **kwargs):
        super(EditChartOptionPopup, self).__init__(*args, **kwargs)
        self.chart_id = chart_id
        self.network_manager = getattr(qApp, '_network')
        self.setAttribute(Qt.WA_DeleteOnClose)
        integer_validate = QIntValidator(self)

        main_layout = QGridLayout()
        title_label = QLabel('左轴调整:', self)
        title_label.setObjectName('titleLabel')
        main_layout.addWidget(title_label, 0, 0, 1, 6)

        main_layout.addWidget(QLabel(' 名 称:', self), 1, 0)
        self.left_name_edit = QLineEdit(self)
        main_layout.addWidget(self.left_name_edit, 1, 1)

        main_layout.addWidget(QLabel('最小值:', self), 1, 2)
        self.left_min_edit = QLineEdit(self)
        self.left_min_edit.setValidator(integer_validate)
        main_layout.addWidget(self.left_min_edit, 1, 3)

        main_layout.addWidget(QLabel('最大值:', self), 1, 4)
        self.left_max_edit = QLineEdit(self)
        self.left_max_edit.setValidator(integer_validate)
        main_layout.addWidget(self.left_max_edit, 1, 5)

        title_label = QLabel('右轴调整:', self)
        title_label.setObjectName('titleLabel')
        main_layout.addWidget(title_label, 2, 0, 1, 6)

        main_layout.addWidget(QLabel(' 名 称:', self), 3, 0)
        self.right_name_edit = QLineEdit(self)
        main_layout.addWidget(self.right_name_edit, 3, 1)

        main_layout.addWidget(QLabel('最小值:', self), 3, 2)
        self.right_min_edit = QLineEdit(self)
        self.right_min_edit.setValidator(integer_validate)
        main_layout.addWidget(self.right_min_edit, 3, 3)

        main_layout.addWidget(QLabel('最大值:', self), 3, 4)
        self.right_max_edit = QLineEdit(self)
        self.right_max_edit.setValidator(integer_validate)
        main_layout.addWidget(self.right_max_edit, 3, 5)

        title_label = QLabel('横轴调整(范围仅限输入年份,为0时表示不限制)', self)
        title_label.setObjectName('titleLabel')
        main_layout.addWidget(title_label, 4, 0, 1, 6)

        main_layout.addWidget(QLabel(' 格 式:', self), 5, 0)
        self.x_axis_format_combobox = QComboBox(self)
        self.x_axis_format_combobox.addItem('年-月-日', 10)
        self.x_axis_format_combobox.addItem('年-月', 7)
        self.x_axis_format_combobox.addItem('年', 4)
        main_layout.addWidget(self.x_axis_format_combobox, 5, 1)

        main_layout.addWidget(QLabel('起始年:', self), 5, 2)
        self.start_year_edit = QLineEdit(self)
        self.start_year_edit.setValidator(integer_validate)
        main_layout.addWidget(self.start_year_edit, 5, 3)
        main_layout.addWidget(QLabel('终止年:', self), 5, 4)
        self.end_year_edit = QLineEdit(self)
        self.end_year_edit.setValidator(integer_validate)
        main_layout.addWidget(self.end_year_edit, 5, 5)

        title_label = QLabel('解说编辑:', self)
        title_label.setObjectName('titleLabel')
        main_layout.addWidget(title_label, 6, 0, 1, 6)
        self.decipherment_edit = QTextEdit(self)
        self.decipherment_edit.setMaximumHeight(50)
        main_layout.addWidget(self.decipherment_edit, 7, 0, 1, 0)

        # 确定按钮
        self.confirm_button = QPushButton("确定")
        self.confirm_button.clicked.connect(self.confirm_modify_option)
        main_layout.addWidget(self.confirm_button, 8, 5)
        self.setLayout(main_layout)
        self.setMaximumWidth(520)
        self.setStyleSheet(
            "#titleLabel{padding:3px;font-size:14px;background:rgb(200,220,230);border-radius:3px}"
        )
        self.get_chart_base_option()

    def get_chart_base_option(self):
        """ 请求图形的基本配置 """
        url = SERVER_API + 'chart/{}/'.format(self.chart_id)
        reply = self.network_manager.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(self.chart_option_reply)

    def chart_option_reply(self):
        """ 图形配置返回 """
        reply = self.sender()
        if reply.error():
            reply.deleteLater()
            self.close()
            return
        data = json.loads(reply.readAll().data().decode("utf8"))
        reply.deleteLater()
        # 填写默认数据
        default_option = data['data']
        left_axis = default_option.get('left_axis')
        right_axis = default_option.get('right_axis')
        self.left_name_edit.setText(left_axis.get("name", ""))
        self.left_min_edit.setText(str(left_axis.get('min', '')))
        self.left_max_edit.setText(str(left_axis.get('max', '')))
        if right_axis:
            self.right_name_edit.setText(right_axis.get('name', ''))
            self.right_min_edit.setText(str(right_axis.get('min', '')))
            self.right_max_edit.setText(str(right_axis.get('max', '')))

        date_format_index = 0
        if default_option['date_length'] == 7:
            date_format_index = 1
        if default_option['date_length'] == 4:
            date_format_index = 2
        self.x_axis_format_combobox.setCurrentIndex(date_format_index)

        self.start_year_edit.setText(default_option['start_year'])
        self.end_year_edit.setText(default_option['end_year'])
        self.decipherment_edit.setText(default_option['decipherment'])

    def get_options(self):
        """ 获取修改后的配置 """
        return {
            'left_name': self.left_name_edit.text().strip(),
            'left_min': self.left_min_edit.text().strip(),
            'left_max': self.left_max_edit.text().strip(),
            'right_name': self.right_name_edit.text().strip(),
            'right_min': self.right_min_edit.text().strip(),
            'right_max': self.right_max_edit.text().strip(),
            'date_length': self.x_axis_format_combobox.currentData(),
            'start_year': self.start_year_edit.text().strip(),
            'end_year': self.end_year_edit.text().strip(),
            'decipherment': self.decipherment_edit.toPlainText().strip()
        }

    def confirm_modify_option(self):
        """ 确定修改配置 """
        url = SERVER_API + "chart/{}/".format(self.chart_id)
        reply = self.network_manager.put(QNetworkRequest(QUrl(url)), json.dumps(self.get_options()).encode('utf8'))
        reply.finished.connect(self.modify_reply)

    def modify_reply(self):
        reply = self.sender()
        if reply.error():
            QMessageBox.information(self, '失败', '修改失败了!')
        else:
            QMessageBox.information(self, '成功', '修改配置成功!')
            self.close()
        reply.deleteLater()


