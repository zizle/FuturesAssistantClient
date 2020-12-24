# _*_ coding:utf-8 _*_
# @File  : net_position.py
# @Time  : 2020-08-21 11:12
# @Author: zizle
import math
import json
from PyQt5.QtWidgets import (qApp, QTableWidgetItem, QWidget, QVBoxLayout, QSplitter, QMainWindow, QListWidget,
                             QListWidgetItem, QLabel, QHBoxLayout, QSpinBox, QPushButton, QTableWidget, QFrame, QComboBox,
                             QHeaderView)
from PyQt5.QtNetwork import QNetworkRequest
from PyQt5.QtCore import QObject, QUrl, Qt, QTimer, QMargins, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QFont
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from utils.constant import HORIZONTAL_SCROLL_STYLE, VERTICAL_SCROLL_STYLE, BLUE_STYLE_HORIZONTAL_STYLE
from settings import SERVER_API
from widgets import OptionWidget, LoadingCover

from .weekly_index import WeeklyPositionPrice  # 周度持仓指数变化

""" 品种全览窗口 """


class BriefPositionWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(BriefPositionWidget, self).__init__(*args, **kwargs)
        """ UI部分 """
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(QMargins(0, 0, 0, 0))
        # 头部操作
        title_widget = OptionWidget(self)
        title_layout = QHBoxLayout()
        self.interval_days = QSpinBox(self)
        self.interval_days.setMinimum(1)
        self.interval_days.setMaximum(30)
        self.interval_days.setValue(5)
        self.interval_days.setPrefix("日期间隔 ")
        self.interval_days.setSuffix(" 天")
        title_layout.addWidget(self.interval_days)

        self.query_button = QPushButton('确定', self)
        title_layout.addWidget(self.query_button)

        title_layout.addWidget(QLabel("字体大小:", self))
        font_size_smaller = QPushButton("-", self)
        font_size_smaller.setFixedWidth(20)
        font_size_larger = QPushButton("+", self)
        font_size_larger.setFixedWidth(20)
        title_layout.addWidget(font_size_smaller)
        title_layout.addWidget(font_size_larger)
        title_layout.addStretch()
        title_widget.setLayout(title_layout)
        title_widget.setFixedHeight(45)
        main_layout.addWidget(title_widget)

        # 显示数据的表
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(QMargins(8, 0, 8, 0))
        self.data_table = QTableWidget(self)
        self.data_table.setContentsMargins(QMargins(5, 8, 5, 5))
        self.data_table.setFrameShape(QFrame.NoFrame)
        # self.data_table.setEditTriggers(QAbstractItemView.NoEditTriggers)   # 不可编辑
        self.data_table.setFocusPolicy(Qt.NoFocus)  # 去选中时的虚线框
        self.data_table.setAlternatingRowColors(True)  # 交替行颜色
        self.data_table.horizontalHeader().setDefaultSectionSize(88)  # 默认的标题头宽
        self.data_table.verticalHeader().setDefaultSectionSize(18)  # 设置行高(与下行代码同时才生效)
        self.data_table.verticalHeader().setMinimumSectionSize(18)
        self.data_table.verticalHeader().setMaximumSectionSize(22)
        self.data_table.verticalHeader().hide()
        self.data_table.hide()
        content_layout.addWidget(self.data_table)

        self.tip_label = QLabel('上方设置查询的间隔天数,确定进行查询数据!', self)
        self.tip_label.setAlignment(Qt.AlignCenter)

        content_layout.addWidget(self.tip_label)

        main_layout.addLayout(content_layout)

        self.setLayout(main_layout)
        font = QFont()
        font.setPointSize(10)
        self.data_table.setFont(font)
        self.data_table.setObjectName("dataTable")
        self.tip_label.setObjectName("tipLabel")
        self.data_table.horizontalScrollBar().setStyleSheet(HORIZONTAL_SCROLL_STYLE)
        self.data_table.verticalScrollBar().setStyleSheet(VERTICAL_SCROLL_STYLE)
        self.data_table.horizontalHeader().setStyleSheet(
            "QHeaderView::section,QTableCornerButton::section{height:25px;background-color:rgb(243,245,248);"
            "font-weight:bold;font-size:13px}"
        )
        self.setStyleSheet(
            "#tipLabel{color:rgb(233,66,66);font-weight:bold}"
            "#dataTable{selection-color:rgb(80,100,200);selection-background-color:rgb(220,220,220);"
            "alternate-background-color:rgb(245,250,248)}"
        )

        # 遮罩层
        self.loading_cover = LoadingCover(self)
        self.loading_cover.resize(self.parent().width(), self.parent().height())
        self.loading_cover.hide()

        """ 逻辑部分 """
        self.network_manager = getattr(qApp, '_network')
        self.query_button.clicked.connect(self.get_net_position)  # 查询数据
        font_size_smaller.clicked.connect(self.content_font_size_smaller)
        font_size_larger.clicked.connect(self.content_font_size_larger)

        self.get_net_position()  # 初始显示

    def resizeEvent(self, event):
        super(BriefPositionWidget, self).resizeEvent(event)
        self.loading_cover.resize(self.parent().width(), self.parent().height())

    def get_net_position(self):
        """ 获取净持仓数据 """
        self.loading_cover.show("正在获取数据")
        # 旧接口,生成处理,速度极慢
        # url = SERVER_API + "position/all-variety/?interval_days=" + str(self.interval_days.value())
        url = SERVER_API + "rank-position/all-variety/?interval_days=" + str(self.interval_days.value())
        reply = self.network_manager.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(self.all_variety_position_reply)

    def all_variety_position_reply(self):
        """ 全品种净持仓数据返回 """
        reply = self.sender()
        if reply.error():
            reply.deleteLater()
            self.tip_label.show()
            self.data_table.hide()
            self.tip_label.setText("获取数据失败了{}!".format(reply.error()))
            return
        data = reply.readAll().data()
        data = json.loads(data.decode('utf-8'))
        reply.deleteLater()
        self.data_table.show()
        self.tip_label.hide()
        self.show_data_in_table(data['data'], data['header_keys'])
        self.loading_cover.hide()

    def show_data_in_table(self, show_data, header_keys):
        """ 将数据在表格中展示出来 """
        self.data_table.clear()
        self.data_table.setRowCount(0)
        self.data_table.setColumnCount(0)
        # 生成表格的列头
        header_length = len(header_keys)  # 有日期和中英文的标头故-1
        self.data_table.setColumnCount(header_length * 2)
        row_count = math.ceil(len(show_data) / 2)
        self.data_table.setRowCount(row_count)
        # 设置表头数据
        interval_day = self.interval_days.value()
        # 2020.11.02: 新增1天前数据的显示
        if interval_day == 1:  # 2020.11.02:当间隔为1天的表头数据
            for count in range(2):
                for index, h_key in enumerate(header_keys):
                    if index == 0:
                        item = QTableWidgetItem('品种')
                    elif index == 1:
                        item = QTableWidgetItem(h_key)
                    else:
                        item = QTableWidgetItem(str((index - 1) * interval_day) + "天前")
                    setattr(item, 'key', h_key)
                    self.data_table.setHorizontalHeaderItem(index + count * len(header_keys), item)
        else:  # 当间隔不为1天的表头数据
            for count in range(2):
                for index, h_key in enumerate(header_keys):
                    if index == 0:
                        item = QTableWidgetItem('品种')
                    elif index == 1:
                        item = QTableWidgetItem(h_key)
                    elif index == 2:  # 新增第二列固定为1天前2020.11.02
                        item = QTableWidgetItem("1天前")
                    else:
                        item = QTableWidgetItem(str((index - 2) * interval_day) + "天前")
                    setattr(item, 'key', h_key)
                    self.data_table.setHorizontalHeaderItem(index + count * len(header_keys), item)

        # 纵向根据交易代码顺序填充数据(2020-10-13修改)
        index_count = 0
        row = 0
        for variety, variety_values in show_data.items():
            if index_count < row_count:  # 前半段数据
                col_start, col_end = 0, header_length
            else:  # 后半段数据
                col_start, col_end = header_length, 2 * header_length
                if index_count == row_count:
                    row = 0  # 回到第一行
            for col in range(col_start, col_end):
                data_key = getattr(self.data_table.horizontalHeaderItem(col), 'key')
                if col == col_start:
                    item = QTableWidgetItem(str(variety_values.get(data_key, 0)))
                    item.setForeground(QBrush(QColor(180, 60, 60)))
                else:
                    item = QTableWidgetItem(str(int(variety_values.get(data_key, 0))))
                item.setTextAlignment(Qt.AlignCenter)
                self.data_table.setItem(row, col, item)
            self.data_table.setRowHeight(row, 18)  # 在此设置才有效
            index_count += 1  # 记录个数切换到后半段
            row += 1

        # 根据交易所品种横向填充数据
        # self.data_table.setRowCount(0)
        # is_pre_half = True
        # for variety, variety_values in show_data.items():
        #     row = self.data_table.rowCount()
        #     if is_pre_half:
        #         col_start = 0
        #         col_end = len(header_keys)
        #         self.data_table.insertRow(row)
        #     else:
        #         row -= 1
        #         col_start = len(header_keys)
        #         col_end = self.data_table.columnCount()
        #     for col in range(col_start, col_end):
        #         data_key = getattr(self.data_table.horizontalHeaderItem(col), 'key')
        #         if col == col_start:
        #             item = QTableWidgetItem(str(variety_values.get(data_key, 0)))
        #             item.setForeground(QBrush(QColor(180, 60, 60)))
        #         else:
        #             item = QTableWidgetItem(str(int(variety_values.get(data_key, 0))))
        #         item.setTextAlignment(Qt.AlignCenter)
        #
        #         self.data_table.setItem(row, col, item)
        #     is_pre_half = not is_pre_half

    def content_font_size_larger(self):
        """ 字体变小 """
        font = self.data_table.font()
        font.setPointSize(font.pointSize() + 1)
        self.data_table.setFont(font)

    def content_font_size_smaller(self):
        """ 字体变小 """
        font = self.data_table.font()
        font.setPointSize(font.pointSize() - 1)
        self.data_table.setFont(font)


