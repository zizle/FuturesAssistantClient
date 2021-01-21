# _*_ coding:utf-8 _*_
# @File  : variety_calculate_widgets.py
# @Time  : 2021-01-21 15:40
# @Author: zizle

# 各品种的计算控件

from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QVBoxLayout, QLineEdit, QPushButton
from PyQt5.QtCore import Qt


class NameLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super(NameLabel, self).__init__(*args, **kwargs)
        self.setStyleSheet('font-size:20px;color:#ff6433;font-weight:bold')


class ResultLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super(ResultLabel, self).__init__(*args, **kwargs)
        self.setStyleSheet('font-size:20px;color:#ff6433;border:none;border-bottom:1px solid #333333')


class CalculateButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super(CalculateButton, self).__init__(*args, **kwargs)
        self.setStyleSheet('color:#ffffff;background-color:#2f75b5')


class A(QWidget):
    def __init__(self, *args, **kwargs):
        super(A, self).__init__(*args, **kwargs)
        main_layout = QVBoxLayout()
        calculate_widget = QWidget(self)
        calculate_widget.setFixedWidth(500)
        layout = QGridLayout()
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.name1 = NameLabel('大豆进口成本', self)
        self.label1 = QLabel('CBOT大豆盘面价格:', self)
        self.label2 = QLabel('FOB升贴水:', self)
        self.label3 = QLabel('海运费:', self)
        self.label4 = QLabel('增值税:', self)
        self.label5 = QLabel('关税:', self)
        self.label6 = QLabel('汇率:', self)
        self.label7 = QLabel('港杂费:', self)

        self.input1 = QLineEdit(self)
        self.input2 = QLineEdit(self)
        self.input3 = QLineEdit('30', self)
        self.input4 = QLineEdit('9', self)
        self.input5 = QLineEdit('3', self)
        self.input6 = QLineEdit(self)
        self.input7 = QLineEdit('120', self)

        self.unit1 = QLabel('美分/蒲式耳', self)
        self.unit2 = QLabel('美分/蒲式耳', self)
        self.unit3 = QLabel('美元/吨', self)
        self.unit4 = QLabel('%', self)
        self.unit5 = QLabel('%', self)
        self.unit6 = QLabel(self)
        self.unit7 = QLabel('元/吨', self)

        self.calculate_button = CalculateButton('计算', self)

        self.label8 = QLabel('结果:', self)
        self.result1 = ResultLabel('=', self)
        self.unit8 = QLabel('元/吨', self)

        layout.addWidget(self.name1, 0, 0)
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
        self.setLayout(main_layout)

        self.calculate_button.clicked.connect(self.calculate1)

    def calculate1(self):
        # 大豆进口成本计算
        # 大豆进口成本 =〔（CBOT期价＋FOB升贴水）×0.367437＋海运费〕×(1+增值税)×(1+关税)×汇率＋港杂费
        r = ((float(self.input1.text()) + float(self.input2.text())) * 0.367437 + float(self.input3.text())) * \
        (1 + float(self.input4.text()) / 100) * (1 + float(self.input5.text()) / 100) * float(self.input6.text()) + \
        float(self.input7.text())
        self.result1.setText("= " + str(round(r, 2)))


class B(QWidget):
    def __init__(self, *args, **kwargs):
        super(B, self).__init__(*args, **kwargs)
        layout = QGridLayout()
        layout.addWidget(QLabel('这是豆二的计算公式界面', self), 0, 0)
        self.setLayout(layout)
