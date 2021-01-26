# _*_ coding:utf-8 _*_
# @File  : introduction.py
# @Time  : 2021-01-21 10:09
# @Author: zizle


from PyQt5.QtCore import QMargins
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QComboBox, QPushButton

from widgets import OptionWidget, PDFContentWidget, LoadingCover

from gglobal import variety
from settings import STATIC_URL


class IntroductionVariety(QWidget):
    def __init__(self, *args, **kwargs):
        super(IntroductionVariety, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        option_widget = OptionWidget(self)
        option_widget.setFixedHeight(40)
        option_layout = QHBoxLayout()
        self.label1 = QLabel('品种:', self)
        self.variety_selector = QComboBox(self)
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

        self.get_all_variety()

        self.view_button.clicked.connect(self.show_file)

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
            self.loading_cover.show()
            current_v = self.reset_variety_en(current_v)
            filepath = STATIC_URL + 'VARIETY/Intro/{}.pdf'.format(current_v)
            self.pdf_show.set_file(filename='品种介绍', filepath=filepath)