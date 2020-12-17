# _*_ coding:utf-8 _*_
# @File  : chart.py
# @Time  : 2020-09-06 19:23
# @Author: zizle
from PyQt5.QtCore import QObject, pyqtSignal


class ChartOptionChannel(QObject):
    # 参数1：图表类型(normal,season); 参数2：图表配置项; 参数3：作图的源数据; 参数4: 数据的表头字典
    chartSource = pyqtSignal(str, str, str, str)


# 跨品种套利计算管道
class ArbitrageChannel(QObject):
    # 参数1:源数据;参数2:基本信息;参数3:图表类型  (必须含这3个参数)
    chartSource = pyqtSignal(str, str, str)
    # 调整图形大小
    chartResize = pyqtSignal(int, int)  # (仅含这两个参数)
