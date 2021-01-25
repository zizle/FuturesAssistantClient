# _*_ coding:utf-8 _*_
# @File  : variety_calculate_widgets.py
# @Time  : 2021-01-21 15:40
# @Author: zizle

# 各品种的计算控件

from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QVBoxLayout, QLineEdit, QPushButton, QFrame
from PyQt5.QtCore import Qt, QRegExp, QMargins
from PyQt5.QtGui import QRegExpValidator

from popup.message import InformationPopup


CALCULATE_WIDGET_WIDTH = 500  # 计算控件的宽度

MARGIN_TOP, MARGIN_RIGHT, MARGIN_BOTTOM, MARGIN_LEFT = (50, 0, 50, 0)


SEP_SPACING = 50  # 分割线控件之间的距离


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


# class LabelLabel(QLabel):
#     def __init__(self, *args, **kwargs):
#         super(LabelLabel, self).__init__(*args, **kwargs)
#         self.setAlignment(Qt.AlignJustify)


class InputEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super(InputEdit, self).__init__(*args, **kwargs)
        self.setValidator(QRegExpValidator(QRegExp(r"^(-?\d+)(\.\d+)?$"), self))
        self.setStyleSheet('border: 1px solid #aaaaaa;height:35px')

    def value(self):
        if not self.text():
            return None
        return float(self.text())


class ResultLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super(ResultLabel, self).__init__(*args, **kwargs)
        self.setStyleSheet('font-size:20px;border:none;border-bottom:1px solid #333333')

    def set_value(self, text) -> None:
        text = "= <span style='color:#ff6433'>{}</span>".format(str(round(text, 2)))
        self.setText(text)


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
        self.label1 = QLabel('CBOT大豆盘面价格:', self) # a
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
        self.input6 = InputEdit(self)
        self.input7 = InputEdit('120', self)

        self.unit1 = QLabel('美分/蒲式耳', self)
        self.unit2 = QLabel('美分/蒲式耳', self)
        self.unit3 = QLabel('美元/吨', self)
        self.unit4 = QLabel('%', self)
        self.unit5 = QLabel('%', self)
        self.unit6 = QLabel('USD/CNY', self)
        self.unit7 = QLabel('元/吨', self)

        self.calculate_button = CalculateButton('试算成本', self)

        self.result1 = ResultLabel('=', self)
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
        layout2.setContentsMargins(QMargins(QMargins(MARGIN_LEFT, MARGIN_TOP, MARGIN_RIGHT, MARGIN_BOTTOM)))
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
        self.result2 = ResultLabel('=', self)

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
        if not all([a, b, c, d, e, f, g]):
            p = InformationPopup('请填写完整参数后进行计算!', self)
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
        r = a * 0.785 + b * 0.19 - c - d
        self.result2.set_value(r)


class B(QWidget):
    def __init__(self, *args, **kwargs):
        super(B, self).__init__(*args, **kwargs)
        layout = QGridLayout()
        layout.addWidget(QLabel('这是豆二的计算公式界面', self), 0, 0)
        self.setLayout(layout)
