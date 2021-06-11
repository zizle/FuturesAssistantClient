# _*_ coding:utf-8 _*_
# @File  : analysis_article.py
# @Time  : 2021-05-31 15:16
# @Author: zizle

import requests
from PyQt5.QtCore import QThread, pyqtSignal
from settings import SERVER_API


# 分析文章
class GetAnalysisArticle(QThread):
    article_reply = pyqtSignal(dict)

    def __init__(self, *args, **kwargs):
        super(GetAnalysisArticle, self).__init__(*args, **kwargs)
        self.url = SERVER_API + 'article/analysis/'

        self.page = 1
        self.page_size = 30

    def set_pages(self, page, page_size):
        self.page = page
        self.page_size = page_size

    def run(self) -> dict:
        try:
            r = requests.get(self.url, params={'page': self.page, 'page_size': self.page_size})
            data = r.json()
        except Exception as e:
            return {}
        else:
            self.article_reply.emit(data)


class PutAnalysisArticle(QThread):
    def __init__(self, *args, **kwargs):
        super(PutAnalysisArticle, self).__init__(*args, **kwargs)
        self.body_data = {}

    def set_body(self, data):
        self.body_data = data

    def run(self) -> None:
        aid = self.body_data.get('id', None)
        if not aid:
            return
        url = SERVER_API + f'article/analysis/{aid}/'
        try:
            r = requests.put(url, json=self.body_data)
        except Exception as e:
            pass