""" 图表分析窗口 """


class ChartChannel(QObject):
    # 参数1:绘图的数据;参数2:图形的基本配置
    chartSource = pyqtSignal(str, str)
    # 参数1:图形宽度;参数2:图形的高度
    chartResize = pyqtSignal(int, int)


class NetPositionChart(QWebEngineView):
    def __init__(self, web_channel, *args, **kwargs):
        super(NetPositionChart, self).__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        # 加载图形容器
        self.page().load(QUrl('file:/html/charts/net_position.html'))  # 加载页面
        # 设置与页面信息交互的通道
        channel_qt_obj = QWebChannel(self.page())  # 实例化qt信道对象,必须传入页面参数
        self.contact_channel = ChartChannel(self)  # 页面信息交互通道
        self.page().setWebChannel(channel_qt_obj)
        channel_qt_obj.registerObject("pageContactChannel", self.contact_channel)  # 信道对象注册信道,只能注册一个

    def resizeEvent(self, event):
        super(NetPositionChart, self).resizeEvent(event)
        self.resize_chart()

    def set_chart_option(self, source_data, base_option):
        """ 传入数据设置图形 """
        self.contact_channel.chartSource.emit(source_data, base_option)
        self.resize_chart()

    def resize_chart(self):
        self.contact_channel.chartResize.emit(self.width(), self.height())


class ChartTablePositionWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(ChartTablePositionWidget, self).__init__(*args, **kwargs)
        """ UI部分 """
        title_widget_width = 45
        layout = QVBoxLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        title_widget = OptionWidget(self)
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel('品种:', self))
        self.variety_combobox = QComboBox(self)
        self.variety_combobox.setMinimumWidth(100)
        title_layout.addWidget(self.variety_combobox)
        self.three_month = QPushButton('近3月', self)
        setattr(self.three_month, 'day_count', 90)
        self.three_month.setFocusPolicy(Qt.NoFocus)
        self.six_month = QPushButton('近6月', self)
        setattr(self.six_month, 'day_count', 180)
        self.six_month.setFocusPolicy(Qt.NoFocus)
        self.twelve_month = QPushButton('近一年', self)
        setattr(self.twelve_month, 'day_count', 360)
        self.twelve_month.setFocusPolicy(Qt.NoFocus)
        title_layout.addWidget(self.three_month)
        title_layout.addWidget(self.six_month)
        title_layout.addWidget(self.twelve_month)
        title_layout.addStretch()
        title_widget.setLayout(title_layout)
        title_widget.setFixedHeight(title_widget_width)
        layout.addWidget(title_widget)

        chart_table_splitter = QSplitter(self)
        chart_table_splitter.setOrientation(Qt.Vertical)
        # 图形展示
        self.chart_container = NetPositionChart(self)
        chart_table_splitter.addWidget(self.chart_container)
        # 表格展示
        self.position_table = QTableWidget(self)
        self.position_table.setColumnCount(6)
        self.position_table.setHorizontalHeaderLabels(['日期', '品种', '多单量', '空单量', '净多量', '净多变化量'])
        self.position_table.verticalHeader().hide()
        self.position_table.horizontalHeader().setMinimumSectionSize(100)
        self.position_table.setMaximumWidth(self.parent().width() * 0.8)
        self.position_table.verticalHeader().setDefaultSectionSize(20)
        self.position_table.horizontalHeader().setDefaultAlignment(Qt.AlignVCenter | Qt.AlignRight)
        self.position_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.position_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)

        chart_table_splitter.addWidget(self.position_table)
        chart_table_splitter.setSizes([(self.parent().height() - title_widget_width) * 0.6,
                                       (self.parent().height() - title_widget_width) * 0.4])
        chart_table_splitter.setContentsMargins(QMargins(10, 5, 10, 5))
        layout.addWidget(chart_table_splitter)

        # 加载提示
        self.loading_cover = LoadingCover(self.parent())
        self.loading_cover.resize(self.parent().width(), self.parent().height())
        self.loading_cover.show('正在加载资源')

        self.setLayout(layout)
        self.position_table.setFocusPolicy(Qt.NoFocus)
        self.position_table.verticalScrollBar().setStyleSheet(VERTICAL_SCROLL_STYLE)
        self.position_table.horizontalHeader().setStyleSheet(BLUE_STYLE_HORIZONTAL_STYLE)
        self.position_table.setAlternatingRowColors(True)
        self.position_table.setObjectName('positionTable')
        self.three_month.setObjectName('monthButton')
        self.six_month.setObjectName('monthButton')
        self.twelve_month.setObjectName('monthButton')
        self.setStyleSheet(
            "#positionTable{selection-color:rgb(80,100,200);selection-background-color:rgb(220,220,220);"
            "alternate-background-color:rgb(242,242,242);gridline-color:rgb(60,60,60)}"
            "#monthButton{background-color:rgb(250,250,250);border-radius: 7px;font-size:12px;color:rgb(120,120,120);"
            "padding:4px 6px}"
        )

        """ 逻辑部分 """
        self.network_manager = getattr(qApp, '_network')

        # 关联品种变化的信号
        self.variety_combobox.currentTextChanged.connect(self.get_position_data)

        self.chart_container.page().loadFinished.connect(self.loading_page_finished)
        # 关联时间范围点击
        self.three_month.clicked.connect(self.get_custom_day_count_position)
        self.six_month.clicked.connect(self.get_custom_day_count_position)
        self.twelve_month.clicked.connect(self.get_custom_day_count_position)

    def loading_page_finished(self):
        """ 加载网页结束 """
        self.loading_cover.hide()
        # 获取所有品种
        self.get_all_variety()

    def get_all_variety(self):
        """ 获取所有品种 """
        self.variety_combobox.clear()
        url = SERVER_API + 'variety/all/?is_real=1'
        reply = self.network_manager.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(self.variety_reply)

    def variety_reply(self):
        """ 品种返回 """
        reply = self.sender()
        if reply.error():
            pass
        else:
            data = json.loads(reply.readAll().data().decode('utf8'))
            for group_name, group_item in data['varieties'].items():
                for variety_item in group_item:
                    self.variety_combobox.addItem(variety_item['variety_name'], variety_item['variety_en'])
        reply.deleteLater()

    def change_month_button_style(self, day_count: int):
        if 90 <= day_count < 180:
            self.three_month.setStyleSheet("background-color:rgb(191,211,249);color:rgb(78,110,242)")
            self.six_month.setStyleSheet("background-color:rgb(250,250,250);color:rgb(120,120,120)")
            self.twelve_month.setStyleSheet("background-color:rgb(250,250,250);color:rgb(120,120,120)")
        elif 180 <= day_count < 360:
            self.six_month.setStyleSheet("background-color:rgb(191,211,249);color:rgb(78,110,242)")
            self.three_month.setStyleSheet("background-color:rgb(250,250,250);color:rgb(120,120,120)")
            self.twelve_month.setStyleSheet("background-color:rgb(250,250,250);color:rgb(120,120,120)")
        elif 360 <= day_count <= 365:
            self.twelve_month.setStyleSheet("background-color:rgb(191,211,249);color:rgb(78,110,242)")
            self.three_month.setStyleSheet("background-color:rgb(250,250,250);color:rgb(120,120,120)")
            self.six_month.setStyleSheet("background-color:rgb(250,250,250);color:rgb(120,120,120)")
        else:
            self.three_month.setStyleSheet("background-color:rgb(250,250,250);color:rgb(120,120,120)")
            self.six_month.setStyleSheet("background-color:rgb(250,250,250);color:rgb(120,120,120)")
            self.twelve_month.setStyleSheet("background-color:rgb(250,250,250);color:rgb(120,120,120)")

    def get_custom_day_count_position(self):
        """ 指定日期范围的数 """
        button = self.sender()
        day_count = getattr(button, 'day_count')
        self.get_position_data(day_count=day_count)

    def get_position_data(self, day_count=30):
        """ 获取净持仓数据 """
        current_variety = self.variety_combobox.currentData()
        if not current_variety:
            return
        if not isinstance(day_count, int):
            day_count = 30
        self.change_month_button_style(day_count)
        url = SERVER_API + 'rank-position/?variety={}&day_count={}'.format(current_variety, day_count)
        reply = self.network_manager.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(self.net_position_reply)

    def net_position_reply(self):
        """ 净持仓数据返回 """
        reply = self.sender()
        if reply.error():
            pass
        else:
            data = json.loads(reply.readAll().data().decode('utf8'))
            position_data = data['data']
            self.show_chart_to_page(position_data)
            self.show_data_to_table(position_data.copy())
        reply.deleteLater()

    def show_data_to_table(self, table_data: list):
        """ 显示数据到表格中 """
        self.position_table.clearContents()
        self.position_table.setRowCount(0)
        self.position_table.setRowCount(len(table_data))
        col_keys = ['date', 'variety_zh', 'long_position', 'short_position', 'net_position', 'net_position_increase']
        table_data.reverse()
        for row, row_item in enumerate(table_data):
            for col, col_key in enumerate(col_keys):
                value = format(row_item[col_key], ',') if col >= 2 else row_item[col_key]
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
                self.position_table.setItem(row, col, item)

    def show_chart_to_page(self, chart_data: list):
        """ 图形显示到界面中 """
        base_option = {
            'title': '{}前20名持仓变化'.format(self.variety_combobox.currentText())
        }
        self.chart_container.set_chart_option(json.dumps(chart_data), json.dumps(base_option))


