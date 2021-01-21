# _*_ coding:utf-8 _*_
# @File  : frameless.py
# @Time  : 2020-08-28 10:28
# @Author: zizle

""" 主窗口事件处理 """
import os
import re
import json
import pickle
import sys
from subprocess import Popen
from PyQt5.QtWidgets import qApp, QLabel
from PyQt5.QtNetwork import QNetworkRequest
from PyQt5.QtCore import Qt, QUrl, QSettings, QTimer

from settings import SERVER_API, ADMINISTRATOR, BASE_DIR, ONLINE_COUNT_INTERVAL, PLATE_FORM, SYS_BIT, logger
from utils.client import get_user_token, is_module_verify, remove_user_logged, get_client_uuid, set_client_uuid_with_ini
from .frameless_ui import FrameLessWindowUI

from admin.operator.user_manager import UserManager
from admin.operator.client_manager import ClientManage
from admin.operator.variety import VarietyAdmin
from admin.industry.user_data import UserDataMaintain
from admin.industry.exchange_spider import ExchangeSpider
from admin.industry.spot_price import SpotPriceAdmin
from admin.operator.user_extension import UserExtensionPage
from admin.receipt_parser import ReceiptParser
from admin.homepage.advertisement import HomepageAdAdmin
from admin.product.message_service import MessageServiceAdmin
from admin.product.consultant_service import ConsultantServiceAdmin
from admin.product.strategy_service import StrategyServiceAdmin
from admin.product.variety_service import VarietyServiceAdmin
from frames.homepage_extend import DailyReport, WeeklyReport, MonthlyReport, AnnualReport
from frames.homepage import Homepage
from frames.product.message_service import ShortMessage
from frames.product import ProductPage
from frames.calculate.calculate_plat import CalculatePlat
from frames.industry.variety_data import VarietyData
from frames.industry.exchange_query import ExchangeQuery
from frames.industry.net_position import NetPositionWidget
from frames.about_us import CheckVersion
from frames.passport import UserPassport
from frames.user_center import UserCenter
from frames.delivery import DeliveryPage
from popup.update import NewVersionPopup
from popup.message import ExitAppPopup, InformationPopup
from popup.password import EditPasswordPopup


