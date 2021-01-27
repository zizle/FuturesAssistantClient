# _*_ coding:utf-8 _*_
# @File  : unit_transform.py
# @Time  : 2021-01-25 15:33
# @Author: zizle

# 单位换算。
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QScrollArea, \
    QFrame
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

    def set_value(self, v, count=5):
        if v == '':
            self.setText('')
        else:
            self.setText(str(round(v, count)))

    def focusOutEvent(self, event):
        super(InputEdit, self).focusOutEvent(event)
        self.focus_out.emit(True)

    def edit_finished(self):
        self.focus_out.emit(True)

# 含汇率的单位转换
class USDCNYWidget(QWidget):
    RATE_DATA = rate.get_all_exchange_rate()

    def __init__(self, *args, **kwargs):
        super(USDCNYWidget, self).__init__(*args, **kwargs)
        self.USD_CNY_RATE = self.RATE_DATA.get('USD/CNY', None)
        if self.USD_CNY_RATE:
            self.USD_CNY_RATE = float(self.USD_CNY_RATE)
        self.reverse_param = 1
        main_layout = QVBoxLayout()

        layout = QHBoxLayout()
        self.widget = QWidget(self)
        self.input1 = InputEdit(self)
        self.unit1 = QLabel(self)
        self.equal2 = EqualLabel(self)
        self.input2 = InputEdit(self)
        self.unit2 = QLabel(self)
        self.equal3 = EqualLabel(self)
        self.input3 = InputEdit(self)
        self.unit3 = QLabel(self)
        layout.addWidget(self.input1)
        layout.addWidget(self.unit1)
        layout.addWidget(self.equal2)
        layout.addWidget(self.input2)
        layout.addWidget(self.unit2)
        layout.addWidget(self.equal3)
        layout.addWidget(self.input3)
        layout.addWidget(self.unit3)
        layout.addStretch()

        self.name_label = NameLabel(self)
        main_layout.addWidget(self.name_label)
        self.widget.setLayout(layout)
        main_layout.addWidget(self.widget)
        self.input1.focus_out.connect(self.input1_finished)
        self.input2.focus_out.connect(self.input2_finished)
        self.input3.focus_out.connect(self.input3_finished)

        self.setLayout(main_layout)

    def set_name(self, name: str):
        self.name_label.setText(name)

    def set_reverse_param(self, value: float):
        self.reverse_param = value
        self.init_calculate()

    def set_units(self, units: list):
        self.unit1.setText(units[0])
        self.unit2.setText(units[1])
        self.unit3.setText(units[2])

    def init_calculate(self):
        self.input1.set_value(1)
        self.input2.set_value(self.reverse_param)
        if self.USD_CNY_RATE:
            self.input3.set_value(self.reverse_param * self.USD_CNY_RATE)

    def input1_finished(self):
        a = self.input1.value()
        if not a:
            return
        b = a * self.reverse_param
        c = ''
        if self.USD_CNY_RATE:
            c = b * self.USD_CNY_RATE
        self.input2.set_value(b)
        self.input3.set_value(c)

    def input2_finished(self):
        b = self.input2.value()
        if not b:
            return
        a = b / self.reverse_param
        c = ''
        if self.USD_CNY_RATE:
            c = b * self.USD_CNY_RATE
        self.input1.set_value(a)
        self.input3.set_value(c)

    def input3_finished(self):
        c = self.input3.value()
        if not c:
            return
        a, b = '', ''
        if self.USD_CNY_RATE:
            b = c / self.USD_CNY_RATE
            a = b / self.reverse_param
        self.input1.set_value(a)
        self.input2.set_value(b)


