# _*_ coding:utf-8 _*_
# @File  : introduction.py
# @Time  : 2021-01-21 08:31
# @Author: zizle
from PyQt5.QtCore import QMargins, QFile
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QComboBox, QPushButton

from widgets import OptionWidget, FilePathLineEdit, PDFContentWidget
from utils.multipart import generate_multipart_data
from apis.variety import VarietyAPI
from popup.message import InformationPopup
from gglobal import variety
from settings import STATIC_URL


class IntroductionAdmin(QWidget):
    def __init__(self, *args, **kwargs):
        super(IntroductionAdmin, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        option_widget = OptionWidget(self)
        option_widget.setFixedHeight(40)
        option_layout = QHBoxLayout()
        self.label1 = QLabel('品种:', self)
        self.variety_selector = QComboBox(self)
        self.view_button = QPushButton('查看', self)
        self.create_button = QPushButton('新建', self)
        self.file_edit = FilePathLineEdit(self)
        self.save_button = QPushButton('保存', self)
        option_layout.addWidget(self.label1)
        option_layout.addWidget(self.variety_selector)
        option_layout.addWidget(self.view_button)
        option_layout.addWidget(self.create_button)
        option_layout.addWidget(self.file_edit)
        option_layout.addWidget(self.save_button)
        option_layout.addStretch()
        option_widget.setLayout(option_layout)
        layout.addWidget(option_widget)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(QMargins(8, 5, 8, 5))
        self.pdf_show = PDFContentWidget(title='', file='')
        self.pdf_show.setParent(self)
        self.pdf_show.set_error_message('还没有此品种的介绍!')
        content_layout.addWidget(self.pdf_show)
        layout.addLayout(content_layout)
        self.setLayout(layout)

        self.get_all_variety()
        self.file_edit.hide()
        self.save_button.hide()
        self.is_show_create = False
        self.create_button.clicked.connect(self.to_create_new_file)
        self.save_button.clicked.connect(self.save_introduction_file)
        self.view_button.clicked.connect(self.show_file)

        self.variety_api = VarietyAPI(self)
        self.variety_api.upload_intro_reply.connect(self.upload_file_reply)

    def get_all_variety(self):
        varieties = variety.get_variety()
        for variety_item in varieties:
            self.variety_selector.addItem(variety_item['variety_name'], variety_item['variety_en'])
        self.show_file()

    def reset_variety_en(self, variety_en):
        if variety_en in ['A', 'B']:
            return '黄大豆期货合约'
        if variety_en in ['AG', 'AU']:
            return '贵金属期货合约'
        if variety_en in ['CU','AL','ZN','PB', 'NI', 'SN']:
            return '有色金属期货合约'
        return variety_en

    def show_file(self):
        current_v = self.variety_selector.currentData()
        if current_v:
            current_v = self.reset_variety_en(current_v)
            filepath = STATIC_URL + 'VARIETY/Intro/{}.pdf'.format(current_v)
            self.pdf_show.set_file(filename='品种介绍', filepath=filepath)

    def to_create_new_file(self):
        if not self.is_show_create:
            self.file_edit.show()
            self.save_button.show()
            self.is_show_create = True
        else:
            self.file_edit.hide()
            self.file_edit.clear()
            self.save_button.hide()
            self.is_show_create = False

    def save_introduction_file(self):
        local_file = self.file_edit.text()
        variety_en = self.variety_selector.currentData()
        if not local_file or not variety_en:
            return
        # 读取文件并上传
        file = QFile(local_file)
        file.open(QFile.ReadOnly)
        file_dict = {'intro_file': file}
        multipart_data = generate_multipart_data(file_dict=file_dict)
        self.variety_api.upload_variety_intro_file(variety_en, multipart_data)

    def upload_file_reply(self, data):
        p = InformationPopup(data['message'], self)
        p.exec_()
        self.file_edit.clear()
