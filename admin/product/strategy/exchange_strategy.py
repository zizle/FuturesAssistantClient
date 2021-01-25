# _*_ coding:utf-8 _*_
# @File  : exchange_strategy.py
# @Time  : 2021-01-19 14:39
# @Author: zizle

# 交易策略的维护界面

import json

from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import (qApp, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTextEdit, QPushButton, QDateEdit,
                             QMessageBox, QTableWidgetItem, QHeaderView)
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt5.QtCore import Qt, QUrl, QMargins

from utils.client import get_user_token
from popup.message import WarningPopup
from widgets import OptionWidget

from settings import SERVER_API


class ExchangeStrategy(QWidget):
    def __init__(self, *args, **kwargs):
        super(ExchangeStrategy, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0,))

        option_widget = OptionWidget(self)
        option_layout = QHBoxLayout()
        self.create_button = QPushButton('新建', self)
        self.back_button = QPushButton('返回', self)
        self.back_button.hide()
        option_layout.addWidget(self.create_button)
        option_layout.addWidget(self.back_button)
        option_layout.addStretch()
        option_widget.setLayout(option_layout)
        option_widget.setFixedHeight(40)

        layout.addWidget(option_widget)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(QMargins(8, 5, 8, 5))
        self.table = QTableWidget(self)
        self.table.verticalHeader().hide()
        self.table.setFocusPolicy(Qt.NoFocus)
        self.edit_text = QTextEdit(self)
        self.edit_text.hide()
        self.confirm_button = QPushButton('确定', self)
        self.confirm_button.hide()

        self.modify_button = QPushButton('确定修改', self)
        self.modify_button.hide()
        content_layout.addWidget(self.table)
        content_layout.addWidget(self.edit_text)
        content_layout.addWidget(self.confirm_button, alignment=Qt.AlignRight)
        content_layout.addWidget(self.modify_button, alignment=Qt.AlignRight)
        layout.addLayout(content_layout)
        self.setLayout(layout)

        """ 业务部分 """
        self.reload = False
        self.current_strategy_id = None
        self.network_manager = getattr(qApp, '_network', QNetworkAccessManager(self))
        self.create_button.clicked.connect(self.to_create_new)
        self.back_button.clicked.connect(self.to_show_table)
        self.confirm_button.clicked.connect(self.create_strategy)
        self.modify_button.clicked.connect(self.modify_strategy)

        self.table.cellClicked.connect(self.table_cell_clicked)

        self.get_strategy()

    def get_strategy(self):
        """ 获取最新100条交易策略 """
        url = QUrl(SERVER_API + 'consultant/strategy/')
        query_params = "admin=1&user_token={}".format(get_user_token(raw=True))
        url.setQuery(query_params)
        reply = self.network_manager.get(QNetworkRequest(url))
        reply.finished.connect(self.strategy_reply)

    def strategy_reply(self):
        reply = self.sender()
        if reply.error():
            pass
        else:
            data = json.loads(reply.readAll().data().decode('utf8'))
            strategy_list = data['strategy']
            # 表格显示策略
            self.table_show_strategy(strategy_list)
        reply.deleteLater()

    def table_show_strategy(self, strategy_list):
        self.table.clear()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['日期', '内容', '修改', '删除'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setRowCount(len(strategy_list))
        for row, row_item in enumerate(strategy_list):
            item0 = QTableWidgetItem(row_item['create_time'])
            item0.setData(Qt.UserRole, row_item['id'])
            self.table.setItem(row, 0, item0)
            item1 = QTableWidgetItem(row_item['content'])
            self.table.setItem(row, 1, item1)
            item2 = QTableWidgetItem('编辑')
            item2.setForeground(QBrush(QColor(66, 66, 233)))
            item2.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 2, item2)
            item3 = QTableWidgetItem('删除')
            item3.setForeground(QBrush(QColor(233, 66, 66)))
            item3.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 3, item3)

    def table_cell_clicked(self, row, col):
        strategy_id = self.table.item(row, 0).data(Qt.UserRole)
        self.current_strategy_id = strategy_id
        if col == 2:  # 编辑
            content = self.table.item(row, 1).text()
            self.edit_text.setText(content)
            self.to_edit_content()
        elif col == 3:  # 删除
            p = WarningPopup('确定删除吗?删除将不可恢复!', self)
            p.confirm_operate.connect(self.delete_strategy)
            p.exec_()

    def to_show_table(self):
        if self.reload:
            self.get_strategy()
            self.reload = False
        self.table.show()
        self.back_button.hide()
        self.create_button.show()
        self.edit_text.hide()
        self.confirm_button.hide()
        self.modify_button.hide()
        self.current_strategy_id = None

    def to_edit_content(self):
        self.table.hide()
        self.edit_text.show()
        self.create_button.hide()
        self.confirm_button.hide()
        self.back_button.show()
        self.modify_button.show()

    def to_create_new(self):
        self.table.hide()
        self.edit_text.show()
        self.confirm_button.show()
        self.create_button.hide()
        self.back_button.show()

    def create_strategy(self):
        data = {
            'user_token': get_user_token(raw=True),
            'content': self.edit_text.toPlainText()
        }
        url = SERVER_API + 'consultant/strategy/'
        reply = self.network_manager.post(QNetworkRequest(QUrl(url)), json.dumps(data).encode('utf8'))
        reply.finished.connect(self.create_strategy_reply)

    def create_strategy_reply(self):
        reply = self.sender()
        if reply.error():
            QMessageBox.information(self, '失败', '创建失败了!')
        else:
            QMessageBox.information(self, '成功', '创建新策略成功!')
            self.edit_text.clear()
            self.reload = True
        reply.deleteLater()

    def modify_strategy(self):
        if not self.current_strategy_id:
            QMessageBox.information(self, '信息', '内部错误，修改失败!')
            return
        data = {
            'user_token': get_user_token(True),
            'strategy_id': self.current_strategy_id,
            'content': self.edit_text.toPlainText()
        }
        url = SERVER_API + 'consultant/strategy/{}/'.format(self.current_strategy_id)
        reply = self.network_manager.put(QNetworkRequest(QUrl(url)), json.dumps(data).encode('utf8'))
        reply.finished.connect(self.modify_strategy_reply)
        
    def modify_strategy_reply(self):
        reply = self.sender()
        if reply.error():
            QMessageBox.information(self, '失败', '修改失败了!')
        else:
            QMessageBox.information(self, '成功', '修改策略成功!')
            self.edit_text.clear()
            self.reload = True
        reply.deleteLater()

    def delete_strategy(self):
        url = QUrl(SERVER_API + 'consultant/strategy/{}/'.format(self.current_strategy_id))
        url.setQuery('user_token={}'.format(get_user_token(True)))
        reply = self.network_manager.deleteResource(QNetworkRequest(url))
        reply.finished.connect(self.delete_strategy_reply)

    def delete_strategy_reply(self):
        reply = self.sender()
        if reply.error():
            QMessageBox.information(self, '失败', '删除失败了!')
        else:
            QMessageBox.information(self, '成功', '删除成功!')
            self.reload = True
            self.current_strategy_id = None
            self.get_strategy()
        reply.deleteLater()
