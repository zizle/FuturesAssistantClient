# _*_ coding:utf-8 _*_
# @File  : report.py
# @Time  : 2020-12-18 15:32
# @Author: zizle
"""
定期报告
界面设计
-------------------------
tab切换上传|管理
-------------------------
显示操作窗口

"""
import json
import os

from PyQt5.QtNetwork import QNetworkRequest
from PyQt5.QtWidgets import (QWidget, QTabWidget, QHBoxLayout, QVBoxLayout, QDateEdit, QLabel, QComboBox, QPushButton,
                             QTableWidget, QHeaderView, QAbstractItemView, QLineEdit, QCompleter, qApp,
                             QTableWidgetItem, QDialog)
from PyQt5.QtCore import QDate, Qt, QUrl, QFile

from settings import SERVER_API, STATIC_URL, logger
from utils.client import get_user_token
from utils.multipart import generate_multipart_data
from utils.constant import REPORT_TYPE
from popup.message import InformationPopup, WarningPopup
from widgets import PDFContentPopup, OperateButton
from widgets.path_edit import FilePathLineEdit
from apis.product import ReportsAPI


class ReportFileAdmin(QTabWidget):
    def __init__(self, *args, **kwargs):
        super(ReportFileAdmin, self).__init__(*args, **kwargs)

        upload_widget = QWidget(self)

        main_layout = QVBoxLayout()
        local_file_layout = QHBoxLayout()

        local_file_layout.addWidget(QLabel('本地文件:', self))
        self.local_file_edit = FilePathLineEdit(self)
        self.local_file_edit.setPlaceholderText("点击选择本地文件进行上传")
        self.local_file_edit.setFixedWidth(400)
        local_file_layout.addWidget(self.local_file_edit)
        self.explain_label = QLabel("说明:[本地文件]或[网络文件]只能选择一种,相关信息共享。", self)
        self.explain_label.setStyleSheet("color:rgb(66,233,66)")
        local_file_layout.addWidget(self.explain_label)
        local_file_layout.addStretch()
        main_layout.addLayout(local_file_layout)

        network_file_layout = QHBoxLayout()
        network_file_layout.addWidget(QLabel('网络文件:', self))
        self.filename = QLabel("从表格选择文件", self)
        self.filename.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.filename.setAlignment(Qt.AlignLeft)
        self.filename.setFixedWidth(400)
        network_file_layout.addWidget(self.filename)
        self.explain_label = QLabel("说明:[本地文件]或[网络文件]只能选择一种,相关信息共享。", self)
        self.explain_label.setStyleSheet("color:rgb(66,233,66)")
        network_file_layout.addWidget(self.explain_label)
        network_file_layout.addStretch()
        main_layout.addLayout(network_file_layout)

        option_layout = QHBoxLayout()

        option_layout.addWidget(QLabel("报告日期:", self))
        self.date_edit = QDateEdit(self)
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setDate(QDate.currentDate())
        option_layout.addWidget(self.date_edit)

        option_layout.addWidget(QLabel("报告类型:", self))
        self.report_type = QComboBox(self)
        option_layout.addWidget(self.report_type)

        option_layout.addWidget(QLabel("备选品种:", self))
        self.variety_combobox = QComboBox(self)
        self.variety_combobox.setMinimumWidth(100)
        self.variety_combobox.setEditable(True)
        self.completer = QCompleter(self.variety_combobox.model(), self)
        self.variety_combobox.setCompleter(self.completer)
        option_layout.addWidget(self.variety_combobox)

        option_layout.addWidget(QLabel("关联品种:", self))
        self.relative_variety = QLabel("下拉框选择品种(多选)", self)
        option_layout.addWidget(self.relative_variety)

        self.clear_relative_button = QPushButton("清除", self)
        option_layout.addWidget(self.clear_relative_button)
        option_layout.addStretch()
        main_layout.addLayout(option_layout)

        rename_layout = QHBoxLayout()
        self.rename_edit = QLineEdit(self)
        self.rename_edit.setPlaceholderText("重命名文件(无需重命名请留空),无需填后缀.")
        self.rename_edit.setFixedWidth(330)
        rename_layout.addWidget(self.rename_edit)

        self.confirm_button = QPushButton("确定添加", self)
        rename_layout.addWidget(self.confirm_button)

        rename_layout.addStretch()
        main_layout.addLayout(rename_layout)

        self.file_table = QTableWidget(self)
        self.file_table.setColumnCount(7)
        self.file_table.verticalHeader().hide()
        self.file_table.setEditTriggers(QHeaderView.NoEditTriggers)
        self.file_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.file_table.setHorizontalHeaderLabels(["序号", "文件名", "大小", "创建时间", "", "", ""])
        self.file_table.horizontalHeader().setDefaultSectionSize(55)
        self.file_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.file_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.file_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        main_layout.addWidget(self.file_table)

        upload_widget.setLayout(main_layout)

        self.addTab(upload_widget, "上传报告")

        # 管理报告
        manager_widget = QWidget(self)
        manager_layout = QVBoxLayout()
        manager_option_layout = QHBoxLayout()
        self.manager_date = QDateEdit(self)
        self.manager_date.setDate(QDate.currentDate())
        self.manager_date.setDisplayFormat("yyyy-MM-dd")
        self.manager_date.setCalendarPopup(True)
        manager_option_layout.addWidget(self.manager_date)

        manager_option_layout.addWidget(QLabel("报告类型:", self))
        self.manager_report_type = QComboBox(self)
        manager_option_layout.addWidget(self.manager_report_type)

        manager_option_layout.addWidget(QLabel("相关品种:", self))
        self.manager_variety_combobox = QComboBox(self)
        manager_option_layout.addWidget(self.manager_variety_combobox)
        manager_layout.addLayout(manager_option_layout)

        self.manager_query_button = QPushButton("查询", self)
        manager_option_layout.addWidget(self.manager_query_button)

        manager_option_layout.addStretch()

        self.manager_table = QTableWidget(self)
        self.manager_table.setColumnCount(11)
        self.manager_table.setHorizontalHeaderLabels([
            "创建时间", "更新时间", "报告日期", "创建者", "关联品种", "标题", "类型", "相对路径", "公开", "阅读量", "删除"])
        self.manager_table.horizontalHeader().setDefaultSectionSize(80)
        self.manager_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.manager_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.manager_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Interactive)
        self.manager_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Interactive)
        self.manager_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Interactive)
        manager_layout.addWidget(self.manager_table)

        manager_widget.setLayout(manager_layout)

        self.addTab(manager_widget, "管理报告")

        self.no_selected_file()
        self.no_relative_variety()

        self.network_manager = getattr(qApp, "_network")

        self.modify_dialog = None
        self.selected_file_path = None  # 选择的文件
        self.local_file_path = None  # 本地文件路径
        self.selected_varieties = list()  # 选择的关联品种
        self.selected_varieties_zh = list()  # 关联品种的中文
        # 添加报告类型
        for k, v in REPORT_TYPE.items():
            self.report_type.addItem(v, k)
            self.manager_report_type.addItem(v, k)

        self._get_user_variety()  # 获取有权限的品种

        # 获取服务端当前的所有文件
        self._get_files_in_server()

        # 监测本地文件选择框
        self.local_file_edit.textChanged.connect(self.selected_local_file)
        # 选择品种
        self.variety_combobox.activated.connect(self.selected_relative_variety)
        # 清除品种
        self.clear_relative_button.clicked.connect(self.clear_relative_variety)
        # 表格操作
        self.file_table.cellClicked.connect(self.file_table_operation)
        # 创建报告
        self.confirm_button.clicked.connect(self.create_report_file)

        # 管理报告查询
        self.manager_query_button.clicked.connect(self.query_reports)
        # 管理表格的点击事件
        self.manager_table.cellClicked.connect(self.clicked_manager_report)

        # Network API
        self.report_api = ReportsAPI(self)
        self.report_api.date_query_reports_response.connect(self.date_query_reports_reply)
        self.report_api.modify_report_message_response.connect(self.modify_report_message_reply)
        self.report_api.delete_report_response.connect(self.delete_report_file_reply)

    def has_selected_file(self):
        self.filename.setStyleSheet("color:rgb(66,66,233);font-size:13px")

    def no_selected_file(self):
        self.filename.setStyleSheet("color:rgb(233,66,66);font-size:13px")

    def has_relative_variety(self):
        self.relative_variety.setStyleSheet("color:rgb(66,66,233);font-size:13px")

    def no_relative_variety(self):
        self.relative_variety.setStyleSheet("color:rgb(233,66,66);font-size:13px")

    def selected_relative_variety(self):
        """ 选择关联的品种 """
        if self.selected_file_path or self.local_file_path:
            variety_en = self.variety_combobox.currentData()
            if variety_en not in self.selected_varieties:
                self.selected_varieties.append(variety_en)
            variety_text = self.variety_combobox.currentText()
            if variety_text not in self.selected_varieties_zh:
                self.selected_varieties_zh.append(variety_text)
            self.relative_variety.setText(";".join(self.selected_varieties_zh))
            self.has_relative_variety()
        else:
            self.clear_relative_variety()
            self.relative_variety.setText("请选择文件再选择品种")

    def clear_relative_variety(self):
        """ 清除关联品种 """
        self.selected_varieties.clear()
        self.selected_varieties_zh.clear()
        self.relative_variety.setText("下拉框选择品种(多选)")
        self.no_relative_variety()

    def selected_local_file(self, text):
        """ 选择本地文件 """
        if text:  # 选择了文件路径
            self.local_file_path = text
            self.filename.setText("从表格选择文件")
            self.no_selected_file()
            self.selected_file_path = None
        else:  # 空文件
            self.local_file_path = None
        self.clear_relative_variety()  # 只要文件变化了就清除关联品种

    def _get_user_variety(self):
        """ 获取用户有权限的品种 """
        url = SERVER_API + "user/variety-authenticate/"
        request = QNetworkRequest(QUrl(url))
        request.setRawHeader("Authorization".encode("utf-8"), get_user_token().encode("utf-8"))
        reply = self.network_manager.get(request)
        reply.finished.connect(self.user_variety_reply)

    def user_variety_reply(self):
        """ 获取用户的品种权限返回 """
        reply = self.sender()
        data = reply.readAll().data()
        if reply.error():
            pass
        else:
            data = json.loads(data.decode("utf-8"))
            current_user = data.get("user")
            if not current_user:
                logger.error("登录过期了,用户获取有权限的品种失败!")
                return
            self._combobox_allow_varieties(data["varieties"])
        reply.deleteLater()

    def _combobox_allow_varieties(self, varieties):
        """ 填充选项 """
        self.manager_variety_combobox.addItem("全部", "0")
        for variety_item in varieties:
            self.variety_combobox.addItem(variety_item["variety_name"], variety_item["variety_en"])
            self.manager_variety_combobox.addItem(variety_item["variety_name"], variety_item["variety_en"])
        # 加入其他选项(没有品种关联的文件为OTHERS)
        self.variety_combobox.addItem('其他', 'OTHERS')

    def _get_files_in_server(self):
        """ 获取服务端当前有的pdf文件 """
        url = SERVER_API + "wechat-files/"
        reply = self.network_manager.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(self.wechat_files_reply)

    def wechat_files_reply(self):
        reply = self.sender()
        if reply.error():
            file_list = list()
        else:
            data = json.loads(reply.readAll().data().decode("utf-8"))
            file_list = data["file_list"]
        reply.deleteLater()
        self.table_show_files(file_list)

    def table_show_files(self, files_list):
        """ 文件信息在表格显示 """
        self.file_table.clearContents()
        self.file_table.setRowCount(len(files_list))
        for row, row_item in enumerate(files_list):
            item0 = QTableWidgetItem(str(row + 1))
            item0.setTextAlignment(Qt.AlignCenter)
            item0.setData(Qt.UserRole, row_item["relative_path"])
            self.file_table.setItem(row, 0, item0)

            item1 = QTableWidgetItem(row_item["filename"])
            item1.setTextAlignment(Qt.AlignCenter)
            self.file_table.setItem(row, 1, item1)

            item2 = QTableWidgetItem(row_item["file_size"])
            item2.setTextAlignment(Qt.AlignCenter)
            self.file_table.setItem(row, 2, item2)

            item3 = QTableWidgetItem(row_item["create_time"])
            item3.setTextAlignment(Qt.AlignCenter)
            self.file_table.setItem(row, 3, item3)

            item4 = QTableWidgetItem("查看")
            item4.setTextAlignment(Qt.AlignCenter)
            self.file_table.setItem(row, 4, item4)

            item5 = QTableWidgetItem("选择")
            item5.setTextAlignment(Qt.AlignCenter)
            self.file_table.setItem(row, 5, item5)

            item6 = QTableWidgetItem("删除")
            item6.setTextAlignment(Qt.AlignCenter)
            self.file_table.setItem(row, 6, item6)

    def file_table_operation(self, row, col):
        """ 表格操作 """
        current_file_path = self.file_table.item(row, 0).data(Qt.UserRole)
        if col == 4:  # 查看
            filename = self.file_table.item(row, 1).text()
            url = SERVER_API + "wechat-files/{}".format(current_file_path)
            p = PDFContentPopup(title=filename, file=url)
            p.exec_()
        elif col == 5:  # 选择
            if self.local_file_path is not None:
                p = InformationPopup("您已选择本地文件,无法再选择网络文件。\n如需取消本地文件,请点击选框后直接取消。", self)
                p.exec_()
                return
            filename = self.file_table.item(row, 1).text()
            self.filename.setText(filename)
            self.selected_file_path = current_file_path
            self.has_selected_file()
        elif col == 6:  # 删除
            self.delete_wechat_file(row, current_file_path)
        else:
            pass

    def create_report_file(self):
        """ 从网络文件创建报告 """
        # 验证是否能发送请求
        if not self.selected_varieties:
            p = InformationPopup("未选择关联品种", self)
            p.exec_()
            return
        # 公共body_data
        body_data = {
            "date": self.date_edit.text(),
            "relative_varieties": ";".join(self.selected_varieties),
            "report_type": self.report_type.currentData(),
            "rename_text": self.rename_edit.text().strip()
        }
        if self.local_file_path:  # 上传本地文件
            self.send_local_report(body_data)
        elif self.selected_file_path:  # 选择网络文件
            self.send_network_report(body_data.copy())
        else:
            p = InformationPopup("未选择相关报告文件", self)
            p.exec_()

    def send_local_report(self, body_data):
        """ 上传本地报告文件 """

        def create_report_reply():
            if reply.error():
                message = "创建报告失败!"
            else:
                message = "创建报告成功!"
                self.local_file_edit.clear()
                self.clear_relative_variety()
                self.rename_edit.clear()
            reply.deleteLater()
            p = InformationPopup(message, self)
            p.exec_()

        # 文件信息
        file = QFile(self.local_file_path)
        file.open(QFile.ReadOnly)
        file_dict = {"report_file": file}
        # 其他信息
        text_dict = body_data.copy()
        multipart_data = generate_multipart_data(text_dict, file_dict)
        url = SERVER_API + 'report-file/'
        request = QNetworkRequest(QUrl(url))
        request.setRawHeader("Authorization".encode("utf-8"), get_user_token().encode("utf-8"))
        reply = self.network_manager.post(request, multipart_data)
        reply.finished.connect(create_report_reply)
        multipart_data.setParent(reply)

    def send_network_report(self, body_data):
        """ 使用网络文件创建 """

        def create_report_reply():
            if reply.error():
                message = "创建报告失败!"
            else:
                message = "创建报告成功!"
                self.file_table.removeRow(self.file_table.currentRow())
                self.selected_file_path = None
                self.filename.setText("从表格选择文件")
                self.no_selected_file()
                self.clear_relative_variety()
                self.rename_edit.clear()
            reply.deleteLater()
            p = InformationPopup(message, self)
            p.exec_()

        url = SERVER_API + "wechat-files/{}".format(self.selected_file_path)
        request = QNetworkRequest(QUrl(url))
        request.setRawHeader("Authorization".encode("utf-8"), get_user_token().encode("utf-8"))
        reply = self.network_manager.post(request, json.dumps(body_data).encode("utf-8"))
        reply.finished.connect(create_report_reply)

    def delete_wechat_file(self, current_row, relative_path):
        """ 删除网络保存的文件 """

        def delete_wechat_file_reply():
            """ 删除网络保存的文件返回 """
            if reply.error():
                p = InformationPopup("删除失败!", self)
                p.exec_()
            else:
                p = InformationPopup("删除成功!", self)
                p.exec_()
                self.file_table.removeRow(current_row)
            reply.deleteLater()

        url = SERVER_API + "wechat-files/{}".format(relative_path)
        request = QNetworkRequest(QUrl(url))
        network_manager = getattr(qApp, "_network")
        reply = network_manager.deleteResource(request)
        reply.finished.connect(delete_wechat_file_reply)

    def query_reports(self):
        """ 查询当前条件下的报告 """
        variety_en = self.manager_variety_combobox.currentData()
        current_date = self.manager_date.text()
        # 进行查询
        self.report_api.get_date_query_reports(query_date=current_date, variety_en=variety_en)

    def date_query_reports_reply(self, data):
        """ 按日查询报告返回 """
        reports = data['reports']
        # 在管理表格中显示数据
        self.manager_table.clearContents()
        self.manager_table.setRowCount(len(reports))
        col_keys = ['create_time', 'update_time', 'file_date', 'username', 'variety_en', 'title', 'type_text',
                    'filepath', 'is_active', 'reading']
        for row, row_item in enumerate(reports):
            for col, col_key in enumerate(col_keys):
                text = str(row_item[col_key])
                if col_key == 'is_active':
                    text = '是' if row_item['is_active'] else '否'
                item = QTableWidgetItem(text)
                if col == 0:
                    item.setData(Qt.UserRole, row_item['id'])
                self.manager_table.setItem(row, col, item)
            # 加一个删除按钮
            delete_button = OperateButton('media/icons/delete.png', 'media/icons/delete_hover.png', self.manager_table)
            setattr(delete_button, 'row_index', row)
            delete_button.clicked.connect(self.delete_current_report)
            self.manager_table.setCellWidget(row, len(col_keys), delete_button)

    def delete_current_report(self):
        """ 删除报告 """

        def confirm_delete_report():
            self.report_api.delete_report(report_id, get_user_token())

        button = self.sender()
        row = getattr(button, 'row_index', None)
        if row is None:
            return
        report_id = self.manager_table.item(row, 0).data(Qt.UserRole)
        print(report_id)
        p = WarningPopup('确定删除当前文件吗?删除将不可恢复!', self)
        p.confirm_operate.connect(confirm_delete_report)
        p.exec_()

    def get_current_message(self, row):
        """ 获取row行报告的信息 """
        report_type_dict = {v: k for k, v in REPORT_TYPE.items()}
        report_type = report_type_dict.get(self.manager_table.item(row, 6).text(), None)
        is_active = 1 if self.manager_table.item(row, 8).text() == '是' else 0
        return {
            'report_id': self.manager_table.item(row, 0).data(Qt.UserRole),
            'file_date': self.manager_table.item(row, 2).text(),
            'variety_en': self.manager_table.item(row, 4).text(),
            'title': self.manager_table.item(row, 5).text(),
            'file_type': report_type,
            'is_active': is_active
        }

    def clicked_manager_report(self, row, col):
        """ 点击管理报告 """
        # 2 修改日期  4 关联品种  5 标题 6 类型 8 公开
        if col in [2, 4, 5, 6, 8]:
            report_item = self.get_current_message(row)
            if col == 2:
                self.modify_file_date(report_item)
            elif col == 4:
                self.modify_file_variety(report_item)
            elif col == 5:
                self.modify_file_title(report_item)
            elif col == 6:
                self.modify_file_type(report_item)
            elif col == 8:
                self.modify_file_is_active(report_item)
            else:
                pass

    def modify_report_message_reply(self, result):
        p = InformationPopup('修改成功!' if result else '修改失败了!', self)
        p.exec_()
        # 刷新数据
        self.query_reports()

    def delete_report_file_reply(self, result):
        p = InformationPopup('删除成功!' if result else '删除失败了!', self)
        p.exec_()
        # 刷新数据
        self.query_reports()

    def modify_file_date(self, report_message):

        def send_request():
            report_message['file_date'] = date_edit.text()
            self.report_api.put_modify_report_message(report_message, get_user_token())
            modify_dialog.close()

        modify_dialog = QDialog(self)
        modify_dialog.setWindowTitle("修改日期")
        layout = QVBoxLayout()
        date_edit = QDateEdit(self.modify_dialog)
        date_edit.setDisplayFormat("yyyy-MM-dd")
        date_edit.setCalendarPopup(True)
        current_date = report_message['file_date']
        date_edit.setDate(QDate(int(current_date[:4]), int(current_date[5:7]), int(current_date[-2:])))
        layout.addWidget(date_edit)
        button = QPushButton("确定", self.modify_dialog)
        button.clicked.connect(send_request)
        layout.addWidget(button, alignment=Qt.AlignRight)
        modify_dialog.setLayout(layout)
        modify_dialog.setFixedSize(250, 90)
        modify_dialog.exec_()

    def modify_file_variety(self, report_message):
        """ 修改关联品种 """
        current_variety = report_message.get('variety_en', '')
        variety_ens = current_variety.split(';')

        def select_variety():
            if variety_combo.currentData() not in variety_ens:
                variety_ens.append(variety_combo.currentData())
            selected_varietys.setText(';'.join(variety_ens))

        def clear_varietys():
            variety_ens.clear()
            selected_varietys.setText(';'.join(variety_ens))

        def send_request():
            if not selected_varietys.text():
                return
            report_message['variety_en'] = selected_varietys.text()
            self.report_api.put_modify_report_message(report_message, get_user_token())
            modify_dialog.close()

        # 弹窗
        modify_dialog = QDialog(self)
        modify_dialog.setWindowTitle("修改品种")
        layout = QVBoxLayout()
        variety_combo = QComboBox(self.modify_dialog)
        for i in range(self.variety_combobox.count()):
            variety_combo.addItem(self.variety_combobox.itemText(i), self.variety_combobox.itemData(i))
        variety_combo.activated.connect(select_variety)
        layout.addWidget(variety_combo)
        button = QPushButton("确定", self.modify_dialog)
        selected_layout = QHBoxLayout()
        selected_layout.addWidget(QLabel("已选品种:", self.modify_dialog))

        selected_varietys = QLabel(current_variety, self.modify_dialog)
        selected_layout.addWidget(selected_varietys)
        clear_button = QPushButton("清除", self.modify_dialog)
        clear_button.clicked.connect(clear_varietys)
        selected_layout.addWidget(clear_button, alignment=Qt.AlignRight)
        layout.addLayout(selected_layout)

        button.clicked.connect(send_request)
        layout.addWidget(button, alignment=Qt.AlignRight)
        modify_dialog.setLayout(layout)
        modify_dialog.setFixedSize(280, 130)
        modify_dialog.exec_()

    def modify_file_title(self, report_message):
        """ 修改标题 """
        current_name = report_message.get('title', '')

        def send_request():
            new_filename = name_edit.text().strip()
            if new_filename:
                report_message['title'] = new_filename
                self.report_api.put_modify_report_message(report_message, get_user_token())
                modify_dialog.close()

        # 弹窗
        modify_dialog = QDialog(self)
        modify_dialog.setWindowTitle("修改名称")
        layout = QVBoxLayout()
        name_edit = QLineEdit(self.modify_dialog)
        name_edit.setText(current_name)
        layout.addWidget(name_edit)
        button = QPushButton("确定", self.modify_dialog)
        button.clicked.connect(send_request)
        layout.addWidget(button, alignment=Qt.AlignRight)
        modify_dialog.setLayout(layout)
        modify_dialog.setFixedSize(250, 90)
        modify_dialog.exec_()

    def modify_file_type(self, report_message):
        """ 修改报告类型 """
        current_type = report_message.get('file_type', 1)

        def send_request():
            report_message['file_type'] = type_combo.currentData()
            self.report_api.put_modify_report_message(report_message, get_user_token())
            modify_dialog.close()

        # 弹窗
        modify_dialog = QDialog(self)
        modify_dialog.setWindowTitle("修改类型")
        layout = QVBoxLayout()
        type_combo = QComboBox(self.modify_dialog)
        for i in range(self.report_type.count()):
            type_combo.addItem(self.report_type.itemText(i), self.report_type.itemData(i))
        type_combo.setCurrentText(REPORT_TYPE.get(current_type))
        layout.addWidget(type_combo)
        button = QPushButton("确定", self.modify_dialog)
        button.clicked.connect(send_request)
        layout.addWidget(button, alignment=Qt.AlignRight)
        modify_dialog.setLayout(layout)
        modify_dialog.setFixedSize(250, 90)
        modify_dialog.exec_()

    def modify_file_is_active(self, report_message):
        """ 修改是否公开 """
        report_message['is_active'] = 0 if report_message['is_active'] else 1
        self.report_api.put_modify_report_message(report_message, get_user_token())

