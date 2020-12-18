# _*_ coding:utf-8 _*_
# @File  : shortmsg.py
# @Time  : 2020-12-18 13:38
# @Author: zizle
""" 短信通管理
界面设计：
操作头：可选择日期和手动创建短信通.(操作头固定不动)
内容显示：可滚动区域(表格)
=================================
日期选择框 |  查询按钮       手动添加
=================================
序号1 | 日期 |  内容  |   修改 | 删除
---------------------------------
序号2 | 日期 |  内容  |   修改 | 删除
---------------------------------
...
"""
import json
import datetime
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QDateEdit, QPushButton, QTableWidget, qApp, \
    QTableWidgetItem, QHeaderView, QDialog, QTextEdit
from PyQt5.QtCore import QDate, Qt, QMargins, QUrl, pyqtSignal
from PyQt5.QtNetwork import QNetworkRequest

from popup.advertisement import TextPopup
from popup.message import InformationPopup, WarningPopup
from utils.client import get_user_token
from widgets import OptionWidget, VerticalSepLine, OperateButton
from settings import SERVER_API


class ModifyMessagePopup(QDialog):
    request_modify = pyqtSignal(str, int)

    def __init__(self, table_row, *args, **kwargs):
        super(ModifyMessagePopup, self).__init__(*args, **kwargs)
        self.setWindowTitle("修改内容")
        self.setMinimumWidth(470)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.table_row = table_row  # 当前修改的行数

        main_layout = QVBoxLayout()
        self.text_edit = QTextEdit(self)
        main_layout.addWidget(self.text_edit)

        self.confirm_button = QPushButton("确定", self)
        self.confirm_button.clicked.connect(self.confirm_modify)
        main_layout.addWidget(self.confirm_button, alignment=Qt.AlignRight)

        self.setLayout(main_layout)

    def confirm_modify(self):
        content = self.text_edit.toPlainText()
        self.request_modify.emit(content, self.table_row)


