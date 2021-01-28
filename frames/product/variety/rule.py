# _*_ coding:utf-8 _*_
# @File  : introduction.py
# @Time  : 2021-01-21 10:09
# @Author: zizle


from PyQt5.QtCore import QMargins
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QComboBox, QPushButton

from widgets import OptionWidget, PDFContentWidget, LoadingCover

from apis.variety import VarietyAPI
from settings import STATIC_URL


class RuleVariety(QWidget):
    def __init__(self, *args, **kwargs):
        super(RuleVariety, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        option_widget = OptionWidget(self)
        option_widget.setFixedHeight(40)
        option_layout = QHBoxLayout()
        self.label1 = QLabel('规则文件:', self)
        self.rule_selector = QComboBox(self)
        self.rule_selector.setMinimumWidth(300)
        self.view_button = QPushButton('查看', self)
        option_layout.addWidget(self.label1)
        option_layout.addWidget(self.rule_selector)
        option_layout.addWidget(self.view_button)
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

        self.loading_cover = LoadingCover(self)
        self.loading_cover.resize(self.parent().width() - 200, self.parent().height())
        self.loading_cover.hide()
        self.pdf_show.file_loaded.connect(self.loading_cover.hide)

        self.view_button.clicked.connect(self.show_file)

        self.variety_api = VarietyAPI(self)
        self.variety_api.get_rule_reply.connect(self.variety_rule_reply)
        self.variety_api.get_variety_rule_file()

    def variety_rule_reply(self, data):
        self.rule_selector.clear()
        rules = data['rules']
        for intro_item in rules:
            self.rule_selector.addItem(intro_item['variety_name'], intro_item['filepath'])
        if len(rules) > 0:
            self.show_file()

    def show_file(self):
        filepath = self.rule_selector.currentData()
        if filepath:
            self.loading_cover.show()
            filepath = STATIC_URL + filepath
            self.pdf_show.set_file(filename='制度规则', filepath=filepath)
