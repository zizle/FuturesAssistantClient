# _*_ coding:utf-8 _*_
# @File  : hooks.py
# @Time  : 2021-03-19 10:29
# @Author: zizle
import sys
import traceback
from settings import logger
from PyQt5.QtWidgets import QMessageBox
from apis import LoggerApi
from utils.client import get_user_token, get_client_uuid_with_ini


def exception_hook(exc_type, exc_value, exc_tb):
    token = get_user_token(raw=True)
    client = get_client_uuid_with_ini()
    log_api = LoggerApi()
    try:
        tb_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
        logger.error('程序异常(flash):\n{}'.format(tb_msg))
        # 保存日志
        data = {
            'token': token,
            'client': client,
            'error': f'程序异常崩溃:{tb_msg}'
        }
        log_api.post(data)
    except Exception as e:
        logger.error('在异常中捕获异常:{}'.format(e))
    finally:
        sys.exit(-1)