# 不含汇率的单位转换(3个)
class UNITThreeWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(UNITThreeWidget, self).__init__(*args, **kwargs)
        self.reverse_param1 = 1
        self.reverse_param2 = 1
        main_layout = QVBoxLayout()

        layout = QHBoxLayout()
        self.widget = QWidget(self)
        self.input1 = InputEdit(self)
        self.unit1 = QLabel(self)
        self.equal2 = EqualLabel(self)
        self.input2 = InputEdit(self)
        self.unit2 = QLabel(self)
        self.equal3 = EqualLabel(self)
        self.input3 = InputEdit(self)
        self.unit3 = QLabel(self)
        layout.addWidget(self.input1)
        layout.addWidget(self.unit1)
        layout.addWidget(self.equal2)
        layout.addWidget(self.input2)
        layout.addWidget(self.unit2)
        layout.addWidget(self.equal3)
        layout.addWidget(self.input3)
        layout.addWidget(self.unit3)
        layout.addStretch()

        self.name_label = NameLabel(self)
        main_layout.addWidget(self.name_label)
        self.widget.setLayout(layout)
        main_layout.addWidget(self.widget)
        self.input1.focus_out.connect(self.input1_finished)
        self.input2.focus_out.connect(self.input2_finished)
        self.input3.focus_out.connect(self.input3_finished)

        self.setLayout(main_layout)

    def set_name(self, name: str):
        self.name_label.setText(name)

    def set_reverse_params(self, values: list):
        self.reverse_param1 = values[0]
        self.reverse_param2 = values[1]
        self.init_calculate()

    def set_units(self, units: list):
        self.unit1.setText(units[0])
        self.unit2.setText(units[1])
        self.unit3.setText(units[2])

    def init_calculate(self):
        self.input1.set_value(1)
        self.input2.set_value(self.reverse_param1)
        self.input3.set_value(self.reverse_param2)

    def input1_finished(self):
        a = self.input1.value()
        if not a:
            return
        b = a * self.reverse_param1
        c = a * self.reverse_param2
        self.input2.set_value(b)
        self.input3.set_value(c)

    def input2_finished(self):
        b = self.input2.value()
        if not b:
            return
        a = b / self.reverse_param1
        c = a * self.reverse_param2
        self.input1.set_value(a)
        self.input3.set_value(c)

    def input3_finished(self):
        c = self.input3.value()
        if not c:
            return
        a = c / self.reverse_param2
        b = a * self.reverse_param1
        self.input1.set_value(a)
        self.input2.set_value(b)


# 不含汇率的单位转换(4个)
class UNITFourWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(UNITFourWidget, self).__init__(*args, **kwargs)
        self.reverse_param1 = 1
        self.reverse_param2 = 1
        self.reverse_param3 = 1
        main_layout = QVBoxLayout()

        layout = QHBoxLayout()
        self.widget = QWidget(self)
        self.input1 = InputEdit(self)
        self.unit1 = QLabel(self)
        self.equal2 = EqualLabel(self)
        self.input2 = InputEdit(self)
        self.unit2 = QLabel(self)
        self.equal3 = EqualLabel(self)
        self.input3 = InputEdit(self)
        self.unit3 = QLabel(self)
        self.equal4 = EqualLabel(self)
        self.input4 = InputEdit(self)
        self.unit4 = QLabel(self)
        layout.addWidget(self.input1)
        layout.addWidget(self.unit1)
        layout.addWidget(self.equal2)
        layout.addWidget(self.input2)
        layout.addWidget(self.unit2)
        layout.addWidget(self.equal3)
        layout.addWidget(self.input3)
        layout.addWidget(self.unit3)
        layout.addWidget(self.equal4)
        layout.addWidget(self.input4)
        layout.addWidget(self.unit4)
        layout.addStretch()

        self.name_label = NameLabel(self)
        main_layout.addWidget(self.name_label)
        self.widget.setLayout(layout)
        main_layout.addWidget(self.widget)
        self.input1.focus_out.connect(self.input1_finished)
        self.input2.focus_out.connect(self.input2_finished)
        self.input3.focus_out.connect(self.input3_finished)
        self.input4.focus_out.connect(self.input4_finished)

        self.setLayout(main_layout)

    def set_name(self, name: str):
        self.name_label.setText(name)

    def set_reverse_params(self, values: list):
        self.reverse_param1 = values[0]
        self.reverse_param2 = values[1]
        self.reverse_param3 = values[2]
        self.init_calculate()

    def set_units(self, units: list):
        self.unit1.setText(units[0])
        self.unit2.setText(units[1])
        self.unit3.setText(units[2])
        self.unit3.setText(units[3])

    def init_calculate(self):
        self.input1.set_value(1)
        self.input2.set_value(self.reverse_param1)
        self.input3.set_value(self.reverse_param2)
        self.input4.set_value(self.reverse_param3)

    def input1_finished(self):
        a = self.input1.value()
        if not a:
            return
        b = a * self.reverse_param1
        c = a * self.reverse_param2
        d = a * self.reverse_param3
        self.input2.set_value(b)
        self.input3.set_value(c)
        self.input4.set_value(d)

    def input2_finished(self):
        b = self.input2.value()
        if not b:
            return
        a = b / self.reverse_param1
        c = a * self.reverse_param2
        d = a * self.reverse_param3
        self.input1.set_value(a)
        self.input3.set_value(c)
        self.input4.set_value(d)

    def input3_finished(self):
        c = self.input3.value()
        if not c:
            return
        a = c / self.reverse_param2
        b = a * self.reverse_param1
        d = a * self.reverse_param3
        self.input1.set_value(a)
        self.input2.set_value(b)
        self.input4.set_value(d)

    def input4_finished(self):
        d = self.input4.value()
        if not d:
            return
        a = d / self.reverse_param3
        b = a * self.reverse_param1
        c = a * self.reverse_param2
        self.input1.set_value(a)
        self.input2.set_value(b)
        self.input3.set_value(c)


