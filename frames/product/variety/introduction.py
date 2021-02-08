# _*_ coding:utf-8 _*_
# @File  : introduction.py
# @Time  : 2021-01-21 10:09
# @Author: zizle


from PyQt5.QtCore import QMargins
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QComboBox, QPushButton

from widgets import OptionWidget, PDFContentWidget, LoadingCover

from apis.variety import VarietyAPI
from settings import STATIC_URL


class IntroductionVariety(QWidget):
    def __init__(self, *args, **kwargs):
        super(IntroductionVariety, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        option_widget = OptionWidget(self)
        option_widget.setFixedHeight(45)
        option_layout = QHBoxLayout()
        self.label1 = QLabel('品种:', self)
        self.variety_selector = QComboBox(self)
        self.variety_selector.setMinimumWidth(100)
        self.view_button = QPushButton('查看', self)
        option_layout.addWidget(self.label1)
        option_layout.addWidget(self.variety_selector)
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
        self.variety_api.get_intro_reply.connect(self.variety_intro_reply)
        self.variety_api.get_variety_intro_file()

    def variety_intro_reply(self, data):
        self.variety_selector.clear()
        intros = data['intros']
        for intro_item in intros:
            self.variety_selector.addItem(intro_item['variety_name'], intro_item['filepath'])
        if len(intros) > 0:
            self.show_file()

    def show_file(self):
        filepath = self.variety_selector.currentData()
        if filepath:
            self.loading_cover.show()
            filepath = STATIC_URL + filepath
            self.pdf_show.set_file(filename='品种介绍', filepath=filepath)
