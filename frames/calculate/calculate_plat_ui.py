# _*_ coding:utf-8 _*_
# @File  : calculate_plat_ui.py
# @Time  : 2020-11-16 14:56
# @Author: zizle

""" 计算平台 """

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QSplitter, QTreeWidget, QMainWindow
from PyQt5.QtCore import Qt


class MenuTreeWidget(QTreeWidget):
    def __init__(self, *args, **kwargs):
        super(MenuTreeWidget, self).__init__(*args, **kwargs)
        self.header().hide()
        self.setFocusPolicy(Qt.NoFocus)
        self.setColumnCount(1)
        self.setIndentation(0)
        self.setObjectName('menuTree')
        self.setStyleSheet("#menuTree{border:none;border-right: 1px solid rgba(50,50,50,100)}"
                           "#menuTree::item:hover{color:rgb(0,164,172);}"
                           "#menuTree::item{height:28px;}"
                           )

    def mouseDoubleClickEvent(self, event, *args, **kwargs):
        event.accept()


class CalculatePlatUi(QWidget):
    def __init__(self, *args, **kwargs):
        super(CalculatePlatUi, self).__init__(*args, **kwargs)
        layout = QHBoxLayout()
        layout.setContentsMargins(2,2,2,2)
        main_splitter = QSplitter(self)
        self.menu_tree = MenuTreeWidget(self)
        main_splitter.addWidget(self.menu_tree)
        main_splitter.setHandleWidth(1)
        self.frame_loader = QMainWindow(self)
        main_splitter.addWidget(self.frame_loader)
        main_splitter.setSizes([self.width() * 0.18, self.width() * 0.82])
        layout.addWidget(main_splitter)
        self.setLayout(layout)
        self.menu_tree.setFocusPolicy(Qt.NoFocus)
        self.menu_tree.setObjectName("menuTree")
        self.setStyleSheet("#menuTree{border:none;border-right: 1px solid rgba(50,50,50,100)}"
                           "#menuTree::item:hover{background-color:rgba(0,255,0,50)}"
                           "#menuTree::item:selected{background-color:rgba(255,0,0,100)}"
                           "#menuTree::item{height:28px;}"
                           )


