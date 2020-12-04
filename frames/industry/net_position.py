# _*_ coding:utf-8 _*_
# @File  : net_position.py
# @Time  : 2020-08-21 11:12
# @Author: zizle
import math
import json
from PyQt5.QtWidgets import (qApp, QTableWidgetItem, QWidget, QVBoxLayout, QSplitter, QMainWindow, QListWidget,
                             QListWidgetItem, QLabel, QHBoxLayout, QSpinBox, QPushButton, QTableWidget, QFrame)
from PyQt5.QtNetwork import QNetworkRequest
from PyQt5.QtCore import QUrl, Qt, QTimer, QMargins
from PyQt5.QtGui import QBrush, QColor, QFont
from utils.constant import HORIZONTAL_SCROLL_STYLE, VERTICAL_SCROLL_STYLE
from settings import SERVER_API
from widgets import OptionWidget, LoadingCover

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
            {"id": 1, "name": "品种全览", "icon": None},
            {"id": 2, "name": "图表分析", "icon": None},
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
        else:
            widget = QLabel("暂未开放", self, alignment=Qt.AlignCenter)
        return widget
