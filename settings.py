# _*_ coding:utf-8 _*_
# Author: zizle  QQ:462894999
import os
import sys
import time
import logging
from PyQt5.QtCore import QSettings

SYS_BIT = "32" if sys.maxsize < 2 ** 32 else "64"
PLATE_FORM = "WIN7"
ADMINISTRATOR = True
WINDOW_TITLE = '分析决策系统(研究员)' if ADMINISTRATOR else '分析决策系统客户端'

SERVER_API = "http://127.0.0.1:8000/api/"
# SERVER_API = "http://210.13.218.130:9004/api/"

STATIC_URL = SERVER_API[:-4] + 'static/'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LOCAL_SPIDER_SRC = os.path.join(BASE_DIR, "sources/")  # 爬取保存文件的本地文件夹

ONLINE_COUNT_INTERVAL = 120000  # 毫秒

# 爬虫使用的User-Agent
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
]
# 本软件User-Agent
USER_AGENT = 'RuiDa_ADSClient_VERSION_1.0.1'
# app设置
app_dawn = QSettings('dawn/initial.ini', QSettings.IniFormat)
cache_dawn = QSettings('dawn/cache.ini', QSettings.IniFormat)  # 解析大商所日排名的缓存文件夹

# 首页广告变化速率，单位毫秒
IMAGE_SLIDER_RATE = 3000
# 标题栏高度
TITLE_BAR_HEIGHT = 27
# 菜单栏高度
NAVIGATION_BAR_HEIGHT = 25
# 首页表格行高
HOMEPAGE_TABLE_ROW_HEIGHT = 28  # 由于字体需要必须大于24

# 支持多级(但模块权限仅遍历3级)
SYSTEM_MENUS = [
    {"id": "0", "name": "首页", "logo": "", "children": None},
    {"id": "1", "name": "产品服务", "logo": "", "children": None},
    {"id": "3", "name": "交割服务", "logo": "", "children": None},
    {"id": "4", "name": "计算平台", "logo": "", "children": None},
    {"id": "2", "name": "行业数据", "logo": "", "children": [
        {"id": "2_0", "name": "品种数据库", "logo": "", "children": None},
        {"id": "2_1", "name": "交易所数据", "logo": "", "children": None},
        {"id": "2_2", "name": "品种数据分析", "logo": "", "children": None},
    ]},
    {"id": "-9", "name": "后台管理", "logo": "", "children": [
        {"id": "-9_1", "name": "运营管理", "logo": "", "children": [
            {"id": "-9_1_0", "name": "品种管理", "logo": "", "children": None},
            {"id": "-9_1_1", "name": "用户管理", "logo": "", "children": None},
            {"id": "-9_1_2", "name": "客户端管理", "logo": "", "children": None}
        ]},
        {"id": "-9_0", "name": "首页管理", "logo": "", "children": [
            {"id": "-9_0_0", "name": "广告设置", "logo": "", "children": None},
        ]},
        {"id": "-9_2", "name": "产品服务", "logo": "", "children": [
            {"id": "-9_2_0", "name": "资讯服务", "logo": "", "children": None},
            {"id": "-9_2_1", "name": "顾问服务", "logo": "", "children": None},
            {"id": "-9_2_2", "name": "策略服务", "logo": "", "children": None},
            {"id": "-9_2_3", "name": "品种服务", "logo": "", "children": None},
        ]},
        {"id": "-9_4", "name": "交割服务", "logo": "", "children": [
            {"id": "-9_4_0", "name": "仓库信息管理", "logo": "", "children": None},
            {"id": "-9_4_1", "name": "仓单数据提取", "logo": "", "children": None},
        ]},
        {"id": "-9_3", "name": "行业数据", "logo": "", "children": [
            {"id": "-9_3_0", "name": "品种数据库", "logo": "", "children": None},
            {"id": "-9_3_1", "name": "交易所数据", "logo": "", "children": None},
            {"id": "-9_3_2", "name": "现货报价数据", "logo": "", "children": None},
        ]},
    ]},
    {"id": "0_0", "name": "关于系统", "logo": "", "children": [
        {"id": "0_0_1", "name": "版本检查", "logo": "", "children": None},
        {"id": "0_0_2", "name": "权限刷新", "logo": "", "children": None},
        {"id": "0_0_3", "name": "密码修改", "logo": "", "children": None},
    ]},
]

# 首页左侧的菜单(2级)
HOMEPAGE_MENUS = [
    {"id": "l_0", "name": "研 究\n报 告", "logo": "", "children": [
        {"id": "l_0_0", "name": "日报周报", "children": [
            {"id": "l_0_0_1", "name": "收盘日评"},
            {"id": "l_0_0_2", "name": "品种周报"},
        ]},
        {"id": "l_0_1", "name": "月报年报", "children": [
            {"id": "l_0_1_1", "name": "月季报告"},
            {"id": "l_0_1_2", "name": "年度报告"},
        ]},
    ]},
    {"id": "l_1", "name": "产 品\n服 务", "logo": "", "children": [
        {"id": "l_1_0", "name": "资讯服务", "children": [
            {"id": "l_1_0_1", "name": "短信通"},
        ]},
    ]}
]


# 设置日志记录
def make_dir(dir_path):
    path = dir_path.strip()
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def config_logger_handler():
    # 日志配置
    log_folder = os.path.join(BASE_DIR, "logs/")
    make_dir(log_folder)
    log_file_name = time.strftime('%Y-%m-%d', time.localtime(time.time())) + '.log'
    log_file_path = log_folder + os.sep + log_file_name

    handler = logging.FileHandler(log_file_path, encoding='UTF-8')
    handler.setLevel(logging.ERROR)
    # "%(asctime)s - %(levelname)s - %(message)s - %(pathname)s[line:%(lineno)d]"
    logger_format = logging.Formatter(
        "%(asctime)s - %(levelname)s : %(message)s"
    )
    handler.setFormatter(logger_format)
    return handler


logger = logging.getLogger('errorlog')
logger.addHandler(config_logger_handler())

# 屏蔽或重命名的品种(品种数据库)
SHIELD_VARIETY = ['CY', 'WR', 'NR']
RENAME_VARIETY = {"CF": '棉花(纱)'}
