# _*_ coding:utf-8 _*_
# @File  : variety.py
# @Time  : 2021-01-20 13:18
# @Author: zizle


class Variety(object):
    varieties = []


def set_variety(varieties: list):
    if isinstance(varieties, list):
        Variety.varieties = varieties


def get_variety():
    return Variety.varieties
