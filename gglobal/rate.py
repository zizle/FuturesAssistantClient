# _*_ coding:utf-8 _*_
# @File  : rate.py
# @Time  : 2021-01-25 10:58
# @Author: zizle


class ExchangeRate(object):  # 汇率数据
    rates = {}


def set_exchange_rate(data_list: list):
    for item in data_list:
        ExchangeRate.rates[item['rate_name']] = item['rate']


def get_exchange_rate(rate_name: str):
    return ExchangeRate.rates.get(rate_name, '')


def get_all_exchange_rate():
    return ExchangeRate.rates
