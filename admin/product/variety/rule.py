# _*_ coding:utf-8 _*_
# @File  : introduction.py
# @Time  : 2021-01-21 08:31
# @Author: zizle
from PyQt5.QtCore import QMargins, QFile, Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QComboBox, QPushButton, QLineEdit, QTableWidget, \
    QHeaderView, QTableWidgetItem

from widgets import OptionWidget, FilePathLineEdit, PDFContentPopup
from utils.multipart import generate_multipart_data
from apis.variety import VarietyAPI
from popup.message import InformationPopup
from gglobal import variety
from settings import STATIC_URL


class RuleAdmin(QWidget):
    def __init__(self, *args, **kwargs):
        super(RuleAdmin, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        option_widget = OptionWidget(self)
        option_widget.setFixedHeight(40)
        option_layout = QHBoxLayout()
        self.create_button = QPushButton('新建', self)
        self.vname_label = QLabel('名称：', self)
        self.vname_edit = QLineEdit(self)
        self.file_edit = FilePathLineEdit(self)
        self.save_button = QPushButton('保存', self)
        option_layout.addWidget(self.create_button)
        option_layout.addWidget(self.vname_label)
        option_layout.addWidget(self.vname_edit)
        option_layout.addWidget(self.file_edit)
        option_layout.addWidget(self.save_button)
        option_layout.addStretch()
        option_widget.setLayout(option_layout)
        layout.addWidget(option_widget)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(QMargins(8, 5, 8, 5))

        # 显示制度规则的表格
        self.table = QTableWidget(self)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(['名称', '操作'])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        content_layout.addWidget(self.table)

        layout.addLayout(content_layout)
        self.setLayout(layout)

        self.is_show_create = True
        self.to_create_new_file()
        self.create_button.clicked.connect(self.to_create_new_file)
        self.save_button.clicked.connect(self.save_introduction_file)
        self.table.cellClicked.connect(self.show_file)

        self.variety_api = VarietyAPI(self)
        self.variety_api.upload_intro_reply.connect(self.upload_file_reply)
        self.variety_api.get_rule_reply.connect(self.set_rules_info)
        # 获取当前的制度规则信息
        self.variety_api.get_variety_rule_file()

    def set_rules_info(self, data):
        rules = data['rules']
        self.table.clearContents()
        self.table.setRowCount(len(rules))
        for row, row_item in enumerate(rules):
            item0 = QTableWidgetItem(row_item['variety_name'])
            item0.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, item0)
            item1 = QTableWidgetItem('查看')
            item1.setTextAlignment(Qt.AlignCenter)
            item1.setData(Qt.UserRole, row_item['filepath'])
            self.table.setItem(row, 1, item1)

    def show_file(self, row, col):
        if col == 1:
            item = self.table.item(row, 1)
            filepath = item.data(Qt.UserRole)
            if filepath:
                filepath = STATIC_URL + filepath
                p = PDFContentPopup(title='制度规则', file=filepath)
                p.exec_()

    def to_create_new_file(self):
        if not self.is_show_create:
            self.file_edit.show()
            self.save_button.show()
            self.vname_label.show()
            self.vname_edit.show()
            self.is_show_create = True
        else:
            self.file_edit.hide()
            self.file_edit.clear()
            self.save_button.hide()
            self.vname_label.hide()
            self.vname_edit.hide()
            self.is_show_create = False

    def save_introduction_file(self):
        local_file = self.file_edit.text()
        variety_name = self.vname_edit.text().strip()
        if not all([local_file, variety_name]):
            p = InformationPopup('填写必须信息再保存!', self)
            p.exec_()
            return
        # 读取文件并上传
        file = QFile(local_file)
        file.open(QFile.ReadOnly)
        file_dict = {'rule_file': file}
        txt_dict = {'rule_name': variety_name}
        multipart_data = generate_multipart_data(file_dict=file_dict, text_dict=txt_dict)
        self.variety_api.upload_variety_rule_file(multipart_data)

    def upload_file_reply(self, data):
        p = InformationPopup(data['message'], self)
        p.exec_()
        self.file_edit.clear()
        if data['success']:
            self.variety_api.get_variety_rule_file()

