# _*_ coding:utf-8 _*_
# @File  : spider_exchange_news.py
# @Time  : 2021-06-11 08:15
# @Author: zizle


# 爬取交易所新闻
import datetime

import requests
from bs4 import BeautifulSoup


def spider_cffex_news():  # 爬取中金所新闻
    host = 'http://www.cffex.com.cn'
    url = 'http://www.cffex.com.cn/jystz/'
    headers = {
        'Referer': 'http://www.cffex.com.cn/jystz/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
    }
    try:
        r = requests.get(url=url, headers=headers)
        r.encoding = 'utf8'
        html = r.text
    except Exception as e:
        print(e)
    else:
        soup = BeautifulSoup(html, 'html.parser')
        notice_list = soup.select('.notice_list')
        for bs_tag in notice_list:
            all_a = bs_tag.find_all(class_='list_a_text')
            for a_tag in all_a:
                href = a_tag.get('href', None)
                title = a_tag.get('title', None)
                if all([href, title]):
                    notice_time = href.split('/')
                    if len(notice_time) > 2:
                        # print(href, title, notice_time[2])
                        print(host+href, notice_time[2], title, )


def spider_czce_news():
    url = 'http://app.czce.com.cn/cms/pub/search/searchdt.jsp'
    # 准备参数
    headers = {
        'Host': 'app.czce.com.cn',
        'Origin': 'http: // app.czce.com.cn',
        'Referer': 'http: // app.czce.com.cn / cms / pub / search / searchdt.jsp',
        'User-Agent': 'Mozilla / 5.0(Windows NT 10.0; WOW64; Trident / 7.0; rv: 11.0) like Gecko'
    }
    now_date = datetime.datetime.now().strftime('%Y-%m-%d')
    form_data = {
        '__go2pageNO': 1,
        'DtName': '',
        'DtbeginDate': '2011-01-01',
        'DtendDate': now_date,
        '__go2pageNum': 1
    }

    try:
        r = requests.post(url, data=form_data, headers=headers)
        html = r.text
    except Exception as e:
        print(e)
    else:
        soup = BeautifulSoup(html, 'html.parser')
        table_list = soup.select('table')
        for table_tag in table_list:
            all_tr = table_tag.find_all('tr')
            for tr_tag in all_tr:
                a_element = tr_tag.find('a')
                all_td = tr_tag.find_all('td')
                date_td = None
                if len(all_td) > 2:
                    date_td = all_td[2]
                if all([a_element, date_td]):
                    href = a_element.get('href')
                    title = a_element.string
                    print(href, date_td.string, title)

def spider_dce_news():
    url = 'http://www.dce.com.cn/dalianshangpin/ywfw/jystz/ywtz/13305-1.html'  # -后面是页码
    host = 'http://www.dce.com.cn'
    headers = {
        'Referer': url,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
    }

    try:
        r = requests.get(url=url, headers=headers)
        r.encoding = 'utf8'
        html = r.text
    except Exception as e:
        print(e)
    else:
        soup = BeautifulSoup(html, 'html.parser')
        ul_tag_list = soup.select('.list_tpye06')
        for ul_tag in ul_tag_list:
            li_list = ul_tag.find_all('li')
            for li_tag in li_list:
                a_element = li_tag.find('a')
                date_element = li_tag.find('span')
                if all([a_element, date_element]):
                    title = a_element.get('title', None)
                    href = host + a_element.get('href', None)
                    date_str = date_element.string
                    print(href, date_str, title)

def spider_shfe_news():
    url = 'http://www.shfe.com.cn/news/notice/index.html'
    host = 'http://www.shfe.com.cn/'
    headers = {
        'Referer': url,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
    }
    try:
        r = requests.get(url=url, headers=headers)
        html = r.text
    except Exception as e:
        print(e)
    else:
        soup = BeautifulSoup(html, 'html.parser')
        news_tag = soup.select('.internews')
        if not news_tag:
            return
        for new_tag in news_tag:
            li_list = new_tag.find_all('li')
            for li_tag in li_list:
                date_ele = li_tag.find('span')
                a_ele = li_tag.find('a')
                if all([date_ele, a_ele]):
                    title = a_ele.get('title', None)
                    href = a_ele.get('href', None)
                    date_str = date_ele.string
                    if all([title, href, date_str]):
                        print(host + href, date_str.replace('[', '').replace(']', ''), title)


if __name__ == '__main__':
    print('开始爬取中金所的公告。。。')
    spider_cffex_news()
    print()
    print('开始爬取郑商所的公告。。。')
    spider_czce_news()
    print()
    print('开始爬取大商所的公告。。。')
    spider_dce_news()
    print()
    print('开始爬取上期所的公告。。。')
    spider_shfe_news()
