# _*_ coding:utf-8 _*_
# @File  : variety_data_ui.py
# @Time  : 2020-09-03 8:29
# @Author: zizle
from PyQt5.QtWidgets import (QWidget, QSplitter, QHBoxLayout, QTabWidget, QTableWidget, QFrame, QPushButton,
                             QAbstractItemView, QHeaderView, QVBoxLayout, QLabel, QComboBox, QCheckBox, QTabBar,
                             QStylePainter, QStyleOptionTab, QStyle)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QMargins, Qt, pyqtSignal
from components.variety_tree import VarietyTree


class SheetTable(QTableWidget):
    """ 用户数据表显示控件 """
    right_mouse_clicked = pyqtSignal()

    def mousePressEvent(self, event):
        super(SheetTable, self).mousePressEvent(event)
        if event.buttons() == Qt.RightButton:
            self.right_mouse_clicked.emit()


class HorizontalTabBar(QTabBar):
    """ 自定义竖向文字显示的tabBar """
    def paintEvent(self, event):
        painter = QStylePainter(self)
        option = QStyleOptionTab()
        painter.begin(self)
        for index in range(self.count()):
            self.initStyleOption(option, index)
            tabRect = self.tabRect(index)
            tabRect.moveLeft(4)
            painter.drawControl(QStyle.CE_TabBarTabShape, option)
            painter.drawText(tabRect, Qt.AlignVCenter | Qt.TextDontClip, self.tabText(index))
        painter.end()


class MyChartsUI(QWidget):
    def __init__(self, *args, **kwargs):
        super(MyChartsUI, self).__init__(*args, **kwargs)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(QMargins(0, 1, 0, 1))

        self.chart_table = QTableWidget(self)
        self.chart_table.setFrameShape(QFrame.NoFrame)
        self.chart_table.setFocusPolicy(Qt.NoFocus)
        self.chart_table.verticalHeader().hide()
        self.chart_table.setEditTriggers(QHeaderView.NoEditTriggers)
        self.chart_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.chart_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.chart_table.setAlternatingRowColors(True)
        self.chart_table.verticalHeader().setDefaultSectionSize(25)  # 设置行高(与下行代码同时才生效)
        self.chart_table.verticalHeader().setMinimumSectionSize(25)

        self.swap_tab = QTabWidget(self)

        self.swap_tab.setTabBar(HorizontalTabBar())

        self.chart_container = QWebEngineView(self)
        self.chart_container.setContextMenuPolicy(Qt.NoContextMenu)

        self.swap_tab.addTab(self.chart_container, "全\n览")

        self.swap_tab.addTab(self.chart_table, "管\n理")
        self.swap_tab.setDocumentMode(True)
        self.swap_tab.setTabPosition(QTabWidget.East)

        main_layout.addWidget(self.swap_tab)

        self.setLayout(main_layout)
        self.chart_table.setObjectName("chartTable")
        self.chart_table.horizontalHeader().setStyleSheet(
            "QHeaderView::section{background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,"
            "stop:0 #fea356, stop: 0.5 #eeeeee,stop: 0.6 #eeeeee, stop:1 #fea356);"
            "border:1px solid rgb(201,202,202);border-left:none;"
            "min-height:25px;min-width:40px;font-weight:bold;};"
        )
        self.swap_tab.tabBar().setObjectName("tabBar")
        self.setStyleSheet(
            "#tabBar::tab{min-height:75px;}"
            "#tipLabel{font-size:15px;color:rgb(180,100,100)}"
            "#chartTable{background-color:rgb(240,240,240);"
            "selection-background-color:qlineargradient(x1:0,y1:0, x2:0, y2:1,"
            "stop:0 #cccccc,stop:0.5 white,stop:0.6 white,stop: 1 #cccccc);"
            "alternate-background-color:rgb(245,250,248);}"
            "#operateButton{border:none;}#operateButton:hover{color:rgb(233,66,66)}"
        )


class VarietyDataUI(QWidget):
    def __init__(self, *args, **kwargs):
        super(VarietyDataUI, self).__init__(*args, **kwargs)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(QMargins(0, 0, 0, 0))
        main_splitter = QSplitter(self)

        self.variety_tree = VarietyTree()
        main_splitter.addWidget(self.variety_tree)

        # 右侧Tab
        self.tab = QTabWidget(self)
        self.tab.setDocumentMode(True)
        self.tab.setTabShape(QTabWidget.Triangular)
        # 数据列表
        self.sheet_table = SheetTable(self)
        self.sheet_table.setFrameShape(QFrame.NoFrame)
        self.sheet_table.setFocusPolicy(Qt.NoFocus)
        self.sheet_table.verticalHeader().hide()
        self.sheet_table.setEditTriggers(QHeaderView.NoEditTriggers)
        self.sheet_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.sheet_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.sheet_table.setAlternatingRowColors(True)

        self.sheet_table.setColumnCount(5)
        self.sheet_table.setHorizontalHeaderLabels(["序号", "标题", "数据起始", "数据结束", "图形"])
        self.sheet_table.verticalHeader().setDefaultSectionSize(25)  # 设置行高(与下行代码同时才生效)
        self.sheet_table.verticalHeader().setMinimumSectionSize(25)
        self.sheet_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.sheet_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.sheet_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        # 图形列表
        self.chart_container = QWebEngineView(self)
        self.chart_container.setContextMenuPolicy(Qt.NoContextMenu)
        self.my_charts = MyChartsUI(self)

        self.tab.addTab(self.chart_container, "图形库")
        self.tab.addTab(self.sheet_table, "数据库")
        self.tab.addTab(self.my_charts, "我的图形库")

        main_splitter.addWidget(self.tab)

        main_splitter.setStretchFactor(1, 4)
        main_splitter.setStretchFactor(2, 6)

        main_splitter.setHandleWidth(1)

        main_layout.addWidget(main_splitter)
        self.setLayout(main_layout)

        self.tab.tabBar().setObjectName("tabBar")
        self.sheet_table.setObjectName("sheetTable")
        self.sheet_table.horizontalHeader().setStyleSheet(
            "QHeaderView::section{background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,"
            "stop:0 #34adf3, stop: 0.5 #ccddff,stop: 0.6 #ccddff, stop:1 #34adf3);"
            "border:1px solid rgb(201,202,202);border-left:none;"
            "min-height:25px;min-width:40px;font-weight:bold;font-size:13px};"
        )
        self.setStyleSheet(
            "#tabBar::tab{min-height:20px;}"
            "#sheetTable{background-color:rgb(240,240,240);"
            "selection-background-color:qlineargradient(x1:0,y1:0, x2:0, y2:1,"
            "stop:0 #cccccc,stop:0.5 white,stop:0.6 white,stop: 1 #cccccc);"
            "alternate-background-color:rgb(245,250,248);}"
        )
