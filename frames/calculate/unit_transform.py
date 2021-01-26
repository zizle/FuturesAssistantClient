# _*_ coding:utf-8 _*_
# @File  : unit_transform.py
# @Time  : 2021-01-25 15:33
# @Author: zizle

# 单位换算。
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit
from PyQt5.QtCore import QMargins, QRegExp, Qt, pyqtSignal
from widgets import OptionWidget
from gglobal import rate


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
    focus_out = pyqtSignal(bool)

    def __init__(self, *args, **kwargs):
        super(InputEdit, self).__init__(*args, **kwargs)
        self.setValidator(QRegExpValidator(QRegExp(r"^(-?\d+)(\.\d+)?$"), self))
        self.setFixedWidth(100)
        self.setStyleSheet('border:none;border-bottom: 1px solid #aaaaaa;height:30px;color:#ff6433')
        self.editingFinished.connect(self.edit_finished)

    def value(self, p=False):
        if not self.text().strip():
            return 0
        if p:
            return float(self.text()) / 100
        else:
            return float(self.text())

    def set_value(self, v, count=2):
        self.setText(str(round(v, count)))

    def focusOutEvent(self, event):
        super(InputEdit, self).focusOutEvent(event)
        self.focus_out.emit(True)

    def edit_finished(self):
        self.focus_out.emit(True)


class Farm(QWidget):
    RATE_DATA = rate.get_all_exchange_rate()

    def __init__(self, *args, **kwargs):
        super(Farm, self).__init__(*args, **kwargs)
        self.USD_CNY_RATE = self.RATE_DATA.get('USD/CNY', None)
        if self.USD_CNY_RATE:
            self.USD_CNY_RATE = float(self.USD_CNY_RATE)

        main_layout = QVBoxLayout()

        layout1 = QHBoxLayout()
        self.widget1 = QWidget(self)
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
        self.widget1.setLayout(layout1)
        main_layout.addWidget(self.widget1)
        self.init_calculate1()
        self.input11.focus_out.connect(self.input11_finished)
        self.input12.focus_out.connect(self.input12_finished)
        self.input13.focus_out.connect(self.input13_finished)

        """ 豆粕价格换算 """
        layout2 = QHBoxLayout()
        self.widget2 = QWidget(self)
        self.input21 = InputEdit('1', self)
        self.unit21 = QLabel('美元/短吨', self)
        self.equal21 = EqualLabel(self)
        self.input22 = InputEdit('1.1025', self)
        self.unit22 = QLabel('美元/吨', self)
        self.equal22 = EqualLabel(self)
        self.input23 = InputEdit(self)
        self.unit23 = QLabel('元/吨', self)
        layout2.addWidget(self.input21)
        layout2.addWidget(self.unit21)
        layout2.addWidget(self.equal21)
        layout2.addWidget(self.input22)
        layout2.addWidget(self.unit22)
        layout2.addWidget(self.equal22)
        layout2.addWidget(self.input23)
        layout2.addWidget(self.unit23)
        layout2.addStretch()

        main_layout.addWidget(NameLabel('豆粕价格换算', self))
        self.widget2.setLayout(layout2)
        main_layout.addWidget(self.widget2)
        self.init_calculate2()
        self.input21.focus_out.connect(self.input21_finished)
        self.input22.focus_out.connect(self.input22_finished)
        self.input23.focus_out.connect(self.input23_finished)

        main_layout.addStretch()
        self.setLayout(main_layout)

    def init_calculate1(self):
        if self.USD_CNY_RATE:
            b = self.input12.value()
            c = b * float(self.USD_CNY_RATE)
            self.input13.set_value(c, count=4)

    def input11_finished(self):
        a = self.input11.value()
        if not a:
            return
        b = a * 36.7437
        c = b * float(self.USD_CNY_RATE)
        self.input12.set_value(b, count=4)
        self.input13.set_value(c, count=4)

    def input12_finished(self):
        b = self.input12.value()
        if not b:
            return
        a = b / 36.7437
        c = b * float(self.USD_CNY_RATE)
        self.input11.set_value(a, count=4)
        self.input13.set_value(c, count=4)

    def input13_finished(self):
        c = self.input13.value()
        if not c:
            return
        b = c / self.USD_CNY_RATE
        a = b / 36.7437
        self.input11.set_value(a, count=4)
        self.input12.set_value(b, count=4)

    def init_calculate2(self):
        if self.USD_CNY_RATE:
            b = self.input22.value()
            c = b * float(self.USD_CNY_RATE)
            self.input23.set_value(c, count=4)

    def input21_finished(self):
        a = self.input21.value()
        if not a:
            return
        b = a * 1.1025
        c = b * float(self.USD_CNY_RATE)
        self.input22.set_value(b, count=4)
        self.input23.set_value(c, count=4)

    def input22_finished(self):
        b = self.input22.value()
        if not b:
            return
        a = b / 1.1025
        c = b * float(self.USD_CNY_RATE)
        self.input21.set_value(a, count=4)
        self.input23.set_value(c, count=4)

    def input23_finished(self):
        c = self.input23.value()
        if not c:
            return
        b = c / self.USD_CNY_RATE
        a = b / 1.1025
        self.input21.set_value(a, count=4)
        self.input22.set_value(b, count=4)


class Metal(QWidget):
    RATE_DATA = rate.get_all_exchange_rate()

    def __init__(self, *args, **kwargs):
        super(Metal, self).__init__(*args, **kwargs)
        self.USD_CNY_RATE = self.RATE_DATA.get('USD/CNY', None)
        if self.USD_CNY_RATE:
            self.USD_CNY_RATE = float(self.USD_CNY_RATE)

        main_layout = QVBoxLayout()

        layout1 = QHBoxLayout()
        self.widget1 = QWidget(self)
        self.input11 = InputEdit('1', self)
        self.unit11 = QLabel('美元/盎司', self)
        self.equal11 = EqualLabel(self)
        self.input12 = InputEdit('', self)
        self.unit12 = QLabel('元/克', self)

        layout1.addWidget(self.input11)
        layout1.addWidget(self.unit11)
        layout1.addWidget(self.equal11)
        layout1.addWidget(self.input12)
        layout1.addWidget(self.unit12)
        layout1.addStretch()

        main_layout.addWidget(NameLabel('黄金/白银价格换算', self))
        self.widget1.setLayout(layout1)
        self.init_calculate1()
        main_layout.addWidget(self.widget1)
        self.input11.focus_out.connect(self.input11_finished)
        self.input12.focus_out.connect(self.input12_finished)

        main_layout.addStretch()
        self.setLayout(main_layout)

    def init_calculate1(self):
        a = self.input11.value()
        b = a * self.USD_CNY_RATE / 31.1035
        self.input12.set_value(b, count=4)

    def input11_finished(self):
        a = self.input11.value()
        if not a:
            return
        b = a * self.USD_CNY_RATE / 31.1035
        self.input12.set_value(b, count=4)

    def input12_finished(self):
        b = self.input12.value()
        if not b:
            return
        a = b * 0.0311035 / self.USD_CNY_RATE
        self.input11.set_value(a, count=4)


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


