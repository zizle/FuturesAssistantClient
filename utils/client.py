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


def get_user_token(raw=False):
    params_path = os.path.join(BASE_DIR, "dawn/client.ini")
    app_params = QSettings(params_path, QSettings.IniFormat)
    jwt_token = app_params.value("USER/BEARER")
    if jwt_token:
        token = "Bearer " + jwt_token
    else:
        token = "Bearer "
    return token if not raw else jwt_token


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


def set_previous_variety(module_name, variety_name, variety_en, flag):
    """ 设置用户最近使用的品种 """
    # {'top':[{variety_en:'',variety_name:''},{}], 'bottom': []}
    previous_filepath = os.path.join(BASE_DIR, "dawn/{}.dat".format(module_name))
    if not os.path.exists(previous_filepath):
        with open(previous_filepath, "wb") as f:
            pickle.dump({'top': [{}, {}], 'bottom': [{}, {}]}, f)
            f.close()
    # 先读取,后写入
    with open(previous_filepath, "rb") as fp:
        old_variety = pickle.load(fp)
        fp.close()
    if flag == 'top':
        top_v = old_variety['top']
        top_v[0], top_v[1] = top_v[1], top_v[0]  # 交换位置
        # 写入第一个
        top_v[0] = {'variety_en': variety_en, 'variety_name': variety_name}
    if flag == 'bottom':
        bottom_v = old_variety['bottom']
        bottom_v[0], bottom_v[1] = bottom_v[1], bottom_v[0]  # 交换位置
        bottom_v[0] = {'variety_en': variety_en, 'variety_name': variety_name}
    with open(previous_filepath, "wb") as fp:
        # 写入文件
        pickle.dump(old_variety, fp)


def get_previous_variety(module_name):
    """ 获取用户最近使用的品种 """
    previous_filepath = os.path.join(BASE_DIR, "dawn/{}.dat".format(module_name))
    if not os.path.exists(previous_filepath):
        return {'top': [{}, {}], 'bottom': [{}, {}]}
    with open(previous_filepath, "rb") as fp:
        variety = pickle.load(fp)
    return variety


def set_weekly_exclude_variety(exclude: str):
    """设置(周度持仓变化)排除的品种 """
    config_filepath = os.path.join(BASE_DIR, "dawn/client.ini")
    config = QSettings(config_filepath, QSettings.IniFormat)
    config.setValue("USER/VEXCLUDE", exclude)


def get_weekly_exclude_variety():
    """ 获取(周度持仓变化)用户排除的品种 """
    config_filepath = os.path.join(BASE_DIR, "dawn/client.ini")
    config = QSettings(config_filepath, QSettings.IniFormat)
    exclude_variety = config.value('USER/VEXCLUDE')
    return exclude_variety if exclude_variety else ''
