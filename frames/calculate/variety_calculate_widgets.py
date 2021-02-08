# _*_ coding:utf-8 _*_
# @File  : variety_calculate_widgets.py
# @Time  : 2021-01-21 15:40
# @Author: zizle

# 各品种的计算控件
import math
import datetime
from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QVBoxLayout, QLineEdit, QPushButton, QFrame, QDateEdit
from PyQt5.QtCore import Qt, QRegExp, QMargins, QDate
from PyQt5.QtGui import QRegExpValidator
from gglobal import rate

from popup.message import InformationPopup

RATE_DATA = rate.get_all_exchange_rate()

CALCULATE_WIDGET_WIDTH = 500  # 计算控件的宽度

MARGIN_TOP, MARGIN_RIGHT, MARGIN_BOTTOM, MARGIN_LEFT = (50, 0, 50, 0)


SEP_SPACING = 50  # 分割线控件之间的距离


def get_date_range_count(d1, d2, c):
    if c == 'month': # 计算月份差
        return (d2.year - d1.year) * 12 + (d2.month - d1.month)
    elif c == 'year': # 计算年份差
        return d2.year - d1.year
    elif c == 'day':
        return (d2 - d1).days
    else:
        return 0


class HorizonSepLine(QFrame):
    def __init__(self, *args, **kwargs):
        super(HorizonSepLine, self).__init__(*args, **kwargs)
        self.setLineWidth(2)
        self.setFrameStyle(QFrame.HLine | QFrame.Plain)
        self.setStyleSheet("color:#bbbbbb")


class NameLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super(NameLabel, self).__init__(*args, **kwargs)
        self.setStyleSheet('font-size:20px;color:#ff6433;font-weight:bold')


class InputEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super(InputEdit, self).__init__(*args, **kwargs)
        self.setValidator(QRegExpValidator(QRegExp(r"^(-?\d+)(\.\d+)?$"), self))
        self.setStyleSheet('border: 1px solid #aaaaaa;height:35px')

    def value(self, p=False):
        if not self.text():
            return None
        if p:
            return float(self.text()) / 100
        else:
            return float(self.text())

    def set_value(self, v, count=4):
        self.setText(str(round(v, count)))


class DateEdit(QDateEdit):
    def __init__(self, *args, **kwargs):
        super(DateEdit, self).__init__(*args, **kwargs)
        self.setCalendarPopup(True)
        self.setDisplayFormat('yyyy-MM-dd')
        self.setDate(QDate.currentDate())
        self.setObjectName('dateEdit')
        self.setStyleSheet('#dateEdit{border: 1px solid #aaaaaa;height:35px}')

    def value(self):
        if not self.text():
            return None
        return datetime.datetime.strptime(self.text(), '%Y-%m-%d')


class ResultLabel(QLabel):
    value = 0

    def __init__(self, *args, **kwargs):
        super(ResultLabel, self).__init__(*args, **kwargs)
        self.setText('=')
        self.setStyleSheet('font-size:20px;border:none;border-bottom:1px solid #333333')

    def set_value(self, text, count=2) -> None:
        v = round(text, count)
        text = " = <span style='color:#ff6433'>{}</span>".format(v)
        self.setText(text)
        self.value = v

    def get_value(self):
        return self.value


class CalculateButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super(CalculateButton, self).__init__(*args, **kwargs)
        # self.setMaximumWidth(200)
        self.setStyleSheet('color:#ffffff;background-color:#2f75b5;height:30px')


class A(QWidget):
    def __init__(self, *args, **kwargs):
        super(A, self).__init__(*args, **kwargs)
        main_layout = QVBoxLayout()
        calculate_widget = QWidget(self)
        calculate_widget.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout = QGridLayout()
        layout.setContentsMargins(QMargins(MARGIN_LEFT, 0, MARGIN_RIGHT, MARGIN_BOTTOM))
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.name1 = NameLabel('大豆进口成本', self)
        self.label1 = QLabel('CBOT大豆盘面价格:', self)  # a
        self.label2 = QLabel('FOB升贴水:', self)  # b
        self.label3 = QLabel('海运费:', self)  # c
        self.label4 = QLabel('增值税:', self)  # d
        self.label5 = QLabel('关税:', self)  # e
        self.label6 = QLabel('汇率:', self)  # f
        self.label7 = QLabel('港杂费:', self) # g

        self.input1 = InputEdit(self)
        self.input2 = InputEdit(self)
        self.input3 = InputEdit('30', self)
        self.input4 = InputEdit('9', self)
        self.input5 = InputEdit('3', self)
        self.input6 = InputEdit(RATE_DATA.get('USD/CNY', ''), self)
        self.input7 = InputEdit('120', self)

        self.unit1 = QLabel('美分/蒲式耳', self)
        self.unit2 = QLabel('美分/蒲式耳', self)
        self.unit3 = QLabel('美元/吨', self)
        self.unit4 = QLabel('%', self)
        self.unit5 = QLabel('%', self)
        self.unit6 = QLabel('USD/CNY', self)
        self.unit7 = QLabel('元/吨', self)

        self.calculate_button = CalculateButton('试算成本', self)

        self.result1 = ResultLabel(self)
        self.unit8 = QLabel('元/吨', self)

        layout.addWidget(self.name1, 0, 0, 1, 3)
        layout.addWidget(self.label1, 1, 0)
        layout.addWidget(self.label2, 2, 0)
        layout.addWidget(self.label3, 3, 0)
        layout.addWidget(self.label4, 4, 0)
        layout.addWidget(self.label5, 5, 0)
        layout.addWidget(self.label6, 6, 0)
        layout.addWidget(self.label7, 7, 0)

        layout.addWidget(self.input1, 1, 1)
        layout.addWidget(self.input2, 2, 1)
        layout.addWidget(self.input3, 3, 1)
        layout.addWidget(self.input4, 4, 1)
        layout.addWidget(self.input5, 5, 1)
        layout.addWidget(self.input6, 6, 1)
        layout.addWidget(self.input7, 7, 1)

        layout.addWidget(self.unit1, 1, 2)
        layout.addWidget(self.unit2, 2, 2)
        layout.addWidget(self.unit3, 3, 2)
        layout.addWidget(self.unit4, 4, 2)
        layout.addWidget(self.unit5, 5, 2)
        layout.addWidget(self.unit6, 6, 2)
        layout.addWidget(self.unit7, 7, 2)

        layout.addWidget(QLabel(self), 8, 0)  # 占位行

        layout.addWidget(self.calculate_button, 9, 0)
        layout.addWidget(self.result1, 9, 1)
        layout.addWidget(self.unit8, 9, 2)

        calculate_widget.setLayout(layout)
        main_layout.addWidget(calculate_widget, alignment=Qt.AlignTop | Qt.AlignHCenter)

        # 间隔横线
        main_layout.addWidget(HorizonSepLine(self), alignment=Qt.AlignTop)

        # 进口大豆现货压榨利润
        widget2 = QWidget(self)
        widget2.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout2 = QGridLayout()
        layout2.setContentsMargins(QMargins(MARGIN_LEFT, MARGIN_TOP, MARGIN_RIGHT, MARGIN_BOTTOM))
        layout2.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.name2 = NameLabel('进口大豆现货压榨利润', self)
        self.label21 = QLabel('豆粕现货价格:', self)  # a
        self.label22 = QLabel('豆油现货价格:', self)  # b
        self.label23 = QLabel('大豆进口成本:', self)  # c
        self.label24 = QLabel('加工费:', self)  # d

        self.input21 = InputEdit(self)
        self.input22 = InputEdit(self)
        self.input23 = InputEdit(self)
        self.input24 = InputEdit('130', self)

        self.unit21 = QLabel('元/吨', self)
        self.unit22 = QLabel('元/吨', self)
        self.unit23 = QLabel('元/吨', self)
        self.unit24 = QLabel('元/吨', self)
        self.unit25 = QLabel('元/吨', self)

        self.calculate_button2 = CalculateButton('试算利润', self)
        self.result2 = ResultLabel(self)

        layout2.addWidget(self.name2, 0, 0, 1, 3)
        layout2.addWidget(self.label21, 1, 0)
        layout2.addWidget(self.label22, 2, 0)
        layout2.addWidget(self.label23, 3, 0)
        layout2.addWidget(self.label24, 4, 0)

        layout2.addWidget(self.input21, 1, 1)
        layout2.addWidget(self.input22, 2, 1)
        layout2.addWidget(self.input23, 3, 1)
        layout2.addWidget(self.input24, 4, 1)

        layout2.addWidget(self.unit21, 1, 2)
        layout2.addWidget(self.unit22, 2, 2)
        layout2.addWidget(self.unit23, 3, 2)
        layout2.addWidget(self.unit24, 4, 2)

        layout2.addWidget(QLabel(self), 5, 0)  # 占位行

        layout2.addWidget(self.calculate_button2, 6, 0)
        layout2.addWidget(self.result2, 6, 1)
        layout2.addWidget(self.unit25, 6, 2)

        widget2.setLayout(layout2)
        main_layout.addWidget(widget2, alignment=Qt.AlignTop | Qt.AlignHCenter)

        self.setLayout(main_layout)
        self.calculate_button.clicked.connect(self.calculate1)  # 计算进口大豆成本
        self.calculate_button2.clicked.connect(self.calculate2)  # 计算进口大豆现货压榨利润

    def calculate1(self):
        # 大豆进口成本计算
        # r = ((a + b) * 0.367437 + c) * (1 + d) * (1 + e) * f + g
        # 大豆进口成本 =〔（CBOT期价＋FOB升贴水）×0.367437＋海运费〕×(1+增值税)×(1+关税)×汇率＋港杂费
        a = self.input1.value()
        b = self.input2.value()
        c = self.input3.value()
        d = self.input4.value()
        e = self.input5.value()
        f = self.input6.value()
        g = self.input7.value()
        params = [a, b, c, d, e, f, g]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        # 计算
        r = ((a + b) * 0.367437 + c) * (1 + d / 100) * (1 + e / 100) * f + g
        self.result1.set_value(r)

    def calculate2(self):
        # 进口大豆现货压榨利润
        # r = a * 0.785 + b * 0.19 - c - d
        # 进口大豆现货压榨利润=豆粕现货价格*0.785+豆油现货价格*0.19-大豆成本-加工费
        a = self.input21.value()
        b = self.input22.value()
        c = self.input23.value()
        d = self.input24.value()
        params = [a, b, c, d]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        r = a * 0.785 + b * 0.19 - c - d
        self.result2.set_value(r)