""" 品种净持仓主窗口 """


class NetPositionWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(NetPositionWidget, self).__init__(*args, **kwargs)
        """ UI部分 """
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(QMargins(0, 2, 2, 2))
        main_splitter = QSplitter(self)
        self.left_menu_list = QListWidget(self)
        # self.left_menu_list.setFrameShape(QFrame.NoFrame)
        main_splitter.addWidget(self.left_menu_list)
        self.right_frame = QMainWindow(self, flags=Qt.Widget)
        main_splitter.addWidget(self.right_frame)
        main_splitter.setSizes([self.parent().width() * 0.18, self.parent().width() * 0.82])
        main_splitter.setHandleWidth(1)
        main_layout.addWidget(main_splitter)
        self.setLayout(main_layout)
        self.left_menu_list.setObjectName('leftMenuList')
        self.setStyleSheet(
            "#leftMenuList{border:none;border-right:1px solid rgba(50,50,50,100)}"
            "#leftMenuList::item{height:28px;}"
        )

        """ 业务逻辑部分 """
        # 添加菜单
        for menu_item in [
            {"id": 1, "name": "品种全览(前20净持仓)", "icon": None},
            {"id": 2, "name": "图表分析(前20持仓)", "icon": None},
            {"id": 3, "name": "周度持仓指数变化", "icon": None},
        ]:
            item = QListWidgetItem(menu_item['name'])
            item.setData(Qt.UserRole, menu_item["id"])
            self.left_menu_list.addItem(item)
        # 点击菜单事件
        self.left_menu_list.itemClicked.connect(self.selected_menu)
        # 默认点击了第一个
        self.selected_menu(self.left_menu_list.item(0))
        self.left_menu_list.setCurrentRow(0)  # 设置当前索引

    def selected_menu(self, item):
        """ 选择菜单 """
        menu_id = item.data(Qt.UserRole)
        widget = self.get_right_widget(menu_id)
        self.right_frame.setCentralWidget(widget)

    def get_right_widget(self, menu_id: int):
        """ 获取右侧显示窗口 """
        if menu_id == 1:
            widget = BriefPositionWidget(self)
        elif menu_id == 2:
            widget = ChartTablePositionWidget(self)
        elif menu_id == 3:
            widget = WeeklyPositionPrice(self)
        else:
            widget = QLabel("暂未开放", self, alignment=Qt.AlignCenter)
        return widget