# 不含汇率的单位转换(5个)
class UNITFiveWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(UNITFiveWidget, self).__init__(*args, **kwargs)
        self.reverse_param1 = 1
        self.reverse_param2 = 1
        self.reverse_param3 = 1
        self.reverse_param4 = 1
        main_layout = QVBoxLayout()

        layout = QHBoxLayout()
        self.widget = QWidget(self)
        self.input1 = InputEdit(self)
        self.unit1 = QLabel(self)
        self.equal2 = EqualLabel(self)
        self.input2 = InputEdit(self)
        self.unit2 = QLabel(self)
        self.equal3 = EqualLabel(self)
        self.input3 = InputEdit(self)
        self.unit3 = QLabel(self)
        self.equal4 = EqualLabel(self)
        self.input4 = InputEdit(self)
        self.unit4 = QLabel(self)
        self.equal5 = EqualLabel(self)
        self.input5 = InputEdit(self)
        self.unit5 = QLabel(self)
        layout.addWidget(self.input1)
        layout.addWidget(self.unit1)
        layout.addWidget(self.equal2)
        layout.addWidget(self.input2)
        layout.addWidget(self.unit2)
        layout.addWidget(self.equal3)
        layout.addWidget(self.input3)
        layout.addWidget(self.unit3)
        layout.addWidget(self.equal4)
        layout.addWidget(self.input4)
        layout.addWidget(self.unit4)
        layout.addWidget(self.equal5)
        layout.addWidget(self.input5)
        layout.addWidget(self.unit5)
        layout.addStretch()

        self.name_label = NameLabel(self)
        main_layout.addWidget(self.name_label)
        self.widget.setLayout(layout)
        main_layout.addWidget(self.widget)
        self.input1.focus_out.connect(self.input1_finished)
        self.input2.focus_out.connect(self.input2_finished)
        self.input3.focus_out.connect(self.input3_finished)
        self.input4.focus_out.connect(self.input4_finished)
        self.input5.focus_out.connect(self.input5_finished)

        self.setLayout(main_layout)

    def set_name(self, name: str):
        self.name_label.setText(name)

    def set_reverse_params(self, values: list):
        self.reverse_param1 = values[0]
        self.reverse_param2 = values[1]
        self.reverse_param3 = values[2]
        self.reverse_param4 = values[3]
        self.init_calculate()

    def set_units(self, units: list):
        self.unit1.setText(units[0])
        self.unit2.setText(units[1])
        self.unit3.setText(units[2])
        self.unit4.setText(units[3])
        self.unit5.setText(units[4])

    def init_calculate(self):
        self.input1.set_value(1)
        self.input2.set_value(self.reverse_param1)
        self.input3.set_value(self.reverse_param2)
        self.input4.set_value(self.reverse_param3)
        self.input5.set_value(self.reverse_param4)

    def input1_finished(self):
        a = self.input1.value()
        if not a:
            return
        b = a * self.reverse_param1
        c = a * self.reverse_param2
        d = a * self.reverse_param3
        e = a * self.reverse_param4
        self.input2.set_value(b)
        self.input3.set_value(c)
        self.input4.set_value(d)
        self.input5.set_value(e)

    def input2_finished(self):
        b = self.input2.value()
        if not b:
            return
        a = b / self.reverse_param1
        c = a * self.reverse_param2
        d = a * self.reverse_param3
        e = a * self.reverse_param4
        self.input1.set_value(a)
        self.input3.set_value(c)
        self.input4.set_value(d)
        self.input5.set_value(e)

    def input3_finished(self):
        c = self.input3.value()
        if not c:
            return
        a = c / self.reverse_param2
        b = a * self.reverse_param1
        d = a * self.reverse_param3
        e = a * self.reverse_param4
        self.input1.set_value(a)
        self.input2.set_value(b)
        self.input4.set_value(d)
        self.input5.set_value(e)

    def input4_finished(self):
        d = self.input4.value()
        if not d:
            return
        a = d / self.reverse_param3
        b = a * self.reverse_param1
        c = a * self.reverse_param2
        e = a * self.reverse_param4
        self.input1.set_value(a)
        self.input2.set_value(b)
        self.input3.set_value(c)
        self.input5.set_value(e)

    def input5_finished(self):
        e = self.input5.value()
        if not e:
            return
        a = e / self.reverse_param4
        b = a * self.reverse_param1
        c = a * self.reverse_param2
        d = a * self.reverse_param3
        self.input1.set_value(a)
        self.input2.set_value(b)
        self.input3.set_value(c)
        self.input4.set_value(d)