class ShortMsgAdmin(QWidget):
    def __init__(self, *args, **kwargs):
        super(ShortMsgAdmin, self).__init__(*args, **kwargs)
        """ UI部分 """
        layout = QVBoxLayout()
        layout.setContentsMargins(QMargins(0, 0, 0,0))
        option_layout = QHBoxLayout()
        option_widget = OptionWidget(self)
        # 日期选择
        self.query_date_edit = QDateEdit(self)
        self.query_date_edit.setDate(QDate.currentDate())
        self.query_date_edit.setCalendarPopup(True)
        self.query_date_edit.setDisplayFormat('yyyy-MM-dd')
        option_layout.addWidget(self.query_date_edit)
        # 查询按钮
        self.query_button = QPushButton('确定', self)
        self.query_button.setCursor(Qt.PointingHandCursor)
        option_layout.addWidget(self.query_button)
        # 分割线
        self.sep_line = VerticalSepLine(self)
        option_layout.addWidget(self.sep_line)
        # 手动添加
        self.create_button = QPushButton('新建')
        option_layout.addWidget(self.create_button)
        option_layout.addStretch()

        option_widget.setFixedHeight(45)
        option_widget.setLayout(option_layout)
        layout.addWidget(option_widget)

        # 内容显示
        content_widget = QWidget(self)

        content_layout = QVBoxLayout()
        self.content_table = QTableWidget(self)
        self.content_table.verticalHeader().hide()
        self.content_table.setColumnCount(4)
        self.content_table.setHorizontalHeaderLabels(['时间', '短讯内容', '修改', '删除'])
        self.content_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.content_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        content_layout.addWidget(self.content_table)

        content_widget.setLayout(content_layout)

        layout.addWidget(content_widget)

        self.setLayout(layout)
        """ 业务部分 """
        self.network_manager = getattr(qApp, '_network')

        self.get_current_messages()

        self.query_button.clicked.connect(self.get_current_messages)
        self.content_table.cellClicked.connect(self.content_table_cell_clicked)

    def get_current_messages(self):
        """ 获取当前日短信通 """
        url = SERVER_API + "short-message/?start_time={}".format(
            datetime.datetime.strptime(self.query_date_edit.text(), '%Y-%m-%d').strftime('%Y-%m-%dT%H:%M:%S'))
        reply = self.network_manager.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(self.current_short_msg_reply)

    def current_short_msg_reply(self):
        """ 获取当前短信通返回 """
        reply = self.sender()
        if reply.error():
            pass
        else:
            data = json.loads(reply.readAll().data().decode('utf8'))
            self.show_messages_in_table(data['short_messages'])
        reply.deleteLater()

    def show_messages_in_table(self, values):
        """ 在表格内显示数据 """
        self.content_table.setRowCount(len(values))
        for row, row_item in enumerate(values):
            item0 = QTableWidgetItem(row_item['time_str'])
            item0.setData(Qt.UserRole, row_item['id'])
            item0.setTextAlignment(Qt.AlignCenter)
            self.content_table.setItem(row, 0, item0)
            item1 = QTableWidgetItem(row_item['raw_content'])
            item1.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.content_table.setItem(row, 1, item1)
            edit_btn = OperateButton(icon_path='media/icons/edit.png', hover_icon_path='media/icons/edit_hover.png')
            edit_btn.setParent(self.content_table)
            setattr(edit_btn, 'row_index', row)
            edit_btn.clicked.connect(self.edit_message_content)
            self.content_table.setCellWidget(row, 2, edit_btn)

            delete_btn = OperateButton(icon_path='media/icons/delete.png', hover_icon_path='media/icons/delete_hover.png')
            delete_btn.setParent(self.content_table)
            setattr(delete_btn, 'row_index', row)
            delete_btn.clicked.connect(self.delete_message_record)
            self.content_table.setCellWidget(row, 3, delete_btn)

    def content_table_cell_clicked(self, row, col):
        """ 点击表格 """
        if col == 1:
            # 查看内容
            item = self.content_table.item(row, col)
            create_time = self.content_table.item(row, 0).text()
            text = "<div style='text-indent:30px;line-height:28px;'>" \
                   "<span style='font-size:16px;font-weight:bold;color:rgb(233,20,20);'>{}</span>" \
                   "</div>" \
                   "<div style='text-indent:30px;line-height:28px;'>{}</div>".format(create_time, item.text())
            p = TextPopup(text, self)
            p.setWindowTitle("即时资讯")
            p.exec_()

    def edit_message_content(self):
        """ 编辑短信通 """
        edit_btn = self.sender()
        row = getattr(edit_btn, 'row_index')
        edit_popup = ModifyMessagePopup(row, self)
        text = self.content_table.item(row, 1).text()
        edit_popup.text_edit.setText(text)
        edit_popup.request_modify.connect(self.confirm_modify_message)
        edit_popup.exec_()

    def confirm_modify_message(self, content, table_row):
        """ 确定修改内容 """
        def modify_finished():
            f_reply = self.sender()
            if f_reply.error():
                p_info = InformationPopup("修改失败了!\n只能修改自己发送的短信通", popup)
                p_info.exec_()
            else:
                p_info = InformationPopup("修改成功!", popup)
                p_info.exec_()
                self.content_table.item(table_row, 1).setText(popup.text_edit.toPlainText())  # 设置修改后的内容
                popup.close()
        popup = self.sender()
        # 发送修改的网络请求
        msg_id = self.content_table.item(table_row, 0).data(Qt.UserRole)
        url = SERVER_API + "short-message/{}/".format(msg_id)
        user_token = get_user_token()
        request = QNetworkRequest(QUrl(url))
        request.setRawHeader("Authorization".encode("utf-8"), user_token.encode("utf-8"))
        body_data = {"message_content": content}
        reply = self.network_manager.put(request, json.dumps(body_data).encode("utf-8"))
        reply.finished.connect(modify_finished)

    def delete_message_record(self):
        """ 删除短信通 """
        delete_btn = self.sender()
        row = getattr(delete_btn, 'row_index')
        p = WarningPopup("确定删除这条短信通吗?\n删除后将不可恢复!", self)
        p.set_data({'row': row})
        p.confirm_operate.connect(self.confirm_delete_short_message)
        p.exec_()

    def confirm_delete_short_message(self, row_data):
        row = row_data.get('row')
        if not row:
            return

        def delete_message_reply():
            if reply.error():
                p = InformationPopup("删除失败!\n您不能对他人的短信通进行这个操作!", self)
                p.exec_()
            else:
                p = InformationPopup("删除成功!", self)
                p.exec_()
                # 表格移除行
                self.content_table.removeRow(row)
            reply.deleteLater()
        msg_id = self.content_table.item(row, 0).data(Qt.UserRole)
        url = SERVER_API + 'short-message/{}/'.format(msg_id)
        request = QNetworkRequest(QUrl(url))
        request.setRawHeader("Authorization".encode("utf-8"), get_user_token().encode("utf-8"))
        reply = self.network_manager.deleteResource(request)
        reply.finished.connect(delete_message_reply)