class AP(QWidget):

    RATE_DATA = rate.get_all_exchange_rate()

    def __init__(self, *args, **kwargs):
        super(AP, self).__init__(*args, **kwargs)
        self.USD_CNY_RATE = self.RATE_DATA.get('USD/CNY', None)
        if self.USD_CNY_RATE:
            self.USD_CNY_RATE = float(self.USD_CNY_RATE)
        main_layout = QVBoxLayout()
        """ 苹果成本价 """
        widget1 = QWidget(self)
        widget1.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout1 = QGridLayout()
        layout1.setContentsMargins(QMargins(MARGIN_LEFT, 0, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name1 = NameLabel('苹果成本价格测算', self)
        self.label11 = QLabel('收购价', self)
        self.input11 = InputEdit(self)
        self.unit11 = QLabel('元/吨', self)

        layout1.addWidget(self.name1, 0, 0, 1, 3)
        layout1.addWidget(self.label11, 1, 0)
        layout1.addWidget(self.input11, 1, 1)
        layout1.addWidget(self.unit11, 1, 2)

        self.label12 = QLabel('等级容许差额', self)
        self.input12 = InputEdit(self)
        self.unit12 = QLabel('元/吨', self)

        layout1.addWidget(self.label12, 2, 0)
        layout1.addWidget(self.input12, 2, 1)
        layout1.addWidget(self.unit12, 2, 2)

        layout1.addWidget(QLabel(self), 3, 0)

        self.calculate_button1 = CalculateButton('试算成本', self)
        self.result1 = ResultLabel(self)
        self.result_unit1 = QLabel('元/吨', self)
        layout1.addWidget(self.calculate_button1, 15, 0)
        layout1.addWidget(self.result1, 15, 1)
        layout1.addWidget(self.result_unit1, 15, 2)
        widget1.setLayout(layout1)
        self.init_calculate1()
        self.calculate_button1.clicked.connect(self.calculate1)
        main_layout.addWidget(widget1, alignment=Qt.AlignTop | Qt.AlignHCenter)

        self.setLayout(main_layout)

    def init_calculate1(self):
        self.input12.set_value(1000)

    def calculate1(self):
        """
        成本公式=山东栖霞一二级富士苹果收购价格+等级容许差额
        """
        a = self.input11.value()
        b = self.input12.value()
        params = [a, b]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        self.result1.set_value(a + b, count=4)


class AL(QWidget):
    RATE_DATA = rate.get_all_exchange_rate()

    def __init__(self, *args, **kwargs):
        super(AL, self).__init__(*args, **kwargs)
        self.USD_CNY_RATE = self.RATE_DATA.get('USD/CNY', None)
        if self.USD_CNY_RATE:
            self.USD_CNY_RATE = float(self.USD_CNY_RATE)
        main_layout = QVBoxLayout()
        """ 铝进口成本 """
        widget1 = QWidget(self)
        widget1.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout1 = QGridLayout()
        layout1.setContentsMargins(QMargins(MARGIN_LEFT, 0, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name1 = NameLabel('铝进口成本', self)
        self.label11 = QLabel('LME三个月期货价', self)
        self.input11 = InputEdit(self)
        self.unit11 = QLabel('美元/吨', self)

        layout1.addWidget(self.name1, 0, 0, 1, 3)
        layout1.addWidget(self.label11, 1, 0)
        layout1.addWidget(self.input11, 1, 1)
        layout1.addWidget(self.unit11, 1, 2)

        self.label12 = QLabel('LME铝升贴水', self)
        self.input12 = InputEdit(self)
        self.unit12 = QLabel('美元/吨', self)

        layout1.addWidget(self.label12, 2, 0)
        layout1.addWidget(self.input12, 2, 1)
        layout1.addWidget(self.unit12, 2, 2)

        self.label13 = QLabel('CIF到岸升贴水', self)
        self.input13 = InputEdit(self)
        self.unit13 = QLabel('美元/吨', self)

        layout1.addWidget(self.label13, 3, 0)
        layout1.addWidget(self.input13, 3, 1)
        layout1.addWidget(self.unit13, 3, 2)

        self.label14 = QLabel('汇率', self)
        self.input14 = InputEdit(self)
        self.unit14 = QLabel('USD/CNY', self)

        layout1.addWidget(self.label14, 4, 0)
        layout1.addWidget(self.input14, 4, 1)
        layout1.addWidget(self.unit14, 4, 2)

        self.label15 = QLabel('增值税率', self)
        self.input15 = InputEdit(self)
        self.unit15 = QLabel('%', self)

        layout1.addWidget(self.label15, 5, 0)
        layout1.addWidget(self.input15, 5, 1)
        layout1.addWidget(self.unit15, 5, 2)

        self.label16 = QLabel('关税税率', self)
        self.input16 = InputEdit(self)
        self.unit16 = QLabel('%', self)

        layout1.addWidget(self.label16, 6, 0)
        layout1.addWidget(self.input16, 6, 1)
        layout1.addWidget(self.unit16, 6, 2)

        self.label17 = QLabel('港杂费', self)
        self.input17 = InputEdit(self)
        self.unit17 = QLabel('元/吨', self)

        layout1.addWidget(self.label17, 7, 0)
        layout1.addWidget(self.input17, 7, 1)
        layout1.addWidget(self.unit17, 7, 2)

        layout1.addWidget(QLabel(self), 8, 0)

        self.calculate_button1 = CalculateButton('试算成本', self)
        self.result1 = ResultLabel(self)
        self.result_unit1 = QLabel('元/吨', self)
        layout1.addWidget(self.calculate_button1, 9, 0)
        layout1.addWidget(self.result1, 9, 1)
        layout1.addWidget(self.result_unit1, 9, 2)
        widget1.setLayout(layout1)
        self.init_calculate1()
        self.calculate_button1.clicked.connect(self.calculate1)
        main_layout.addWidget(widget1, alignment=Qt.AlignTop | Qt.AlignHCenter)

        """ 铝生产成本 """
        main_layout.addWidget(HorizonSepLine(self))

        widget2 = QWidget(self)
        widget2.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout2 = QGridLayout()
        layout2.setContentsMargins(QMargins(MARGIN_LEFT, MARGIN_TOP, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name2 = NameLabel('铝生产成本', self)
        self.label21 = QLabel('氧化铝价格', self)
        self.input21 = InputEdit(self)
        self.unit21 = QLabel('元/吨', self)

        layout2.addWidget(self.name2, 0, 0, 1, 3)
        layout2.addWidget(self.label21, 1, 0)
        layout2.addWidget(self.input21, 1, 1)
        layout2.addWidget(self.unit21, 1, 2)

        self.label22 = QLabel('冶炼电价', self)
        self.input22 = InputEdit(self)
        self.unit22 = QLabel('元/度', self)

        layout2.addWidget(self.label22, 2, 0)
        layout2.addWidget(self.input22, 2, 1)
        layout2.addWidget(self.unit22, 2, 2)

        self.label23 = QLabel('预焙阳极', self)
        self.input23 = InputEdit(self)
        self.unit23 = QLabel('元/吨', self)

        layout2.addWidget(self.label23, 3, 0)
        layout2.addWidget(self.input23, 3, 1)
        layout2.addWidget(self.unit23, 3, 2)

        self.label24 = QLabel('冰晶石', self)
        self.input24 = InputEdit(self)
        self.unit24 = QLabel('元/吨', self)

        layout2.addWidget(self.label24, 4, 0)
        layout2.addWidget(self.input24, 4, 1)
        layout2.addWidget(self.unit24, 4, 2)

        self.label25 = QLabel('干法氟化铝', self)
        self.input25 = InputEdit(self)
        self.unit25 = QLabel('元/吨', self)

        layout2.addWidget(self.label25, 5, 0)
        layout2.addWidget(self.input25, 5, 1)
        layout2.addWidget(self.unit25, 5, 2)

        self.label26 = QLabel('其他费用', self)
        self.input26 = InputEdit(self)
        self.unit26 = QLabel('元/吨', self)

        layout2.addWidget(self.label26, 6, 0)
        layout2.addWidget(self.input26, 6, 1)
        layout2.addWidget(self.unit26, 6, 2)

        layout2.addWidget(QLabel(self), 7, 0)

        self.calculate_button2 = CalculateButton('试算成本', self)
        self.result2 = ResultLabel(self)
        self.result_unit2 = QLabel('元/吨', self)
        layout2.addWidget(self.calculate_button2, 8, 0)
        layout2.addWidget(self.result2, 8, 1)
        layout2.addWidget(self.result_unit2, 8, 2)
        widget2.setLayout(layout2)
        self.init_calculate2()
        self.calculate_button2.clicked.connect(self.calculate2)
        main_layout.addWidget(widget2, alignment=Qt.AlignTop | Qt.AlignHCenter)
        self.setLayout(main_layout)

    def init_calculate1(self):
        if self.USD_CNY_RATE:
            self.input14.set_value(self.USD_CNY_RATE, count=4)
        self.input15.set_value(13)
        self.input16.set_value(0)
        self.input17.set_value(150)

    def init_calculate2(self):
        self.input22.set_value(0.325)
        self.input26.set_value(2000)

    def calculate1(self):
        # 计算铝进口成本
        # result = (a + b + c) * r * (1 + d) * (1 + e) + f
        # 铝进口成本=（LME三个月期货价格+现货升贴水+到岸升贴水）*汇率*（1+增值税率）*(1+关税税率)+港杂费
        a = self.input11.value()
        b = self.input12.value()
        c = self.input13.value()
        r = self.input14.value()
        d = self.input15.value(p=True)
        e = self.input16.value(p=True)
        f = self.input17.value()
        params = [a, b, c, r, d, e, f]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = (a + b + c) * r * (1 + d) * (1 + e) + f
        self.result1.set_value(result, count=4)

    def calculate2(self):
        # result = 1.93 * a + 13500 * b + 0.48 * c + 0.01 * d + 0.02 * e + f
        # 铝生产成本=1.93*氧化铝价格+13500*冶炼电价+0.48*预焙阳极+0.01*冰晶石+0.02*干法氟化铝+其他费用
        a = self.input21.value()
        b = self.input22.value()
        c = self.input23.value()
        d = self.input24.value()
        e = self.input25.value()
        f = self.input26.value()

        params = [a, b, c, d, e, f]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = 1.93 * a + 13500 * b + 0.48 * c + 0.01 * d + 0.02 * e + f
        self.result2.set_value(result, count=4)


class C(QWidget):
    RATE_DATA = rate.get_all_exchange_rate()

    def __init__(self, *args, **kwargs):
        super(C, self).__init__(*args, **kwargs)
        self.USD_CNY_RATE = self.RATE_DATA.get('USD/CNY', None)
        if self.USD_CNY_RATE:
            self.USD_CNY_RATE = float(self.USD_CNY_RATE)
        main_layout = QVBoxLayout()
        """ 玉米进口成本 """
        widget1 = QWidget(self)
        widget1.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout1 = QGridLayout()
        layout1.setContentsMargins(QMargins(MARGIN_LEFT, 0, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name1 = NameLabel('玉米进口成本', self)
        self.label11 = QLabel('CBOT玉米盘面价', self)
        self.input11 = InputEdit(self)
        self.unit11 = QLabel('美分/蒲式耳', self)

        layout1.addWidget(self.name1, 0, 0, 1, 3)
        layout1.addWidget(self.label11, 1, 0)
        layout1.addWidget(self.input11, 1, 1)
        layout1.addWidget(self.unit11, 1, 2)

        self.label12 = QLabel('FOB升贴水', self)
        self.input12 = InputEdit(self)
        self.unit12 = QLabel('美分/蒲式耳', self)

        layout1.addWidget(self.label12, 2, 0)
        layout1.addWidget(self.input12, 2, 1)
        layout1.addWidget(self.unit12, 2, 2)

        self.label13 = QLabel('海运费', self)
        self.input13 = InputEdit(self)
        self.unit13 = QLabel('美元/吨', self)

        layout1.addWidget(self.label13, 3, 0)
        layout1.addWidget(self.input13, 3, 1)
        layout1.addWidget(self.unit13, 3, 2)

        self.label14 = QLabel('增值税', self)
        self.input14 = InputEdit(self)
        self.unit14 = QLabel('%', self)

        layout1.addWidget(self.label14, 4, 0)
        layout1.addWidget(self.input14, 4, 1)
        layout1.addWidget(self.unit14, 4, 2)

        self.label15 = QLabel('关税', self)
        self.input15 = InputEdit(self)
        self.unit15 = QLabel('%', self)

        layout1.addWidget(self.label15, 5, 0)
        layout1.addWidget(self.input15, 5, 1)
        layout1.addWidget(self.unit15, 5, 2)

        self.label16 = QLabel('汇率', self)
        self.input16 = InputEdit(self)
        self.unit16 = QLabel('USD/CNY', self)

        layout1.addWidget(self.label16, 6, 0)
        layout1.addWidget(self.input16, 6, 1)
        layout1.addWidget(self.unit16, 6, 2)

        self.label17 = QLabel('港杂费', self)
        self.input17 = InputEdit(self)
        self.unit17 = QLabel('元/吨', self)

        layout1.addWidget(self.label17, 7, 0)
        layout1.addWidget(self.input17, 7, 1)
        layout1.addWidget(self.unit17, 7, 2)

        layout1.addWidget(QLabel(self), 8, 0)

        self.calculate_button1 = CalculateButton('试算成本', self)
        self.result1 = ResultLabel(self)
        self.result_unit1 = QLabel('元/吨', self)
        layout1.addWidget(self.calculate_button1, 8, 0)
        layout1.addWidget(self.result1, 8, 1)
        layout1.addWidget(self.result_unit1, 8, 2)
        widget1.setLayout(layout1)
        self.init_calculate1()
        self.calculate_button1.clicked.connect(self.calculate1)
        main_layout.addWidget(widget1, alignment=Qt.AlignTop | Qt.AlignHCenter)

        """ 玉米淀粉加工利润 """
        main_layout.addWidget(HorizonSepLine(self))

        widget2 = QWidget(self)
        widget2.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout2 = QGridLayout()
        layout2.setContentsMargins(QMargins(MARGIN_LEFT, MARGIN_TOP, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name2 = NameLabel('玉米淀粉加工利润', self)
        self.label21 = QLabel('淀粉现货价格', self)
        self.input21 = InputEdit(self)
        self.unit21 = QLabel('元/吨', self)

        layout2.addWidget(self.name2, 0, 0, 1, 3)
        layout2.addWidget(self.label21, 1, 0)
        layout2.addWidget(self.input21, 1, 1)
        layout2.addWidget(self.unit21, 1, 2)

        self.label22 = QLabel('蛋白粉现货价格', self)
        self.input22 = InputEdit(self)
        self.unit22 = QLabel('元/吨', self)

        layout2.addWidget(self.label22, 2, 0)
        layout2.addWidget(self.input22, 2, 1)
        layout2.addWidget(self.unit22, 2, 2)

        self.label23 = QLabel('胚芽现货价格', self)
        self.input23 = InputEdit(self)
        self.unit23 = QLabel('元/吨', self)

        layout2.addWidget(self.label23, 3, 0)
        layout2.addWidget(self.input23, 3, 1)
        layout2.addWidget(self.unit23, 3, 2)

        self.label24 = QLabel('纤维现货价格', self)
        self.input24 = InputEdit(self)
        self.unit24 = QLabel('元/吨', self)

        layout2.addWidget(self.label24, 4, 0)
        layout2.addWidget(self.input24, 4, 1)
        layout2.addWidget(self.unit24, 4, 2)

        self.label25 = QLabel('玉米现货价格', self)
        self.input25 = InputEdit(self)
        self.unit25 = QLabel('元/吨', self)

        layout2.addWidget(self.label25, 5, 0)
        layout2.addWidget(self.input25, 5, 1)
        layout2.addWidget(self.unit25, 5, 2)

        self.label26 = QLabel('加工费', self)
        self.input26 = InputEdit(self)
        self.unit26 = QLabel('元/吨', self)

        layout2.addWidget(self.label26, 6, 0)
        layout2.addWidget(self.input26, 6, 1)
        layout2.addWidget(self.unit26, 6, 2)

        layout2.addWidget(QLabel(self), 7, 0)
        self.calculate_button2 = CalculateButton('试算加工利润', self)
        self.result2 = ResultLabel(self)
        self.result_unit2 = QLabel('元/吨', self)
        layout2.addWidget(self.calculate_button2, 8, 0)
        layout2.addWidget(self.result2, 8, 1)
        layout2.addWidget(self.result_unit2, 8, 2)
        widget2.setLayout(layout2)
        self.init_calculate2()
        self.calculate_button2.clicked.connect(self.calculate2)
        main_layout.addWidget(widget2, alignment=Qt.AlignTop | Qt.AlignHCenter)
        self.setLayout(main_layout)

    def init_calculate1(self):
        if self.USD_CNY_RATE:
            self.input16.set_value(self.USD_CNY_RATE, count=4)
        self.input14.set_value(9)
        self.input15.set_value(1)
        self.input17.set_value(100)

    def init_calculate2(self):
        self.input26.set_value(500)

    def calculate1(self):
        # 玉米进口成本
        # result = ((a + b) * 0.393683 + c) * (1 + d) * (1 + e) * r + f
        # 玉米进口成本 =〔（CBOT期价＋FOB升贴水）×0.393683＋海运费〕×(1+增值税)×(1+关税)×汇率＋港杂费
        a = self.input11.value()
        b = self.input12.value()
        c = self.input13.value()
        d = self.input14.value(p=True)
        e = self.input15.value(p=True)
        r = self.input16.value()
        f = self.input17.value()
        params = [a, b, c, d,e, f, r]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = ((a + b) * 0.393683 + c) * (1 + d) * (1 + e) * r + f
        self.result1.set_value(result, count=4)

    def calculate2(self):
        # 玉米淀粉加工利润=（淀粉价格*0.7+玉米蛋白粉价格*0.05+玉米胚芽价格*0.07+玉米纤维价格*0.115）-玉米价格-加工费
        # result = (a * 0.7 + b * 0.05 + c * 0.07 + d * 0.115) - e - f
        a = self.input21.value()
        b = self.input22.value()
        c = self.input23.value()
        d = self.input24.value()
        e = self.input25.value()
        f = self.input26.value()
        params = [a, b, c, d, e, f]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = (a * 0.7 + b * 0.05 + c * 0.07 + d * 0.115) - e - f
        self.result2.set_value(result, count=4)


class CF(QWidget):

    RATE_DATA = rate.get_all_exchange_rate()

    def __init__(self, *args, **kwargs):
        super(CF, self).__init__(*args, **kwargs)
        self.USD_CNY_RATE = self.RATE_DATA.get('USD/CNY', None)
        if self.USD_CNY_RATE:
            self.USD_CNY_RATE = float(self.USD_CNY_RATE)
        main_layout = QVBoxLayout()
        """ 皮棉价格 """
        widget1 = QWidget(self)
        widget1.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout1 = QGridLayout()
        layout1.setContentsMargins(QMargins(MARGIN_LEFT, 0, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name1 = NameLabel('皮棉价格', self)
        self.label11 = QLabel('衣分率', self)
        self.input11 = InputEdit(self)
        self.unit11 = QLabel('%', self)

        layout1.addWidget(self.name1, 0, 0, 1, 3)
        layout1.addWidget(self.label11, 1, 0)
        layout1.addWidget(self.input11, 1, 1)
        layout1.addWidget(self.unit11, 1, 2)

        self.label12 = QLabel('棉籽价格', self)
        self.input12 = InputEdit(self)
        self.unit12 = QLabel('元/斤', self)

        layout1.addWidget(self.label12, 2, 0)
        layout1.addWidget(self.input12, 2, 1)
        layout1.addWidget(self.unit12, 2, 2)

        self.label13 = QLabel('籽棉价格', self)
        self.input13 = InputEdit(self)
        self.unit13 = QLabel('元/斤', self)

        layout1.addWidget(self.label13, 3, 0)
        layout1.addWidget(self.input13, 3, 1)
        layout1.addWidget(self.unit13, 3, 2)

        layout1.addWidget(QLabel(self), 4, 0)

        self.calculate_button1 = CalculateButton('试算价格', self)
        self.result1 = ResultLabel(self)
        self.result_unit1 = QLabel('元/吨', self)
        layout1.addWidget(self.calculate_button1, 5, 0)
        layout1.addWidget(self.result1, 5, 1)
        layout1.addWidget(self.result_unit1, 5, 2)
        widget1.setLayout(layout1)
        self.init_calculate1()
        self.calculate_button1.clicked.connect(self.calculate1)
        main_layout.addWidget(widget1, alignment=Qt.AlignTop | Qt.AlignHCenter)

        """ 皮棉成本计算 """
        widget2 = QWidget(self)
        widget2.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout2 = QGridLayout()
        layout2.setContentsMargins(QMargins(MARGIN_LEFT, 0, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name2 = NameLabel('皮棉成本计算', self)
        self.label21 = QLabel('衣分率', self)
        self.input21 = InputEdit(self)
        self.unit21 = QLabel('%', self)

        layout2.addWidget(self.name2, 0, 0, 1, 3)
        layout2.addWidget(self.label21, 1, 0)
        layout2.addWidget(self.input21, 1, 1)
        layout2.addWidget(self.unit21, 1, 2)

        self.label22 = QLabel('籽棉单价', self)
        self.input22 = InputEdit(self)
        self.unit22 = QLabel('元/斤', self)

        layout2.addWidget(self.label22, 2, 0)
        layout2.addWidget(self.input22, 2, 1)
        layout2.addWidget(self.unit22, 2, 2)

        self.label23 = QLabel('耗损率', self)
        self.input23 = InputEdit(self)
        self.unit23 = QLabel('%', self)

        layout2.addWidget(self.label23, 3, 0)
        layout2.addWidget(self.input23, 3, 1)
        layout2.addWidget(self.unit23, 3, 2)

        self.label24 = QLabel('购进棉籽单价', self)
        self.input24 = InputEdit(self)
        self.unit24 = QLabel('元/斤', self)

        layout2.addWidget(self.label24, 4, 0)
        layout2.addWidget(self.input24, 4, 1)
        layout2.addWidget(self.unit24, 4, 2)

        self.label25 = QLabel('购进数量', self)
        self.input25 = InputEdit(self)
        self.unit25 = QLabel('斤', self)

        layout2.addWidget(self.label25, 5, 0)
        layout2.addWidget(self.input25, 5, 1)
        layout2.addWidget(self.unit25, 5, 2)

        # self.label26 = QLabel('收购价格', self)
        # self.input26 = InputEdit(self)
        # self.unit26 = QLabel('元/斤', self)
        #
        # layout2.addWidget(self.label26, 6, 0)
        # layout2.addWidget(self.input26, 6, 1)
        # layout2.addWidget(self.unit26, 6, 2)

        layout2.addWidget(QLabel(self), 7, 0)

        self.calculate_button2 = CalculateButton('试算成本', self)
        self.result2 = ResultLabel(self)
        self.result_unit2 = QLabel('元/吨', self)
        layout2.addWidget(self.calculate_button2, 8, 0)
        layout2.addWidget(self.result2, 8, 1)
        layout2.addWidget(self.result_unit2, 8, 2)
        widget2.setLayout(layout2)
        self.init_calculate2()
        self.calculate_button2.clicked.connect(self.calculate2)
        main_layout.addWidget(widget2, alignment=Qt.AlignTop | Qt.AlignHCenter)

        """ 进口棉花配额内成本测算 """
        widget3 = QWidget(self)
        widget3.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout3 = QGridLayout()
        layout3.setContentsMargins(QMargins(MARGIN_LEFT, 0, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name3 = NameLabel('进口棉花配额内成本测算', self)
        self.label31 = QLabel('NYBOT棉花CNF报价', self)
        self.input31 = InputEdit(self)
        self.unit31 = QLabel('美分/磅', self)

        layout3.addWidget(self.name3, 0, 0, 1, 3)
        layout3.addWidget(self.label31, 1, 0)
        layout3.addWidget(self.input31, 1, 1)
        layout3.addWidget(self.unit31, 1, 2)

        self.label32 = QLabel('海运保险费率', self)
        self.input32 = InputEdit(self)
        self.unit32 = QLabel('%', self)

        layout3.addWidget(self.label32, 2, 0)
        layout3.addWidget(self.input32, 2, 1)
        layout3.addWidget(self.unit32, 2, 2)

        self.label33 = QLabel('进口代理费率', self)
        self.input33 = InputEdit(self)
        self.unit33 = QLabel('%', self)

        layout3.addWidget(self.label33, 3, 0)
        layout3.addWidget(self.input33, 3, 1)
        layout3.addWidget(self.unit33, 3, 2)

        self.label34 = QLabel('关税税率', self)
        self.input34 = InputEdit(self)
        self.unit34 = QLabel('元/斤', self)

        layout3.addWidget(self.label34, 4, 0)
        layout3.addWidget(self.input34, 4, 1)
        layout3.addWidget(self.unit34, 4, 2)

        self.label35 = QLabel('汇率', self)
        self.input35 = InputEdit(self)
        self.unit35 = QLabel('USD/CNY', self)

        layout3.addWidget(self.label35, 5, 0)
        layout3.addWidget(self.input35, 5, 1)
        layout3.addWidget(self.unit35, 5, 2)

        self.label36 = QLabel('增值税率', self)
        self.input36 = InputEdit(self)
        self.unit36 = QLabel('%', self)

        layout3.addWidget(self.label36, 6, 0)
        layout3.addWidget(self.input36, 6, 1)
        layout3.addWidget(self.unit36, 6, 2)

        # self.label26 = QLabel('收购价格', self)
        # self.input26 = InputEdit(self)
        # self.unit26 = QLabel('元/斤', self)
        #
        # layout2.addWidget(self.label26, 6, 0)
        # layout2.addWidget(self.input26, 6, 1)
        # layout2.addWidget(self.unit26, 6, 2)

        layout3.addWidget(QLabel(self), 7, 0)

        self.calculate_button3 = CalculateButton('试算成本', self)
        self.result3 = ResultLabel(self)
        self.result_unit3 = QLabel('元/吨', self)
        layout3.addWidget(self.calculate_button3, 8, 0)
        layout3.addWidget(self.result3, 8, 1)
        layout3.addWidget(self.result_unit3, 8, 2)
        widget3.setLayout(layout3)
        self.init_calculate3()
        self.calculate_button3.clicked.connect(self.calculate3)
        main_layout.addWidget(widget3, alignment=Qt.AlignTop | Qt.AlignHCenter)

        self.setLayout(main_layout)

    def init_calculate1(self):
        self.input11.set_value(38)

    def init_calculate2(self):
        self.input21.set_value(38)
        self.input23.set_value(1)
        self.input25.set_value(1)

    def init_calculate3(self):
        if self.USD_CNY_RATE:
            self.input35.set_value(self.USD_CNY_RATE)
        self.input32.set_value(0.2)
        self.input33.set_value(1)
        self.input34.set_value(1)
        self.input36.set_value(13)

    def calculate1(self):
        # result = (a -b * (1 - c - 0.01)) / (c - 0.01) * 2000
        # 皮棉价格=(籽棉价格-棉籽价格 x(1-衣分率-0.01))÷(衣分率-0.01)X2000
        a = self.input13.value()
        b = self.input12.value()
        c = self.input11.value(p=True)
        params = [a, b, c]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = (a -b * (1 - c - 0.01)) / (c - 0.01) * 2000
        self.result1.set_value(result, count=4)

    def calculate2(self):
        ## 收购价格 =  (籽棉价格-棉籽价格 x (1-衣分-0.01))÷(衣分- 0.01) x 2000
        # 购进籽棉成本＝购进数量×籽棉单价
        # 棉籽成本＝（1－衣分率－损耗率）×购进棉籽单价
        # 每吨皮棉成本＝（购进籽棉成本－其中的棉籽成本） / 衣分率 ×100 ×200
        # 每吨皮棉成本＝（ 购进数量×籽棉单价 － （1－衣分率－损耗率）×购进棉籽单价 ）/ 衣分率 ×100 ×20
        # result = (a * b - (1 - c -d) * e) / c * 100 * 20
        a = self.input25.value()
        b = self.input22.value()
        c = self.input21.value(p=True)
        d = self.input23.value(p=True)
        e = self.input24.value()
        params = [a, b, c, d, e]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = (a * b - (1 - c - d) * e) / c * 2000
        self.result2.set_value(result, count=4)

    def calculate3(self):
        # 配额内成本 ＝ 外棉报价（美分/磅）× 22.0462×汇率 x (1+税率) x (1+增值税）
        # result = a * 22.0462 * r * (1 + b) * (1 + c)
        a = self.input31.value()
        r = self.input35.value()
        b = self.input34.value(p=True)
        c = self.input36.value(p=True)
        params = [a, b, c, r]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = a * 22.0462 * r * (1 + b) * (1 + c)
        self.result3.set_value(result, count=4)


class CU(QWidget):
    RATE_DATA = rate.get_all_exchange_rate()

    def __init__(self, *args, **kwargs):
        super(CU, self).__init__(*args, **kwargs)
        self.USD_CNY_RATE = self.RATE_DATA.get('USD/CNY', None)
        if self.USD_CNY_RATE:
            self.USD_CNY_RATE = float(self.USD_CNY_RATE)
        main_layout = QVBoxLayout()
        """ 铜进口成本 """
        widget1 = QWidget(self)
        widget1.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout1 = QGridLayout()
        layout1.setContentsMargins(QMargins(MARGIN_LEFT, 0, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name1 = NameLabel('铜进口成本', self)
        self.label11 = QLabel('LME三个月期货价', self)
        self.input11 = InputEdit(self)
        self.unit11 = QLabel('美元/吨', self)

        layout1.addWidget(self.name1, 0, 0, 1, 3)
        layout1.addWidget(self.label11, 1, 0)
        layout1.addWidget(self.input11, 1, 1)
        layout1.addWidget(self.unit11, 1, 2)

        self.label12 = QLabel('LME铜升贴水', self)
        self.input12 = InputEdit(self)
        self.unit12 = QLabel('美元/吨', self)

        layout1.addWidget(self.label12, 2, 0)
        layout1.addWidget(self.input12, 2, 1)
        layout1.addWidget(self.unit12, 2, 2)

        self.label13 = QLabel('CIF到岸升贴水', self)
        self.input13 = InputEdit(self)
        self.unit13 = QLabel('美元/吨', self)

        layout1.addWidget(self.label13, 3, 0)
        layout1.addWidget(self.input13, 3, 1)
        layout1.addWidget(self.unit13, 3, 2)

        self.label14 = QLabel('汇率', self)
        self.input14 = InputEdit(self)
        self.unit14 = QLabel('USD/CNY', self)

        layout1.addWidget(self.label14, 4, 0)
        layout1.addWidget(self.input14, 4, 1)
        layout1.addWidget(self.unit14, 4, 2)

        self.label15 = QLabel('增值税率', self)
        self.input15 = InputEdit(self)
        self.unit15 = QLabel('%', self)

        layout1.addWidget(self.label15, 5, 0)
        layout1.addWidget(self.input15, 5, 1)
        layout1.addWidget(self.unit15, 5, 2)

        self.label16 = QLabel('关税税率', self)
        self.input16 = InputEdit(self)
        self.unit16 = QLabel('%', self)

        layout1.addWidget(self.label16, 6, 0)
        layout1.addWidget(self.input16, 6, 1)
        layout1.addWidget(self.unit16, 6, 2)

        self.label17 = QLabel('港杂费', self)
        self.input17 = InputEdit(self)
        self.unit17 = QLabel('元/吨', self)

        layout1.addWidget(self.label17, 7, 0)
        layout1.addWidget(self.input17, 7, 1)
        layout1.addWidget(self.unit17, 7, 2)

        layout1.addWidget(QLabel(self), 8, 0)

        self.calculate_button1 = CalculateButton('试算成本', self)
        self.result1 = ResultLabel(self)
        self.result_unit1 = QLabel('元/吨', self)
        layout1.addWidget(self.calculate_button1, 9, 0)
        layout1.addWidget(self.result1, 9, 1)
        layout1.addWidget(self.result_unit1, 9, 2)
        widget1.setLayout(layout1)
        self.init_calculate1()
        self.calculate_button1.clicked.connect(self.calculate1)
        main_layout.addWidget(widget1, alignment=Qt.AlignTop | Qt.AlignHCenter)

        """ 铜生产成本 """
        main_layout.addWidget(HorizonSepLine(self))

        widget2 = QWidget(self)
        widget2.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout2 = QGridLayout()
        layout2.setContentsMargins(QMargins(MARGIN_LEFT, MARGIN_TOP, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name2 = NameLabel('铜生产成本', self)
        self.label21 = QLabel('LME三个月期货价', self)
        self.input21 = InputEdit(self)
        self.unit21 = QLabel('美元/吨', self)

        layout2.addWidget(self.name2, 0, 0, 1, 3)
        layout2.addWidget(self.label21, 1, 0)
        layout2.addWidget(self.input21, 1, 1)
        layout2.addWidget(self.unit21, 1, 2)

        self.label22 = QLabel('TC', self)
        self.input22 = InputEdit(self)
        self.unit22 = QLabel('美元/吨', self)

        layout2.addWidget(self.label22, 2, 0)
        layout2.addWidget(self.input22, 2, 1)
        layout2.addWidget(self.unit22, 2, 2)

        self.label23 = QLabel('RC', self)
        self.input23 = InputEdit(self)
        self.unit23 = QLabel('美元/吨', self)

        layout2.addWidget(self.label23, 3, 0)
        layout2.addWidget(self.input23, 3, 1)
        layout2.addWidget(self.unit23, 3, 2)

        self.label24 = QLabel('汇率', self)
        self.input24 = InputEdit(self)
        self.unit24 = QLabel('USD/CNY', self)

        layout2.addWidget(self.label24, 4, 0)
        layout2.addWidget(self.input24, 4, 1)
        layout2.addWidget(self.unit24, 4, 2)

        self.label25 = QLabel('铜矿品味', self)
        self.input25 = InputEdit(self)
        self.unit25 = QLabel('%', self)

        layout2.addWidget(self.label25, 5, 0)
        layout2.addWidget(self.input25, 5, 1)
        layout2.addWidget(self.unit25, 5, 2)

        self.label26 = QLabel('回收率', self)
        self.input26 = InputEdit(self)
        self.unit26 = QLabel('%', self)

        layout2.addWidget(self.label26, 6, 0)
        layout2.addWidget(self.input26, 6, 1)
        layout2.addWidget(self.unit26, 6, 2)

        self.label27 = QLabel('冶炼加工费', self)
        self.input27 = InputEdit(self)
        self.unit27 = QLabel('元/吨', self)

        layout2.addWidget(self.label27, 7, 0)
        layout2.addWidget(self.input27, 7, 1)
        layout2.addWidget(self.unit27, 7, 2)

        layout2.addWidget(QLabel(self), 8, 0)

        self.calculate_button2 = CalculateButton('试算成本', self)
        self.result2 = ResultLabel(self)
        self.result_unit2 = QLabel('元/吨', self)
        layout2.addWidget(self.calculate_button2, 9, 0)
        layout2.addWidget(self.result2, 9, 1)
        layout2.addWidget(self.result_unit2, 9, 2)
        widget2.setLayout(layout2)
        self.init_calculate2()
        self.calculate_button2.clicked.connect(self.calculate2)
        main_layout.addWidget(widget2, alignment=Qt.AlignTop | Qt.AlignHCenter)
        self.setLayout(main_layout)

    def init_calculate1(self):
        if self.USD_CNY_RATE:
            self.input14.set_value(self.USD_CNY_RATE, count=4)
        self.input15.set_value(13)
        self.input16.set_value(0)
        self.input17.set_value(150)

    def init_calculate2(self):
        if self.USD_CNY_RATE:
            self.input24.set_value(self.USD_CNY_RATE, count=4)
        self.input25.set_value(25.3)
        self.input26.set_value(96.5)
        self.input27.set_value(6000)

    def calculate1(self):
        # 计算铜进口成本
        # result = (a + b + c) * r * (1 + d) * (1 + e) + f
        # 铜进口成本=（LME三个月期货价格+现货升贴水+到岸升贴水）*汇率*（1+增值税率）*(1+关税税率)+港杂费
        a = self.input11.value()
        b = self.input12.value()
        c = self.input13.value()
        r = self.input14.value()
        d = self.input15.value(p=True)
        e = self.input16.value(p=True)
        f = self.input17.value()
        params = [a, b, c, r, d, e, f]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = (a + b + c) * r * (1 + d) * (1 + e) + f
        self.result1.set_value(result, count=4)

    def calculate2(self):
        # result = (a - (tc/(b * c + rc * 22.0462))) * r + d
        # 铜生产成本=(LME三月期价格-(TC/(铜矿品味*回收率+RC*22.0462))*汇率+冶炼加工费
        a = self.input21.value()
        tc = self.input22.value()
        b = self.input25.value(p=True)
        c = self.input26.value(p=True)
        rc = self.input23.value()
        r = self.input24.value()
        d = self.input27.value()
        params = [a, tc, b, c, rc, r, d]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = (a - (tc / (b * c + rc * 22.0462))) * r + d
        self.result2.set_value(result, count=4)


class CJ(QWidget):

    RATE_DATA = rate.get_all_exchange_rate()

    def __init__(self, *args, **kwargs):
        super(CJ, self).__init__(*args, **kwargs)
        self.USD_CNY_RATE = self.RATE_DATA.get('USD/CNY', None)
        if self.USD_CNY_RATE:
            self.USD_CNY_RATE = float(self.USD_CNY_RATE)
        main_layout = QVBoxLayout()
        """ 红枣成本价格测算 """
        widget1 = QWidget(self)
        widget1.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout1 = QGridLayout()
        layout1.setContentsMargins(QMargins(MARGIN_LEFT, 0, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name1 = NameLabel('红枣成本价格测算', self)
        self.label11 = QLabel('沧州红枣价格', self)
        self.input11 = InputEdit(self)
        self.unit11 = QLabel('元/吨', self)

        layout1.addWidget(self.name1, 0, 0, 1, 3)
        layout1.addWidget(self.label11, 1, 0)
        layout1.addWidget(self.input11, 1, 1)
        layout1.addWidget(self.unit11, 1, 2)

        self.label12 = QLabel('加工费', self)
        self.input12 = InputEdit(self)
        self.unit12 = QLabel('元/吨', self)

        layout1.addWidget(self.label12, 2, 0)
        layout1.addWidget(self.input12, 2, 1)
        layout1.addWidget(self.unit12, 2, 2)

        layout1.addWidget(QLabel(self), 3, 0)

        self.calculate_button1 = CalculateButton('试算成本', self)
        self.result1 = ResultLabel(self)
        self.result_unit1 = QLabel('元/吨', self)
        layout1.addWidget(self.calculate_button1, 15, 0)
        layout1.addWidget(self.result1, 15, 1)
        layout1.addWidget(self.result_unit1, 15, 2)
        widget1.setLayout(layout1)
        self.init_calculate1()
        self.calculate_button1.clicked.connect(self.calculate1)
        main_layout.addWidget(widget1, alignment=Qt.AlignTop | Qt.AlignHCenter)

        self.setLayout(main_layout)

    def init_calculate1(self):
        self.input12.set_value(400)

    def calculate1(self):
        """
        成本公式=沧州价格+加工费
        """
        a = self.input11.value()
        b = self.input12.value()
        params = [a, b]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        self.result1.set_value(a + b, count=4)


class EB(QWidget):
    RATE_DATA = rate.get_all_exchange_rate()

    def __init__(self, *args, **kwargs):
        super(EB, self).__init__(*args, **kwargs)
        self.USD_CNY_RATE = self.RATE_DATA.get('USD/CNY', None)
        if self.USD_CNY_RATE:
            self.USD_CNY_RATE = float(self.USD_CNY_RATE)
        main_layout = QVBoxLayout()
        """ 苯乙烯进口成本 """
        widget1 = QWidget(self)
        widget1.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout1 = QGridLayout()
        layout1.setContentsMargins(QMargins(MARGIN_LEFT, 0, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name1 = NameLabel('苯乙烯进口成本', self)
        self.label11 = QLabel('CFR中国', self)
        self.input11 = InputEdit(self)
        self.unit11 = QLabel('美元/吨', self)

        layout1.addWidget(self.name1, 0, 0, 1, 3)
        layout1.addWidget(self.label11, 1, 0)
        layout1.addWidget(self.input11, 1, 1)
        layout1.addWidget(self.unit11, 1, 2)

        self.label12 = QLabel('汇率', self)
        self.input12 = InputEdit(self)
        self.unit12 = QLabel('USD/CNY', self)

        layout1.addWidget(self.label12, 2, 0)
        layout1.addWidget(self.input12, 2, 1)
        layout1.addWidget(self.unit12, 2, 2)

        self.label13 = QLabel('关税', self)
        self.input13 = InputEdit(self)
        self.unit13 = QLabel('%', self)

        layout1.addWidget(self.label13, 3, 0)
        layout1.addWidget(self.input13, 3, 1)
        layout1.addWidget(self.unit13, 3, 2)

        self.label14 = QLabel('增值税', self)
        self.input14 = InputEdit(self)
        self.unit14 = QLabel('%', self)

        layout1.addWidget(self.label14, 4, 0)
        layout1.addWidget(self.input14, 4, 1)
        layout1.addWidget(self.unit14, 4, 2)

        layout1.addWidget(QLabel(self), 5, 0)

        self.calculate_button1 = CalculateButton('试算成本', self)
        self.result1 = ResultLabel(self)
        self.result_unit1 = QLabel('元/吨', self)
        layout1.addWidget(self.calculate_button1, 6, 0)
        layout1.addWidget(self.result1, 6, 1)
        layout1.addWidget(self.result_unit1, 6, 2)
        widget1.setLayout(layout1)
        self.init_calculate1()
        self.calculate_button1.clicked.connect(self.calculate1)
        main_layout.addWidget(widget1, alignment=Qt.AlignTop | Qt.AlignHCenter)

        """ 苯乙烯生产成本 """
        main_layout.addWidget(HorizonSepLine(self))

        widget2 = QWidget(self)
        widget2.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout2 = QGridLayout()
        layout2.setContentsMargins(QMargins(MARGIN_LEFT, MARGIN_TOP, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name2 = NameLabel('苯乙烯生产成本', self)
        self.label21 = QLabel('CFR乙烯', self)
        self.input21 = InputEdit(self)
        self.unit21 = QLabel('美元/吨', self)

        layout2.addWidget(self.name2, 0, 0, 1, 3)
        layout2.addWidget(self.label21, 1, 0)
        layout2.addWidget(self.input21, 1, 1)
        layout2.addWidget(self.unit21, 1, 2)

        self.label22 = QLabel('CFR纯苯', self)
        self.input22 = InputEdit(self)
        self.unit22 = QLabel('美元/吨', self)

        layout2.addWidget(self.label22, 2, 0)
        layout2.addWidget(self.input22, 2, 1)
        layout2.addWidget(self.unit22, 2, 2)

        self.label23 = QLabel('汇率', self)
        self.input23 = InputEdit(self)
        self.unit23 = QLabel('USD/CNY', self)

        layout2.addWidget(self.label23, 3, 0)
        layout2.addWidget(self.input23, 3, 1)
        layout2.addWidget(self.unit23, 3, 2)

        self.label24 = QLabel('杂费', self)
        self.input24 = InputEdit(self)
        self.unit24 = QLabel('元/吨', self)

        layout2.addWidget(self.label24, 4, 0)
        layout2.addWidget(self.input24, 4, 1)
        layout2.addWidget(self.unit24, 4, 2)

        layout2.addWidget(QLabel(self), 5, 0)
        self.calculate_button2 = CalculateButton('试算成本', self)
        self.result2 = ResultLabel(self)
        self.result_unit2 = QLabel('元/吨', self)
        layout2.addWidget(self.calculate_button2, 6, 0)
        layout2.addWidget(self.result2, 6, 1)
        layout2.addWidget(self.result_unit2, 6, 2)
        widget2.setLayout(layout2)
        self.init_calculate2()
        self.calculate_button2.clicked.connect(self.calculate2)
        main_layout.addWidget(widget2, alignment=Qt.AlignTop | Qt.AlignHCenter)

        self.setLayout(main_layout)

    def init_calculate1(self):
        if self.USD_CNY_RATE:
            self.input12.set_value(self.USD_CNY_RATE, count=4)
        self.input13.set_value(6.5)
        self.input14.set_value(13)

    def init_calculate2(self):
        if self.USD_CNY_RATE:
            self.input23.set_value(self.USD_CNY_RATE, count=4)
        self.input24.set_value(1500)

    def calculate1(self):
        # 苯乙烯进口成本=CFR中国*汇率*关税*增值税
        # result = a * r *(1 + b) * (1 + c)
        a = self.input11.value()
        r = self.input12.value()
        b = self.input13.value(p=True)
        c = self.input14.value(p=True)

        params = [a, b, c, r]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = a * r *(1 + b) * (1 + c)
        self.result1.set_value(result, count=4)

    def calculate2(self):
        # （CFR乙烯*0.29+CFR纯苯*0.79）*汇率+杂费
        # result = (a * 0.29 + b * 0.79) * r + c
        a = self.input21.value()
        b = self.input22.value()
        r = self.input23.value()
        c = self.input24.value()

        params = [a, b, c, r]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = (a * 0.29 + b * 0.79) * r + c
        self.result2.set_value(result, count=4)


class EG(QWidget):
    RATE_DATA = rate.get_all_exchange_rate()

    def __init__(self, *args, **kwargs):
        super(EG, self).__init__(*args, **kwargs)
        self.USD_CNY_RATE = self.RATE_DATA.get('USD/CNY', None)
        if self.USD_CNY_RATE:
            self.USD_CNY_RATE = float(self.USD_CNY_RATE)
        main_layout = QVBoxLayout()
        """ 乙二醇到港成本 """
        widget1 = QWidget(self)
        widget1.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout1 = QGridLayout()
        layout1.setContentsMargins(QMargins(MARGIN_LEFT, 0, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name1 = NameLabel('乙二醇到港成本', self)
        self.label11 = QLabel('布伦特原油收盘价', self)
        self.input11 = InputEdit(self)
        self.unit11 = QLabel('美元/吨', self)

        layout1.addWidget(self.name1, 0, 0, 1, 3)
        layout1.addWidget(self.label11, 1, 0)
        layout1.addWidget(self.input11, 1, 1)
        layout1.addWidget(self.unit11, 1, 2)

        self.label12 = QLabel('石脑加工费', self)
        self.input12 = InputEdit(self)
        self.unit12 = QLabel('美元/吨', self)

        layout1.addWidget(self.label12, 2, 0)
        layout1.addWidget(self.input12, 2, 1)
        layout1.addWidget(self.unit12, 2, 2)

        self.label13 = QLabel('乙二醇加工费', self)
        self.input13 = InputEdit(self)
        self.unit13 = QLabel('美元/吨', self)

        layout1.addWidget(self.label13, 3, 0)
        layout1.addWidget(self.input13, 3, 1)
        layout1.addWidget(self.unit13, 3, 2)

        self.label14 = QLabel('增值税', self)
        self.input14 = InputEdit(self)
        self.unit14 = QLabel('%', self)

        layout1.addWidget(self.label14, 4, 0)
        layout1.addWidget(self.input14, 4, 1)
        layout1.addWidget(self.unit14, 4, 2)

        self.label15 = QLabel('关税', self)
        self.input15 = InputEdit(self)
        self.unit15 = QLabel('%', self)

        layout1.addWidget(self.label15, 5, 0)
        layout1.addWidget(self.input15, 5, 1)
        layout1.addWidget(self.unit15, 5, 2)

        self.label16 = QLabel('汇率', self)
        self.input16 = InputEdit(self)
        self.unit16 = QLabel('USD/CNY', self)

        layout1.addWidget(self.label16, 6, 0)
        layout1.addWidget(self.input16, 6, 1)
        layout1.addWidget(self.unit16, 6, 2)

        self.label17 = QLabel('港杂费', self)
        self.input17 = InputEdit(self)
        self.unit17 = QLabel('元/吨', self)

        layout1.addWidget(self.label17, 7, 0)
        layout1.addWidget(self.input17, 7, 1)
        layout1.addWidget(self.unit17, 7, 2)

        layout1.addWidget(QLabel(self), 8, 0)

        self.calculate_button1 = CalculateButton('试算成本', self)
        self.result1 = ResultLabel(self)
        self.result_unit1 = QLabel('元/吨', self)
        layout1.addWidget(self.calculate_button1, 9, 0)
        layout1.addWidget(self.result1, 9, 1)
        layout1.addWidget(self.result_unit1, 9, 2)
        widget1.setLayout(layout1)
        self.init_calculate1()
        self.calculate_button1.clicked.connect(self.calculate1)
        main_layout.addWidget(widget1, alignment=Qt.AlignTop | Qt.AlignHCenter)

        self.setLayout(main_layout)

    def init_calculate1(self):
        if self.USD_CNY_RATE:
            self.input16.set_value(self.USD_CNY_RATE, count=4)
        self.input12.set_value(50)
        self.input13.set_value(350)
        self.input14.set_value(13)
        self.input15.set_value(5.5)
        self.input17.set_value(75)

    def calculate1(self):
        # 乙二醇到港成本=[（布伦特原油收盘价×7.35）+石脑油加工费+乙二醇加工费]×汇率×（1+增值税）×（1+关税）+港杂费
        # result = (a * 7.35 + b + c) * r * (1 + d) * (1 + e) + f
        a = self.input11.value()
        b = self.input12.value()
        c = self.input13.value()
        d = self.input14.value(p=True)
        e = self.input15.value(p=True)
        f = self.input17.value()
        r = self.input16.value()
        params = [a, b, c, d, e,f, r]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = (a * 7.35 + b + c) * r * (1 + d) * (1 + e) + f
        self.result1.set_value(result, count=4)


class FU(QWidget):
    RATE_DATA = rate.get_all_exchange_rate()

    def __init__(self, *args, **kwargs):
        super(FU, self).__init__(*args, **kwargs)
        self.USD_CNY_RATE = self.RATE_DATA.get('USD/CNY', None)
        if self.USD_CNY_RATE:
            self.USD_CNY_RATE = float(self.USD_CNY_RATE)
        main_layout = QVBoxLayout()
        """ 进口保税燃料油成本 """
        widget1 = QWidget(self)
        widget1.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout1 = QGridLayout()
        layout1.setContentsMargins(QMargins(MARGIN_LEFT, 0, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name1 = NameLabel('进口保税燃料油成本', self)
        self.label11 = QLabel('MOPS价格', self)
        self.input11 = InputEdit(self)
        self.unit11 = QLabel('美元/吨', self)

        layout1.addWidget(self.name1, 0, 0, 1, 3)
        layout1.addWidget(self.label11, 1, 0)
        layout1.addWidget(self.input11, 1, 1)
        layout1.addWidget(self.unit11, 1, 2)

        self.label12 = QLabel('升贴水', self)
        self.input12 = InputEdit(self)
        self.unit12 = QLabel('美元/吨', self)

        layout1.addWidget(self.label12, 2, 0)
        layout1.addWidget(self.input12, 2, 1)
        layout1.addWidget(self.unit12, 2, 2)

        self.label13 = QLabel('汇率', self)
        self.input13 = InputEdit(self)
        self.unit13 = QLabel('USD/CNY', self)

        layout1.addWidget(self.label13, 3, 0)
        layout1.addWidget(self.input13, 3, 1)
        layout1.addWidget(self.unit13, 3, 2)

        self.label14 = QLabel('其他费用', self)
        self.input14 = InputEdit(self)
        self.unit14 = QLabel('元/吨', self)

        layout1.addWidget(self.label14, 4, 0)
        layout1.addWidget(self.input14, 4, 1)
        layout1.addWidget(self.unit14, 4, 2)

        layout1.addWidget(QLabel(self), 5, 0)

        self.calculate_button1 = CalculateButton('试算成本', self)
        self.result1 = ResultLabel(self)
        self.result_unit1 = QLabel('元/吨', self)
        layout1.addWidget(self.calculate_button1, 6, 0)
        layout1.addWidget(self.result1, 6, 1)
        layout1.addWidget(self.result_unit1, 6, 2)
        widget1.setLayout(layout1)
        self.init_calculate1()
        self.calculate_button1.clicked.connect(self.calculate1)
        main_layout.addWidget(widget1, alignment=Qt.AlignTop | Qt.AlignHCenter)

        self.setLayout(main_layout)

    def init_calculate1(self):
        if self.USD_CNY_RATE:
            self.input13.set_value(self.USD_CNY_RATE, count=4)
        self.input14.set_value(90)

    def calculate1(self):
        # 进口保税燃料油成本=(MOPS价格+贴水)×汇率+其他费用
        # result = (a + b) * r + c
        a = self.input11.value()
        b = self.input12.value()
        r = self.input13.value()
        c = self.input14.value()

        params = [a, b, c, r]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = (a + b) * r + c
        self.result1.set_value(result, count=4)


class GZ(QWidget):  # 国债
    def __init__(self, *args, **kwargs):
        super(GZ, self).__init__(*args, **kwargs)
        main_layout = QVBoxLayout()
        """ 可交割国债转换因子 """
        widget1 = QWidget(self)
        widget1.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout1 = QGridLayout()
        layout1.setContentsMargins(QMargins(MARGIN_LEFT, 0, MARGIN_RIGHT, MARGIN_BOTTOM))
        layout1.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.name1 = NameLabel('可交割国债转换因子', self)

        self.label11 = QLabel('10年国债期货票面利率', self)
        self.input11 = InputEdit('3', self)  # r
        self.unit11 = QLabel('%', self)

        self.label12 = QLabel('可交割国债交割月', self)
        self.input12 = DateEdit(self)  # m1
        self.unit12 = QLabel(self)

        self.label13 = QLabel('下一付息月', self)
        self.input13 = DateEdit(self)  # m2
        self.unit13 = QLabel(self)

        self.label14 = QLabel('可交割国债票面利率', self)
        self.input14 = InputEdit(self)  # c
        self.unit14 = QLabel('%', self)

        self.label15 = QLabel('可交割国债每年付息次数', self)
        self.input15 = InputEdit(self)  # f
        self.unit15 = QLabel(self)

        self.label16 = QLabel('可交割国债剩余付息次数', self)
        self.input16 = InputEdit(self)  # n
        self.unit16 = QLabel(self)

        layout1.addWidget(self.name1, 0, 0, 1, 3)
        layout1.addWidget(self.label11, 1, 0)
        layout1.addWidget(self.input11, 1, 1)
        layout1.addWidget(self.unit11, 1, 2)
        layout1.addWidget(self.label12, 2, 0)
        layout1.addWidget(self.input12, 2, 1)
        layout1.addWidget(self.unit12, 2, 2)
        layout1.addWidget(self.label13, 3, 0)
        layout1.addWidget(self.input13, 3, 1)
        layout1.addWidget(self.unit13, 3, 2)
        layout1.addWidget(self.label14, 4, 0)
        layout1.addWidget(self.input14, 4, 1)
        layout1.addWidget(self.unit14, 4, 2)
        layout1.addWidget(self.label15, 5, 0)
        layout1.addWidget(self.input15, 5, 1)
        layout1.addWidget(self.unit15, 5, 2)
        layout1.addWidget(self.label16, 6, 0)
        layout1.addWidget(self.input16, 6, 1)
        layout1.addWidget(self.unit16, 6, 2)

        layout1.addWidget(QLabel(self), 7, 0)  # 占位行
        self.calculate_button1 = CalculateButton('计算转换因子', self)
        self.calculate_button1.clicked.connect(self.calculate1)
        self.result1 = ResultLabel(self)

        layout1.addWidget(self.calculate_button1, 8, 0)
        layout1.addWidget(self.result1, 8, 1)

        widget1.setLayout(layout1)

        main_layout.addWidget(widget1, alignment=Qt.AlignTop | Qt.AlignHCenter)

        """ 国债基差 """
        # 间隔横线
        main_layout.addWidget(HorizonSepLine(self), alignment=Qt.AlignTop)

        widget2 = QWidget(self)
        widget2.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout2 = QGridLayout()
        layout2.setContentsMargins(QMargins(MARGIN_LEFT, MARGIN_TOP, MARGIN_RIGHT, MARGIN_BOTTOM))

        self.name2 = NameLabel('国债基差', self)
        self.label21 = QLabel('面值100元国债现券净价', self)
        self.input21 = InputEdit(self)
        self.unit21 = QLabel(self)

        self.label22 = QLabel('面值100元国债期货价', self)
        self.input22 = InputEdit(self)
        self.unit22 = QLabel(self)

        self.label24 = QLabel('转换因子', self)
        self.input24 = InputEdit(self)
        self.unit24 = QLabel(self)

        layout2.addWidget(self.name2, 0, 1, 1, 3)
        layout2.addWidget(self.label21, 1, 0)
        layout2.addWidget(self.input21, 1, 1)
        layout2.addWidget(self.unit21, 1, 2)
        layout2.addWidget(self.label22, 2, 0)
        layout2.addWidget(self.input22, 2, 1)
        layout2.addWidget(self.unit22, 2, 2)
        layout2.addWidget(self.label24, 3, 0)
        layout2.addWidget(self.input24, 3, 1)
        layout2.addWidget(self.unit24, 3, 2)

        layout2.addWidget(QLabel(self), 4, 0)  # 占位行

        self.calculate_button2 = CalculateButton('计算基差', self)
        self.calculate_button2.clicked.connect(self.calculate2)
        self.result2 = ResultLabel(self)
        self.unit24 = QLabel(self)

        layout2.addWidget(self.calculate_button2, 5, 0)
        layout2.addWidget(self.result2, 5, 1)
        layout2.addWidget(self.unit24, 5, 2)

        widget2.setLayout(layout2)
        main_layout.addWidget(widget2, alignment=Qt.AlignTop | Qt.AlignHCenter)

        """ 100元可交割国债应计利息 """
        # 间隔横线
        main_layout.addWidget(HorizonSepLine(self), alignment=Qt.AlignTop)

        widget3 = QWidget(self)
        widget3.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout3 = QGridLayout()
        layout3.setContentsMargins(QMargins(MARGIN_LEFT, MARGIN_TOP, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name3 = NameLabel('100元可交割国债应计利息', self)
        self.label31 = QLabel('可交割国债票面利率', self)
        self.input31 = InputEdit('3.46', self)
        self.unit31 = QLabel('%', self)

        layout3.addWidget(self.name3, 0, 0, 1, 3)
        layout3.addWidget(self.label31, 1, 0)
        layout3.addWidget(self.input31, 1, 1)
        layout3.addWidget(self.unit31, 1, 2)

        self.label32 = QLabel('每年付息次数', self)
        self.input32 = InputEdit(self)
        self.unit32 = QLabel(self)

        layout3.addWidget(self.label32, 2, 0)
        layout3.addWidget(self.input32, 2, 1)
        layout3.addWidget(self.unit32, 2, 2)

        self.label33 = QLabel('第二交割日', self)
        self.input33 = DateEdit(self)
        self.unit33 = QLabel(self)

        layout3.addWidget(self.label33, 3, 0)
        layout3.addWidget(self.input33, 3, 1)
        layout3.addWidget(self.unit33, 3, 2)

        self.label34 = QLabel('上一付息日', self)
        self.input34 = DateEdit(self)
        self.unit34 = QLabel(self)

        layout3.addWidget(self.label34, 4, 0)
        layout3.addWidget(self.input34, 4, 1)
        layout3.addWidget(self.unit34, 4, 2)

        self.label35 = QLabel('当前付息周期实际天数', self)
        self.input35 = InputEdit('365', self)
        self.unit35 = QLabel(self)

        layout3.addWidget(self.label35, 5, 0)
        layout3.addWidget(self.input35, 5, 1)
        layout3.addWidget(self.unit35, 5, 2)

        layout3.addWidget(QLabel(self), 6, 0)

        self.calculate_button3 = CalculateButton('试算应计利息', self)
        self.result3 = ResultLabel(self)
        self.result_unit3 = QLabel('', self)
        self.calculate_button3.clicked.connect(self.calculate3)
        layout3.addWidget(self.calculate_button3, 7, 0)
        layout3.addWidget(self.result3, 7, 1)
        layout3.addWidget(self.result_unit3, 7, 2)
        widget3.setLayout(layout3)
        main_layout.addWidget(widget3, alignment=Qt.AlignTop | Qt.AlignHCenter)

        """ 国债期货交割货款"""
        # 间隔横线
        main_layout.addWidget(HorizonSepLine(self), alignment=Qt.AlignTop)

        widget4 = QWidget(self)
        widget4.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout4 = QGridLayout()
        layout4.setContentsMargins(QMargins(MARGIN_LEFT, MARGIN_TOP, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name4 = NameLabel('国债交割货款', self)
        self.label41 = QLabel('交割数量', self)
        self.input41 = InputEdit(self)
        self.unit41 = QLabel('', self)

        layout4.addWidget(self.name4, 0, 0, 1, 3)
        layout4.addWidget(self.label41, 1, 0)
        layout4.addWidget(self.input41, 1, 1)
        layout4.addWidget(self.unit41, 1, 2)

        self.label42 = QLabel('交割结算价', self)
        self.input42 = InputEdit(self)
        self.unit42 = QLabel('', self)

        layout4.addWidget(self.label42, 2, 0)
        layout4.addWidget(self.input42, 2, 1)
        layout4.addWidget(self.unit42, 2, 2)

        self.label43 = QLabel('合约面值', self)
        self.input43 = InputEdit(self)
        self.unit43 = QLabel('', self)

        layout4.addWidget(self.label43, 3, 0)
        layout4.addWidget(self.input43, 3, 1)
        layout4.addWidget(self.unit43, 3, 2)

        self.label44 = QLabel('应计利息', self)
        self.input44 = InputEdit(self)
        self.unit44 = QLabel('', self)

        layout4.addWidget(self.label44, 4, 0)
        layout4.addWidget(self.input44, 4, 1)
        layout4.addWidget(self.unit44, 4, 2)

        self.label45 = QLabel('转换因子', self)
        self.input45 = InputEdit(self)
        self.unit45 = QLabel('', self)

        layout4.addWidget(self.label45, 5, 0)
        layout4.addWidget(self.input45, 5, 1)
        layout4.addWidget(self.unit45, 5, 2)

        layout4.addWidget(QLabel(self), 6, 0)

        self.calculate_button4 = CalculateButton('试算货款', self)
        self.result4 = ResultLabel(self)
        self.result_unit4 = QLabel('', self)
        self.calculate_button4.clicked.connect(self.calculate4)
        layout4.addWidget(self.calculate_button4, 7, 0)
        layout4.addWidget(self.result4, 7, 1)
        layout3.addWidget(self.result_unit4, 7, 2)
        widget4.setLayout(layout4)
        main_layout.addWidget(widget4, alignment=Qt.AlignTop | Qt.AlignHCenter)

        self.setLayout(main_layout)

    def calculate1(self):
        # 可交割国债转换因子计算
        # 交割月至下一付息月的月份数
        r = self.input11.value(p=True)
        x = get_date_range_count(self.input12.value(), self.input13.value(), c='month')
        if x <= 0:
            p = InformationPopup('下一付息月需大于交割月', self)
            p.exec_()
            return
        n = self.input16.value()
        c = self.input14.value(p=True)
        f = self.input15.value()
        params = [r, x, n, c, f]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算', self)
            p.exec_()
            return
        if r == 0 or f == 0:
            p = InformationPopup('国债票面利率或付息次数不能为0', self)
            p.exec_()
            return
        # print('10年期国债期货合约票面利率3%-r',r)
        # print('交割月至下月付息月月份-x', x)
        # print('剩余付息次数-n', n)
        # print('票面利率-c', c)
        # print('每年付息次数-f', f)
        # 计算
        v1 = 1 / math.pow((1 + r / f), x * f / 12)
        v2 = c/f + c/r + (1 - c/r) * (1 / math.pow((1+r/f), n-1))
        v3 = c/f * (1 - x*f/12)
        result = v1 * v2 - v3
        self.result1.set_value(result, count=4)
        self.input24.setText(str(self.result1.get_value()))
        self.input45.setText(str(self.result1.get_value()))

    def calculate2(self):  # 国债基差
        # B = P - (F * C)
        # 国债基差 ＝ 面值100元国债现货净价 - (面值100元期货合约价 x 转换因子)
        a = self.input21.value()
        c = self.input22.value()
        r = self.input24.value()
        params = [a, c, r]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算', self)
            p.exec_()
            return
        result = a - c * r
        self.result2.set_value(result, count=4)

    def calculate3(self):
        # result = (a * 100 / b) * (days / c)
        # 应计利息 = (票面利率 * 100 / 每年付息次数 ) * (第二交割日 - 上一付息日) / 当前付息周期实际天数
        days = get_date_range_count(self.input34.value(), self.input33.value(), c='day')
        a = self.input31.value(p=True)
        b = self.input32.value()
        c = self.input35.value()
        params = [a, b, c]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算', self)
            p.exec_()
            return
        result = (a * 100 / b) * (days / c)
        self.result3.set_value(result, count=7)
        self.input44.setText(str(self.result3.get_value()))

    def calculate4(self):
        # result = a * (b * r + c) * (d / 100)
        # 交割货款＝交割数量×（交割结算价×转换因子 + 应计利息）×（合约面值 / 100元）
        a = self.input41.value()
        b = self.input42.value()
        r = self.input45.value()
        c = self.input44.value()
        d = self.input43.value()
        params = [a, b, c, d, r]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算', self)
            p.exec_()
            return
        result = a * (b * r + c) * (d / 100)
        self.result4.set_value(result, count=2)


class HC(QWidget):
    RATE_DATA = rate.get_all_exchange_rate()

    def __init__(self, *args, **kwargs):
        super(HC, self).__init__(*args, **kwargs)
        self.USD_CNY_RATE = self.RATE_DATA.get('USD/CNY', None)
        if self.USD_CNY_RATE:
            self.USD_CNY_RATE = float(self.USD_CNY_RATE)
        main_layout = QVBoxLayout()
        """ 热卷生产成本 """
        widget1 = QWidget(self)
        widget1.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout1 = QGridLayout()
        layout1.setContentsMargins(QMargins(MARGIN_LEFT, 0, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name1 = NameLabel('热轧卷板生产成本', self)
        self.label11 = QLabel('铁矿石价格', self)
        self.input11 = InputEdit(self)
        self.unit11 = QLabel('元/吨', self)

        layout1.addWidget(self.name1, 0, 0, 1, 3)
        layout1.addWidget(self.label11, 1, 0)
        layout1.addWidget(self.input11, 1, 1)
        layout1.addWidget(self.unit11, 1, 2)

        self.label12 = QLabel('焦炭价格', self)
        self.input12 = InputEdit(self)
        self.unit12 = QLabel('元/吨', self)

        layout1.addWidget(self.label12, 2, 0)
        layout1.addWidget(self.input12, 2, 1)
        layout1.addWidget(self.unit12, 2, 2)

        self.label13 = QLabel('废钢价格', self)
        self.input13 = InputEdit(self)
        self.unit13 = QLabel('元/吨', self)

        layout1.addWidget(self.label13, 3, 0)
        layout1.addWidget(self.input13, 3, 1)
        layout1.addWidget(self.unit13, 3, 2)

        self.label14 = QLabel('轧钢费用', self)
        self.input14 = InputEdit(self)
        self.unit14 = QLabel('元/吨', self)

        layout1.addWidget(self.label14, 4, 0)
        layout1.addWidget(self.input14, 4, 1)
        layout1.addWidget(self.unit14, 4, 2)

        layout1.addWidget(QLabel(self), 5, 0)

        self.calculate_button1 = CalculateButton('试算成本', self)
        self.result1 = ResultLabel(self)
        self.result_unit1 = QLabel('元/吨', self)
        layout1.addWidget(self.calculate_button1, 6, 0)
        layout1.addWidget(self.result1, 6, 1)
        layout1.addWidget(self.result_unit1, 6, 2)
        widget1.setLayout(layout1)
        self.init_calculate1()
        self.calculate_button1.clicked.connect(self.calculate1)
        main_layout.addWidget(widget1, alignment=Qt.AlignTop | Qt.AlignHCenter)

        self.setLayout(main_layout)

    def init_calculate1(self):
        self.input14.set_value(300)

    def calculate1(self):
        # 热卷生产成本 =〔（（1.6×铁矿石+0.4×焦炭）/0.9）×0.96＋（0.12×废钢）〕/0.9＋轧钢费用
        # result = ((1.6 * a + 0.4 * b) / 0.9 * 0.96 + (0.12 * c)) / 0.9 + d
        a = self.input11.value()
        b = self.input12.value()
        c = self.input13.value()
        d = self.input14.value()
        params = [a, b, c, d]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = ((1.6 * a + 0.4 * b) / 0.9 * 0.96 + (0.12 * c)) / 0.9 + d
        self.result1.set_value(result, count=4)


class I(QWidget):
    RATE_DATA = rate.get_all_exchange_rate()

    def __init__(self, *args, **kwargs):
        super(I, self).__init__(*args, **kwargs)
        self.USD_CNY_RATE = self.RATE_DATA.get('USD/CNY', None)
        if self.USD_CNY_RATE:
            self.USD_CNY_RATE = float(self.USD_CNY_RATE)
        main_layout = QVBoxLayout()
        """ 铁矿石进口成本 """
        widget1 = QWidget(self)
        widget1.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout1 = QGridLayout()
        layout1.setContentsMargins(QMargins(MARGIN_LEFT, 0, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name1 = NameLabel('铁矿石进口成本', self)
        self.label11 = QLabel('普氏62%铁矿石指数', self)
        self.input11 = InputEdit(self)
        self.unit11 = QLabel('美元/吨', self)

        layout1.addWidget(self.name1, 0, 0, 1, 3)
        layout1.addWidget(self.label11, 1, 0)
        layout1.addWidget(self.input11, 1, 1)
        layout1.addWidget(self.unit11, 1, 2)

        self.label12 = QLabel('增值税', self)
        self.input12 = InputEdit(self)
        self.unit12 = QLabel('%', self)

        layout1.addWidget(self.label12, 2, 0)
        layout1.addWidget(self.input12, 2, 1)
        layout1.addWidget(self.unit12, 2, 2)

        self.label13 = QLabel('汇率', self)
        self.input13 = InputEdit(self)
        self.unit13 = QLabel('USD/CNY', self)

        layout1.addWidget(self.label13, 3, 0)
        layout1.addWidget(self.input13, 3, 1)
        layout1.addWidget(self.unit13, 3, 2)

        self.label14 = QLabel('港杂费', self)
        self.input14 = InputEdit(self)
        self.unit14 = QLabel('元/吨', self)

        layout1.addWidget(self.label14, 4, 0)
        layout1.addWidget(self.input14, 4, 1)
        layout1.addWidget(self.unit14, 4, 2)

        layout1.addWidget(QLabel(self), 5, 0)

        self.calculate_button1 = CalculateButton('试算成本', self)
        self.result1 = ResultLabel(self)
        self.result_unit1 = QLabel('元/吨', self)
        layout1.addWidget(self.calculate_button1, 6, 0)
        layout1.addWidget(self.result1, 6, 1)
        layout1.addWidget(self.result_unit1, 6, 2)
        widget1.setLayout(layout1)
        self.init_calculate1()
        self.calculate_button1.clicked.connect(self.calculate1)
        main_layout.addWidget(widget1, alignment=Qt.AlignTop | Qt.AlignHCenter)


        self.setLayout(main_layout)

    def init_calculate1(self):
        if self.USD_CNY_RATE:
            self.input13.set_value(self.USD_CNY_RATE, count=4)
        self.input12.set_value(13)
        self.input14.set_value(35)

    def calculate1(self):
        # 铁矿石进口成本 =普氏62%铁矿石指数×(1+增值税)×汇率＋港杂费
        # result = a * (1+b) * r + c
        a = self.input11.value()
        b = self.input12.value(p=True)
        r = self.input13.value()
        c = self.input14.value()
        params = [a, b, c]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = a * (1+b) * r + c
        self.result1.set_value(result, count=4)


class J(QWidget):
    RATE_DATA = rate.get_all_exchange_rate()

    def __init__(self, *args, **kwargs):
        super(J, self).__init__(*args, **kwargs)
        self.USD_CNY_RATE = self.RATE_DATA.get('USD/CNY', None)
        if self.USD_CNY_RATE:
            self.USD_CNY_RATE = float(self.USD_CNY_RATE)
        main_layout = QVBoxLayout()
        """ 焦炭生辰成本 """
        widget1 = QWidget(self)
        widget1.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout1 = QGridLayout()
        layout1.setContentsMargins(QMargins(MARGIN_LEFT, 0, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name1 = NameLabel('焦炭生产成本', self)
        self.label11 = QLabel('主焦煤价格', self)
        self.input11 = InputEdit(self)
        self.unit11 = QLabel('元/吨', self)

        layout1.addWidget(self.name1, 0, 0, 1, 3)
        layout1.addWidget(self.label11, 1, 0)
        layout1.addWidget(self.input11, 1, 1)
        layout1.addWidget(self.unit11, 1, 2)

        self.label12 = QLabel('瘦煤价格', self)
        self.input12 = InputEdit(self)
        self.unit12 = QLabel('元/吨', self)

        layout1.addWidget(self.label12, 2, 0)
        layout1.addWidget(self.input12, 2, 1)
        layout1.addWidget(self.unit12, 2, 2)

        self.label13 = QLabel('肥煤价格', self)
        self.input13 = InputEdit(self)
        self.unit13 = QLabel('元/吨', self)

        layout1.addWidget(self.label13, 3, 0)
        layout1.addWidget(self.input13, 3, 1)
        layout1.addWidget(self.unit13, 3, 2)

        self.label14 = QLabel('气煤价格', self)
        self.input14 = InputEdit(self)
        self.unit14 = QLabel('元/吨', self)

        layout1.addWidget(self.label14, 4, 0)
        layout1.addWidget(self.input14, 4, 1)
        layout1.addWidget(self.unit14, 4, 2)

        self.label15 = QLabel('1/3焦煤价格', self)
        self.input15 = InputEdit(self)
        self.unit15 = QLabel('元/吨', self)

        layout1.addWidget(self.label15, 5, 0)
        layout1.addWidget(self.input15, 5, 1)
        layout1.addWidget(self.unit15, 5, 2)

        layout1.addWidget(QLabel(self), 6, 0)

        self.calculate_button1 = CalculateButton('试算成本', self)
        self.result1 = ResultLabel(self)
        self.result_unit1 = QLabel('元/吨', self)
        layout1.addWidget(self.calculate_button1, 7, 0)
        layout1.addWidget(self.result1, 7, 1)
        layout1.addWidget(self.result_unit1, 7, 2)
        widget1.setLayout(layout1)
        self.init_calculate1()
        self.calculate_button1.clicked.connect(self.calculate1)
        main_layout.addWidget(widget1, alignment=Qt.AlignTop | Qt.AlignHCenter)


        self.setLayout(main_layout)

    def init_calculate1(self):
        pass

    def calculate1(self):
        # 计算锰矿成本
        # 焦炭成本=1.35*(0.3主焦煤+0.15瘦煤+0.15气煤+0.15肥煤+0.25 1/3焦煤)
        # result = 1.35 * (0.3 * a +0.15 * b +0.15 * c +0.15 * d +0.25* e)
        a = self.input11.value()
        b = self.input12.value()
        c = self.input14.value()
        d = self.input13.value()
        e = self.input15.value()
        params = [a, b, c, d, e]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = 1.35 * (0.3 * a +0.15 * b +0.15 * c +0.15 * d +0.25* e)
        self.result1.set_value(result, count=4)


class JD(QWidget):
    RATE_DATA = rate.get_all_exchange_rate()

    def __init__(self, *args, **kwargs):
        super(JD, self).__init__(*args, **kwargs)
        self.USD_CNY_RATE = self.RATE_DATA.get('USD/CNY', None)
        if self.USD_CNY_RATE:
            self.USD_CNY_RATE = float(self.USD_CNY_RATE)
        main_layout = QVBoxLayout()
        """ 蛋鸡养殖成本 """
        widget1 = QWidget(self)
        widget1.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout1 = QGridLayout()
        layout1.setContentsMargins(QMargins(MARGIN_LEFT, 0, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name1 = NameLabel('蛋鸡养殖成本', self)
        self.label11 = QLabel('仔鸡价格', self)
        self.input11 = InputEdit(self)
        self.unit11 = QLabel('元/只', self)

        layout1.addWidget(self.name1, 0, 0, 1, 3)
        layout1.addWidget(self.label11, 1, 0)
        layout1.addWidget(self.input11, 1, 1)
        layout1.addWidget(self.unit11, 1, 2)

        self.label12 = QLabel('饲料成本', self)
        self.input12 = InputEdit(self)
        self.unit12 = QLabel('元/斤', self)

        layout1.addWidget(self.label12, 2, 0)
        layout1.addWidget(self.input12, 2, 1)
        layout1.addWidget(self.unit12, 2, 2)

        self.label13 = QLabel('消耗量', self)
        self.input13 = InputEdit(self)
        self.unit13 = QLabel('斤', self)

        layout1.addWidget(self.label13, 3, 0)
        layout1.addWidget(self.input13, 3, 1)
        layout1.addWidget(self.unit13, 3, 2)

        self.label14 = QLabel('防疫费', self)
        self.input14 = InputEdit(self)
        self.unit14 = QLabel('元', self)

        layout1.addWidget(self.label14, 4, 0)
        layout1.addWidget(self.input14, 4, 1)
        layout1.addWidget(self.unit14, 4, 2)

        self.label15 = QLabel('水电费', self)
        self.input15 = InputEdit(self)
        self.unit15 = QLabel('元', self)

        layout1.addWidget(self.label15, 5, 0)
        layout1.addWidget(self.input15, 5, 1)
        layout1.addWidget(self.unit15, 5, 2)

        layout1.addWidget(QLabel(self), 6, 0)

        self.calculate_button1 = CalculateButton('试算成本', self)
        self.result1 = ResultLabel(self)
        self.result_unit1 = QLabel('元/只', self)
        layout1.addWidget(self.calculate_button1, 7, 0)
        layout1.addWidget(self.result1, 7, 1)
        layout1.addWidget(self.result_unit1, 7, 2)
        widget1.setLayout(layout1)
        self.init_calculate1()
        self.calculate_button1.clicked.connect(self.calculate1)
        main_layout.addWidget(widget1, alignment=Qt.AlignTop | Qt.AlignHCenter)

        """ 蛋鸡养殖收益 """
        main_layout.addWidget(HorizonSepLine(self))

        widget2 = QWidget(self)
        widget2.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout2 = QGridLayout()
        layout2.setContentsMargins(QMargins(MARGIN_LEFT, MARGIN_TOP, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name2 = NameLabel('蛋鸡养殖收益', self)
        self.label21 = QLabel('鸡蛋收入', self)
        self.input21 = InputEdit(self)
        self.unit21 = QLabel('元/只', self)

        layout2.addWidget(self.name2, 0, 0, 1, 3)
        layout2.addWidget(self.label21, 1, 0)
        layout2.addWidget(self.input21, 1, 1)
        layout2.addWidget(self.unit21, 1, 2)

        self.label22 = QLabel('淘汰鸡收入', self)
        self.input22 = InputEdit(self)
        self.unit22 = QLabel('元/只', self)

        layout2.addWidget(self.label22, 2, 0)
        layout2.addWidget(self.input22, 2, 1)
        layout2.addWidget(self.unit22, 2, 2)

        self.label23 = QLabel('鸡粪收入', self)
        self.input23 = InputEdit(self)
        self.unit23 = QLabel('元/只', self)

        layout2.addWidget(self.label23, 3, 0)
        layout2.addWidget(self.input23, 3, 1)
        layout2.addWidget(self.unit23, 3, 2)

        layout2.addWidget(QLabel(self), 4, 0)
        self.calculate_button2 = CalculateButton('试算加工利润', self)
        self.result2 = ResultLabel(self)
        self.result_unit2 = QLabel('元/只', self)
        layout2.addWidget(self.calculate_button2, 5, 0)
        layout2.addWidget(self.result2, 5, 1)
        layout2.addWidget(self.result_unit2, 5, 2)
        widget2.setLayout(layout2)
        self.init_calculate2()
        self.calculate_button2.clicked.connect(self.calculate2)
        main_layout.addWidget(widget2, alignment=Qt.AlignTop | Qt.AlignHCenter)

        """ 蛋价成本 """
        main_layout.addWidget(HorizonSepLine(self))

        widget3 = QWidget(self)
        widget3.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout3 = QGridLayout()
        layout3.setContentsMargins(QMargins(MARGIN_LEFT, MARGIN_TOP, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name3 = NameLabel('蛋价成本', self)
        self.label31 = QLabel('蛋鸡养殖成本', self)
        self.input31 = InputEdit(self)
        self.unit31 = QLabel('元/只', self)

        layout3.addWidget(self.name3, 0, 0, 1, 3)
        layout3.addWidget(self.label31, 1, 0)
        layout3.addWidget(self.input31, 1, 1)
        layout3.addWidget(self.unit31, 1, 2)

        self.label32 = QLabel('淘汰鸡收入', self)
        self.input32 = InputEdit(self)
        self.unit32 = QLabel('元/只', self)

        layout3.addWidget(self.label32, 2, 0)
        layout3.addWidget(self.input32, 2, 1)
        layout3.addWidget(self.unit32, 2, 2)

        self.label33 = QLabel('鸡粪收入', self)
        self.input33 = InputEdit(self)
        self.unit33 = QLabel('元/只', self)

        layout3.addWidget(self.label33, 3, 0)
        layout3.addWidget(self.input33, 3, 1)
        layout3.addWidget(self.unit33, 3, 2)

        self.label34 = QLabel('产蛋量', self)
        self.input34 = InputEdit(self)
        self.unit34 = QLabel('斤', self)

        layout3.addWidget(self.label34, 4, 0)
        layout3.addWidget(self.input34, 4, 1)
        layout3.addWidget(self.unit34, 4, 2)

        layout3.addWidget(QLabel(self), 5, 0)

        self.calculate_button3 = CalculateButton('试算成本', self)
        self.result3 = ResultLabel(self)
        self.result_unit3 = QLabel('元/斤', self)
        layout3.addWidget(self.calculate_button3, 6, 0)
        layout3.addWidget(self.result3, 6, 1)
        layout3.addWidget(self.result_unit3, 6, 2)
        widget3.setLayout(layout3)
        self.init_calculate3()
        self.calculate_button3.clicked.connect(self.calculate3)
        main_layout.addWidget(widget3, alignment=Qt.AlignTop | Qt.AlignHCenter)
        self.setLayout(main_layout)

    def init_calculate1(self):
        self.input13.set_value(122.7)
        self.input14.set_value(3)
        self.input15.set_value(0.5)

    def init_calculate2(self):
        self.input23.set_value(3.4)

    def init_calculate3(self):
        self.input33.set_value(3.4)
        self.input34.set_value(37.5)

    def calculate1(self):
        # result = a + b * c + d + e
        # 蛋鸡养殖成本=仔鸡价格+饲料成本（饲料价格*消耗量）+防疫费+水电费
        a = self.input11.value()
        b = self.input12.value()
        c = self.input13.value()
        d = self.input14.value()
        e = self.input15.value()
        params = [a, b, c, d, e]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = a + b * c + d + e
        self.result1.set_value(result, count=4)

    def calculate2(self):
        # 蛋鸡养殖收益=鸡蛋收入（蛋价*产蛋量）+淘汰鸡收入+鸡粪收入
        # result = a + b + c
        a = self.input21.value()
        b = self.input22.value()
        c = self.input23.value()
        params = [a, b, c]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = a + b + c
        self.result2.set_value(result, count=4)

    def calculate3(self):
        # 蛋价成本=（蛋鸡养殖成本-淘汰鸡收入-鸡粪收入）/产蛋量
        # result = (a - b - c) / d
        a = self.input31.value()
        b = self.input32.value()
        c = self.input33.value()
        d = self.input34.value()
        params = [a, b, c, d]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = (a - b - c) / d
        self.result3.set_value(result, count=4)


class L(QWidget):
    RATE_DATA = rate.get_all_exchange_rate()

    def __init__(self, *args, **kwargs):
        super(L, self).__init__(*args, **kwargs)
        self.USD_CNY_RATE = self.RATE_DATA.get('USD/CNY', None)
        if self.USD_CNY_RATE:
            self.USD_CNY_RATE = float(self.USD_CNY_RATE)
        main_layout = QVBoxLayout()
        """ 线性进口成本 """
        widget1 = QWidget(self)
        widget1.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout1 = QGridLayout()
        layout1.setContentsMargins(QMargins(MARGIN_LEFT, 0, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name1 = NameLabel('聚乙烯进口成本', self)
        self.label11 = QLabel('亚洲线性价格', self)
        self.input11 = InputEdit(self)
        self.unit11 = QLabel('美元/吨', self)

        layout1.addWidget(self.name1, 0, 0, 1, 3)
        layout1.addWidget(self.label11, 1, 0)
        layout1.addWidget(self.input11, 1, 1)
        layout1.addWidget(self.unit11, 1, 2)

        self.label12 = QLabel('关税', self)
        self.input12 = InputEdit(self)
        self.unit12 = QLabel('%', self)

        layout1.addWidget(self.label12, 2, 0)
        layout1.addWidget(self.input12, 2, 1)
        layout1.addWidget(self.unit12, 2, 2)

        self.label13 = QLabel('增值税', self)
        self.input13 = InputEdit(self)
        self.unit13 = QLabel('%', self)

        layout1.addWidget(self.label13, 3, 0)
        layout1.addWidget(self.input13, 3, 1)
        layout1.addWidget(self.unit13, 3, 2)

        self.label14 = QLabel('汇率', self)
        self.input14 = InputEdit(self)
        self.unit14 = QLabel('USD/CNY', self)

        layout1.addWidget(self.label14, 4, 0)
        layout1.addWidget(self.input14, 4, 1)
        layout1.addWidget(self.unit14, 4, 2)

        self.label15 = QLabel('杂费', self)
        self.input15 = InputEdit(self)
        self.unit15 = QLabel('元/吨', )

        layout1.addWidget(self.label15, 5, 0)
        layout1.addWidget(self.input15, 5, 1)
        layout1.addWidget(self.unit15, 5, 2)

        layout1.addWidget(QLabel(self), 6, 0)

        self.calculate_button1 = CalculateButton('试算成本', self)
        self.result1 = ResultLabel(self)
        self.result_unit1 = QLabel('元/吨', self)
        layout1.addWidget(self.calculate_button1, 7, 0)
        layout1.addWidget(self.result1, 7, 1)
        layout1.addWidget(self.result_unit1, 7, 2)
        widget1.setLayout(layout1)
        self.init_calculate1()
        self.calculate_button1.clicked.connect(self.calculate1)
        main_layout.addWidget(widget1, alignment=Qt.AlignTop | Qt.AlignHCenter)

        """ 油制线性生产成本 """
        main_layout.addWidget(HorizonSepLine(self))

        widget2 = QWidget(self)
        widget2.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout2 = QGridLayout()
        layout2.setContentsMargins(QMargins(MARGIN_LEFT, MARGIN_TOP, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name2 = NameLabel('油制聚乙烯生产成本', self)
        self.label21 = QLabel('亚洲石脑油', self)
        self.input21 = InputEdit(self)
        self.unit21 = QLabel('美元/吨', self)

        layout2.addWidget(self.name2, 0, 0, 1, 3)
        layout2.addWidget(self.label21, 1, 0)
        layout2.addWidget(self.input21, 1, 1)
        layout2.addWidget(self.unit21, 1, 2)

        self.label22 = QLabel('生产比', self)
        self.input22 = InputEdit(self)
        self.unit22 = QLabel('', self)

        layout2.addWidget(self.label22, 2, 0)
        layout2.addWidget(self.input22, 2, 1)
        layout2.addWidget(self.unit22, 2, 2)

        self.label23 = QLabel('增值税', self)
        self.input23 = InputEdit(self)
        self.unit23 = QLabel('%', self)

        layout2.addWidget(self.label23, 3, 0)
        layout2.addWidget(self.input23, 3, 1)
        layout2.addWidget(self.unit23, 3, 2)

        self.label24 = QLabel('汇率', self)
        self.input24 = InputEdit(self)
        self.unit24 = QLabel('USD/CNY', self)

        layout2.addWidget(self.label24, 4, 0)
        layout2.addWidget(self.input24, 4, 1)
        layout2.addWidget(self.unit24, 4, 2)

        self.label25 = QLabel('杂费', self)
        self.input25 = InputEdit(self)
        self.unit25 = QLabel('元/吨', self)

        layout2.addWidget(self.label25, 5, 0)
        layout2.addWidget(self.input25, 5, 1)
        layout2.addWidget(self.unit25, 5, 2)

        layout2.addWidget(QLabel(self), 6, 0)
        self.calculate_button2 = CalculateButton('试算成本', self)
        self.result2 = ResultLabel(self)
        self.result_unit2 = QLabel('元/吨', self)
        layout2.addWidget(self.calculate_button2, 7, 0)
        layout2.addWidget(self.result2, 7, 1)
        layout2.addWidget(self.result_unit2, 7, 2)
        widget2.setLayout(layout2)
        self.init_calculate2()
        self.calculate_button2.clicked.connect(self.calculate2)
        main_layout.addWidget(widget2, alignment=Qt.AlignTop | Qt.AlignHCenter)

        self.setLayout(main_layout)

    def init_calculate1(self):
        if self.USD_CNY_RATE:
            self.input14.set_value(self.USD_CNY_RATE, count=4)
        self.input12.set_value(6.5)
        self.input13.set_value(13)
        self.input15.set_value(150)

    def init_calculate2(self):
        if self.USD_CNY_RATE:
            self.input24.set_value(self.USD_CNY_RATE, count=4)
        self.input22.set_value(1.35)
        self.input23.set_value(13)
        self.input25.set_value(1300)

    def calculate1(self):
        # 线性进口成本=亚洲线性价格*关税*增值值*汇率+杂费
        # result = a * (1 + b) * (1 + c) * r + d
        a = self.input11.value()
        b = self.input12.value(p=True)
        c = self.input13.value(p=True)
        r = self.input14.value()
        d = self.input15.value()

        params = [a, b, c, d, r]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = a * (1 + b) * (1 + c) * r + d
        self.result1.set_value(result, count=4)

    def calculate2(self):
        # 油制线性生产成本=亚洲石脑油*汇率*聚乙烯生产比*增值税+杂费
        # 油制线性生产成本=亚洲石脑油*聚乙烯生产比*增值税*汇率+杂费
        # result = a * b * (1 + c) * r + d
        a = self.input21.value()
        b = self.input22.value()
        c = self.input23.value(p=True)
        r = self.input24.value()
        d = self.input25.value()

        params = [a, b, c, d, r]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = a * b * (1 + c) * r + d
        self.result2.set_value(result, count=4)


class LH(QWidget):
    RATE_DATA = rate.get_all_exchange_rate()

    def __init__(self, *args, **kwargs):
        super(LH, self).__init__(*args, **kwargs)
        self.USD_CNY_RATE = self.RATE_DATA.get('USD/CNY', None)
        if self.USD_CNY_RATE:
            self.USD_CNY_RATE = float(self.USD_CNY_RATE)
        main_layout = QVBoxLayout()
        """ 生猪自繁自养成本 """
        widget1 = QWidget(self)
        widget1.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout1 = QGridLayout()
        layout1.setContentsMargins(QMargins(MARGIN_LEFT, 0, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name1 = NameLabel('生猪自繁自养成本(出栏120kg)', self)
        self.label11 = QLabel('仔猪成本', self)
        self.input11 = InputEdit(self)
        self.unit11 = QLabel('元/公斤', self)

        layout1.addWidget(self.name1, 0, 0, 1, 3)
        layout1.addWidget(self.label11, 1, 0)
        layout1.addWidget(self.input11, 1, 1)
        layout1.addWidget(self.unit11, 1, 2)

        self.label12 = QLabel('饲料成本', self)
        self.input12 = InputEdit(self)
        self.unit12 = QLabel('元/公斤', self)

        layout1.addWidget(self.label12, 2, 0)
        layout1.addWidget(self.input12, 2, 1)
        layout1.addWidget(self.unit12, 2, 2)

        self.label13 = QLabel('疫苗兽药成本', self)
        self.input13 = InputEdit(self)
        self.unit13 = QLabel('元/公斤', self)

        layout1.addWidget(self.label13, 3, 0)
        layout1.addWidget(self.input13, 3, 1)
        layout1.addWidget(self.unit13, 3, 2)

        self.label14 = QLabel('人工成本', self)
        self.input14 = InputEdit(self)
        self.unit14 = QLabel('元/公斤', self)

        layout1.addWidget(self.label14, 4, 0)
        layout1.addWidget(self.input14, 4, 1)
        layout1.addWidget(self.unit14, 4, 2)

        self.label15 = QLabel('厂房折旧成本', self)
        self.input15 = InputEdit(self)
        self.unit15 = QLabel('元/公斤', self)

        layout1.addWidget(self.label15, 5, 0)
        layout1.addWidget(self.input15, 5, 1)
        layout1.addWidget(self.unit15, 5, 2)

        layout1.addWidget(QLabel(self), 6, 0)

        self.calculate_button1 = CalculateButton('试算成本', self)
        self.result1 = ResultLabel(self)
        self.result_unit1 = QLabel('元/公斤', self)
        layout1.addWidget(self.calculate_button1, 7, 0)
        layout1.addWidget(self.result1, 7, 1)
        layout1.addWidget(self.result_unit1, 7, 2)
        widget1.setLayout(layout1)
        self.init_calculate1()
        self.calculate_button1.clicked.connect(self.calculate1)
        main_layout.addWidget(widget1, alignment=Qt.AlignTop | Qt.AlignHCenter)

        """ 公司+农户养殖成本(出栏120kg) """
        main_layout.addWidget(HorizonSepLine(self))

        widget2 = QWidget(self)
        widget2.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout2 = QGridLayout()
        layout2.setContentsMargins(QMargins(MARGIN_LEFT, MARGIN_TOP, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name2 = NameLabel('公司+农户养殖成本(出栏120kg)', self)
        self.label21 = QLabel('仔猪成本', self)
        self.input21 = InputEdit(self)
        self.unit21 = QLabel('元/公斤', self)

        layout2.addWidget(self.name2, 0, 0, 1, 3)
        layout2.addWidget(self.label21, 1, 0)
        layout2.addWidget(self.input21, 1, 1)
        layout2.addWidget(self.unit21, 1, 2)

        self.label22 = QLabel('饲料成本', self)
        self.input22 = InputEdit(self)
        self.unit22 = QLabel('元/公斤', self)

        layout2.addWidget(self.label22, 2, 0)
        layout2.addWidget(self.input22, 2, 1)
        layout2.addWidget(self.unit22, 2, 2)

        self.label23 = QLabel('疫苗兽药成本', self)
        self.input23 = InputEdit(self)
        self.unit23 = QLabel('元/公斤', self)

        layout2.addWidget(self.label23, 3, 0)
        layout2.addWidget(self.input23, 3, 1)
        layout2.addWidget(self.unit23, 3, 2)

        self.label24 = QLabel('人工成本', self)
        self.input24 = InputEdit(self)
        self.unit24 = QLabel('元/公斤', self)

        layout2.addWidget(self.label24, 4, 0)
        layout2.addWidget(self.input24, 4, 1)
        layout2.addWidget(self.unit24, 4, 2)

        self.label25 = QLabel('水电煤气成本', self)
        self.input25 = InputEdit(self)
        self.unit25 = QLabel('元/公斤', self)

        layout2.addWidget(self.label25, 5, 0)
        layout2.addWidget(self.input25, 5, 1)
        layout2.addWidget(self.unit25, 5, 2)

        self.label26 = QLabel('非瘟防疫成本', self)
        self.input26 = InputEdit(self)
        self.unit26 = QLabel('元/公斤', self)

        layout2.addWidget(self.label26, 6, 0)
        layout2.addWidget(self.input26, 6, 1)
        layout2.addWidget(self.unit26, 6, 2)

        layout2.addWidget(QLabel(self), 7, 0)
        self.calculate_button2 = CalculateButton('试算成本', self)
        self.result2 = ResultLabel(self)
        self.result_unit2 = QLabel('元/吨', self)
        layout2.addWidget(self.calculate_button2, 8, 0)
        layout2.addWidget(self.result2, 8, 1)
        layout2.addWidget(self.result_unit2, 8, 2)
        widget2.setLayout(layout2)
        self.init_calculate2()
        self.calculate_button2.clicked.connect(self.calculate2)
        main_layout.addWidget(widget2, alignment=Qt.AlignTop | Qt.AlignHCenter)
        self.setLayout(main_layout)

    def init_calculate1(self):
        self.input11.set_value(2.9)
        self.input13.set_value(0.33)
        self.input14.set_value(0.21)
        self.input15.set_value(0.66)

    def init_calculate2(self):
        self.input21.set_value(2.9)
        self.input23.set_value(0.62)
        self.input24.set_value(2.9)
        self.input25.set_value(0.33)
        self.input26.set_value(0.16)

    def calculate1(self):
        # 计算镍进口成本
        # result = a + b + c + d + e
        # 生猪自繁自养成本=仔猪成本+饲料成本+疫苗兽药成本+人工成本+厂房折旧成本
        a = self.input11.value()
        b = self.input12.value()
        c = self.input13.value()
        d = self.input14.value()
        e = self.input15.value()
        params = [a, b, c, d, e]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = a + b + c + d + e
        self.result1.set_value(result, count=4)

    def calculate2(self):
        # 生猪公司+农户养殖成本=仔猪成本+饲料成本+疫苗兽药成本+人工成本+水电煤气成本+非瘟防疫成本
        # result = a + b + c + d + e + f
        a = self.input21.value()
        b = self.input22.value()
        c = self.input23.value()
        d = self.input24.value()
        e = self.input25.value()
        f = self.input26.value()
        params = [a, b, c, d, e, f]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = a + b + c + d + e + f
        self.result2.set_value(result, count=4)


class MA(QWidget):
    RATE_DATA = rate.get_all_exchange_rate()

    def __init__(self, *args, **kwargs):
        super(MA, self).__init__(*args, **kwargs)
        self.USD_CNY_RATE = self.RATE_DATA.get('USD/CNY', None)
        if self.USD_CNY_RATE:
            self.USD_CNY_RATE = float(self.USD_CNY_RATE)
        main_layout = QVBoxLayout()
        """ 甲醇进口利润 """
        widget1 = QWidget(self)
        widget1.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout1 = QGridLayout()
        layout1.setContentsMargins(QMargins(MARGIN_LEFT, 0, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name1 = NameLabel('甲醇进口利润', self)
        self.label11 = QLabel('华东甲醇现货', self)
        self.input11 = InputEdit(self)
        self.unit11 = QLabel('元/吨', self)

        layout1.addWidget(self.name1, 0, 0, 1, 3)
        layout1.addWidget(self.label11, 1, 0)
        layout1.addWidget(self.input11, 1, 1)
        layout1.addWidget(self.unit11, 1, 2)

        self.label12 = QLabel('CFR中国主港甲醇', self)
        self.input12 = InputEdit(self)
        self.unit12 = QLabel('美元/吨', self)

        layout1.addWidget(self.label12, 2, 0)
        layout1.addWidget(self.input12, 2, 1)
        layout1.addWidget(self.unit12, 2, 2)

        self.label13 = QLabel('汇率', self)
        self.input13 = InputEdit(self)
        self.unit13 = QLabel('USD/CNY', self)

        layout1.addWidget(self.label13, 3, 0)
        layout1.addWidget(self.input13, 3, 1)
        layout1.addWidget(self.unit13, 3, 2)

        self.label14 = QLabel('增值税', self)
        self.input14 = InputEdit(self)
        self.unit14 = QLabel('%', self)

        layout1.addWidget(self.label14, 4, 0)
        layout1.addWidget(self.input14, 4, 1)
        layout1.addWidget(self.unit14, 4, 2)

        self.label15 = QLabel('关税', self)
        self.input15 = InputEdit(self)
        self.unit15 = QLabel('%', )

        layout1.addWidget(self.label15, 5, 0)
        layout1.addWidget(self.input15, 5, 1)
        layout1.addWidget(self.unit15, 5, 2)

        self.label16 = QLabel('港杂费', self)
        self.input16 = InputEdit(self)
        self.unit16 = QLabel('元/吨', self)

        layout1.addWidget(self.label16, 6, 0)
        layout1.addWidget(self.input16, 6, 1)
        layout1.addWidget(self.unit16, 6, 2)

        layout1.addWidget(QLabel(self), 7, 0)

        self.calculate_button1 = CalculateButton('试算利润', self)
        self.result1 = ResultLabel(self)
        self.result_unit1 = QLabel('元/吨', self)
        layout1.addWidget(self.calculate_button1, 8, 0)
        layout1.addWidget(self.result1, 8, 1)
        layout1.addWidget(self.result_unit1, 8, 2)
        widget1.setLayout(layout1)
        self.init_calculate1()
        self.calculate_button1.clicked.connect(self.calculate1)
        main_layout.addWidget(widget1, alignment=Qt.AlignTop | Qt.AlignHCenter)

        """ 甲醇制烯烃盘面利润 """
        main_layout.addWidget(HorizonSepLine(self))

        widget2 = QWidget(self)
        widget2.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout2 = QGridLayout()
        layout2.setContentsMargins(QMargins(MARGIN_LEFT, MARGIN_TOP, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name2 = NameLabel('甲醇制烯烃盘面利润', self)
        self.label21 = QLabel('聚丙烯期货价格', self)
        self.input21 = InputEdit(self)
        self.unit21 = QLabel('元/吨', self)

        layout2.addWidget(self.name2, 0, 0, 1, 3)
        layout2.addWidget(self.label21, 1, 0)
        layout2.addWidget(self.input21, 1, 1)
        layout2.addWidget(self.unit21, 1, 2)

        self.label22 = QLabel('甲醇期货价格', self)
        self.input22 = InputEdit(self)
        self.unit22 = QLabel('元/吨', self)

        layout2.addWidget(self.label22, 2, 0)
        layout2.addWidget(self.input22, 2, 1)
        layout2.addWidget(self.unit22, 2, 2)

        layout2.addWidget(QLabel(self), 3, 0)
        self.calculate_button2 = CalculateButton('试算利润', self)
        self.result2 = ResultLabel(self)
        self.result_unit2 = QLabel('元/吨', self)
        layout2.addWidget(self.calculate_button2, 4, 0)
        layout2.addWidget(self.result2, 4, 1)
        layout2.addWidget(self.result_unit2, 4, 2)
        widget2.setLayout(layout2)
        self.init_calculate2()
        self.calculate_button2.clicked.connect(self.calculate2)
        main_layout.addWidget(widget2, alignment=Qt.AlignTop | Qt.AlignHCenter)

        self.setLayout(main_layout)

    def init_calculate1(self):
        if self.USD_CNY_RATE:
            self.input13.set_value(self.USD_CNY_RATE, count=4)
        self.input14.set_value(13)
        self.input15.set_value(5.5)
        self.input16.set_value(50)

    def init_calculate2(self):
        pass

    def calculate1(self):
        # 甲醇进口利润=华东甲醇现货-CFR中国主港甲醇×美元兑人民币汇率×(1+增值税)×(1+关税)＋港杂费
        # result = a - (b * r * (1 + c) * (1 + d) + e)
        a = self.input11.value()
        b = self.input12.value()
        r = self.input13.value()
        c = self.input14.value(p=True)
        d = self.input15.value(p=True)
        e = self.input16.value()

        params = [a, b, c, d, e, r]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = a - (b * r * (1 + c) * (1 + d) + e)
        self.result1.set_value(result, count=4)

    def calculate2(self):
        # 甲醇制烯烃盘面利润=聚丙烯期货价格-甲醇期货价格:×3
        # result = a - b * 3
        a = self.input21.value()
        b = self.input22.value()

        params = [a, b]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = a - b * 3
        self.result2.set_value(result, count=4)


class NI(QWidget):
    RATE_DATA = rate.get_all_exchange_rate()

    def __init__(self, *args, **kwargs):
        super(NI, self).__init__(*args, **kwargs)
        self.USD_CNY_RATE = self.RATE_DATA.get('USD/CNY', None)
        if self.USD_CNY_RATE:
            self.USD_CNY_RATE = float(self.USD_CNY_RATE)
        main_layout = QVBoxLayout()
        """ 镍进口成本 """
        widget1 = QWidget(self)
        widget1.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout1 = QGridLayout()
        layout1.setContentsMargins(QMargins(MARGIN_LEFT, 0, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name1 = NameLabel('镍进口成本', self)
        self.label11 = QLabel('LME三个月期货价', self)
        self.input11 = InputEdit(self)
        self.unit11 = QLabel('美元/吨', self)

        layout1.addWidget(self.name1, 0, 0, 1, 3)
        layout1.addWidget(self.label11, 1, 0)
        layout1.addWidget(self.input11, 1, 1)
        layout1.addWidget(self.unit11, 1, 2)

        self.label12 = QLabel('LME镍升贴水', self)
        self.input12 = InputEdit(self)
        self.unit12 = QLabel('美元/吨', self)

        layout1.addWidget(self.label12, 2, 0)
        layout1.addWidget(self.input12, 2, 1)
        layout1.addWidget(self.unit12, 2, 2)

        self.label13 = QLabel('CIF到岸升贴水', self)
        self.input13 = InputEdit(self)
        self.unit13 = QLabel('美元/吨', self)

        layout1.addWidget(self.label13, 3, 0)
        layout1.addWidget(self.input13, 3, 1)
        layout1.addWidget(self.unit13, 3, 2)

        self.label14 = QLabel('汇率', self)
        self.input14 = InputEdit(self)
        self.unit14 = QLabel('USD/CNY', self)

        layout1.addWidget(self.label14, 4, 0)
        layout1.addWidget(self.input14, 4, 1)
        layout1.addWidget(self.unit14, 4, 2)

        self.label15 = QLabel('增值税率', self)
        self.input15 = InputEdit(self)
        self.unit15 = QLabel('%', self)

        layout1.addWidget(self.label15, 5, 0)
        layout1.addWidget(self.input15, 5, 1)
        layout1.addWidget(self.unit15, 5, 2)

        self.label16 = QLabel('关税税率', self)
        self.input16 = InputEdit(self)
        self.unit16 = QLabel('%', self)

        layout1.addWidget(self.label16, 6, 0)
        layout1.addWidget(self.input16, 6, 1)
        layout1.addWidget(self.unit16, 6, 2)

        self.label17 = QLabel('港杂费', self)
        self.input17 = InputEdit(self)
        self.unit17 = QLabel('元/吨', self)

        layout1.addWidget(self.label17, 7, 0)
        layout1.addWidget(self.input17, 7, 1)
        layout1.addWidget(self.unit17, 7, 2)

        layout1.addWidget(QLabel(self), 8, 0)

        self.calculate_button1 = CalculateButton('试算成本', self)
        self.result1 = ResultLabel(self)
        self.result_unit1 = QLabel('元/吨', self)
        layout1.addWidget(self.calculate_button1, 9, 0)
        layout1.addWidget(self.result1, 9, 1)
        layout1.addWidget(self.result_unit1, 9, 2)
        widget1.setLayout(layout1)
        self.init_calculate1()
        self.calculate_button1.clicked.connect(self.calculate1)
        main_layout.addWidget(widget1, alignment=Qt.AlignTop | Qt.AlignHCenter)

        """ 镍生产成本 """
        main_layout.addWidget(HorizonSepLine(self))

        widget2 = QWidget(self)
        widget2.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout2 = QGridLayout()
        layout2.setContentsMargins(QMargins(MARGIN_LEFT, MARGIN_TOP, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name2 = NameLabel('镍生产成本', self)
        self.label21 = QLabel('镍矿Ni1.5-1.6价格', self)
        self.input21 = InputEdit(self)
        self.unit21 = QLabel('元/吨', self)

        layout2.addWidget(self.name2, 0, 0, 1, 3)
        layout2.addWidget(self.label21, 1, 0)
        layout2.addWidget(self.input21, 1, 1)
        layout2.addWidget(self.unit21, 1, 2)

        self.label22 = QLabel('运费', self)
        self.input22 = InputEdit(self)
        self.unit22 = QLabel('元/吨', self)

        layout2.addWidget(self.label22, 2, 0)
        layout2.addWidget(self.input22, 2, 1)
        layout2.addWidget(self.unit22, 2, 2)

        self.label23 = QLabel('硫酸价格', self)
        self.input23 = InputEdit(self)
        self.unit23 = QLabel('元/吨', self)

        layout2.addWidget(self.label23, 3, 0)
        layout2.addWidget(self.input23, 3, 1)
        layout2.addWidget(self.unit23, 3, 2)

        self.label24 = QLabel('石灰石价格', self)
        self.input24 = InputEdit(self)
        self.unit24 = QLabel('元/吨', self)

        layout2.addWidget(self.label24, 4, 0)
        layout2.addWidget(self.input24, 4, 1)
        layout2.addWidget(self.unit24, 4, 2)

        self.label25 = QLabel('冶炼电价', self)
        self.input25 = InputEdit(self)
        self.unit25 = QLabel('元/吨', self)

        layout2.addWidget(self.label25, 5, 0)
        layout2.addWidget(self.input25, 5, 1)
        layout2.addWidget(self.unit25, 5, 2)

        self.label26 = QLabel('焦炭价格', self)
        self.input26 = InputEdit(self)
        self.unit26 = QLabel('元/吨', self)

        layout2.addWidget(self.label26, 6, 0)
        layout2.addWidget(self.input26, 6, 1)
        layout2.addWidget(self.unit26, 6, 2)

        self.label27 = QLabel('其他费用', self)
        self.input27 = InputEdit(self)
        self.unit27 = QLabel('元/吨', self)

        layout2.addWidget(self.label27, 7, 0)
        layout2.addWidget(self.input27, 7, 1)
        layout2.addWidget(self.unit27, 7, 2)

        layout2.addWidget(QLabel(self), 8, 0)

        self.calculate_button2 = CalculateButton('试算成本', self)
        self.result2 = ResultLabel(self)
        self.result_unit2 = QLabel('元/吨', self)
        layout2.addWidget(self.calculate_button2, 9, 0)
        layout2.addWidget(self.result2, 9, 1)
        layout2.addWidget(self.result_unit2, 9, 2)
        widget2.setLayout(layout2)
        self.init_calculate2()
        self.calculate_button2.clicked.connect(self.calculate2)
        main_layout.addWidget(widget2, alignment=Qt.AlignTop | Qt.AlignHCenter)
        self.setLayout(main_layout)

    def init_calculate1(self):
        if self.USD_CNY_RATE:
            self.input14.set_value(self.USD_CNY_RATE, count=4)
        self.input15.set_value(13)
        self.input16.set_value(0)
        self.input17.set_value(150)

    def init_calculate2(self):
        self.input22.set_value(100)
        self.input25.set_value(0.5)
        self.input27.set_value(5000)

    def calculate1(self):
        # 计算镍进口成本
        # result = (a + b + c) * r * (1 + d) * (1 + e) + f
        # 镍进口成本=（LME三个月期货价格+现货升贴水+到岸升贴水）*汇率*（1+增值税率）*(1+关税税率)+港杂费
        a = self.input11.value()
        b = self.input12.value()
        c = self.input13.value()
        r = self.input14.value()
        d = self.input15.value(p=True)
        e = self.input16.value(p=True)
        f = self.input17.value()
        params = [a, b, c, r, d, e, f]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = (a + b + c) * r * (1 + d) * (1 + e) + f
        self.result1.set_value(result, count=4)

    def calculate2(self):
        # result = 100 * a + 100 * b + 70 * c + 10 * d + 15000 * e + 4 * f + g
        # 镍生产成本=100*镍矿价格+100*运费+70*硫酸价格+10*石灰石价格+15000*冶炼电价+4*焦炭价格+其他费用
        a = self.input21.value()
        b = self.input22.value()
        c = self.input23.value()
        d = self.input24.value()
        e = self.input25.value()
        f = self.input26.value()
        g = self.input27.value()
        params = [a, b, c, d, e, f, g]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = 100 * a + 100 * b + 70 * c + 10 * d + 15000 * e + 4 * f + g
        self.result2.set_value(result, count=4)


class P(QWidget):
    RATE_DATA = rate.get_all_exchange_rate()

    def __init__(self, *args, **kwargs):
        super(P, self).__init__(*args, **kwargs)
        self.USD_CNY_RATE = self.RATE_DATA.get('USD/CNY', None)
        if self.USD_CNY_RATE:
            self.USD_CNY_RATE = float(self.USD_CNY_RATE)
        main_layout = QVBoxLayout()
        """ 棕榈油进口成本 """
        widget1 = QWidget(self)
        widget1.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout1 = QGridLayout()
        layout1.setContentsMargins(QMargins(MARGIN_LEFT, 0, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name1 = NameLabel('棕榈油进口成本', self)
        self.label11 = QLabel('FOB价格', self)
        self.input11 = InputEdit(self)
        self.unit11 = QLabel('美元/吨', self)

        layout1.addWidget(self.name1, 0, 0, 1, 3)
        layout1.addWidget(self.label11, 1, 0)
        layout1.addWidget(self.input11, 1, 1)
        layout1.addWidget(self.unit11, 1, 2)

        self.label12 = QLabel('运费', self)
        self.input12 = InputEdit(self)
        self.unit12 = QLabel('美元/吨', self)

        layout1.addWidget(self.label12, 2, 0)
        layout1.addWidget(self.input12, 2, 1)
        layout1.addWidget(self.unit12, 2, 2)

        self.label13 = QLabel('增值税', self)
        self.input13 = InputEdit(self)
        self.unit13 = QLabel('%', self)

        layout1.addWidget(self.label13, 3, 0)
        layout1.addWidget(self.input13, 3, 1)
        layout1.addWidget(self.unit13, 3, 2)

        self.label14 = QLabel('关税', self)
        self.input14 = InputEdit(self)
        self.unit14 = QLabel('%', self)

        layout1.addWidget(self.label14, 4, 0)
        layout1.addWidget(self.input14, 4, 1)
        layout1.addWidget(self.unit14, 4, 2)

        self.label15 = QLabel('汇率', self)
        self.input15 = InputEdit(self)
        self.unit15 = QLabel('USD/CNY', self)

        layout1.addWidget(self.label15, 5, 0)
        layout1.addWidget(self.input15, 5, 1)
        layout1.addWidget(self.unit15, 5, 2)

        self.label16 = QLabel('港杂费', self)
        self.input16 = InputEdit(self)
        self.unit16 = QLabel('元/吨', self)

        layout1.addWidget(self.label16, 6, 0)
        layout1.addWidget(self.input16, 6, 1)
        layout1.addWidget(self.unit16, 6, 2)

        layout1.addWidget(QLabel(self), 7, 0)

        self.calculate_button1 = CalculateButton('试算成本', self)
        self.result1 = ResultLabel(self)
        self.result_unit1 = QLabel('元/吨', self)
        layout1.addWidget(self.calculate_button1, 8, 0)
        layout1.addWidget(self.result1, 8, 1)
        layout1.addWidget(self.result_unit1, 8, 2)
        widget1.setLayout(layout1)
        self.init_calculate1()
        self.calculate_button1.clicked.connect(self.calculate1)
        main_layout.addWidget(widget1, alignment=Qt.AlignTop | Qt.AlignHCenter)

        self.setLayout(main_layout)

    def init_calculate1(self):
        if self.USD_CNY_RATE:
            self.input15.set_value(self.USD_CNY_RATE, count=4)
        self.input12.set_value(24)
        self.input13.set_value(13)
        self.input14.set_value(9)
        self.input16.set_value(120)

    def calculate1(self):
        # 棕榈油进口成本=（FOB价格+运费）*（1+增值税）*（1+关税）*汇率+港杂费
        # result = (a + b) * (1 + c) * (1 + d) * r + e
        a = self.input11.value()
        b = self.input12.value()
        c = self.input13.value(p=True)
        d = self.input14.value(p=True)
        r = self.input15.value()
        e = self.input16.value()
        params = [a, b, c, d, r, e]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = (a + b) * (1 + c) * (1 + d) * r + e
        self.result1.set_value(result, count=4)


class PB(QWidget):

    RATE_DATA = rate.get_all_exchange_rate()

    def __init__(self, *args, **kwargs):
        super(PB, self).__init__(*args, **kwargs)
        self.USD_CNY_RATE = self.RATE_DATA.get('USD/CNY', None)
        if self.USD_CNY_RATE:
            self.USD_CNY_RATE = float(self.USD_CNY_RATE)
        main_layout = QVBoxLayout()
        """ 铅进口成本 """
        widget1 = QWidget(self)
        widget1.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout1 = QGridLayout()
        layout1.setContentsMargins(QMargins(MARGIN_LEFT, 0, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name1 = NameLabel('铅进口成本', self)
        self.label11 = QLabel('LME三个月期货价', self)
        self.input11 = InputEdit(self)
        self.unit11 = QLabel('美元/吨', self)

        layout1.addWidget(self.name1, 0, 0, 1, 3)
        layout1.addWidget(self.label11, 1, 0)
        layout1.addWidget(self.input11, 1, 1)
        layout1.addWidget(self.unit11, 1, 2)

        self.label12 = QLabel('现货升贴水', self)
        self.input12 = InputEdit(self)
        self.unit12 = QLabel('美元/吨', self)

        layout1.addWidget(self.label12, 2, 0)
        layout1.addWidget(self.input12, 2, 1)
        layout1.addWidget(self.unit12, 2, 2)

        self.label13 = QLabel('到岸升贴水', self)
        self.input13 = InputEdit(self)
        self.unit13 = QLabel('美元/吨', self)

        layout1.addWidget(self.label13, 3, 0)
        layout1.addWidget(self.input13, 3, 1)
        layout1.addWidget(self.unit13, 3, 2)

        self.label14 = QLabel('汇率', self)
        self.input14 = InputEdit(self)
        self.unit14 = QLabel('USD/CNY', self)

        layout1.addWidget(self.label14, 4, 0)
        layout1.addWidget(self.input14, 4, 1)
        layout1.addWidget(self.unit14, 4, 2)

        self.label15 = QLabel('增值税率', self)
        self.input15 = InputEdit(self)
        self.unit15 = QLabel('%', self)

        layout1.addWidget(self.label15, 5, 0)
        layout1.addWidget(self.input15, 5, 1)
        layout1.addWidget(self.unit15, 5, 2)

        self.label16 = QLabel('关税税率', self)
        self.input16 = InputEdit(self)
        self.unit16 = QLabel('%', self)

        layout1.addWidget(self.label16, 6, 0)
        layout1.addWidget(self.input16, 6, 1)
        layout1.addWidget(self.unit16, 6, 2)

        self.label17 = QLabel('港杂费', self)
        self.input17 = InputEdit(self)
        self.unit17 = QLabel('元/吨', self)

        layout1.addWidget(self.label17, 7, 0)
        layout1.addWidget(self.input17, 7, 1)
        layout1.addWidget(self.unit17, 7, 2)

        layout1.addWidget(QLabel(self), 8, 0)

        self.calculate_button1 = CalculateButton('试算成本', self)
        self.result1 = ResultLabel(self)
        self.result_unit1 = QLabel('元/吨', self)
        layout1.addWidget(self.calculate_button1, 9, 0)
        layout1.addWidget(self.result1, 9, 1)
        layout1.addWidget(self.result_unit1, 9, 2)
        widget1.setLayout(layout1)
        self.init_calculate1()
        self.calculate_button1.clicked.connect(self.calculate1)
        main_layout.addWidget(widget1, alignment=Qt.AlignTop | Qt.AlignHCenter)

        self.setLayout(main_layout)

    def init_calculate1(self):
        if self.USD_CNY_RATE:
            self.input14.set_value(self.USD_CNY_RATE, count=4)
        self.input15.set_value(13)
        self.input16.set_value(3)
        self.input17.set_value(150)

    def calculate1(self):
        # 计算铅进口成本
        # result = (a + b + c) * r * (1 + d) * (1 + e) + f
        # 铅进口成本=（LME三个月期货价格+现货升贴水+到岸升贴水）*汇率*（1+增值税率）*(1+关税税率)+港杂费
        a = self.input11.value()
        b = self.input12.value()
        c = self.input13.value()
        r = self.input14.value()
        d = self.input15.value(p=True)
        e = self.input16.value(p=True)
        f = self.input17.value()
        params = [a, b, c, r, d, e, f]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = (a + b + c) * r * (1 + d) * (1 + e) + f
        self.result1.set_value(result, count=4)


class PF(QWidget):
    RATE_DATA = rate.get_all_exchange_rate()

    def __init__(self, *args, **kwargs):
        super(PF, self).__init__(*args, **kwargs)
        self.USD_CNY_RATE = self.RATE_DATA.get('USD/CNY', None)
        if self.USD_CNY_RATE:
            self.USD_CNY_RATE = float(self.USD_CNY_RATE)
        main_layout = QVBoxLayout()
        """ 短纤原料成本 """
        widget1 = QWidget(self)
        widget1.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout1 = QGridLayout()
        layout1.setContentsMargins(QMargins(MARGIN_LEFT, 0, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name1 = NameLabel('短纤原料成本', self)
        self.label11 = QLabel('乙二醇现货价(华东)', self)
        self.input11 = InputEdit(self)
        self.unit11 = QLabel('元/吨', self)

        layout1.addWidget(self.name1, 0, 0, 1, 3)
        layout1.addWidget(self.label11, 1, 0)
        layout1.addWidget(self.input11, 1, 1)
        layout1.addWidget(self.unit11, 1, 2)

        self.label12 = QLabel('PTA现货价(华东)', self)
        self.input12 = InputEdit(self)
        self.unit12 = QLabel('元/吨', self)

        layout1.addWidget(self.label12, 2, 0)
        layout1.addWidget(self.input12, 2, 1)
        layout1.addWidget(self.unit12, 2, 2)

        layout1.addWidget(QLabel(self), 3, 0)

        self.calculate_button1 = CalculateButton('试算成本', self)
        self.result1 = ResultLabel(self)
        self.result_unit1 = QLabel('元/吨', self)
        layout1.addWidget(self.calculate_button1, 4, 0)
        layout1.addWidget(self.result1, 4, 1)
        layout1.addWidget(self.result_unit1, 4, 2)
        widget1.setLayout(layout1)
        self.init_calculate1()
        self.calculate_button1.clicked.connect(self.calculate1)
        main_layout.addWidget(widget1, alignment=Qt.AlignTop | Qt.AlignHCenter)

        self.setLayout(main_layout)

    def init_calculate1(self):
        pass

    def calculate1(self):
        # 短纤原料成本=乙二醇现货价（华东）×0.335+PTA现货价（华东）×0.855
        # result = a * 0.335 + b * 0.855
        a = self.input11.value()
        b = self.input12.value()
        params = [a, b]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = a * 0.335 + b * 0.855
        self.result1.set_value(result, count=4)


class PG(QWidget):
    RATE_DATA = rate.get_all_exchange_rate()

    def __init__(self, *args, **kwargs):
        super(PG, self).__init__(*args, **kwargs)
        self.USD_CNY_RATE = self.RATE_DATA.get('USD/CNY', None)
        if self.USD_CNY_RATE:
            self.USD_CNY_RATE = float(self.USD_CNY_RATE)
        main_layout = QVBoxLayout()
        """ 液化石油气进口成本 """
        widget1 = QWidget(self)
        widget1.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout1 = QGridLayout()
        layout1.setContentsMargins(QMargins(MARGIN_LEFT, 0, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name1 = NameLabel('液化石油气进口成本', self)
        self.label11 = QLabel('液化气到岸价', self)
        self.input11 = InputEdit(self)
        self.unit11 = QLabel('美元/吨', self)

        layout1.addWidget(self.name1, 0, 0, 1, 3)
        layout1.addWidget(self.label11, 1, 0)
        layout1.addWidget(self.input11, 1, 1)
        layout1.addWidget(self.unit11, 1, 2)

        self.label12 = QLabel('关税', self)
        self.input12 = InputEdit(self)
        self.unit12 = QLabel('%', self)

        layout1.addWidget(self.label12, 2, 0)
        layout1.addWidget(self.input12, 2, 1)
        layout1.addWidget(self.unit12, 2, 2)

        self.label13 = QLabel('增值税', self)
        self.input13 = InputEdit(self)
        self.unit13 = QLabel('%', self)

        layout1.addWidget(self.label13, 3, 0)
        layout1.addWidget(self.input13, 3, 1)
        layout1.addWidget(self.unit13, 3, 2)

        self.label14 = QLabel('汇率', self)
        self.input14 = InputEdit(self)
        self.unit14 = QLabel('USD/CNY', self)

        layout1.addWidget(self.label14, 4, 0)
        layout1.addWidget(self.input14, 4, 1)
        layout1.addWidget(self.unit14, 4, 2)

        layout1.addWidget(QLabel(self), 5, 0)

        self.calculate_button1 = CalculateButton('试算成本', self)
        self.result1 = ResultLabel(self)
        self.result_unit1 = QLabel('元/吨', self)
        layout1.addWidget(self.calculate_button1, 6, 0)
        layout1.addWidget(self.result1, 6, 1)
        layout1.addWidget(self.result_unit1, 6, 2)
        widget1.setLayout(layout1)
        self.init_calculate1()
        self.calculate_button1.clicked.connect(self.calculate1)
        main_layout.addWidget(widget1, alignment=Qt.AlignTop | Qt.AlignHCenter)

        self.setLayout(main_layout)

    def init_calculate1(self):
        if self.USD_CNY_RATE:
            self.input14.set_value(self.USD_CNY_RATE, count=4)
        self.input12.set_value(1)
        self.input13.set_value(9)

    def calculate1(self):
        # 液化石油气进口成本 =液化石油气到岸价×(1+增值税)×(1+关税)×汇率
        # result = a * (1 + b) * (1 + c) * r
        a = self.input11.value()
        b = self.input12.value(p=True)
        c = self.input13.value(p=True)
        r = self.input14.value()
        params = [a, b, c, r]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = a * (1 + b) * (1 + c) * r
        self.result1.set_value(result, count=4)


class PM(QWidget):
    RATE_DATA = rate.get_all_exchange_rate()

    def __init__(self, *args, **kwargs):
        super(PM, self).__init__(*args, **kwargs)
        self.USD_CNY_RATE = self.RATE_DATA.get('USD/CNY', None)
        if self.USD_CNY_RATE:
            self.USD_CNY_RATE = float(self.USD_CNY_RATE)
        main_layout = QVBoxLayout()
        """ 小麦进口成本 """
        widget1 = QWidget(self)
        widget1.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout1 = QGridLayout()
        layout1.setContentsMargins(QMargins(MARGIN_LEFT, 0, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name1 = NameLabel('小麦进口成本', self)
        self.label11 = QLabel('CBOT小麦期价', self)
        self.input11 = InputEdit(self)
        self.unit11 = QLabel('美分/蒲式耳', self)

        layout1.addWidget(self.name1, 0, 0, 1, 3)
        layout1.addWidget(self.label11, 1, 0)
        layout1.addWidget(self.input11, 1, 1)
        layout1.addWidget(self.unit11, 1, 2)

        self.label12 = QLabel('升贴水', self)
        self.input12 = InputEdit(self)
        self.unit12 = QLabel('美分/蒲式耳', self)

        layout1.addWidget(self.label12, 2, 0)
        layout1.addWidget(self.input12, 2, 1)
        layout1.addWidget(self.unit12, 2, 2)

        self.label13 = QLabel('海运费', self)
        self.input13 = InputEdit(self)
        self.unit13 = QLabel('美元/吨', self)

        layout1.addWidget(self.label13, 3, 0)
        layout1.addWidget(self.input13, 3, 1)
        layout1.addWidget(self.unit13, 3, 2)

        self.label14 = QLabel('增值税', self)
        self.input14 = InputEdit(self)
        self.unit14 = QLabel('%', self)

        layout1.addWidget(self.label14, 4, 0)
        layout1.addWidget(self.input14, 4, 1)
        layout1.addWidget(self.unit14, 4, 2)

        self.label15 = QLabel('关税', self)
        self.input15 = InputEdit(self)
        self.unit15 = QLabel('%', self)

        layout1.addWidget(self.label15, 5, 0)
        layout1.addWidget(self.input15, 5, 1)
        layout1.addWidget(self.unit15, 5, 2)

        self.label16 = QLabel('汇率', self)
        self.input16 = InputEdit(self)
        self.unit16 = QLabel('USD/CNY', self)

        layout1.addWidget(self.label16, 6, 0)
        layout1.addWidget(self.input16, 6, 1)
        layout1.addWidget(self.unit16, 6, 2)

        self.label17 = QLabel('港杂费', self)
        self.input17 = InputEdit(self)
        self.unit17 = QLabel('元/吨', self)

        layout1.addWidget(self.label17, 7, 0)
        layout1.addWidget(self.input17, 7, 1)
        layout1.addWidget(self.unit17, 7, 2)

        layout1.addWidget(QLabel(self), 8, 0)

        self.calculate_button1 = CalculateButton('试算成本', self)
        self.result1 = ResultLabel(self)
        self.result_unit1 = QLabel('元/吨', self)
        layout1.addWidget(self.calculate_button1, 9, 0)
        layout1.addWidget(self.result1, 9, 1)
        layout1.addWidget(self.result_unit1, 9, 2)
        widget1.setLayout(layout1)
        self.init_calculate1()
        self.calculate_button1.clicked.connect(self.calculate1)
        main_layout.addWidget(widget1, alignment=Qt.AlignTop | Qt.AlignHCenter)

        self.setLayout(main_layout)

    def init_calculate1(self):
        if self.USD_CNY_RATE:
            self.input16.set_value(self.USD_CNY_RATE, count=4)
        self.input13.set_value(27)
        self.input14.set_value(9)
        self.input15.set_value(1)

    def calculate1(self):
        # 小麦进口成本=〔（CBOT小麦期价＋升贴水）×0.367437＋海运费〕×(1+增值税)×(1+关税)×汇率＋港杂费
        # result = ((a + b) * 0.367437 + c) * (1 + d) * (1 + e) * r + f
        a = self.input11.value()
        b = self.input12.value()
        c = self.input13.value()
        d = self.input14.value(p=True)
        e = self.input15.value(p=True)
        r = self.input16.value()
        f = self.input17.value()
        params = [a, b, c, d, e, r, f]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = ((a + b) * 0.367437 + c) * (1 + d) * (1 + e) * r + f
        self.result1.set_value(result, count=4)


class PP(QWidget):
    RATE_DATA = rate.get_all_exchange_rate()

    def __init__(self, *args, **kwargs):
        super(PP, self).__init__(*args, **kwargs)
        self.USD_CNY_RATE = self.RATE_DATA.get('USD/CNY', None)
        if self.USD_CNY_RATE:
            self.USD_CNY_RATE = float(self.USD_CNY_RATE)
        main_layout = QVBoxLayout()
        """ 油制PP生产成本 """
        widget1 = QWidget(self)
        widget1.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout1 = QGridLayout()
        layout1.setContentsMargins(QMargins(MARGIN_LEFT, 0, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name1 = NameLabel('油制PP生产成本', self)
        self.label11 = QLabel('亚洲石脑油', self)
        self.input11 = InputEdit(self)
        self.unit11 = QLabel('美元', self)

        layout1.addWidget(self.name1, 0, 0, 1, 3)
        layout1.addWidget(self.label11, 1, 0)
        layout1.addWidget(self.input11, 1, 1)
        layout1.addWidget(self.unit11, 1, 2)

        self.label12 = QLabel('汇率', self)
        self.input12 = InputEdit(self)
        self.unit12 = QLabel('USD/CNY', self)

        layout1.addWidget(self.label12, 2, 0)
        layout1.addWidget(self.input12, 2, 1)
        layout1.addWidget(self.unit12, 2, 2)

        self.label13 = QLabel('生产比', self)
        self.input13 = InputEdit(self)
        self.unit13 = QLabel(self)

        layout1.addWidget(self.label13, 3, 0)
        layout1.addWidget(self.input13, 3, 1)
        layout1.addWidget(self.unit13, 3, 2)

        self.label14 = QLabel('桶吨比', self)
        self.input14 = InputEdit(self)
        self.unit14 = QLabel(self)

        layout1.addWidget(self.label14, 4, 0)
        layout1.addWidget(self.input14, 4, 1)
        layout1.addWidget(self.unit14, 4, 2)

        self.label15 = QLabel('增值税', self)
        self.input15 = InputEdit(self)
        self.unit15 = QLabel('%', )

        layout1.addWidget(self.label15, 5, 0)
        layout1.addWidget(self.input15, 5, 1)
        layout1.addWidget(self.unit15, 5, 2)

        self.label16 = QLabel('杂费', self)
        self.input16 = InputEdit(self)
        self.unit16 = QLabel('元/吨', self)

        layout1.addWidget(self.label16, 6, 0)
        layout1.addWidget(self.input16, 6, 1)
        layout1.addWidget(self.unit16, 6, 2)

        layout1.addWidget(QLabel(self), 7, 0)

        self.calculate_button1 = CalculateButton('试算成本', self)
        self.result1 = ResultLabel(self)
        self.result_unit1 = QLabel('元/吨', self)
        layout1.addWidget(self.calculate_button1, 8, 0)
        layout1.addWidget(self.result1, 8, 1)
        layout1.addWidget(self.result_unit1, 8, 2)
        widget1.setLayout(layout1)
        self.init_calculate1()
        self.calculate_button1.clicked.connect(self.calculate1)
        main_layout.addWidget(widget1, alignment=Qt.AlignTop | Qt.AlignHCenter)

        """ 煤制PP生产成本 """
        main_layout.addWidget(HorizonSepLine(self))

        widget2 = QWidget(self)
        widget2.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout2 = QGridLayout()
        layout2.setContentsMargins(QMargins(MARGIN_LEFT, MARGIN_TOP, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name2 = NameLabel('煤制PP生产成本', self)
        self.label21 = QLabel('原煤', self)
        self.input21 = InputEdit(self)
        self.unit21 = QLabel('元', self)

        layout2.addWidget(self.name2, 0, 0, 1, 3)
        layout2.addWidget(self.label21, 1, 0)
        layout2.addWidget(self.input21, 1, 1)
        layout2.addWidget(self.unit21, 1, 2)

        self.label22 = QLabel('甲醇生产比', self)
        self.input22 = InputEdit(self)
        self.unit22 = QLabel('', self)

        layout2.addWidget(self.label22, 2, 0)
        layout2.addWidget(self.input22, 2, 1)
        layout2.addWidget(self.unit22, 2, 2)

        self.label23 = QLabel('甲醇生产杂费', self)
        self.input23 = InputEdit(self)
        self.unit23 = QLabel('元', self)

        layout2.addWidget(self.label23, 3, 0)
        layout2.addWidget(self.input23, 3, 1)
        layout2.addWidget(self.unit23, 3, 2)

        self.label24 = QLabel('丙烯生产比', self)
        self.input24 = InputEdit(self)
        self.unit24 = QLabel(self)

        layout2.addWidget(self.label24, 4, 0)
        layout2.addWidget(self.input24, 4, 1)
        layout2.addWidget(self.unit24, 4, 2)

        self.label25 = QLabel('丙烯生产杂费', self)
        self.input25 = InputEdit(self)
        self.unit25 = QLabel('元', self)

        layout2.addWidget(self.label25, 5, 0)
        layout2.addWidget(self.input25, 5, 1)
        layout2.addWidget(self.unit25, 5, 2)

        self.label26 = QLabel('聚丙烯生产比', self)
        self.input26 = InputEdit(self)
        self.unit26 = QLabel('', self)

        layout2.addWidget(self.label26, 6, 0)
        layout2.addWidget(self.input26, 6, 1)
        layout2.addWidget(self.unit26, 6, 2)

        self.label27 = QLabel('聚丙烯生产杂费', self)
        self.input27 = InputEdit(self)
        self.unit27 = QLabel('元', self)

        layout2.addWidget(self.label27, 7, 0)
        layout2.addWidget(self.input27, 7, 1)
        layout2.addWidget(self.unit27, 7, 2)

        layout2.addWidget(QLabel(self), 8, 0)
        self.calculate_button2 = CalculateButton('试算成本', self)
        self.result2 = ResultLabel(self)
        self.result_unit2 = QLabel('元/吨', self)
        layout2.addWidget(self.calculate_button2, 9, 0)
        layout2.addWidget(self.result2, 9, 1)
        layout2.addWidget(self.result_unit2, 9, 2)
        widget2.setLayout(layout2)
        self.init_calculate2()
        self.calculate_button2.clicked.connect(self.calculate2)
        main_layout.addWidget(widget2, alignment=Qt.AlignTop | Qt.AlignHCenter)

        """ PDH PP生产成本 """
        main_layout.addWidget(HorizonSepLine(self))

        widget3 = QWidget(self)
        widget3.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout3 = QGridLayout()
        layout3.setContentsMargins(QMargins(MARGIN_LEFT, MARGIN_TOP, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name3 = NameLabel('PDH PP生产成本', self)
        self.label31 = QLabel('北亚地区丙烷', self)
        self.input31 = InputEdit(self)
        self.unit31 = QLabel('美元', self)

        layout3.addWidget(self.name3, 0, 0, 1, 3)
        layout3.addWidget(self.label31, 1, 0)
        layout3.addWidget(self.input31, 1, 1)
        layout3.addWidget(self.unit31, 1, 2)

        self.label32 = QLabel('聚丙烯生产比', self)
        self.input32 = InputEdit(self)
        self.unit32 = QLabel('', self)

        layout3.addWidget(self.label32, 2, 0)
        layout3.addWidget(self.input32, 2, 1)
        layout3.addWidget(self.unit32, 2, 2)

        self.label33 = QLabel('汇率', self)
        self.input33 = InputEdit(self)
        self.unit33 = QLabel('USD/CNY', self)

        layout3.addWidget(self.label33, 3, 0)
        layout3.addWidget(self.input33, 3, 1)
        layout3.addWidget(self.unit33, 3, 2)

        self.label34 = QLabel('杂费', self)
        self.input34 = InputEdit(self)
        self.unit34 = QLabel('元/吨', self)

        layout3.addWidget(self.label34, 4, 0)
        layout3.addWidget(self.input34, 4, 1)
        layout3.addWidget(self.unit34, 4, 2)

        layout3.addWidget(QLabel(self), 5, 0)

        self.calculate_button3 = CalculateButton('试算成本', self)
        self.result3 = ResultLabel(self)
        self.result_unit3 = QLabel('元/吨', self)
        layout3.addWidget(self.calculate_button3, 6, 0)
        layout3.addWidget(self.result3, 6, 1)
        layout3.addWidget(self.result_unit3, 6, 2)
        widget3.setLayout(layout3)
        self.init_calculate3()
        self.calculate_button3.clicked.connect(self.calculate3)
        main_layout.addWidget(widget3, alignment=Qt.AlignTop | Qt.AlignHCenter)

        """ 外采甲醇 PP生产成本 """
        main_layout.addWidget(HorizonSepLine(self))

        widget4 = QWidget(self)
        widget4.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout4 = QGridLayout()
        layout4.setContentsMargins(QMargins(MARGIN_LEFT, MARGIN_TOP, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name4 = NameLabel('外采甲醇 PP生产成本', self)
        self.label41 = QLabel('甲醇价格', self)
        self.input41 = InputEdit(self)
        self.unit41 = QLabel('元/吨', self)

        layout4.addWidget(self.name4, 0, 0, 1, 3)
        layout4.addWidget(self.label41, 1, 0)
        layout4.addWidget(self.input41, 1, 1)
        layout4.addWidget(self.unit41, 1, 2)

        self.label42 = QLabel('生产比', self)
        self.input42 = InputEdit(self)
        self.unit42 = QLabel('', self)

        layout4.addWidget(self.label42, 2, 0)
        layout4.addWidget(self.input42, 2, 1)
        layout4.addWidget(self.unit42, 2, 2)

        self.label43 = QLabel('杂费', self)
        self.input43 = InputEdit(self)
        self.unit43 = QLabel('元/吨', self)

        layout4.addWidget(self.label43, 3, 0)
        layout4.addWidget(self.input43, 3, 1)
        layout4.addWidget(self.unit43, 3, 2)

        layout4.addWidget(QLabel(self), 4, 0)

        self.calculate_button4 = CalculateButton('试算成本', self)
        self.result4 = ResultLabel(self)
        self.result_unit4 = QLabel('元/吨', self)
        layout4.addWidget(self.calculate_button4, 5, 0)
        layout4.addWidget(self.result4, 5, 1)
        layout4.addWidget(self.result_unit4, 5, 2)
        widget4.setLayout(layout4)
        self.init_calculate4()
        self.calculate_button4.clicked.connect(self.calculate4)
        main_layout.addWidget(widget4, alignment=Qt.AlignTop | Qt.AlignHCenter)

        self.setLayout(main_layout)

    def init_calculate1(self):
        if self.USD_CNY_RATE:
            self.input12.set_value(self.USD_CNY_RATE, count=4)
        self.input13.set_value(1.35)
        self.input14.set_value(7.2)
        self.input15.set_value(13)
        self.input16.set_value(1085)

    def init_calculate2(self):
        self.input22.set_value(1.5)
        self.input23.set_value(300)
        self.input24.set_value(3)
        self.input25.set_value(1800)
        self.input26.set_value(1.1)
        self.input27.set_value(800)

    def init_calculate3(self):
        if self.USD_CNY_RATE:
            self.input33.set_value(self.USD_CNY_RATE, count=4)
        self.input32.set_value(1.18)
        self.input34.set_value(2300)

    def init_calculate4(self):
        self.input42.set_value(3)
        self.input43.set_value(1500)

    def calculate1(self):
        # 油制PP生产成本=（Brent原油+4）*聚丙烯生产比*汇率*7.2桶吨比*增值税+杂费
        # result = (a + 4) * b * r * c * (1 + d) + e
        a = self.input11.value()
        b = self.input13.value()
        r = self.input12.value()
        c = self.input14.value()
        d = self.input15.value()
        e = self.input16.value()

        params = [a, b, c, d, e, r]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = (a + 4) * b * r * c * (1 + d) + e
        self.result1.set_value(result, count=4)

    def calculate2(self):
        # 煤制PP生产成本={3*（1.5煤+300其他费用）+1800}*1.1+800
        # 煤制PP生产成本={丙烯生产比 *（甲醇生产比 * 煤 + 生产杂费）+ 丙烯生产杂费}* 聚丙烯生产比 + 聚丙烯生产杂费
        # result = (a * (b * c + d) + e) * f + g
        a = self.input24.value()
        b = self.input22.value()
        c = self.input21.value()
        d = self.input23.value()
        e = self.input25.value()
        f = self.input26.value()
        g = self.input27.value()
        params = [a, b, c, d, e, f, g]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = (a * (b * c + d) + e) * f + g
        self.result2.set_value(result, count=4)

    def calculate3(self):
        # PDH  PP生产成本=北亚地区丙烷*聚丙烯生产比*汇率+杂费
        # result = a * b * r + c
        a = self.input31.value()
        b = self.input32.value()
        r = self.input33.value()
        c = self.input34.value()
        params = [a, b, c, r]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = a * b * r + c
        self.result3.set_value(result, count=4)

    def calculate4(self):
        # 外采甲醇  PP生产成本=甲醇价格*聚丙烯生产比+杂费
        # result = a * b + c
        a = self.input41.value()
        b = self.input42.value()
        c = self.input43.value()
        params = [a, b, c]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = a * b + c
        self.result4.set_value(result, count=4)


class RB(QWidget):
    RATE_DATA = rate.get_all_exchange_rate()

    def __init__(self, *args, **kwargs):
        super(RB, self).__init__(*args, **kwargs)
        self.USD_CNY_RATE = self.RATE_DATA.get('USD/CNY', None)
        if self.USD_CNY_RATE:
            self.USD_CNY_RATE = float(self.USD_CNY_RATE)
        main_layout = QVBoxLayout()
        """ 螺纹钢生产成本 """
        widget1 = QWidget(self)
        widget1.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout1 = QGridLayout()
        layout1.setContentsMargins(QMargins(MARGIN_LEFT, 0, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name1 = NameLabel('螺纹钢生产成本', self)
        self.label11 = QLabel('铁矿石价格', self)
        self.input11 = InputEdit(self)
        self.unit11 = QLabel('元/吨', self)

        layout1.addWidget(self.name1, 0, 0, 1, 3)
        layout1.addWidget(self.label11, 1, 0)
        layout1.addWidget(self.input11, 1, 1)
        layout1.addWidget(self.unit11, 1, 2)

        self.label12 = QLabel('焦炭价格', self)
        self.input12 = InputEdit(self)
        self.unit12 = QLabel('元/吨', self)

        layout1.addWidget(self.label12, 2, 0)
        layout1.addWidget(self.input12, 2, 1)
        layout1.addWidget(self.unit12, 2, 2)

        self.label13 = QLabel('废钢价格', self)
        self.input13 = InputEdit(self)
        self.unit13 = QLabel('元/吨', self)

        layout1.addWidget(self.label13, 3, 0)
        layout1.addWidget(self.input13, 3, 1)
        layout1.addWidget(self.unit13, 3, 2)

        self.label14 = QLabel('合金', self)
        self.input14 = InputEdit(self)
        self.unit14 = QLabel('元/吨', self)

        layout1.addWidget(self.label14, 4, 0)
        layout1.addWidget(self.input14, 4, 1)
        layout1.addWidget(self.unit14, 4, 2)

        self.label15 = QLabel('轧钢费用', self)
        self.input15 = InputEdit(self)
        self.unit15 = QLabel('元/吨', self)

        layout1.addWidget(self.label15, 5, 0)
        layout1.addWidget(self.input15, 5, 1)
        layout1.addWidget(self.unit15, 5, 2)

        layout1.addWidget(QLabel(self), 6, 0)

        self.calculate_button1 = CalculateButton('试算成本', self)
        self.result1 = ResultLabel(self)
        self.result_unit1 = QLabel('元/吨', self)
        layout1.addWidget(self.calculate_button1, 7, 0)
        layout1.addWidget(self.result1, 7, 1)
        layout1.addWidget(self.result_unit1, 7, 2)
        widget1.setLayout(layout1)
        self.init_calculate1()
        self.calculate_button1.clicked.connect(self.calculate1)
        main_layout.addWidget(widget1, alignment=Qt.AlignTop | Qt.AlignHCenter)

        self.setLayout(main_layout)

    def init_calculate1(self):
        self.input14.set_value(80)
        self.input15.set_value(150)

    def calculate1(self):
        # 螺纹钢生产成本 =〔（（1.6×铁矿石+0.4×焦炭）/0.9）×0.96＋（0.12×废钢）〕/0.9 + 合金 + 轧钢费用
        # result = ((1.6 * a + 0.4 * b) / 0.9 * 0.96 + (0.12 * c)) / 0.9 + d + e
        a = self.input11.value()
        b = self.input12.value()
        c = self.input13.value()
        d = self.input14.value()
        e = self.input15.value()
        params = [a, b, c, d, e]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = ((1.6 * a + 0.4 * b) / 0.9 * 0.96 + (0.12 * c)) / 0.9 + d + e
        self.result1.set_value(result, count=4)


class RS(QWidget):
    RATE_DATA = rate.get_all_exchange_rate()

    def __init__(self, *args, **kwargs):
        super(RS, self).__init__(*args, **kwargs)
        self.USD_CNY_RATE = self.RATE_DATA.get('USD/CNY', None)
        if self.USD_CNY_RATE:
            self.USD_CNY_RATE = float(self.USD_CNY_RATE)
        main_layout = QVBoxLayout()
        """ 油菜籽进口成本 """
        widget1 = QWidget(self)
        widget1.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout1 = QGridLayout()
        layout1.setContentsMargins(QMargins(MARGIN_LEFT, 0, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name1 = NameLabel('油菜籽进口成本', self)
        self.label11 = QLabel('CNF到岸价', self)
        self.input11 = InputEdit(self)
        self.unit11 = QLabel('美元/吨', self)

        layout1.addWidget(self.name1, 0, 0, 1, 3)
        layout1.addWidget(self.label11, 1, 0)
        layout1.addWidget(self.input11, 1, 1)
        layout1.addWidget(self.unit11, 1, 2)

        self.label12 = QLabel('增值税', self)
        self.input12 = InputEdit(self)
        self.unit12 = QLabel('%', self)

        layout1.addWidget(self.label12, 2, 0)
        layout1.addWidget(self.input12, 2, 1)
        layout1.addWidget(self.unit12, 2, 2)

        self.label13 = QLabel('关税', self)
        self.input13 = InputEdit(self)
        self.unit13 = QLabel('%', self)

        layout1.addWidget(self.label13, 3, 0)
        layout1.addWidget(self.input13, 3, 1)
        layout1.addWidget(self.unit13, 3, 2)

        self.label14 = QLabel('汇率', self)
        self.input14 = InputEdit(self)
        self.unit14 = QLabel('USD/CNY', self)

        layout1.addWidget(self.label14, 4, 0)
        layout1.addWidget(self.input14, 4, 1)
        layout1.addWidget(self.unit14, 4, 2)

        self.label15 = QLabel('港杂费', self)
        self.input15 = InputEdit(self)
        self.unit15 = QLabel('元/吨', self)

        layout1.addWidget(self.label15, 5, 0)
        layout1.addWidget(self.input15, 5, 1)
        layout1.addWidget(self.unit15, 5, 2)

        layout1.addWidget(QLabel(self), 6, 0)

        self.calculate_button1 = CalculateButton('试算成本', self)
        self.result1 = ResultLabel(self)
        self.result_unit1 = QLabel('元/吨', self)
        layout1.addWidget(self.calculate_button1, 7, 0)
        layout1.addWidget(self.result1, 7, 1)
        layout1.addWidget(self.result_unit1, 7, 2)
        widget1.setLayout(layout1)
        self.init_calculate1()
        self.calculate_button1.clicked.connect(self.calculate1)
        main_layout.addWidget(widget1, alignment=Qt.AlignTop | Qt.AlignHCenter)

        """ 油菜籽压榨利润 """
        main_layout.addWidget(HorizonSepLine(self))

        widget2 = QWidget(self)
        widget2.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout2 = QGridLayout()
        layout2.setContentsMargins(QMargins(MARGIN_LEFT, MARGIN_TOP, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name2 = NameLabel('油菜籽压榨利润', self)
        self.label21 = QLabel('菜粕现货价格', self)
        self.input21 = InputEdit(self)
        self.unit21 = QLabel('元/吨', self)

        layout2.addWidget(self.name2, 0, 0, 1, 3)
        layout2.addWidget(self.label21, 1, 0)
        layout2.addWidget(self.input21, 1, 1)
        layout2.addWidget(self.unit21, 1, 2)

        self.label22 = QLabel('菜油现货价格', self)
        self.input22 = InputEdit(self)
        self.unit22 = QLabel('元/吨', self)

        layout2.addWidget(self.label22, 2, 0)
        layout2.addWidget(self.input22, 2, 1)
        layout2.addWidget(self.unit22, 2, 2)

        self.label23 = QLabel('油菜籽成本', self)
        self.input23 = InputEdit(self)
        self.unit23 = QLabel('元/吨', self)

        layout2.addWidget(self.label23, 3, 0)
        layout2.addWidget(self.input23, 3, 1)
        layout2.addWidget(self.unit23, 3, 2)

        self.label24 = QLabel('加工费', self)
        self.input24 = InputEdit(self)
        self.unit24 = QLabel('元/吨', self)

        layout2.addWidget(self.label24, 4, 0)
        layout2.addWidget(self.input24, 4, 1)
        layout2.addWidget(self.unit24, 4, 2)

        layout2.addWidget(QLabel(self), 5, 0)
        self.calculate_button2 = CalculateButton('试算利润', self)
        self.result2 = ResultLabel(self)
        self.result_unit2 = QLabel('元/吨', self)
        layout2.addWidget(self.calculate_button2, 6, 0)
        layout2.addWidget(self.result2, 6, 1)
        layout2.addWidget(self.result_unit2, 6, 2)
        widget2.setLayout(layout2)
        self.init_calculate2()
        self.calculate_button2.clicked.connect(self.calculate2)
        main_layout.addWidget(widget2, alignment=Qt.AlignTop | Qt.AlignHCenter)
        self.setLayout(main_layout)

    def init_calculate1(self):
        if self.USD_CNY_RATE:
            self.input14.set_value(self.USD_CNY_RATE, count=4)
        self.input12.set_value(9)
        self.input13.set_value(9)
        self.input15.set_value(110)

    def init_calculate2(self):
        self.input24.set_value(200)

    def calculate1(self):
        # 计算镍进口成本
        # result = a *(1 + b)*(1+c) * r + d
        # 油菜籽进口成本 =CNF到岸价×(1+增值税)×(1+关税)×汇率＋港杂费
        a = self.input11.value()
        b = self.input12.value(p=True)
        c = self.input13.value(p=True)
        r = self.input14.value()
        d = self.input15.value()
        params = [a, b, c, d, r]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = a * (1 + b) * (1+c) * r + d
        self.result1.set_value(result, count=4)

    def calculate2(self):
        # 油菜籽压榨利润=菜粕现货价格*0.53+菜油现货价格*0.43-油菜籽成本-加工费
        # result = a * 0.53 + b * 0.43 - c - d
        a = self.input21.value()
        b = self.input22.value()
        c = self.input23.value()
        d = self.input24.value()
        params = [a, b, c, d]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = a * 0.53 + b * 0.43 - c - d
        self.result2.set_value(result, count=4)


class RU(QWidget):
    RATE_DATA = rate.get_all_exchange_rate()

    def __init__(self, *args, **kwargs):
        super(RU, self).__init__(*args, **kwargs)
        self.USD_CNY_RATE = self.RATE_DATA.get('USD/CNY', None)
        self.CNY_THB_RATE = self.RATE_DATA.get('CNY/THB', None)
        if self.USD_CNY_RATE:
            self.USD_CNY_RATE = float(self.USD_CNY_RATE)
        if self.CNY_THB_RATE:
            self.CNY_THB_RATE = float(self.CNY_THB_RATE)
        if self.USD_CNY_RATE and self.CNY_THB_RATE:
            self.USD_THB_RATE = round(self.USD_CNY_RATE * self.CNY_THB_RATE, 4)
        else:
            self.USD_THB_RATE = None
        main_layout = QVBoxLayout()
        """ 烟片成本 """
        widget1 = QWidget(self)
        widget1.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout1 = QGridLayout()
        layout1.setContentsMargins(QMargins(MARGIN_LEFT, 0, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name1 = NameLabel('烟片成本', self)
        self.label11 = QLabel('白片价格', self)
        self.input11 = InputEdit(self)
        self.unit11 = QLabel('泰铢/公斤', self)

        layout1.addWidget(self.name1, 0, 0, 1, 3)
        layout1.addWidget(self.label11, 1, 0)
        layout1.addWidget(self.input11, 1, 1)
        layout1.addWidget(self.unit11, 1, 2)

        self.label12 = QLabel('加工费', self)
        self.input12 = InputEdit(self)
        self.unit12 = QLabel('泰铢/公斤', self)

        layout1.addWidget(self.label12, 2, 0)
        layout1.addWidget(self.input12, 2, 1)
        layout1.addWidget(self.unit12, 2, 2)

        self.label13 = QLabel('汇率', self)
        self.input13 = InputEdit(self)
        self.unit13 = QLabel('USD/THB', self)

        layout1.addWidget(self.label13, 3, 0)
        layout1.addWidget(self.input13, 3, 1)
        layout1.addWidget(self.unit13, 3, 2)

        layout1.addWidget(QLabel(self), 4, 0)

        self.calculate_button1 = CalculateButton('试算成本', self)
        self.result1 = ResultLabel(self)
        self.result_unit1 = QLabel('美元/吨', self)
        layout1.addWidget(self.calculate_button1, 5, 0)
        layout1.addWidget(self.result1, 5, 1)
        layout1.addWidget(self.result_unit1, 5, 2)
        widget1.setLayout(layout1)
        self.init_calculate1()
        self.calculate_button1.clicked.connect(self.calculate1)
        main_layout.addWidget(widget1, alignment=Qt.AlignTop | Qt.AlignHCenter)

        """ 标胶成本 """
        main_layout.addWidget(HorizonSepLine(self))

        widget2 = QWidget(self)
        widget2.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout2 = QGridLayout()
        layout2.setContentsMargins(QMargins(MARGIN_LEFT, MARGIN_TOP, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name2 = NameLabel('标胶成本', self)
        self.label21 = QLabel('杯胶价格', self)
        self.input21 = InputEdit(self)
        self.unit21 = QLabel('泰铢/公斤', self)

        layout2.addWidget(self.name2, 0, 0, 1, 3)
        layout2.addWidget(self.label21, 1, 0)
        layout2.addWidget(self.input21, 1, 1)
        layout2.addWidget(self.unit21, 1, 2)

        self.label22 = QLabel('加工费', self)
        self.input22 = InputEdit(self)
        self.unit22 = QLabel('泰铢/公斤', self)

        layout2.addWidget(self.label22, 2, 0)
        layout2.addWidget(self.input22, 2, 1)
        layout2.addWidget(self.unit22, 2, 2)

        self.label23 = QLabel('汇率', self)
        self.input23 = InputEdit(self)
        self.unit23 = QLabel('USD/THB', self)

        layout2.addWidget(self.label23, 3, 0)
        layout2.addWidget(self.input23, 3, 1)
        layout2.addWidget(self.unit23, 3, 2)

        layout2.addWidget(QLabel(self), 4, 0)
        self.calculate_button2 = CalculateButton('试算成本', self)
        self.result2 = ResultLabel(self)
        self.result_unit2 = QLabel('美元/吨', self)
        layout2.addWidget(self.calculate_button2, 5, 0)
        layout2.addWidget(self.result2, 5, 1)
        layout2.addWidget(self.result_unit2, 5, 2)
        widget2.setLayout(layout2)
        self.init_calculate2()
        self.calculate_button2.clicked.connect(self.calculate2)
        main_layout.addWidget(widget2, alignment=Qt.AlignTop | Qt.AlignHCenter)

        """ 天然橡胶进口利润 """
        main_layout.addWidget(HorizonSepLine(self))

        widget3 = QWidget(self)
        widget3.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout3 = QGridLayout()
        layout3.setContentsMargins(QMargins(MARGIN_LEFT, MARGIN_TOP, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name3 = NameLabel('天然橡胶进口利润', self)
        self.label31 = QLabel('全乳胶现货价', self)
        self.input31 = InputEdit(self)
        self.unit31 = QLabel('元/吨', self)

        layout3.addWidget(self.name3, 0, 0, 1, 3)
        layout3.addWidget(self.label31, 1, 0)
        layout3.addWidget(self.input31, 1, 1)
        layout3.addWidget(self.unit31, 1, 2)

        self.label32 = QLabel('CIF青岛主港STR20', self)
        self.input32 = InputEdit(self)
        self.unit32 = QLabel('美元/吨', self)

        layout3.addWidget(self.label32, 2, 0)
        layout3.addWidget(self.input32, 2, 1)
        layout3.addWidget(self.unit32, 2, 2)

        self.label33 = QLabel('汇率', self)
        self.input33 = InputEdit(self)
        self.unit33 = QLabel('USD/CNY', self)

        layout3.addWidget(self.label33, 3, 0)
        layout3.addWidget(self.input33, 3, 1)
        layout3.addWidget(self.unit33, 3, 2)

        self.label34 = QLabel('增值税', self)
        self.input34 = InputEdit(self)
        self.unit34 = QLabel('%', self)

        layout3.addWidget(self.label34, 4, 0)
        layout3.addWidget(self.input34, 4, 1)
        layout3.addWidget(self.unit34, 4, 2)

        self.label35 = QLabel('关税', self)
        self.input35 = InputEdit(self)
        self.unit35 = QLabel('%', self)

        layout3.addWidget(self.label35, 5, 0)
        layout3.addWidget(self.input35, 5, 1)
        layout3.addWidget(self.unit35, 5, 2)

        self.label36 = QLabel('港杂费', self)
        self.input36 = InputEdit(self)
        self.unit36 = QLabel('元/吨', self)

        layout3.addWidget(self.label36, 6, 0)
        layout3.addWidget(self.input36, 6, 1)
        layout3.addWidget(self.unit36, 6, 2)

        layout3.addWidget(QLabel(self), 7, 0)

        self.calculate_button3 = CalculateButton('试算成本', self)
        self.result3 = ResultLabel(self)
        self.result_unit3 = QLabel('元/斤', self)
        layout3.addWidget(self.calculate_button3, 8, 0)
        layout3.addWidget(self.result3, 8, 1)
        layout3.addWidget(self.result_unit3, 8, 2)
        widget3.setLayout(layout3)
        self.init_calculate3()
        self.calculate_button3.clicked.connect(self.calculate3)
        main_layout.addWidget(widget3, alignment=Qt.AlignTop | Qt.AlignHCenter)
        self.setLayout(main_layout)

    def init_calculate1(self):
        if self.USD_THB_RATE:
            self.input13.set_value(self.USD_THB_RATE)
        self.input12.set_value(9)

    def init_calculate2(self):
        self.input22.set_value(9)
        if self.USD_THB_RATE:
            self.input23.set_value(self.USD_THB_RATE)

    def init_calculate3(self):
        if self.USD_CNY_RATE:
            self.input33.set_value(self.USD_CNY_RATE, count=4)
        self.input34.set_value(13)
        self.input35.set_value(20)
        self.input36.set_value(350)

    def calculate1(self):
        # 烟片成本=（白片+加工费）*1000/汇率
        # result = (a + b) * 1000 / r
        a = self.input11.value()
        b = self.input12.value()
        r = self.input13.value()
        params = [a, b, r]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = (a + b) * 1000 / r
        self.result1.set_value(result, count=4)

    def calculate2(self):
        # 标胶成本=（杯胶+加工费）*1000/汇率
        # result = (a + b) * 1000 / r
        a = self.input21.value()
        b = self.input22.value()
        r = self.input23.value()
        params = [a, b, r]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = (a + b) * 1000 / r
        self.result2.set_value(result, count=4)

    def calculate3(self):
        # 天然橡胶进口利润=全乳胶现货价-CIF青岛主港STR20*汇率*(1 + 增值税) * （1 + 关税） - 港杂费
        # result = a - b * r * (1 + c) * (1 + d) - e
        a = self.input31.value()
        b = self.input32.value()
        c = self.input34.value(p=True)
        d = self.input35.value(p=True)
        e = self.input36.value()
        r = self.input33.value()
        params = [a, b, c, d, e, r]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = a - b * r * (1 + c) * (1 + d) - e
        self.result3.set_value(result, count=4)


class SC(QWidget):
    RATE_DATA = rate.get_all_exchange_rate()

    def __init__(self, *args, **kwargs):
        super(SC, self).__init__(*args, **kwargs)
        self.USD_CNY_RATE = self.RATE_DATA.get('USD/CNY', None)
        if self.USD_CNY_RATE:
            self.USD_CNY_RATE = float(self.USD_CNY_RATE)
        main_layout = QVBoxLayout()
        """ 进口保税原油成本 """
        widget1 = QWidget(self)
        widget1.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout1 = QGridLayout()
        layout1.setContentsMargins(QMargins(MARGIN_LEFT, 0, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name1 = NameLabel('进口保税原油成本', self)
        self.label11 = QLabel('原油现货价格', self)
        self.input11 = InputEdit(self)
        self.unit11 = QLabel('美元/桶', self)

        layout1.addWidget(self.name1, 0, 0, 1, 3)
        layout1.addWidget(self.label11, 1, 0)
        layout1.addWidget(self.input11, 1, 1)
        layout1.addWidget(self.unit11, 1, 2)

        self.label12 = QLabel('升贴水', self)
        self.input12 = InputEdit(self)
        self.unit12 = QLabel('美元/桶', self)

        layout1.addWidget(self.label12, 2, 0)
        layout1.addWidget(self.input12, 2, 1)
        layout1.addWidget(self.unit12, 2, 2)

        self.label13 = QLabel('海运费', self)
        self.input13 = InputEdit(self)
        self.unit13 = QLabel('美元/桶', self)

        layout1.addWidget(self.label13, 3, 0)
        layout1.addWidget(self.input13, 3, 1)
        layout1.addWidget(self.unit13, 3, 2)

        self.label14 = QLabel('汇率', self)
        self.input14 = InputEdit(self)
        self.unit14 = QLabel('USD/CNY', self)

        layout1.addWidget(self.label14, 4, 0)
        layout1.addWidget(self.input14, 4, 1)
        layout1.addWidget(self.unit14, 4, 2)

        self.label15 = QLabel('港杂费', self)
        self.input15 = InputEdit(self)
        self.unit15 = QLabel('元/吨', self)

        layout1.addWidget(self.label15, 5, 0)
        layout1.addWidget(self.input15, 5, 1)
        layout1.addWidget(self.unit15, 5, 2)

        layout1.addWidget(QLabel(self), 6, 0)

        self.calculate_button1 = CalculateButton('试算成本', self)
        self.result1 = ResultLabel(self)
        self.result_unit1 = QLabel('元/吨', self)
        layout1.addWidget(self.calculate_button1, 7, 0)
        layout1.addWidget(self.result1, 7, 1)
        layout1.addWidget(self.result_unit1, 7, 2)
        widget1.setLayout(layout1)
        self.init_calculate1()
        self.calculate_button1.clicked.connect(self.calculate1)
        main_layout.addWidget(widget1, alignment=Qt.AlignTop | Qt.AlignHCenter)

        self.setLayout(main_layout)

    def init_calculate1(self):
        if self.USD_CNY_RATE:
            self.input14.set_value(self.USD_CNY_RATE, count=4)

    def calculate1(self):
        # 进口保税原油成本 =〔（原油价格＋升贴水）＋海运费〕×汇率＋港杂费
        # result = (a + b + c) * r + d
        a = self.input11.value()
        b = self.input12.value()
        c = self.input13.value()
        r = self.input14.value()
        d = self.input15.value()

        params = [a, b, c, d, r]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = (a + b + c) * r + d
        self.result1.set_value(result, count=4)


class SF(QWidget):
    RATE_DATA = rate.get_all_exchange_rate()

    def __init__(self, *args, **kwargs):
        super(SF, self).__init__(*args, **kwargs)
        self.USD_CNY_RATE = self.RATE_DATA.get('USD/CNY', None)
        if self.USD_CNY_RATE:
            self.USD_CNY_RATE = float(self.USD_CNY_RATE)
        main_layout = QVBoxLayout()
        """ 硅铁生产成本 """
        widget1 = QWidget(self)
        widget1.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout1 = QGridLayout()
        layout1.setContentsMargins(QMargins(MARGIN_LEFT, 0, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name1 = NameLabel('硅铁生产成本', self)
        self.label11 = QLabel('硅石价格', self)
        self.input11 = InputEdit(self)
        self.unit11 = QLabel('元/吨', self)

        layout1.addWidget(self.name1, 0, 0, 1, 3)
        layout1.addWidget(self.label11, 1, 0)
        layout1.addWidget(self.input11, 1, 1)
        layout1.addWidget(self.unit11, 1, 2)

        self.label12 = QLabel('兰炭价格', self)
        self.input12 = InputEdit(self)
        self.unit12 = QLabel('元/吨', self)

        layout1.addWidget(self.label12, 2, 0)
        layout1.addWidget(self.input12, 2, 1)
        layout1.addWidget(self.unit12, 2, 2)

        self.label13 = QLabel('用电价格', self)
        self.input13 = InputEdit(self)
        self.unit13 = QLabel('元/吨', self)

        layout1.addWidget(self.label13, 3, 0)
        layout1.addWidget(self.input13, 3, 1)
        layout1.addWidget(self.unit13, 3, 2)

        self.label14 = QLabel('氧化铁皮', self)
        self.input14 = InputEdit(self)
        self.unit14 = QLabel('元/吨', self)

        layout1.addWidget(self.label14, 4, 0)
        layout1.addWidget(self.input14, 4, 1)
        layout1.addWidget(self.unit14, 4, 2)

        self.label15 = QLabel('辅料价格', self)
        self.input15 = InputEdit(self)
        self.unit15 = QLabel('元/吨', self)

        layout1.addWidget(self.label15, 5, 0)
        layout1.addWidget(self.input15, 5, 1)
        layout1.addWidget(self.unit15, 5, 2)

        layout1.addWidget(QLabel(self), 6, 0)
        self.calculate_button1 = CalculateButton('试算成本', self)
        self.result1 = ResultLabel(self)
        self.result_unit1 = QLabel('元/吨', self)
        layout1.addWidget(self.calculate_button1, 7, 0)
        layout1.addWidget(self.result1, 7, 1)
        layout1.addWidget(self.result_unit1, 7, 2)
        widget1.setLayout(layout1)
        self.init_calculate1()
        self.calculate_button1.clicked.connect(self.calculate1)
        main_layout.addWidget(widget1, alignment=Qt.AlignTop | Qt.AlignHCenter)

        self.setLayout(main_layout)

    def init_calculate1(self):
        self.input15.set_value(300)

    def calculate1(self):
        # result = 1.75 * a + 1.15 * b + 8000 * c + 0.025 * d + e
        # 硅铁成本=1.75*硅石+1.15*兰炭+8000*电价+0.025*氧化铁皮+辅料
        a = self.input11.value()
        b = self.input12.value()
        c = self.input13.value()
        d = self.input14.value()
        e = self.input15.value()
        params = [a, b, c, d, e]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = 1.75 * a + 1.15 * b + 8000 * c + 0.025 * d + e
        self.result1.set_value(result, count=4)


class SM(QWidget):
    RATE_DATA = rate.get_all_exchange_rate()

    def __init__(self, *args, **kwargs):
        super(SM, self).__init__(*args, **kwargs)
        self.USD_CNY_RATE = self.RATE_DATA.get('USD/CNY', None)
        if self.USD_CNY_RATE:
            self.USD_CNY_RATE = float(self.USD_CNY_RATE)
        main_layout = QVBoxLayout()
        """ 锰矿成本 """
        widget1 = QWidget(self)
        widget1.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout1 = QGridLayout()
        layout1.setContentsMargins(QMargins(MARGIN_LEFT, 0, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name1 = NameLabel('锰矿成本计算', self)
        self.label11 = QLabel('澳块价格', self)
        self.input11 = InputEdit(self)
        self.unit11 = QLabel('元/吨', self)

        layout1.addWidget(self.name1, 0, 0, 1, 3)
        layout1.addWidget(self.label11, 1, 0)
        layout1.addWidget(self.input11, 1, 1)
        layout1.addWidget(self.unit11, 1, 2)

        self.label12 = QLabel('南非半碳酸', self)
        self.input12 = InputEdit(self)
        self.unit12 = QLabel('元/吨', self)

        layout1.addWidget(self.label12, 2, 0)
        layout1.addWidget(self.input12, 2, 1)
        layout1.addWidget(self.unit12, 2, 2)

        self.label13 = QLabel('加蓬', self)
        self.input13 = InputEdit(self)
        self.unit13 = QLabel('元/吨', self)

        layout1.addWidget(self.label13, 3, 0)
        layout1.addWidget(self.input13, 3, 1)
        layout1.addWidget(self.unit13, 3, 2)

        self.label14 = QLabel('巴西', self)
        self.input14 = InputEdit(self)
        self.unit14 = QLabel('元/吨', self)

        layout1.addWidget(self.label14, 4, 0)
        layout1.addWidget(self.input14, 4, 1)
        layout1.addWidget(self.unit14, 4, 2)

        self.label15 = QLabel('低品半碳酸', self)
        self.input15 = InputEdit(self)
        self.unit15 = QLabel('元/吨', self)

        layout1.addWidget(self.label15, 5, 0)
        layout1.addWidget(self.input15, 5, 1)
        layout1.addWidget(self.unit15, 5, 2)

        self.label16 = QLabel('其他', self)
        self.input16 = InputEdit(self)
        self.unit16 = QLabel('元/吨', self)

        layout1.addWidget(self.label16, 6, 0)
        layout1.addWidget(self.input16, 6, 1)
        layout1.addWidget(self.unit16, 6, 2)

        layout1.addWidget(QLabel(self), 7, 0)

        self.calculate_button1 = CalculateButton('试算成本', self)
        self.result1 = ResultLabel(self)
        self.result_unit1 = QLabel('元/吨', self)
        layout1.addWidget(self.calculate_button1, 8, 0)
        layout1.addWidget(self.result1, 8, 1)
        layout1.addWidget(self.result_unit1, 8, 2)
        widget1.setLayout(layout1)
        self.init_calculate1()
        self.calculate_button1.clicked.connect(self.calculate1)
        main_layout.addWidget(widget1, alignment=Qt.AlignTop | Qt.AlignHCenter)

        """ 锰硅生产成本 """
        main_layout.addWidget(HorizonSepLine(self))

        widget2 = QWidget(self)
        widget2.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout2 = QGridLayout()
        layout2.setContentsMargins(QMargins(MARGIN_LEFT, MARGIN_TOP, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name2 = NameLabel('锰硅生产成本', self)
        self.label21 = QLabel('锰矿价格', self)
        self.input21 = InputEdit(self)
        self.unit21 = QLabel('元/吨', self)

        layout2.addWidget(self.name2, 0, 0, 1, 3)
        layout2.addWidget(self.label21, 1, 0)
        layout2.addWidget(self.input21, 1, 1)
        layout2.addWidget(self.unit21, 1, 2)

        self.label22 = QLabel('焦炭价格', self)
        self.input22 = InputEdit(self)
        self.unit22 = QLabel('元/吨', self)

        layout2.addWidget(self.label22, 2, 0)
        layout2.addWidget(self.input22, 2, 1)
        layout2.addWidget(self.unit22, 2, 2)

        self.label23 = QLabel('电费', self)
        self.input23 = InputEdit(self)
        self.unit23 = QLabel('元/吨', self)

        layout2.addWidget(self.label23, 3, 0)
        layout2.addWidget(self.input23, 3, 1)
        layout2.addWidget(self.unit23, 3, 2)

        self.label24 = QLabel('辅料', self)
        self.input24 = InputEdit(self)
        self.unit24 = QLabel('元/吨', self)

        layout2.addWidget(self.label24, 4, 0)
        layout2.addWidget(self.input24, 4, 1)
        layout2.addWidget(self.unit24, 4, 2)

        layout2.addWidget(QLabel(self), 5, 0)
        self.calculate_button2 = CalculateButton('试算成本', self)
        self.result2 = ResultLabel(self)
        self.result_unit2 = QLabel('元/吨', self)
        layout2.addWidget(self.calculate_button2, 6, 0)
        layout2.addWidget(self.result2, 6, 1)
        layout2.addWidget(self.result_unit2, 6, 2)
        widget2.setLayout(layout2)
        self.init_calculate2()
        self.calculate_button2.clicked.connect(self.calculate2)
        main_layout.addWidget(widget2, alignment=Qt.AlignTop | Qt.AlignHCenter)
        self.setLayout(main_layout)

    def init_calculate1(self):
        self.input16.set_value(80)

    def init_calculate2(self):
        self.input24.set_value(400)

    def calculate1(self):
        # 计算锰矿成本
        # 锰矿成本=（澳块*15%+南非半碳酸*40%+加蓬*15%+巴西*15%+低品半碳酸*15%）+其他
        # 锰矿成本= 南非半碳酸 * 40% + (澳块+加蓬+巴西+低品半碳酸) * 0.15 +其他
        # result = a * 0.4 + (b + c + d + e) * 0.15 + f
        a = self.input12.value()
        b = self.input11.value()
        c = self.input13.value()
        d = self.input14.value()
        e = self.input15.value()
        f = self.input16.value()
        params = [a, b, c, d, e, f]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = a * 0.4 + (b + c + d + e) * 0.15 + f
        self.result1.set_value(result, count=4)

    def calculate2(self):
        # result = 2.1 * a + 0.55 * b + 4000 * c + d
        # 锰硅成本=2.1*锰矿+0.55*焦炭+4000*电费+辅料
        a = self.input21.value()
        b = self.input22.value()
        c = self.input23.value()
        d = self.input24.value()
        params = [a, b, c, d]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = 2.1 * a + 0.55 * b + 4000 * c + d
        self.result2.set_value(result, count=4)


class SN(QWidget):
    RATE_DATA = rate.get_all_exchange_rate()

    def __init__(self, *args, **kwargs):
        super(SN, self).__init__(*args, **kwargs)
        self.USD_CNY_RATE = self.RATE_DATA.get('USD/CNY', None)
        if self.USD_CNY_RATE:
            self.USD_CNY_RATE = float(self.USD_CNY_RATE)
        main_layout = QVBoxLayout()
        """ 锡进口成本 """
        widget1 = QWidget(self)
        widget1.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout1 = QGridLayout()
        layout1.setContentsMargins(QMargins(MARGIN_LEFT, 0, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name1 = NameLabel('锡进口成本', self)
        self.label11 = QLabel('LME三个月期货价', self)
        self.input11 = InputEdit(self)
        self.unit11 = QLabel('美元/吨', self)

        layout1.addWidget(self.name1, 0, 0, 1, 3)
        layout1.addWidget(self.label11, 1, 0)
        layout1.addWidget(self.input11, 1, 1)
        layout1.addWidget(self.unit11, 1, 2)

        self.label12 = QLabel('LME锡升贴水', self)
        self.input12 = InputEdit(self)
        self.unit12 = QLabel('美元/吨', self)

        layout1.addWidget(self.label12, 2, 0)
        layout1.addWidget(self.input12, 2, 1)
        layout1.addWidget(self.unit12, 2, 2)

        self.label13 = QLabel('CIF到岸升贴水', self)
        self.input13 = InputEdit(self)
        self.unit13 = QLabel('美元/吨', self)

        layout1.addWidget(self.label13, 3, 0)
        layout1.addWidget(self.input13, 3, 1)
        layout1.addWidget(self.unit13, 3, 2)

        self.label14 = QLabel('汇率', self)
        self.input14 = InputEdit(self)
        self.unit14 = QLabel('USD/CNY', self)

        layout1.addWidget(self.label14, 4, 0)
        layout1.addWidget(self.input14, 4, 1)
        layout1.addWidget(self.unit14, 4, 2)

        self.label15 = QLabel('增值税率', self)
        self.input15 = InputEdit(self)
        self.unit15 = QLabel('%', self)

        layout1.addWidget(self.label15, 5, 0)
        layout1.addWidget(self.input15, 5, 1)
        layout1.addWidget(self.unit15, 5, 2)

        self.label16 = QLabel('关税税率', self)
        self.input16 = InputEdit(self)
        self.unit16 = QLabel('%', self)

        layout1.addWidget(self.label16, 6, 0)
        layout1.addWidget(self.input16, 6, 1)
        layout1.addWidget(self.unit16, 6, 2)

        self.label17 = QLabel('港杂费', self)
        self.input17 = InputEdit(self)
        self.unit17 = QLabel('元/吨', self)

        layout1.addWidget(self.label17, 7, 0)
        layout1.addWidget(self.input17, 7, 1)
        layout1.addWidget(self.unit17, 7, 2)

        layout1.addWidget(QLabel(self), 8, 0)

        self.calculate_button1 = CalculateButton('试算成本', self)
        self.result1 = ResultLabel(self)
        self.result_unit1 = QLabel('元/吨', self)
        layout1.addWidget(self.calculate_button1, 9, 0)
        layout1.addWidget(self.result1, 9, 1)
        layout1.addWidget(self.result_unit1, 9, 2)
        widget1.setLayout(layout1)
        self.init_calculate1()
        self.calculate_button1.clicked.connect(self.calculate1)
        main_layout.addWidget(widget1, alignment=Qt.AlignTop | Qt.AlignHCenter)

        self.setLayout(main_layout)

    def init_calculate1(self):
        if self.USD_CNY_RATE:
            self.input14.set_value(self.USD_CNY_RATE, count=4)
        self.input15.set_value(13)
        self.input16.set_value(8)
        self.input17.set_value(150)

    def calculate1(self):
        # 计算锡进口成本
        # result = (a + b + c) * r * (1 + d) * (1 + e) + f
        # 锡进口成本=（LME三个月期货价格+现货升贴水+到岸升贴水）*汇率*（1+增值税率）*(1+关税税率)+港杂费
        a = self.input11.value()
        b = self.input12.value()
        c = self.input13.value()
        r = self.input14.value()
        d = self.input15.value(p=True)
        e = self.input16.value(p=True)
        f = self.input17.value()
        params = [a, b, c, r, d, e, f]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = (a + b + c) * r * (1 + d) * (1 + e) + f
        self.result1.set_value(result, count=4)


class SP(QWidget):
    RATE_DATA = rate.get_all_exchange_rate()

    def __init__(self, *args, **kwargs):
        super(SP, self).__init__(*args, **kwargs)
        self.USD_CNY_RATE = self.RATE_DATA.get('USD/CNY', None)
        if self.USD_CNY_RATE:
            self.USD_CNY_RATE = float(self.USD_CNY_RATE)
        main_layout = QVBoxLayout()
        """ 银星纸浆进口成本 """
        widget1 = QWidget(self)
        widget1.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout1 = QGridLayout()
        layout1.setContentsMargins(QMargins(MARGIN_LEFT, 0, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name1 = NameLabel('银星纸浆进口成本', self)
        self.label11 = QLabel('银星CFR', self)
        self.input11 = InputEdit(self)
        self.unit11 = QLabel('美元/吨', self)

        layout1.addWidget(self.name1, 0, 0, 1, 3)
        layout1.addWidget(self.label11, 1, 0)
        layout1.addWidget(self.input11, 1, 1)
        layout1.addWidget(self.unit11, 1, 2)

        self.label12 = QLabel('汇率', self)
        self.input12 = InputEdit(self)
        self.unit12 = QLabel('USD/CNY', self)

        layout1.addWidget(self.label12, 2, 0)
        layout1.addWidget(self.input12, 2, 1)
        layout1.addWidget(self.unit12, 2, 2)

        self.label13 = QLabel('港杂费', self)
        self.input13 = InputEdit(self)
        self.unit13 = QLabel('元/吨', self)

        layout1.addWidget(self.label13, 3, 0)
        layout1.addWidget(self.input13, 3, 1)
        layout1.addWidget(self.unit13, 3, 2)

        layout1.addWidget(QLabel(self), 4, 0)

        self.calculate_button1 = CalculateButton('试算成本', self)
        self.result1 = ResultLabel(self)
        self.result_unit1 = QLabel('元/吨', self)
        layout1.addWidget(self.calculate_button1, 5, 0)
        layout1.addWidget(self.result1, 5, 1)
        layout1.addWidget(self.result_unit1, 5, 2)
        widget1.setLayout(layout1)
        self.init_calculate1()
        self.calculate_button1.clicked.connect(self.calculate1)
        main_layout.addWidget(widget1, alignment=Qt.AlignTop | Qt.AlignHCenter)

        self.setLayout(main_layout)

    def init_calculate1(self):
        if self.USD_CNY_RATE:
            self.input12.set_value(self.USD_CNY_RATE, count=4)
        self.input13.set_value(22)

    def calculate1(self):
        # 银星纸浆进口成本=银星CFR*汇率+港杂费
        # result = a * r + b
        a = self.input11.value()
        b = self.input13.value()
        r = self.input12.value()
        params = [a, b, r]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = a * r + b
        self.result1.set_value(result, count=4)


class SR(QWidget):

    RATE_DATA = rate.get_all_exchange_rate()

    def __init__(self, *args, **kwargs):
        super(SR, self).__init__(*args, **kwargs)
        self.USD_CNY_RATE = self.RATE_DATA.get('USD/CNY', None)
        if self.USD_CNY_RATE:
            self.USD_CNY_RATE = float(self.USD_CNY_RATE)
        main_layout = QVBoxLayout()
        """ 进口糖成本测算 """
        widget1 = QWidget(self)
        widget1.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout1 = QGridLayout()
        layout1.setContentsMargins(QMargins(MARGIN_LEFT, 0, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name1 = NameLabel('进口糖成本测算', self)
        self.label11 = QLabel('原糖价格', self)
        self.input11 = InputEdit(self)
        self.unit11 = QLabel('美分/磅', self)

        layout1.addWidget(self.name1, 0, 0, 1, 3)
        layout1.addWidget(self.label11, 1, 0)
        layout1.addWidget(self.input11, 1, 1)
        layout1.addWidget(self.unit11, 1, 2)

        self.label12 = QLabel('升贴水', self)
        self.input12 = InputEdit(self)
        self.unit12 = QLabel('', self)

        layout1.addWidget(self.label12, 2, 0)
        layout1.addWidget(self.input12, 2, 1)
        layout1.addWidget(self.unit12, 2, 2)

        self.label13 = QLabel('海外运费', self)
        self.input13 = InputEdit(self)
        self.unit13 = QLabel('美元/吨', self)

        layout1.addWidget(self.label13, 3, 0)
        layout1.addWidget(self.input13, 3, 1)
        layout1.addWidget(self.unit13, 3, 2)

        self.label14 = QLabel('银行手续费率', self)
        self.input14 = InputEdit(self)
        self.unit14 = QLabel('%', self)

        layout1.addWidget(self.label14, 4, 0)
        layout1.addWidget(self.input14, 4, 1)
        layout1.addWidget(self.unit14, 4, 2)

        self.label15 = QLabel('增值税率', self)
        self.input15 = InputEdit(self)
        self.unit15 = QLabel('%', self)

        layout1.addWidget(self.label15, 5, 0)
        layout1.addWidget(self.input15, 5, 1)
        layout1.addWidget(self.unit15, 5, 2)

        self.label16 = QLabel('耗损率', self)
        self.input16 = InputEdit(self)
        self.unit16 = QLabel('%', self)

        layout1.addWidget(self.label16, 6, 0)
        layout1.addWidget(self.input16, 6, 1)
        layout1.addWidget(self.unit16, 6, 2)

        self.label17 = QLabel('汇率', self)
        self.input17 = InputEdit(self)
        self.unit17 = QLabel('USD/CNY', self)

        layout1.addWidget(self.label17, 7, 0)
        layout1.addWidget(self.input17, 7, 1)
        layout1.addWidget(self.unit17, 7, 2)

        self.label18 = QLabel('海外保险费率', self)
        self.input18 = InputEdit(self)
        self.unit18 = QLabel('%', self)

        layout1.addWidget(self.label18, 8, 0)
        layout1.addWidget(self.input18, 8, 1)
        layout1.addWidget(self.unit18, 8, 2)

        self.label19 = QLabel('利息及劳务费', self)
        self.input19 = InputEdit(self)
        self.unit19 = QLabel('美元/吨', self)

        layout1.addWidget(self.label19, 9, 0)
        layout1.addWidget(self.input19, 9, 1)
        layout1.addWidget(self.unit19, 9, 2)

        self.label110 = QLabel('外贸代理费率', self)
        self.input110 = InputEdit(self)
        self.unit110 = QLabel('%', self)

        layout1.addWidget(self.label110, 10, 0)
        layout1.addWidget(self.input110, 10, 1)
        layout1.addWidget(self.unit110, 10, 2)

        self.label111 = QLabel('海关关税率', self)
        self.input111 = InputEdit(self)
        self.unit111 = QLabel('%', self)

        layout1.addWidget(self.label111, 11, 0)
        layout1.addWidget(self.input111, 11, 1)
        layout1.addWidget(self.unit111, 11, 2)

        self.label112 = QLabel('加工及运杂费', self)
        self.input112 = InputEdit(self)
        self.unit112 = QLabel('美元/吨', self)

        layout1.addWidget(self.label112, 12, 0)
        layout1.addWidget(self.input112, 12, 1)
        layout1.addWidget(self.unit112, 12, 2)

        self.label113 = QLabel('旋光度增值', self)
        self.input113 = InputEdit(self)
        self.unit113 = QLabel('', self)

        layout1.addWidget(self.label113, 13, 0)
        layout1.addWidget(self.input113, 13, 1)
        layout1.addWidget(self.unit113, 13, 2)

        layout1.addWidget(QLabel(self), 14, 0)

        self.calculate_button1 = CalculateButton('试算成本', self)
        self.result1 = ResultLabel(self)
        self.result_unit1 = QLabel('元/吨', self)
        layout1.addWidget(self.calculate_button1, 15, 0)
        layout1.addWidget(self.result1, 15, 1)
        layout1.addWidget(self.result_unit1, 15, 2)
        widget1.setLayout(layout1)
        self.init_calculate1()
        self.calculate_button1.clicked.connect(self.calculate1)
        main_layout.addWidget(widget1, alignment=Qt.AlignTop | Qt.AlignHCenter)

        self.setLayout(main_layout)

    def init_calculate1(self):
        if self.USD_CNY_RATE:
            self.input17.set_value(self.USD_CNY_RATE)
        self.input11.set_value(16)
        self.input12.set_value(0.05)
        self.input13.set_value(30)
        self.input14.set_value(0.0125)
        self.input15.set_value(13)
        self.input16.set_value(3)
        self.input18.set_value(0.4616)
        self.input19.set_value(25)
        self.input110.set_value(1)
        self.input111.set_value(15)
        self.input112.set_value(300)
        self.input113.set_value(1.04)

    def calculate1(self):
        """
        初价=（原糖价格＋升贴水）*22.04623(重量单位换算)*1.0275(旋光度增值)；
        海运保险费= 初价*海运保险费率；
        到岸价(人民币)= (初价+海运保险费+海外运费)*汇率；
        不含税价= 到岸价*（1+外贸代理费率）*（1+银行手续费率）+利息及劳务费；
        含税价= 不含税价*（1+海关税率）*（1+增值税率）；
        """
        a = self.input11.value()  # 原糖价格
        b = self.input12.value()  # 升贴水
        c = self.input13.value()  # 海外运费
        d = self.input14.value(p=True)  # 银行首手续费
        e = self.input15.value(p=True)  # 增值税率
        f = self.input16.value(p=True)  # 耗损率
        g = self.input17.value()  # 汇率
        h = self.input18.value(p=True)  # 海外保险费率
        i = self.input19.value()  # 利息劳务费
        j = self.input110.value(p=True)  # 外贸代理费率
        k = self.input111.value(p=True)  # 海关关税
        l = self.input112.value()  # 加工与杂费
        m = self.input113.value()  # 旋光度增值
        params = [a, b, c, d, e, f, g, h, i, j, k, l, m]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        chujia = (a + b) * 22.04623 * m
        daoanjia = (chujia + chujia * h + c) * g
        result = (daoanjia * (1 + j) * (1 + d) + i) * (1 + k) * (1 + e)
        self.result1.set_value(result, count=4)


class SS(QWidget):
    RATE_DATA = rate.get_all_exchange_rate()

    def __init__(self, *args, **kwargs):
        super(SS, self).__init__(*args, **kwargs)
        self.USD_CNY_RATE = self.RATE_DATA.get('USD/CNY', None)
        if self.USD_CNY_RATE:
            self.USD_CNY_RATE = float(self.USD_CNY_RATE)
        main_layout = QVBoxLayout()
        """ 不锈钢生产成本 """
        widget1 = QWidget(self)
        widget1.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout1 = QGridLayout()
        layout1.setContentsMargins(QMargins(MARGIN_LEFT, 0, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name1 = NameLabel('不锈钢生产成本', self)
        self.label11 = QLabel('高镍铁价格', self)
        self.input11 = InputEdit(self)
        self.unit11 = QLabel('元/镍', self)

        layout1.addWidget(self.name1, 0, 0, 1, 3)
        layout1.addWidget(self.label11, 1, 0)
        layout1.addWidget(self.input11, 1, 1)
        layout1.addWidget(self.unit11, 1, 2)

        self.label12 = QLabel('废不锈钢价格', self)
        self.input12 = InputEdit(self)
        self.unit12 = QLabel('元/吨', self)

        layout1.addWidget(self.label12, 2, 0)
        layout1.addWidget(self.input12, 2, 1)
        layout1.addWidget(self.unit12, 2, 2)

        self.label13 = QLabel('镍板价格', self)
        self.input13 = InputEdit(self)
        self.unit13 = QLabel('元/吨', self)

        layout1.addWidget(self.label13, 3, 0)
        layout1.addWidget(self.input13, 3, 1)
        layout1.addWidget(self.unit13, 3, 2)

        self.label14 = QLabel('高碳铬铁价格', self)
        self.input14 = InputEdit(self)
        self.unit14 = QLabel('元/吨', self)

        layout1.addWidget(self.label14, 4, 0)
        layout1.addWidget(self.input14, 4, 1)
        layout1.addWidget(self.unit14, 4, 2)

        self.label15 = QLabel('其他费用', self)
        self.input15 = InputEdit(self)
        self.unit15 = QLabel('元/吨', self)

        layout1.addWidget(self.label15, 5, 0)
        layout1.addWidget(self.input15, 5, 1)
        layout1.addWidget(self.unit15, 5, 2)

        layout1.addWidget(QLabel(self), 6, 0)
        self.calculate_button1 = CalculateButton('试算成本', self)
        self.result1 = ResultLabel(self)
        self.result_unit1 = QLabel('元/吨', self)
        layout1.addWidget(self.calculate_button1, 7, 0)
        layout1.addWidget(self.result1, 7, 1)
        layout1.addWidget(self.result_unit1, 7, 2)
        widget1.setLayout(layout1)
        self.init_calculate1()
        self.calculate_button1.clicked.connect(self.calculate1)
        main_layout.addWidget(widget1, alignment=Qt.AlignTop | Qt.AlignHCenter)

        self.setLayout(main_layout)

    def init_calculate1(self):
        self.input15.set_value(3350)

    def calculate1(self):
        # result = (a * 70 + b / 9 *22 + c / 100 * 8) / 100 * 8 + d * 0.36 + e
        # 不锈钢生产成本=(高镍铁价格*70+废不锈钢价格/9*22+镍板价格/100*8)/100*8+高碳铬铁价格*0.36+其他费用
        a = self.input11.value()
        b = self.input12.value()
        c = self.input13.value()
        d = self.input14.value()
        e = self.input15.value()
        params = [a, b, c, d, e]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = (a * 70 + b / 9 * 22 + c / 100 * 8) / 100 * 8 + d * 0.36 + e
        self.result1.set_value(result, count=4)


class TA(QWidget):
    RATE_DATA = rate.get_all_exchange_rate()

    def __init__(self, *args, **kwargs):
        super(TA, self).__init__(*args, **kwargs)
        self.USD_CNY_RATE = self.RATE_DATA.get('USD/CNY', None)
        if self.USD_CNY_RATE:
            self.USD_CNY_RATE = float(self.USD_CNY_RATE)
        main_layout = QVBoxLayout()
        """ PTA原料成本 """
        widget1 = QWidget(self)
        widget1.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout1 = QGridLayout()
        layout1.setContentsMargins(QMargins(MARGIN_LEFT, 0, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name1 = NameLabel('PTA原料成本', self)
        self.label11 = QLabel('PX现货价(FOB韩国)', self)
        self.input11 = InputEdit(self)
        self.unit11 = QLabel('美元/吨', self)

        layout1.addWidget(self.name1, 0, 0, 1, 3)
        layout1.addWidget(self.label11, 1, 0)
        layout1.addWidget(self.input11, 1, 1)
        layout1.addWidget(self.unit11, 1, 2)

        self.label12 = QLabel('增值税', self)
        self.input12 = InputEdit(self)
        self.unit12 = QLabel('%', self)

        layout1.addWidget(self.label12, 2, 0)
        layout1.addWidget(self.input12, 2, 1)
        layout1.addWidget(self.unit12, 2, 2)

        self.label13 = QLabel('关税', self)
        self.input13 = InputEdit(self)
        self.unit13 = QLabel('%', self)

        layout1.addWidget(self.label13, 3, 0)
        layout1.addWidget(self.input13, 3, 1)
        layout1.addWidget(self.unit13, 3, 2)

        self.label14 = QLabel('汇率', self)
        self.input14 = InputEdit(self)
        self.unit14 = QLabel('USD/CNY', self)

        layout1.addWidget(self.label14, 4, 0)
        layout1.addWidget(self.input14, 4, 1)
        layout1.addWidget(self.unit14, 4, 2)

        self.label15 = QLabel('生产系数', self)
        self.input15 = InputEdit(self)
        self.unit15 = QLabel('', self)

        layout1.addWidget(self.label15, 5, 0)
        layout1.addWidget(self.input15, 5, 1)
        layout1.addWidget(self.unit15, 5, 2)

        self.label16 = QLabel('加工费', self)
        self.input16 = InputEdit(self)
        self.unit16 = QLabel('元/吨', self)

        layout1.addWidget(self.label16, 6, 0)
        layout1.addWidget(self.input16, 6, 1)
        layout1.addWidget(self.unit16, 6, 2)

        layout1.addWidget(QLabel(self), 7, 0)

        self.calculate_button1 = CalculateButton('试算成本', self)
        self.result1 = ResultLabel(self)
        self.result_unit1 = QLabel('元/吨', self)
        layout1.addWidget(self.calculate_button1, 8, 0)
        layout1.addWidget(self.result1, 8, 1)
        layout1.addWidget(self.result_unit1, 8, 2)
        widget1.setLayout(layout1)
        self.init_calculate1()
        self.calculate_button1.clicked.connect(self.calculate1)
        main_layout.addWidget(widget1, alignment=Qt.AlignTop | Qt.AlignHCenter)

        """ PTA成本 """
        main_layout.addWidget(HorizonSepLine(self))

        widget2 = QWidget(self)
        widget2.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout2 = QGridLayout()
        layout2.setContentsMargins(QMargins(MARGIN_LEFT, MARGIN_TOP, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name2 = NameLabel('企业进口原油生产PTA成本', self)
        self.label21 = QLabel('布伦特原油收盘价', self)
        self.input21 = InputEdit(self)
        self.unit21 = QLabel('美元/吨', self)

        layout2.addWidget(self.name2, 0, 0, 1, 3)
        layout2.addWidget(self.label21, 1, 0)
        layout2.addWidget(self.input21, 1, 1)
        layout2.addWidget(self.unit21, 1, 2)

        self.label22 = QLabel('石脑加工费', self)
        self.input22 = InputEdit(self)
        self.unit22 = QLabel('美元/吨', self)

        layout2.addWidget(self.label22, 2, 0)
        layout2.addWidget(self.input22, 2, 1)
        layout2.addWidget(self.unit22, 2, 2)

        self.label23 = QLabel('PX加工费', self)
        self.input23 = InputEdit(self)
        self.unit23 = QLabel('美元/吨', self)

        layout2.addWidget(self.label23, 3, 0)
        layout2.addWidget(self.input23, 3, 1)
        layout2.addWidget(self.unit23, 3, 2)

        self.label24 = QLabel('汇率', self)
        self.input24 = InputEdit(self)
        self.unit24 = QLabel('USD/CNY', self)

        layout2.addWidget(self.label24, 4, 0)
        layout2.addWidget(self.input24, 4, 1)
        layout2.addWidget(self.unit24, 4, 2)

        self.label25 = QLabel('生产系数', self)
        self.input25 = InputEdit(self)
        self.unit25 = QLabel('', self)

        layout2.addWidget(self.label25, 5, 0)
        layout2.addWidget(self.input25, 5, 1)
        layout2.addWidget(self.unit25, 5, 2)

        self.label26 = QLabel('加工费', self)
        self.input26 = InputEdit(self)
        self.unit26 = QLabel('元/吨', self)

        layout2.addWidget(self.label26, 6, 0)
        layout2.addWidget(self.input26, 6, 1)
        layout2.addWidget(self.unit26, 6, 2)

        layout2.addWidget(QLabel(self), 7, 0)
        self.calculate_button2 = CalculateButton('试算成本', self)
        self.result2 = ResultLabel(self)
        self.result_unit2 = QLabel('元/吨', self)
        layout2.addWidget(self.calculate_button2, 8, 0)
        layout2.addWidget(self.result2, 8, 1)
        layout2.addWidget(self.result_unit2, 8, 2)
        widget2.setLayout(layout2)
        self.init_calculate2()
        self.calculate_button2.clicked.connect(self.calculate2)
        main_layout.addWidget(widget2, alignment=Qt.AlignTop | Qt.AlignHCenter)

        self.setLayout(main_layout)

    def init_calculate1(self):
        if self.USD_CNY_RATE:
            self.input14.set_value(self.USD_CNY_RATE, count=4)
        self.input12.set_value(13)
        self.input13.set_value(2)
        self.input15.set_value(0.655)
        self.input16.set_value(400)

    def init_calculate2(self):
        if self.USD_CNY_RATE:
            self.input24.set_value(self.USD_CNY_RATE, count=4)
        self.input22.set_value(80)
        self.input23.set_value(150)
        self.input25.set_value(0.655)
        self.input26.set_value(400)

    def calculate1(self):
        # PTA原料成本 =PX现货价：FOB韩国×(1+增值税)×(1+关税)×汇率×生产系数+PTA加工费
        # result = a * (1 + b) * (1 + c) * r * d + e
        a = self.input11.value()
        b = self.input12.value(p=True)
        c = self.input13.value(p=True)
        r = self.input14.value()
        d = self.input15.value()
        e = self.input16.value()

        params = [a, b, c, d, e, r]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = a * (1 + b) * (1 + c) * r * d + e
        self.result1.set_value(result, count=4)

    def calculate2(self):
        # PTA成本=[（布伦特原油收盘价×7.35）+石脑油加工费+PX加工费]×汇率×0.655+PTA加工费
        # PTA成本=[（布伦特原油收盘价×7.35）+石脑油加工费+PX加工费]×汇率×生产系数+PTA加工费
        # result = (a * 7.35 + b + c) * r * d + e
        a = self.input21.value()
        b = self.input22.value()
        c = self.input23.value()
        r = self.input24.value()
        d = self.input25.value()
        e = self.input26.value()
        params = [a, b, c, d, e, r]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = (a * 7.35 + b + c) * r * d + e
        self.result2.set_value(result, count=4)


class V(QWidget):
    RATE_DATA = rate.get_all_exchange_rate()

    def __init__(self, *args, **kwargs):
        super(V, self).__init__(*args, **kwargs)
        self.USD_CNY_RATE = self.RATE_DATA.get('USD/CNY', None)
        if self.USD_CNY_RATE:
            self.USD_CNY_RATE = float(self.USD_CNY_RATE)
        main_layout = QVBoxLayout()
        """ 电石法PVC生产成本 """
        widget1 = QWidget(self)
        widget1.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout1 = QGridLayout()
        layout1.setContentsMargins(QMargins(MARGIN_LEFT, 0, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name1 = NameLabel('电石法PVC生产成本', self)
        self.label11 = QLabel('西北电石价格', self)
        self.input11 = InputEdit(self)
        self.unit11 = QLabel('元/吨', self)

        layout1.addWidget(self.name1, 0, 0, 1, 3)
        layout1.addWidget(self.label11, 1, 0)
        layout1.addWidget(self.input11, 1, 1)
        layout1.addWidget(self.unit11, 1, 2)

        self.label12 = QLabel('生产比', self)
        self.input12 = InputEdit(self)
        self.unit12 = QLabel(self)

        layout1.addWidget(self.label12, 2, 0)
        layout1.addWidget(self.input12, 2, 1)
        layout1.addWidget(self.unit12, 2, 2)

        self.label13 = QLabel('杂费', self)
        self.input13 = InputEdit(self)
        self.unit13 = QLabel('元/吨', self)

        layout1.addWidget(self.label13, 3, 0)
        layout1.addWidget(self.input13, 3, 1)
        layout1.addWidget(self.unit13, 3, 2)

        layout1.addWidget(QLabel(self), 4, 0)

        self.calculate_button1 = CalculateButton('试算成本', self)
        self.result1 = ResultLabel(self)
        self.result_unit1 = QLabel('元/吨', self)
        layout1.addWidget(self.calculate_button1, 5, 0)
        layout1.addWidget(self.result1, 5, 1)
        layout1.addWidget(self.result_unit1, 5, 2)
        widget1.setLayout(layout1)
        self.init_calculate1()
        self.calculate_button1.clicked.connect(self.calculate1)
        main_layout.addWidget(widget1, alignment=Qt.AlignTop | Qt.AlignHCenter)

        """ 乙烯法PVC生产成本 """
        main_layout.addWidget(HorizonSepLine(self))

        widget2 = QWidget(self)
        widget2.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout2 = QGridLayout()
        layout2.setContentsMargins(QMargins(MARGIN_LEFT, MARGIN_TOP, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name2 = NameLabel('乙烯法PVC生产成本', self)
        self.label21 = QLabel('氯乙烯', self)
        self.input21 = InputEdit(self)
        self.unit21 = QLabel('美元', self)

        layout2.addWidget(self.name2, 0, 0, 1, 3)
        layout2.addWidget(self.label21, 1, 0)
        layout2.addWidget(self.input21, 1, 1)
        layout2.addWidget(self.unit21, 1, 2)

        self.label22 = QLabel('汇率', self)
        self.input22 = InputEdit(self)
        self.unit22 = QLabel('USD/CNY', self)

        layout2.addWidget(self.label22, 2, 0)
        layout2.addWidget(self.input22, 2, 1)
        layout2.addWidget(self.unit22, 2, 2)

        self.label23 = QLabel('增值税', self)
        self.input23 = InputEdit(self)
        self.unit23 = QLabel('%', self)

        layout2.addWidget(self.label23, 3, 0)
        layout2.addWidget(self.input23, 3, 1)
        layout2.addWidget(self.unit23, 3, 2)

        self.label24 = QLabel('生产比', self)
        self.input24 = InputEdit(self)
        self.unit24 = QLabel(self)

        layout2.addWidget(self.label24, 4, 0)
        layout2.addWidget(self.input24, 4, 1)
        layout2.addWidget(self.unit24, 4, 2)

        self.label25 = QLabel('杂费', self)
        self.input25 = InputEdit(self)
        self.unit25 = QLabel('元/吨', self)

        layout2.addWidget(self.label25, 5, 0)
        layout2.addWidget(self.input25, 5, 1)
        layout2.addWidget(self.unit25, 5, 2)

        layout2.addWidget(QLabel(self), 6, 0)
        self.calculate_button2 = CalculateButton('试算成本', self)
        self.result2 = ResultLabel(self)
        self.result_unit2 = QLabel('元/吨', self)
        layout2.addWidget(self.calculate_button2, 7, 0)
        layout2.addWidget(self.result2, 7, 1)
        layout2.addWidget(self.result_unit2, 7, 2)
        widget2.setLayout(layout2)
        self.init_calculate2()
        self.calculate_button2.clicked.connect(self.calculate2)
        main_layout.addWidget(widget2, alignment=Qt.AlignTop | Qt.AlignHCenter)

        """ PVC进口成本 """
        main_layout.addWidget(HorizonSepLine(self))

        widget3 = QWidget(self)
        widget3.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout3 = QGridLayout()
        layout3.setContentsMargins(QMargins(MARGIN_LEFT, MARGIN_TOP, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name3 = NameLabel('PVC进口成本', self)
        self.label31 = QLabel('CFR远东价', self)
        self.input31 = InputEdit(self)
        self.unit31 = QLabel('美元', self)

        layout3.addWidget(self.name3, 0, 0, 1, 3)
        layout3.addWidget(self.label31, 1, 0)
        layout3.addWidget(self.input31, 1, 1)
        layout3.addWidget(self.unit31, 1, 2)

        self.label32 = QLabel('汇率', self)
        self.input32 = InputEdit(self)
        self.unit32 = QLabel('USD/CNY', self)

        layout3.addWidget(self.label32, 2, 0)
        layout3.addWidget(self.input32, 2, 1)
        layout3.addWidget(self.unit32, 2, 2)

        self.label33 = QLabel('关税', self)
        self.input33 = InputEdit(self)
        self.unit33 = QLabel('%', self)

        layout3.addWidget(self.label33, 3, 0)
        layout3.addWidget(self.input33, 3, 1)
        layout3.addWidget(self.unit33, 3, 2)

        self.label34 = QLabel('增值税', self)
        self.input34 = InputEdit(self)
        self.unit34 = QLabel('%', self)

        layout3.addWidget(self.label34, 4, 0)
        layout3.addWidget(self.input34, 4, 1)
        layout3.addWidget(self.unit34, 4, 2)

        layout3.addWidget(QLabel(self), 5, 0)

        self.calculate_button3 = CalculateButton('试算成本', self)
        self.result3 = ResultLabel(self)
        self.result_unit3 = QLabel('元/吨', self)
        layout3.addWidget(self.calculate_button3, 6, 0)
        layout3.addWidget(self.result3, 6, 1)
        layout3.addWidget(self.result_unit3, 6, 2)
        widget3.setLayout(layout3)
        self.init_calculate3()
        self.calculate_button3.clicked.connect(self.calculate3)
        main_layout.addWidget(widget3, alignment=Qt.AlignTop | Qt.AlignHCenter)
        self.setLayout(main_layout)

    def init_calculate1(self):
        self.input12.set_value(1.45)
        self.input13.set_value(1400)

    def init_calculate2(self):
        if self.USD_CNY_RATE:
            self.input22.set_value(self.USD_CNY_RATE, count=4)
        self.input23.set_value(13)
        self.input24.set_value(1.02)
        self.input25.set_value(1000)

    def init_calculate3(self):
        if self.USD_CNY_RATE:
            self.input32.set_value(self.USD_CNY_RATE, count=4)
        self.input33.set_value(6.5)
        self.input34.set_value(13)

    def calculate1(self):
        # 电石法PVC生产成本=西北电石价格*PVC生产比+杂费
        # result = a * b + c
        a = self.input11.value()
        b = self.input12.value()
        c = self.input13.value()
        params = [a, b, c]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = a * b + c
        self.result1.set_value(result, count=4)

    def calculate2(self):
        # 乙烯法PVC生产成本=氯乙烯*汇率*增值税*PVC生产比+杂费
        # result = a * r * (1 + b) * c + d
        a = self.input21.value()
        r = self.input22.value()
        b = self.input23.value(p=True)
        c = self.input24.value()
        d = self.input25.value()
        params = [a, b, c, d, r]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = a * r * (1 + b) * c + d
        self.result2.set_value(result, count=4)

    def calculate3(self):
        # PVC进口成本=CFR远东价*汇率*关税*增值税
        # result = a * r * (1 + b) * (1 + c)
        a = self.input31.value()
        r = self.input32.value()
        b = self.input33.value(p=True)
        c = self.input34.value(p=True)
        params = [a, b, c, r]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = a * r * (1 + b) * (1 + c)
        self.result3.set_value(result, count=4)


class ZN(QWidget):

    RATE_DATA = rate.get_all_exchange_rate()

    def __init__(self, *args, **kwargs):
        super(ZN, self).__init__(*args, **kwargs)
        self.USD_CNY_RATE = self.RATE_DATA.get('USD/CNY', None)
        if self.USD_CNY_RATE:
            self.USD_CNY_RATE = float(self.USD_CNY_RATE)
        main_layout = QVBoxLayout()
        """ 锌进口成本 """
        widget1 = QWidget(self)
        widget1.setFixedWidth(CALCULATE_WIDGET_WIDTH)
        layout1 = QGridLayout()
        layout1.setContentsMargins(QMargins(MARGIN_LEFT, 0, MARGIN_RIGHT, MARGIN_BOTTOM))
        self.name1 = NameLabel('锌进口成本', self)
        self.label11 = QLabel('LME三个月期货价', self)
        self.input11 = InputEdit(self)
        self.unit11 = QLabel('美元/吨', self)

        layout1.addWidget(self.name1, 0, 0, 1, 3)
        layout1.addWidget(self.label11, 1, 0)
        layout1.addWidget(self.input11, 1, 1)
        layout1.addWidget(self.unit11, 1, 2)

        self.label12 = QLabel('现货升贴水', self)
        self.input12 = InputEdit(self)
        self.unit12 = QLabel('美元/吨', self)

        layout1.addWidget(self.label12, 2, 0)
        layout1.addWidget(self.input12, 2, 1)
        layout1.addWidget(self.unit12, 2, 2)

        self.label13 = QLabel('到岸升贴水', self)
        self.input13 = InputEdit(self)
        self.unit13 = QLabel('美元/吨', self)

        layout1.addWidget(self.label13, 3, 0)
        layout1.addWidget(self.input13, 3, 1)
        layout1.addWidget(self.unit13, 3, 2)

        self.label14 = QLabel('汇率', self)
        self.input14 = InputEdit(self)
        self.unit14 = QLabel('USD/CNY', self)

        layout1.addWidget(self.label14, 4, 0)
        layout1.addWidget(self.input14, 4, 1)
        layout1.addWidget(self.unit14, 4, 2)

        self.label15 = QLabel('增值税率', self)
        self.input15 = InputEdit(self)
        self.unit15 = QLabel('%', self)

        layout1.addWidget(self.label15, 5, 0)
        layout1.addWidget(self.input15, 5, 1)
        layout1.addWidget(self.unit15, 5, 2)

        self.label16 = QLabel('关税税率', self)
        self.input16 = InputEdit(self)
        self.unit16 = QLabel('%', self)

        layout1.addWidget(self.label16, 6, 0)
        layout1.addWidget(self.input16, 6, 1)
        layout1.addWidget(self.unit16, 6, 2)

        self.label17 = QLabel('港杂费', self)
        self.input17 = InputEdit(self)
        self.unit17 = QLabel('元/吨', self)

        layout1.addWidget(self.label17, 7, 0)
        layout1.addWidget(self.input17, 7, 1)
        layout1.addWidget(self.unit17, 7, 2)

        layout1.addWidget(QLabel(self), 8, 0)

        self.calculate_button1 = CalculateButton('试算成本', self)
        self.result1 = ResultLabel(self)
        self.result_unit1 = QLabel('元/吨', self)
        layout1.addWidget(self.calculate_button1, 9, 0)
        layout1.addWidget(self.result1, 9, 1)
        layout1.addWidget(self.result_unit1, 9, 2)
        widget1.setLayout(layout1)
        self.init_calculate1()
        self.calculate_button1.clicked.connect(self.calculate1)
        main_layout.addWidget(widget1, alignment=Qt.AlignTop | Qt.AlignHCenter)

        self.setLayout(main_layout)

    def init_calculate1(self):
        if self.USD_CNY_RATE:
            self.input14.set_value(self.USD_CNY_RATE, count=4)
        self.input15.set_value(13)
        self.input16.set_value(1)
        self.input17.set_value(150)

    def calculate1(self):
        # 计算锌进口成本
        # result = (a + b + c) * r * (1 + d) * (1 + e) + f
        # 锌进口成本=（LME三个月期货价格+现货升贴水+到岸升贴水）*汇率*（1+增值税率）*(1+关税税率)+港杂费
        a = self.input11.value()
        b = self.input12.value()
        c = self.input13.value()
        r = self.input14.value()
        d = self.input15.value(p=True)
        e = self.input16.value(p=True)
        f = self.input17.value()
        params = [a, b, c, r, d, e, f]
        params = list(filter(lambda x: x != 0, params))
        if not all(params):
            p = InformationPopup('请填写完整数据再试算!', self)
            p.exec_()
            return
        result = (a + b + c) * r * (1 + d) * (1 + e) + f
        self.result1.set_value(result, count=4)

