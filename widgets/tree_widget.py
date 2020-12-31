# _*_ coding:utf-8 _*_
# @File  : tree_widget.py
# @Time  : 2020-12-04 10:32
# @Author: zizle
from PyQt5.QtWidgets import QTreeWidget
from PyQt5.QtCore import Qt


class TreeWidget(QTreeWidget):
    def __init__(self, *args, **kwargs):
        super(TreeWidget, self).__init__(*args, **kwargs)
        self.header().hide()
        self.setFocusPolicy(Qt.NoFocus)
        self.setColumnCount(1)
        self.setIndentation(0)
        self.setObjectName("listTree")
        # "#exchangeTree::item:selected{background-color:rgba(255,0,0,100)}"
        self.setStyleSheet("#listTree{border:none;border-right: 1px solid rgba(50,50,50,100)}"
                           "#listTree::item:hover{color:rgb(0,164,172);}"
                           "#listTree::item{height:28px;}"
                           )

    def mouseDoubleClickEvent(self, event):
        event.accept()