class ClientMainApp(FrameLessWindowUI):
    """ 主程序 """
    def __init__(self, *args, **kwargs):
        super(ClientMainApp, self).__init__(*args, **kwargs)

        qApp.applicationStateChanged.connect(self.application_state_changed)

        self.current_page_id = None  # 当前的页面
        self.user_online_timer = QTimer(self)                                              # 用户登录时间定时器
        self.user_online_timer.timeout.connect(self.update_user_online_time)

        self.navigation_bar.username_button.clicked.connect(self.clicked_username_button)  # 点击登录或跳转个人中心
        self.navigation_bar.logout_button.clicked.connect(self.user_logout_proxy)          # 用户退出
        self.navigation_bar.menu_clicked.connect(self.enter_module_page)

        self.set_default_homepage()

        self._user_login_automatic()                                                      # 用户启动自动登录

        if not self.user_online_timer.isActive():                       # 开启在线时间统计
            self.user_online_timer.start(ONLINE_COUNT_INTERVAL)

        self._checking_new_version()

    def close(self):
        """ 程序退出 """
        def confirm_exit():
            super(ClientMainApp, self).close()
        # 提示是否退出
        p = ExitAppPopup("确定退出分析决策系统?", self)
        p.confirm_operate.connect(confirm_exit)
        p.exec_()

    def _checking_new_version(self):
        """ 检测新版本 """
        # 获取当前版本号
        json_file = os.path.join(BASE_DIR, "classini/update_{}_{}.json".format(PLATE_FORM, SYS_BIT))
        if not os.path.exists(json_file):
            return
        with open(json_file, "r", encoding="utf-8") as jf:
            update_json = json.load(jf)
        is_manager = 1 if ADMINISTRATOR else 0
        url = SERVER_API + "check_version/?version={}&plateform={}&sys_bit={}&is_manager={}".format(
            update_json["VERSION"], PLATE_FORM, SYS_BIT, is_manager)
        request = QNetworkRequest(QUrl(url))
        network_manager = getattr(qApp, "_network")
        reply = network_manager.get(request)
        reply.finished.connect(self.last_version_back)

    def last_version_back(self):
        """ 检测版本结果 """
        reply = self.sender()
        if reply.error():
            reply.deleteLater()
            return
        data = reply.readAll().data()
        u_data = json.loads(data.decode("utf-8"))
        if u_data["update_needed"]:
            # 写入待更新信息
            for_update_file = os.path.join(BASE_DIR, "classini/for_update_{}.json".format(SYS_BIT))
            f_data = {
                "VERSION": u_data["last_version"],
                "SERVER": u_data["file_server"],
                "FILES": u_data["update_files"]
            }
            with open(for_update_file, "w", encoding="utf-8") as f:
                json.dump(f_data, f, indent=4, ensure_ascii=False)
            message = u_data["update_detail"]
            p = NewVersionPopup(message, self)
            p.to_update.connect(self.to_update_page)
            if u_data.get("update_force"):  # 强制更新
                p.set_force()
            p.exec_()
        else:
            pass
        reply.deleteLater()

    def to_update_page(self):
        """ 退出当前程序，启动更新更新 """
        # script_file = os.path.join(BASE_DIR, "AutoUpdate.exe")
        script_file = os.path.join(BASE_DIR, "Update.exe")
        is_close = True
        if os.path.exists(script_file):
            try:
                Popen(script_file, shell=False)
            except OSError as e:
                self.run_message.setText(str(e))
                is_close = False
        else:
            p = InformationPopup("更新程序丢失...", self)
            p.exec_()
            is_close = False
        if is_close:
            sys.exit()

    def application_state_changed(self, state):
        """ 应用程序状态发生变化 """
        if state == Qt.ApplicationInactive:
            if self.user_online_timer.isActive():
                self.user_online_timer.stop()
        elif state == Qt.ApplicationActive:
            if not self.user_online_timer.isActive():
                self.user_online_timer.start(ONLINE_COUNT_INTERVAL)

    def update_user_online_time(self):
        """ 更新用户 (客户端)在线时间"""
        client_ini_path = os.path.join(BASE_DIR, "dawn/client.ini")
        token_config = QSettings(client_ini_path, QSettings.IniFormat)
        is_logged = self.navigation_bar.get_user_login_status()
        client_uuid = token_config.value("TOKEN/UUID") if token_config.value("TOKEN/UUID") else ""
        user_token = ""
        if is_logged:
            user_token = token_config.value("USER/BEARER") if token_config.value("USER/BEARER") else ""
        token = "Bearer " + user_token
        network_manager = getattr(qApp, '_network')
        url = SERVER_API + "user/online/?machine_uuid=" + client_uuid
        request = QNetworkRequest(QUrl(url))
        request.setRawHeader("Authorization".encode("utf-8"), token.encode("utf-8"))
        reply = network_manager.put(request, None)  # 此处不用post：发现Qt查询参数丢失
        reply.finished.connect(reply.deleteLater)

    def set_default_homepage(self):
        """ 设置默认的首页 """
        homepage = Homepage()
        # 关联菜单信号
        homepage.SkipPage.connect(self.homepage_menu_selected)
        self.center_widget.setCentralWidget(homepage)
        self.current_page_id = None

    def clicked_username_button(self):
        """ 点击了登录/用户名
            未登录就跳转到登录页面,已登录则跳转到个人中心
        """
        username_button = self.sender()
        is_user_logged = getattr(username_button, 'is_logged')
        if is_user_logged:
            center_widget = UserCenter()
            center_widget.reset_password_signal.connect(self.user_logout_proxy)
        else:
            center_widget = UserPassport()
            center_widget.username_signal.connect(self.user_login_successfully)
            self.current_page_id = "login"  # 赋予id,登录成功可以跳转到首页
        self.center_widget.setCentralWidget(center_widget)

    def user_login_successfully(self, username):
        """ 用户登录成功 """
        self.navigation_bar.username_button.setText(username)
        self.navigation_bar.set_user_login_status(status=1)
        self.navigation_bar.logout_button.show()
        # 当前不是首页就跳转到首页(防止启动自动登录2次跳转首页)
        if self.current_page_id is not None:
            self.set_default_homepage()
        # 刷新当前用户权限
        self.refresh_authorization()

    def _user_login_automatic(self):
        """ 用户自动登录 """
        configs_path = os.path.join(BASE_DIR, "dawn/client.ini")
        app_config = QSettings(configs_path, QSettings.IniFormat)
        is_auto_login = app_config.value("USER/AUTOLOGIN")
        if is_auto_login:  # 使用TOKEN自动登录
            user_token = app_config.value("USER/BEARER") if app_config.value("USER/BEARER") else ''
            url = SERVER_API + "user/token-login/?client=" + get_client_uuid()
            request = QNetworkRequest(QUrl(url))
            token = "Bearer " + user_token
            request.setRawHeader("Authorization".encode("utf-8"), token.encode("utf-8"))
            network_manager = getattr(qApp, '_network')
            reply = network_manager.get(request)
            reply.finished.connect(self._user_login_automatic_reply)

    def _user_login_automatic_reply(self):
        """ 自动登录返回 """
        reply = self.sender()
        data = reply.readAll().data()
        if reply.error():
            center_widget = QLabel(
                "登录信息已经失效了···\n请重新登录后再进行使用,访问【首页】查看更多资讯。",
                styleSheet='font-size:16px;font-weight:bold;color:rgb(230,50,50)',
                alignment=Qt.AlignCenter
            )
            self.center_widget.setCentralWidget(center_widget)
        else:
            data = json.loads(data.decode("utf-8"))
            # 写入客户端号
            set_client_uuid_with_ini(data["machine_uuid"])
            self.user_login_successfully(data["show_username"])
        reply.deleteLater()

    def user_logout_proxy(self):
        """ 用户主动点击退出
            由于QPushButton的clicked信号默认传过来的参数为False。此函数为代理
        """
        self.user_logout()

    def user_logout(self, to_homepage=True):
        """ 用户退出
        """
        self.navigation_bar.username_button.setText('登录')
        self.navigation_bar.set_user_login_status(status=0)
        self.navigation_bar.logout_button.hide()
        # 跳转到首页
        if to_homepage:
            self.set_default_homepage()
        # 刷新权限
        self.refresh_authorization()
        # 去除自动登录
        remove_user_logged()

    def refresh_authorization(self):
        """ 刷新当前用户的权限 """
        is_logged = self.navigation_bar.get_user_login_status()
        # 用户未登录,权限为[],直接写入
        if not is_logged:
            auth_filepath = os.path.join(BASE_DIR, "dawn/auth.dat")
            with open(auth_filepath, "wb") as fp:
                pickle.dump({"role": '', "auth": []}, fp)
            return
        # 用户已登录,后端请求权限
        network_manager = getattr(qApp, '_network')
        url = SERVER_API + "user/module-authenticate/"
        request = QNetworkRequest(QUrl(url))
        request.setRawHeader("Authorization".encode("utf-8"), get_user_token().encode("utf-8"))
        reply = network_manager.get(request)
        reply.finished.connect(self.user_authorization_reply)

    def user_authorization_reply(self):
        """ 获取用户的权限返回 """
        reply = self.sender()
        if reply.error():
            logger.error("Refresh authorization fail! Qt error code: {}".format(reply.error()))
        else:
            data = json.loads(reply.readAll().data().decode("utf-8"))
            user_info = data["user"]
            auth = data["modules"]
            auth_filepath = os.path.join(BASE_DIR, "dawn/auth.dat")
            with open(auth_filepath, "wb") as fp:
                pickle.dump({"role": user_info.get("role", ""), "auth": auth}, fp)
        reply.deleteLater()

    def set_system_page(self, module_id):
        """ 进入关于系统 """
        if module_id == "0_0_1":
            page = CheckVersion()  # 版本检查页面
        elif module_id == "0_0_2":
            self.refresh_authorization()  # 刷新权限
            p = InformationPopup("权限刷新成功!", self)
            p.exec_()
            return
        elif module_id == "0_0_3":
            is_logged = self.navigation_bar.get_user_login_status()
            if not is_logged:
                p = InformationPopup("您还未登录,不能进行这个操作!", self)
                p.exec_()
                return
            p = EditPasswordPopup(self)
            p.re_login.connect(self.user_logout_proxy)  # 修改成功退出登录
            p.exec_()
            return
        else:
            page = QLabel(
                "暂未开放···\n更多资讯请访问【首页】查看.",
                styleSheet='font-size:16px;font-weight:bold;color:rgb(230,50,50)',
                alignment=Qt.AlignCenter)
        self.center_widget.setCentralWidget(page)
        self.current_page_id = module_id

    def homepage_menu_selected(self, menu_id, menu_text):
        """ 主页需要跳转页面的菜单 """
        page = self.get_homepage_skip_page(menu_id, menu_text)
        if page:
            self.center_widget.setCentralWidget(page)

    def get_homepage_skip_page(self, page_id, page_name):
        """ 获取主页跳转的页面 """
        if re.match(r"^[A-Z]{1,2}$", page_id):  # 如果是品种则请求权限跳转到品种数据库
            # 验证用户的品种数据库权限
            can_enter, tips = is_module_verify("2_0", "品种数据")
            if can_enter:
                page = VarietyData(page_id)
            else:
                p = InformationPopup(tips, self)
                p.exec_()
                return None
        elif page_id == "l_0_0_1":
            page = DailyReport()   # 日常报告
        elif page_id == "l_0_0_2":
            page = WeeklyReport()  # 周度报告
        elif page_id == "l_0_1_1":
            page = MonthlyReport()  # 月度报告
        elif page_id == "l_0_1_2":
            page = AnnualReport()   # 年度报告
        elif page_id == "l_1_0_1":
            page = ShortMessage()   # 短信通
        else:
            page = QLabel(
                "「" + page_name + "」暂未开放···\n更多资讯请访问【首页】查看.",
                styleSheet='font-size:16px;font-weight:bold;color:rgb(230,50,50)',
                alignment=Qt.AlignCenter)
        return page

    def enter_module_page(self, module_id, module_text):
        """ 根据菜单,进入不同的功能界面 """
        self.current_page_id = module_id
        if module_id == "0":                 # 进入首页
            self.set_default_homepage()
            return
        if module_id[:3] == "0_0":
            self.set_system_page(module_id)  # 进入关于系统的菜单
            return
        # 其他模块菜单验证权限
        can_enter, tips = is_module_verify(module_id, module_text)
        if can_enter:
            page = self.get_module_page(module_id, module_text)
            self.center_widget.setCentralWidget(page)
        else:
            p = InformationPopup(tips, self)
            p.exec_()

    #     client_params = QSettings('dawn/client.ini', QSettings.IniFormat)
    #
    #     network_manager = getattr(qApp, '_network')
    #     url = SERVER_API + 'user/module-authenticate/'
    #     request = QNetworkRequest(QUrl(url))
    #     request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json;charset=utf-8")
    #     user_token = client_params.value("USER/BEARER") if self.navigation_bar.get_user_login_status() else ''
    #     body_data = {
    #         "module_id": module_id,
    #         "module_text": module_text,
    #         "client_uuid": client_params.value("TOKEN/UUID"),
    #         "user_token": user_token
    #     }
    #     reply = network_manager.post(request, json.dumps(body_data).encode("utf-8"))
    #     reply.finished.connect(self.access_module_reply)
    #
    # def access_module_reply(self):
    #     reply = self.sender()
    #     data = reply.readAll().data()
    #     data = json.loads(data.decode('utf-8'))
    #     reply.deleteLater()
    #     if reply.error():
    #         center_widget = QLabel(
    #             data.get("detail", reply.error()),
    #             styleSheet='font-size:16px;font-weight:bold;color:rgb(230,50,50)',
    #             alignment=Qt.AlignCenter
    #         )
    #         if reply.error() == 201 and self.navigation_bar.get_user_login_status():
    #             self.user_logout(to_homepage=False)  # 不跳转首页
    #
    #     else:
    #         if data["authenticate"]:
    #             # 进入相应模块
    #             center_widget = self.get_module_page(data["module_id"], data["module_text"])
    #         else:
    #             center_widget = QLabel(
    #                 data["message"],
    #                 styleSheet='font-size:16px;font-weight:bold;color:rgb(230,50,50)',
    #                 alignment=Qt.AlignCenter
    #             )
    #
    #     self.center_widget.setCentralWidget(center_widget)

    def get_module_page(self, module_id, module_text):
        """ 通过权限验证,进入功能页面 """
        if module_id == "1":             # 产品服务
            page = ProductPage(self)
        elif module_id == "2_0":         # 产业数据库
            page = VarietyData()
        elif module_id == "2_1":         # 交易所数据
            page = ExchangeQuery(self)
        elif module_id == "2_2":         # 品种净持仓
            page = NetPositionWidget(self)
        elif module_id == "3":           # 交割服务
            page = DeliveryPage()
        elif module_id == "4":           # 计算平台
            page = CalculatePlat()
        elif module_id == "-9_0_0":      # 后台管理-广告设置
            page = HomepageAdAdmin(self)
        elif module_id == "-9_1_0":
            page = VarietyAdmin(self)        # 后台管理-品种管理
        elif module_id == "-9_1_1":      # 后台管理-用户管理
            page = UserManager(self)
        elif module_id == "-9_1_2":
            page = ClientManage(self)
        elif module_id == "-9_1_3":      # 后台管理-研究员微信ID
            page = UserExtensionPage(self)
        elif module_id == "-9_2_0":
            page = MessageServiceAdmin(self)      # 后台管理资讯服务
        elif module_id == "-9_2_1":
            page = ConsultantServiceAdmin(self)      # 后台管理顾问服务
        elif module_id == "-9_2_2":
            page = StrategyServiceAdmin(self)      # 后台管理策略服务
        elif module_id == '-9_2_3':
            page = VarietyServiceAdmin(self)       # 后台管理品种服务
        elif module_id == "-9_3_0":      # 后台管理-产业数据库
            page = UserDataMaintain(self)
        elif module_id == "-9_3_1":
            page = ExchangeSpider(self)
        elif module_id == "-9_3_2":
            page = SpotPriceAdmin(self)     # 后台管理-现货价格数据提取
        elif module_id == "-9_4_0":
            from admin.delivery_b import DeliveryInfoAdmin
            page = DeliveryInfoAdmin(self)  # 后台管理-交割服务-仓库管理
        elif module_id == '-9_4_1':
            page = ReceiptParser(self)      # 后台管理-交割服务-仓单数据提取
        else:
            page = QLabel(
                "「" + module_text + "」暂未开放···\n更多资讯请访问【首页】查看.",
                styleSheet='font-size:16px;font-weight:bold;color:rgb(230,50,50)',
                alignment=Qt.AlignCenter)
        return page

