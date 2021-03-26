# _*_ coding:utf-8 _*_
# @File  : threads.py
# @Time  : 2021-03-26 10:13
# @Author: zizle

import random
import datetime
from PyQt5.QtCore import QThread, pyqtSignal


class HandleSourceThread(QThread):
    handle_finished = pyqtSignal(list)

    def __init__(self, *args, **kwargs):
        super(HandleSourceThread, self).__init__(*args, **kwargs)

    def generate_date(self):
        date = []
        s = datetime.datetime.strptime('2020.09.30', '%Y.%m.%d')
        e = datetime.datetime.strptime('2021.03.20', '%Y.%m.%d')
        while s < e:
            date.append(s.strftime('%Y-%m-%d'))
            s += datetime.timedelta(days=1)

        return date

    def run(self):
        import time
        source = []
        # 随机生成一些数据
        #  {'date': '日期',
        #  'profit': '权益',
        #  'degree_of_risk': '风险度',
        #  'net_profits': '净利润',
        #  'date_net_value': '日净值',
        #  'max_roe': '最大本金收益率'
        #  }
        for d in self.generate_date():
            source.append(
                {'date': d, 'profit': round(random.uniform(50000, 250000), 2),
                 'degree_of_risk': f'{round(random.uniform(1, 100), 2)}%', 'net_profits': round(random.uniform(700, 5000), 2),
                 'date_net_value': round(random.uniform(300, 1000), 2), 'max_roe': f'{round(random.uniform(-20, 80), 2)}%'}
            )
            time.sleep(0.0001)
        self.handle_finished.emit(source)


