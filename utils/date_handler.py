# _*_ coding:utf-8 _*_
# @File  : date_handler.py
# @Time  : 2020-12-07 17:16
# @Author: zizle
import datetime


def generate_date_with_limit(min_date, max_date):
    date_list = []
    min_date = datetime.datetime.strptime(min_date, '%Y%m%d')
    max_date = datetime.datetime.strptime(max_date, '%Y%m%d')
    while min_date < max_date:
        date_list.append(min_date.strftime("%m%d"))
        min_date += datetime.timedelta(days=1)
    return date_list
