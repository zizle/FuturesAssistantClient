# _*_ coding:utf-8 _*_
# @File  : hooks.py
# @Time  : 2021-03-19 10:29
# @Author: zizle
import sys
import traceback
from settings import logger
from PyQt5.QtWidgets import QMessageBox


def exception_hook(exc_type, exc_value, exc_tb):
    try:
        tb_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
        logger.error('程序异常(flash):\n{}'.format(tb_msg))
    except Exception as e:
        logger.error('在异常中捕获异常:{}'.format(e))
    finally:
        sys.exit(-1)
