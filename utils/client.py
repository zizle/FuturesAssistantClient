# _*_ coding:utf-8 _*_
# @File  : client.py
# @Time  : 2020-08-31 9:08
# @Author: zizle
import re
import os
import pickle
from datetime import datetime
from PyQt5.QtCore import QProcess, QSettings
from settings import logger, BASE_DIR


def get_client_uuid():
    p = QProcess()
    p.start("wmic csproduct get UUID")
    p.waitForFinished()
    result = p.readAllStandardOutput().data().decode('utf-8')
    result_list = re.split(r'\s+', result)
    if len(result_list[1]) != 36:  # 获取uuid失败
        logger.error("Get Client UUID failed!")
        return ''
    return result_list[1]


def get_client_uuid_with_ini():
    config_filepath = os.path.join(BASE_DIR, "dawn/client.ini")
    config = QSettings(config_filepath, QSettings.IniFormat)
    client_uuid = config.value("TOKEN/UUID") if config.value("TOKEN/UUID") else 'Unknown'
    return client_uuid


def set_client_uuid_with_ini(client_uuid):
    config_filepath = os.path.join(BASE_DIR, "dawn/client.ini")
    config = QSettings(config_filepath, QSettings.IniFormat)
    config.setValue("TOKEN/UUID", client_uuid)


def remove_user_logged():
    config_filepath = os.path.join(BASE_DIR, "dawn/client.ini")
    config = QSettings(config_filepath, QSettings.IniFormat)
    config.remove("USER/AUTOLOGIN")


def get_user_token():
    params_path = os.path.join(BASE_DIR, "dawn/client.ini")
    app_params = QSettings(params_path, QSettings.IniFormat)
    jwt_token = app_params.value("USER/BEARER")
    if jwt_token:
        token = "Bearer " + jwt_token
    else:
        token = "Bearer "
    return token


def auth_module(module_id, module_name, modules):
    is_auth = False
    current_date = datetime.today().strftime("%%Y-%m-%d")
    for module_item in modules:
        if module_item["module_id"] == module_id and module_item["expire_date"] > current_date:
            is_auth = True
            break
    if is_auth:
        return True, "验证通过"
    else:
        return False, "您还没有【" + module_name + "】的权限,\n请联系管理员开通!"


def is_module_verify(module_id, module_name):
    """ 获取用户权限 """
    auth_filepath = os.path.join(BASE_DIR, "dawn/auth.dat")
    with open(auth_filepath, "rb") as fp:
        authorization = pickle.load(fp)
    user_info = authorization["role"]
    modules = authorization["auth"]
    if user_info in ["superuser", "operator"]:
        return True, '运营全模块通过'
    elif user_info in ["collector", "research"]:
        if module_id.startswith("-9"):
            # 后台模块需要验证
            return auth_module(module_id, module_name, modules)
        else:
            return True, '内部其他除后台全模块通过'
    else:
        if not user_info:
            return False, "您还未登录,请登录后再进行操作!"
        return auth_module(module_id, module_name, modules)

