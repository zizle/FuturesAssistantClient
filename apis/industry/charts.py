# _*_ coding:utf-8 _*_
# @File  : charts.py
# @Time  : 2021-05-19 10:44
# @Author: zizle

import requests
from PyQt5.QtCore import QThread, pyqtSignal
from settings import SERVER_API, logger


class SwapChartSorted(QThread):
    def __init__(self, *args, **kwargs):
        super(SwapChartSorted, self).__init__(*args, **kwargs)
        self.body_data = {}

    def set_body_data(self, data):
        self.body_data = data

    def run(self):
        try:
            requests.put(SERVER_API + "chart/suffix/", json=self.body_data)
        except Exception as e:
            logger.error(f'用户交换数据表排序错误{e}')


class SaveComparesThread(QThread):  # 保存图形的对比解读
    request_finished = pyqtSignal(dict)

    def __init__(self, *args, **kwargs):
        super(SaveComparesThread, self).__init__(*args, **kwargs)
        self.body_data = {}
        self.chart_id = 0

    def set_body_data(self, data, cid):
        self.body_data = data
        self.chart_id = cid

    def run(self):
        if self.chart_id < 1:
            return
        try:
            r = requests.post(SERVER_API + f"chart/{self.chart_id}/compare/", json=self.body_data)
            rep = r.json()
        except Exception as e:
            logger.error(f'保存图形对比解读错误{e}')
        else:
            self.request_finished.emit(rep)

