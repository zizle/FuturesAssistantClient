# _*_ coding:utf-8 _*_
# @File  : exchange_strategy.py
# @Time  : 2021-01-19 14:39
# @Author: zizle

# 交易策略的维护界面

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTextEdit, QPushButton


class ExchangeStrategy(QWidget):
    def __init__(self, *args, **kwargs):
        super(ExchangeStrategy, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        self.back_button = QPushButton('返回', self)
        layout.addWidget(self.back_button)
        self.back_button.hide()
        # 表格
        self.content_table = QTableWidget(self)
        layout.addWidget(self.content_table)
        self.content_table.hide()
        # 编辑控件
        self.edit_text = QTextEdit(self)
        layout.addWidget(self.edit_text)
        self.edit_text.hide()
        self.setLayout(layout)

        """ 业务部分 """
        self.back_button.clicked.connect(self.to_show_table)


    def to_show_table(self):
        self.content_table.show()
        self.back_button.hide()
        self.edit_text.hide()

    def to_edit_content(self):
        self.content_table.hide()
        self.back_button.show()
        self.edit_text.show()







