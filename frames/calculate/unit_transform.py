# _*_ coding:utf-8 _*_
# @File  : unit_transform.py
# @Time  : 2021-01-25 15:33
# @Author: zizle

# 单位换算。
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit
from PyQt5.QtCore import QMargins, QRegExp, Qt
from widgets import OptionWidget
from gglobal import rate

RATE_DATA = rate.get_all_exchange_rate()


class NameLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super(NameLabel, self).__init__(*args, **kwargs)
        self.setStyleSheet('font-size:20px;color:#163d78;font-weight:bold')


class EqualLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super(EqualLabel, self).__init__(*args, **kwargs)
        self.setStyleSheet('font-size:20px;color:#163d78;font-weight:bold')
        self.setText(' = ')


class InputEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super(InputEdit, self).__init__(*args, **kwargs)
        self.setValidator(QRegExpValidator(QRegExp(r"^(-?\d+)(\.\d+)?$"), self))
        self.setFixedWidth(100)
        self.setStyleSheet('border:none;border-bottom: 1px solid #aaaaaa;height:30px;color:#ff6433')

    def value(self, p=False):
        if not self.text():
            return 0
        if p:
            return float(self.text()) / 100
        else:
            return float(self.text())

    def set_value(self, v, count=2):
        self.setText(str(round(v, count)))


class Farm(QWidget):
    def __init__(self, *args, **kwargs):
        super(Farm, self).__init__(*args, **kwargs)
        main_layout = QVBoxLayout()

        layout1 = QHBoxLayout()
        self.input11 = InputEdit('1', self)
        self.unit11 = QLabel('美元/蒲式耳', self)
        self.equal11 = EqualLabel(self)
        self.input12 = InputEdit('36.7437', self)
        self.unit12 = QLabel('美元/吨', self)
        self.equal12 = EqualLabel(self)
        self.input13 = InputEdit(self)
        self.unit13 = QLabel('元/吨', self)
        layout1.addWidget(self.input11)
        layout1.addWidget(self.unit11)
        layout1.addWidget(self.equal11)
        layout1.addWidget(self.input12)
        layout1.addWidget(self.unit12)
        layout1.addWidget(self.equal12)
        layout1.addWidget(self.input13)
        layout1.addWidget(self.unit13)
        layout1.addStretch()

        main_layout.addWidget(NameLabel('大豆价格换算', self))
        main_layout.addLayout(layout1)
        try:
            self.init_calculate1()
        except Exception as e:
            import traceback
            traceback.print_exc()

        main_layout.addStretch()
        self.setLayout(main_layout)

    def init_calculate1(self):
        v = RATE_DATA.get('USD/CNY', None)
        if v:
            a = self.input11.value()
            b = self.input12.value()
            c = b * float(v)
            self.input13.set_value(c, count=4)


class Metal(QWidget):
    def __init__(self, *args, **kwargs):
        super(Metal, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()

        layout.addWidget(QLabel('金属产业'))
        self.setLayout(layout)


class Chemical(QWidget):
    def __init__(self, *args, **kwargs):
        super(Chemical, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()

        layout.addWidget(QLabel('能源化工'))
        self.setLayout(layout)


class UnitTransform(QWidget):

    def __init__(self, *args, **kwargs):
        super(UnitTransform, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        option_widget = OptionWidget(self)
        option_widget.setFixedHeight(40)
        option_layout = QHBoxLayout()
        self.farm_button = QPushButton('农副产品', self)
        setattr(self.farm_button, 'type_name', 'Farm')
        self.metal_button = QPushButton('金属产业', self)
        setattr(self.metal_button, 'type_name', 'Metal')
        self.chemical_button = QPushButton('能源化工', self)
        setattr(self.chemical_button, 'type_name', 'Chemical')
        option_layout.addWidget(self.farm_button)
        option_layout.addWidget(self.metal_button)
        option_layout.addWidget(self.chemical_button)
        option_layout.addStretch()
        option_widget.setLayout(option_layout)
        layout.addWidget(option_widget)

        self.current_type = 'Farm'
        self.current_widget = Farm(self)
        layout.addWidget(self.current_widget)
        self.farm_button.clicked.connect(self.set_current_type)
        self.metal_button.clicked.connect(self.set_current_type)
        self.chemical_button.clicked.connect(self.set_current_type)
        self.setLayout(layout)

    def set_current_type(self):
        btn = self.sender()
        self.current_type = getattr(btn, 'type_name', None)

        self.show_current_widget()

    def show_current_widget(self):
        if not self.current_type:
            return
        self.current_widget.deleteLater()
        if self.current_type == 'Farm':
            self.current_widget = Farm()
        elif self.current_type == "Metal":
            self.current_widget = Metal()
        elif self.current_type == 'Chemical':
            self.current_widget = Chemical()
        else:
            return
        self.layout().addWidget(self.current_widget)


