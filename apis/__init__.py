# _*_ coding:utf-8 _*_
# @File  : __init__.py.py
# @Time  : 2020-12-22 13:33
# @Author: zizle
""" 网络请求api """

import requests
from settings import SERVER_API, USER_AGENT, logger


class LoggerApi(object):
    def __init__(self):
        self.url = SERVER_API + 'logger/'

    def post(self, data):
        headers = {'User-Agent': USER_AGENT}
        try:
            requests.post(self.url, json=data, headers=headers)
        except Exception as e:
            logger.error(f'保存日志出错:{e}')
            return False
        else:
            return True