class Farm(QWidget):
    RATE_DATA = rate.get_all_exchange_rate()

    def __init__(self, *args, **kwargs):
        super(Farm, self).__init__(*args, **kwargs)
        self.USD_CNY_RATE = self.RATE_DATA.get('USD/CNY', None)
        if self.USD_CNY_RATE:
            self.USD_CNY_RATE = float(self.USD_CNY_RATE)

        main_layout = QVBoxLayout()

        # 大豆价格换算
        self.a1 = USDCNYWidget(self)
        self.a1.set_name('大豆价格换算')
        self.a1.set_units(['美元/蒲式耳', '美元/吨', '元/吨'])
        self.a1.set_reverse_param(36.7437)
        main_layout.addWidget(self.a1)

        # 大豆单产换算
        self.a2 = UNITThreeWidget(self)
        self.a2.set_name('大豆单产换算')
        self.a2.set_units(['蒲式耳/英亩', '吨/公顷', '斤/亩'])
        self.a2.set_reverse_params([0.0672, 4.4799])
        main_layout.addWidget(self.a2)

        # 大豆重量容积换算
        self.a3 = UNITFiveWidget(self)
        self.a3.set_name('大豆重量容积换算')
        self.a3.set_units(['蒲式耳', '磅', '公吨', '长吨', '短吨'])
        self.a3.set_reverse_params([60, 0.0272, 0.0268, 0.03])
        main_layout.addWidget(self.a3)

        # 豆粕价格换算
        self.m1 = USDCNYWidget(self)
        self.m1.set_name('豆粕价格换算')
        self.m1.set_units(['美元/短吨', '美元/吨', '元/吨'])
        self.m1.set_reverse_param(1.1025)
        main_layout.addWidget(self.m1)

        # 豆粕重量容积换算
        self.m2 = UNITThreeWidget(self)
        self.m2.set_name('豆粕重量容积换算')
        self.m2.set_units(['短吨', '磅', '公吨'])
        self.m2.set_reverse_params([2000, 0.9072])
        main_layout.addWidget(self.m2)

        # 豆油价格换算
        self.y1 = USDCNYWidget(self)
        self.y1.set_name('豆油价格换算')
        self.y1.set_units(['美分/磅', '美元/吨', '元/吨'])
        self.y1.set_reverse_param(22.0462)
        main_layout.addWidget(self.y1)

        # 豆油重量容积换算
        self.y2 = UNITThreeWidget(self)
        self.y2.set_name('豆油重量容积换算')
        self.y2.set_units(['短吨', '磅', '公吨'])
        self.y2.set_reverse_params([2000, 0.9072])
        main_layout.addWidget(self.y2)

        # 玉米价格换算
        self.c1 = USDCNYWidget(self)
        self.c1.set_name('玉米价格换算')
        self.c1.set_units(['美元/蒲式耳', '美元/吨', '元/吨'])
        self.c1.set_reverse_param(39.36825)
        main_layout.addWidget(self.c1)

        # 玉米单产换算
        self.c2 = UNITThreeWidget(self)
        self.c2.set_name('玉米单产换算')
        self.c2.set_units(['蒲式耳/英亩', '吨/公顷', '公斤/亩'])
        self.c2.set_reverse_params([0.062719012, 4.18126749])
        main_layout.addWidget(self.c2)

        # 玉米重量容积换算
        self.c3 = UNITFiveWidget(self)
        self.c3.set_name('玉米重量容积换算')
        self.c3.set_units(['蒲式耳', '磅', '公吨', '长吨', '短吨'])
        self.c3.set_reverse_params([56, 0.0254012, 0.025, 0.028])
        main_layout.addWidget(self.c3)

        # 棉花价格换算
        self.cf1 = USDCNYWidget(self)
        self.cf1.set_name('棉花价格换算')
        self.cf1.set_units(['美分/磅', '美元/吨', '元/吨'])
        self.cf1.set_reverse_param(22.0462)
        main_layout.addWidget(self.cf1)

        # 棉花单产换算
        self.cf2 = UNITThreeWidget(self)
        self.cf2.set_name('棉花单产换算')
        self.cf2.set_units(['磅/英亩', '吨/公顷', '公斤/亩'])
        self.cf2.set_reverse_params([0.00112, 0.074666667])
        main_layout.addWidget(self.cf2)

        # 棉花重量容积换算
        self.cf3 = UNITThreeWidget(self)
        self.cf3.set_name('棉花重量容积换算')
        self.cf3.set_units(['磅', '公吨', '包'])
        self.cf3.set_reverse_params([0.0004536, 0.002083334])
        main_layout.addWidget(self.cf3)

        # 小麦价格换算
        self.pm1 = USDCNYWidget(self)
        self.pm1.set_name('小麦价格换算')
        self.pm1.set_units(['美元/蒲式耳', '美元/吨', '元/吨'])
        self.pm1.set_reverse_param(36.7437)
        main_layout.addWidget(self.pm1)

        # 小麦单产换算
        self.pm2 = UNITThreeWidget(self)
        self.pm2.set_name('小麦单产换算')
        self.pm2.set_units(['蒲式耳/英亩', '吨/公顷', '公斤/亩'])
        self.pm2.set_reverse_params([0.0671987654, 4.4799176955])
        main_layout.addWidget(self.pm2)

        # 小麦重量容积换算
        self.pm3 = UNITFiveWidget(self)
        self.pm3.set_name('小麦重量容积换算')
        self.pm3.set_units(['蒲式耳', '磅', '公吨', '长吨', '短吨'])
        self.pm3.set_reverse_params([60, 0.0272155, 0.0267857, 0.03])
        main_layout.addWidget(self.pm3)

        # 纽约原糖价格换算
        self.sr1 = USDCNYWidget(self)
        self.sr1.set_name('纽约原糖价格换算')
        self.sr1.set_units(['美分/磅', '美元/吨', '元/吨'])
        self.sr1.set_reverse_param(22.0462)
        main_layout.addWidget(self.sr1)

        # 纽约原糖重量容量换算
        self.sr2 = UNITThreeWidget(self)
        self.sr2.set_name('纽约原糖重量容量换算')
        self.sr2.set_units(['短吨', '磅', '公吨'])
        self.sr2.set_reverse_params([2000, 0.9072])
        main_layout.addWidget(self.sr2)

        main_layout.addStretch()
        self.setLayout(main_layout)


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

        self.content_area = QScrollArea(self)
        self.content_area.setWidgetResizable(True)
        self.content_area.setFrameShape(QFrame.NoFrame)
        layout.addWidget(self.content_area)

        self.current_type = 'Farm'

        self.farm_button.clicked.connect(self.set_current_type)
        self.metal_button.clicked.connect(self.set_current_type)
        self.chemical_button.clicked.connect(self.set_current_type)

        self.setLayout(layout)

        self.show_current_widget()

    def set_current_type(self):
        btn = self.sender()
        self.current_type = getattr(btn, 'type_name', None)
        self.show_current_widget()

    def show_current_widget(self):
        if not self.current_type:
            return
        if self.current_type == 'Farm':
            current_widget = Farm(self)
        elif self.current_type == "Metal":
            current_widget = Metal(self)
        elif self.current_type == 'Chemical':
            current_widget = Chemical(self)
        else:
            return
        self.content_area.setWidget(current_widget)


