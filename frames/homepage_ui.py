# _*_ coding:utf-8 _*_
# @File  : homepage_ui.py
# @Time  : 2020-07-19 15:12
# @Author: zizle
import math
import os
import json
from datetime import datetime
from PyQt5.QtWidgets import (qApp, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QListWidget,
                             QStackedWidget, QGridLayout, QTableWidget, QFrame, QHeaderView, QTableWidgetItem,
                             QAbstractItemView, QGraphicsDropShadowEffect, QTextEdit, QMessageBox)
from PyQt5.QtCore import Qt, QRect, QMargins, QSize, QUrl, QThread, pyqtSignal
from PyQt5.QtGui import QPainter, QPixmap, QIcon, QImage, QBrush, QColor
from PyQt5.QtNetwork import QNetworkRequest, QNetworkAccessManager
from widgets.sliding_stacked import SlidingStackedWidget
from utils.client import get_user_token
from settings import BASE_DIR, STATIC_URL, SERVER_API, HOMEPAGE_TABLE_ROW_HEIGHT, HOMEPAGE_MENUS


class MenusContainerWidget(QWidget):
    """ 左侧菜单容器控件 """
    def __init__(self, *args, **kwargs):
        super(MenusContainerWidget, self).__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_StyledBackground, True)  # 必须设置,如果不设置将导致子控件产生阴影
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setOffset(0, 1)
        shadow.setColor(QColor(100, 100, 100))
        shadow.setBlurRadius(5)
        self.setGraphicsEffect(shadow)
        self.setObjectName("menuContainer")
        # background-color:rgb(250,250,250);必须设置,不设置将导致子控件产生阴影
        self.setStyleSheet(
            "#menuContainer{background-color:rgb(250,250,250);border-radius:2px}"
            "#pushButton{border:none;text-align:left;padding:2px 1px 2px 8px;}"
            "#pushButton:hover{border:none;background-color:rgb(220,220,220);color:rgb(248,121,27)}"
        )

    def enterEvent(self, event):
        effect = self.graphicsEffect()
        effect.setOffset(1, 2)
        self.setGraphicsEffect(effect)

    def leaveEvent(self, event):
        effect = self.graphicsEffect()
        effect.setOffset(0, 1)
        self.setGraphicsEffect(effect)


class LeftChildrenMenuWidget(QWidget):
    """ 左侧子菜单的显示 """
    SelectedMenu = pyqtSignal(str, str)

    def __init__(self, menus, *args, **kwargs):
        super(LeftChildrenMenuWidget, self).__init__(*args, **kwargs)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(QMargins(0, 0, 0, 5))
        for menu_item in menus:
            menu_layout = QVBoxLayout()
            menu_layout.setSpacing(5)
            menu_layout.setContentsMargins(QMargins(5, 0, 5, 5))
            menu_label = QLabel(menu_item["name"], self)
            menu_label.setObjectName("menuLabel")
            menu_layout.addWidget(menu_label)

            # 子菜单控件
            menus_widget = MenusContainerWidget(self)
            layout = QGridLayout()
            layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            layout.setContentsMargins(QMargins(5, 5, 5, 5))
            layout.setSpacing(0)

            # 增加button按钮
            row, col = 0, 0
            for children_item in menu_item["children"]:
                button = QPushButton(children_item["name"], menus_widget)
                setattr(button, "menu_id", children_item["id"])
                button.setObjectName("pushButton")
                button.setFixedSize(110, 22)
                button.setCursor(Qt.PointingHandCursor)
                button.clicked.connect(self.menu_selected)
                layout.addWidget(button, row, col)
                col += 1
                if col >= 3:
                    col = 0
                    row += 1

            menus_widget.setLayout(layout)
            menu_layout.addWidget(menus_widget)

            main_layout.addLayout(menu_layout)

        self.setLayout(main_layout)
        main_layout.addStretch()
        self.setStyleSheet(
            "#menuLabel{padding-left:0px;font-weight:bold}"
        )

    def menu_selected(self):
        """ 菜单点击 """
        sender = self.sender()
        self.SelectedMenu.emit(getattr(sender, "menu_id"), sender.text())


class AdImageThread(QThread):
    """ 请求广告图片的线程 """
    get_back_image = pyqtSignal(QImage)

    def __init__(self, image_url, *args, **kwargs):
        super(AdImageThread, self).__init__(*args, **kwargs)
        self.image_url = image_url

    def run(self):
        network_manager = QNetworkAccessManager()  # 当前是子线程,设置parent会引发警告,使用主线程的manager也会引发警告,重新实例化
        reply = network_manager.get(QNetworkRequest(QUrl(self.image_url)))
        reply.finished.connect(self.image_reply)
        self.exec_()

    def image_reply(self):
        reply = self.sender()
        if reply.error():
            pass
        else:
            image = QImage.fromData(reply.readAll().data())
            self.get_back_image.emit(image)
        reply.deleteLater()
        reply.manager().deleteLater()  # 当前是子线程,无法为manger设置parent,手动删除
        self.quit()


class PixMapLabel(QLabel):
    """ 显示图片的label """

    def __init__(self, ad_data, *args, **kwargs):
        super(PixMapLabel, self).__init__(*args)
        self.ad_data = ad_data
        url = STATIC_URL + self.ad_data.get("image", '')
        # # 无法在本控件内直接使用异步访问图片(可能是由于上一级QEventLoop影响)
        # # 如果上一级不用QEventLoop则无法加载除控制的按钮
        # self.image_thread = AdImageThread(url)
        # self.image_thread.finished.connect(self.image_thread.deleteLater)
        # self.image_thread.get_back_image.connect(self.fill_image_pixmap)
        # self.image_thread.start()
        imagepath = os.path.join(BASE_DIR, 'cache/' + ad_data['image'])
        self.fill_image_pixmap(image=imagepath)

    def fill_image_pixmap(self, image: str):
        self.setPixmap(QPixmap(image))
        self.setScaledContents(True)

    def get_ad_data(self):
        return self.ad_data


class ControlButton(QPushButton):
    """ 跳转轮播位置按钮 """

    def __init__(self, icon_path, hover_icon_path, *args):
        super(ControlButton, self).__init__(*args)
        self.icon_path = icon_path
        self.hover_icon_path = hover_icon_path
        self.setCursor(Qt.PointingHandCursor)
        self.setIcon(QIcon(self.icon_path))
        self.setObjectName("controlButton")
        self.setStyleSheet(
            "#controlButton{border:none;}#controlButton:hover{color:#d81e06}"
            "#controlButton:focus{outline: none;} "
        )
        self.setIconSize(QSize(13, 13))

    # def enterEvent(self, *args, **kwargs):
    #     self.setIcon(QIcon(self.hover_icon_path))
    #
    # def leaveEvent(self, *args, **kwargs):
    #     self.setIcon(QIcon(self.icon_path))


""" 模块控件内的信息展示表格 """


class ModuleWidgetTable(QTableWidget):
    def __init__(self, *args, **kwargs):
        super(ModuleWidgetTable, self).__init__(*args)
        self.setMouseTracking(True)
        self.horizontalHeader().hide()
        self.verticalHeader().hide()
        self.setFrameShape(QFrame.NoFrame)
        self.setFocusPolicy(Qt.NoFocus)
        self.setEditTriggers(QHeaderView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setShowGrid(False)
        self.setWordWrap(False)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("contentTable")
        # self.setStyleSheet(
        #     "#contentTable::item:hover{color:rgb(248,121,27);}"
        # )

        # 保存显示的内容信息和参数
        self.content_values = []
        self.content_keys = []
        self.data_keys = []
        self.resize_cols = []
        self.column_text_color = {}
        self.zero_text_color = []
        self.center_alignment_columns = []

        # 鼠标移动整行颜色变化
        self.mouse_last_row = -1
        self.itemEntered.connect(self.mouse_enter_item)

    def mouse_enter_item(self, item):
        current_row = self.row(item)
        # 改变当前行的颜色
        for col in range(self.columnCount()):
            self.item(current_row, col).setForeground(QBrush(QColor(248, 121, 27)))
        # 恢复离开行的颜色
        self.recover_row_color()
        self.mouse_last_row = current_row

    def recover_row_color(self):
        if self.mouse_last_row >= 0:
            for col in range(self.columnCount()):
                self.item(self.mouse_last_row, col).setForeground(QBrush(QColor(0, 0, 0)))
                # 如果原来有设置颜色的恢复原来的颜色
                if col in self.column_text_color.keys():
                    self.item(self.mouse_last_row, col).setForeground(QBrush(self.column_text_color.get(col)))
                if col in self.zero_text_color:
                    num = self.item(self.mouse_last_row, col).text()
                    if float(num) > 0:
                        self.item(self.mouse_last_row, col).setForeground(QBrush(QColor(203, 0, 0)))
                    elif float(num) < 0:
                        self.item(self.mouse_last_row, col).setForeground(QBrush(QColor(0, 124, 0)))
                    else:  # 已经设置为黑色了
                        pass

    def leaveEvent(self, *args, **kwargs):
        """ 鼠标离开事件 """
        # 将最后记录行颜色变为原来的样子,且修改记录行为-1
        self.recover_row_color()
        self.mouse_last_row = -1

    def set_contents(
            self, content_values, content_keys, data_keys, resize_cols, column_text_color: dict,
            zero_text_color: list, center_alignment_columns: list
    ):
        self.content_values = content_values
        self.content_keys = content_keys
        self.data_keys = data_keys
        self.resize_cols = resize_cols
        self.column_text_color = column_text_color
        self.zero_text_color = zero_text_color
        self.center_alignment_columns = center_alignment_columns

        self.show_contents()

    def show_contents(self):
        max_row_count = math.ceil(self.height() / HOMEPAGE_TABLE_ROW_HEIGHT)
        self.clearContents()
        self.setRowCount(max_row_count)
        self.setColumnCount(len(self.content_keys))
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for col in self.resize_cols:
            self.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeToContents)
        for row, row_item in enumerate(self.content_values):
            self.setRowHeight(row, HOMEPAGE_TABLE_ROW_HEIGHT)
            for col, col_key in enumerate(self.content_keys):
                item = QTableWidgetItem(str(row_item[col_key]))
                if col == 0:
                    item.setData(Qt.UserRole, {key: row_item[key] for key in self.data_keys})
                if col in self.column_text_color.keys():
                    item.setForeground(QBrush(self.column_text_color.get(col)))
                if col in self.zero_text_color:
                    if float(row_item[col_key]) > 0:  # 将内容转数字与0比较大小设置颜色
                        color = QColor(203, 0, 0)
                    elif float(row_item[col_key]) < 0:
                        color = QColor(0, 124, 0)
                    else:
                        color = QColor(0, 0, 0)
                    item.setForeground(QBrush(color))
                if col in self.center_alignment_columns:
                    item.setTextAlignment(Qt.AlignCenter)
                else:
                    item.setTextAlignment(Qt.AlignVCenter)
                self.setItem(row, col, item)

    def resizeEvent(self, *args, **kwargs):
        super(ModuleWidgetTable, self).resizeEvent(*args, **kwargs)
        # 计算能显示的行数,重新显示数据
        self.show_contents()


""" 各模块控件 """


class ModuleWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(ModuleWidget, self).__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_StyledBackground, True)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(QMargins(1, 1, 1, 1))
        main_layout.setSpacing(0)
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(QMargins(8, 0, 8, 0))
        title_layout.setAlignment(Qt.AlignVCenter)
        self.title_label = QLabel(self)
        self.title_label.setFixedHeight(40)  # 固定标题高度
        self.title_label.setObjectName("titleLabel")
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        self.more_button = QPushButton("更多>>", self)
        self.more_button.setCursor(Qt.PointingHandCursor)
        title_layout.addWidget(self.more_button)
        main_layout.addLayout(title_layout)
        # 分割线
        h_line = QFrame(self)
        h_line.setLineWidth(2)
        h_line.setFrameStyle(QFrame.HLine | QFrame.Plain)
        h_line.setStyleSheet("color:rgb(228,228,228)")
        main_layout.addWidget(h_line)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(QMargins(8, 3, 8, 8))
        self.content_table = ModuleWidgetTable(self)
        content_layout.addWidget(self.content_table)
        main_layout.addLayout(content_layout)

        self.setLayout(main_layout)
        self.more_button.setObjectName("moreButton")

        # 设置阴影
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setOffset(0, 1)
        shadow.setColor(QColor(100, 100, 100))
        shadow.setBlurRadius(5)
        self.setGraphicsEffect(shadow)
        self.setObjectName("moduleWidget")

        self.setStyleSheet(
            "#moduleWidget{background-color:rgb(254,254,254);border:1px solid rgb(240,240,240)}"
            "#titleLabel{color:rgb(233,66,66);font-size:15px;font-weight:bold}"
            "#moreButton{border:none;font-size:12px;color:rgb(104,104,104)}"
            "#moreButton:hover{color:rgb(233,66,66)}"
        )

    def enterEvent(self, event):
        effect = self.graphicsEffect()
        effect.setOffset(1, 2)
        self.setGraphicsEffect(effect)

    def leaveEvent(self, event):
        effect = self.graphicsEffect()
        effect.setOffset(0, 1)
        self.setGraphicsEffect(effect)

    def set_title(self, title: str):
        """ 设置标题 """
        self.title_label.setText(title)

    def set_contents(
            self, content_values, content_keys, data_keys, resize_cols, column_text_color: dict,
            zero_text_color: list, center_alignment_columns: list
    ):
        """
        设置内容
        :params:content_values 内容列表
        :params: content_keys  内容的key
        :params: data_keys 设置在首个item中的DataKeys
        :params: resize_cols 设置随内容大小的列
        :params: column_text_color 设置改变文字颜色的列
        :params: zero_text_color 根据比0大小设置颜色的列
        """
        self.content_table.set_contents(
            content_values, content_keys, data_keys, resize_cols, column_text_color, zero_text_color,
            center_alignment_columns
        )


""" 意见反馈控件 """


class SuggestWidget(QWidget):

    def __init__(self, *args, **kwargs):
        super(SuggestWidget, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        title_label = QLabel('意见建议', self)
        title_label.setStyleSheet('font-weight:bold')
        layout.addWidget(title_label, alignment=Qt.AlignLeft | Qt.AlignTop)

        self.text_edit = QTextEdit(self)
        self.text_edit.setMinimumHeight(300)
        layout.addWidget(self.text_edit)

        self.submit_button = QPushButton('提交', self)
        self.submit_button.clicked.connect(self.submit_suggestion)
        layout.addWidget(self.submit_button, alignment=Qt.AlignBottom | Qt.AlignRight)
        msg = "<div style=font-size:11px>如有其他问题或更多建议也可联系QQ:<span style=color:red>3482137862</span>" \
              "或发送邮件到邮箱<span style=color:red>3482137862@qq.com</span>进行反馈。</div>"
        tip_label = QLabel(msg, self)
        tip_label.setWordWrap(True)
        tip_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(tip_label)
        self.setLayout(layout)

    def submit_suggestion(self):
        if not self.text_edit.toPlainText().strip():
            return
        """ 提交意见反馈 """
        data = dict()
        data['content'] = self.text_edit.toHtml()
        data['user_token'] = get_user_token(raw=True)
        print(data)
        self.submit_button.setEnabled(False)
        # 发起请求
        url = SERVER_API + 'suggest/'
        network_manager = getattr(qApp, '_network', None)
        if not network_manager:
            return
        req = QNetworkRequest(QUrl(url))
        req.setHeader(QNetworkRequest.ContentTypeHeader, 'application/json')
        reply = network_manager.post(req, json.dumps(data).encode('utf8'))
        reply.finished.connect(self.suggest_reply)

    def suggest_reply(self):
        reply = self.sender()
        self.submit_button.setEnabled(True)
        if reply.error():
            msg = '提交反馈失败了,原因：{}'.format(reply.error())
        else:
            msg = '提交成功!'
            self.text_edit.clear()
        QMessageBox.information(self, '信息', msg)
        reply.deleteLater()


        # 首页布局
#  ——————————————————————————————
# | 侧 |          |              |
# | 边 |    菜单   |    广告      |
# | 菜 |          | ————————————
# | 单 |          |              |
# |    |          |模块方块展示   |
# |    |          |              |
#  ——————————————————————————————

class HomepageUI(QWidget):
    """ 首页UI """
    LEFT_STACKED_WIDTH = 360  # 110 * 3 + 15 + 15

    def __init__(self, *args, **kwargs):
        super(HomepageUI, self).__init__(*args, **kwargs)
        # self.container = QWidget(self)  # 全局控件(scrollArea的幕布)
        layout = QHBoxLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        layout.setSpacing(0)

        # 左侧的菜单列表控件
        self.left_menu = QListWidget(self)
        self.left_menu.setFocusPolicy(Qt.NoFocus)
        # 固定宽度
        self.left_menu.setFixedWidth(42)
        layout.addWidget(self.left_menu)

        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(QMargins(0, 0, 0, 0))

        # 左侧菜单对应的stackedWidget
        menu_layout = QVBoxLayout()
        menu_layout.setContentsMargins(QMargins(28, 16, 28, 28))  # 上方稍微小些
        self.left_stacked = QStackedWidget(self)
        # 固定宽度
        self.left_stacked.setFixedWidth(self.LEFT_STACKED_WIDTH)  # 固定宽度,广告的高度
        menu_layout.addWidget(self.left_stacked)
        menu_layout.addStretch()

        content_layout.addLayout(menu_layout)

        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(QMargins(0, 28, 28, 28))  # 左侧在menu_layout处理
        # 图片轮播控件
        self.slide_stacked = SlidingStackedWidget(self)
        # 广告图片的高度
        self.slide_stacked.setFixedHeight(300)
        right_layout.addWidget(self.slide_stacked)

        # 在轮播控件上选择按钮
        self.control_widget = QWidget(self)
        self.control_widget.setFixedHeight(300)
        self.control_widget.move(self.LEFT_STACKED_WIDTH + 66, 0)  # 66 = 28(左侧间距) + 15(菜单内距) + 15 + 8(距离控件左侧)
        control_layout = QVBoxLayout()
        control_layout.setAlignment(Qt.AlignVCenter)
        self.control_widget.setLayout(control_layout)

        # 其他模块
        modules_layout = QGridLayout()
        modules_layout.setContentsMargins(QMargins(0, 20, 0, 0))
        modules_layout.setSpacing(15)
        modules_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # 短信通
        self.instant_message_widget = ModuleWidget(self)
        # self.instant_message_widget.setFixedSize(370, 300)
        self.instant_message_widget.set_title("即时资讯")
        modules_layout.addWidget(self.instant_message_widget, 0, 0, 1, 2)

        # 现货报价
        self.spot_price_widget = ModuleWidget(self)
        # self.spot_price_widget.setFixedSize(370, 300)
        self.spot_price_widget.set_title("现货报价")
        modules_layout.addWidget(self.spot_price_widget, 1, 0)

        # 日报
        self.daily_report_widget = ModuleWidget(self)
        # self.daily_report_widget.setFixedSize(370, 300)
        self.daily_report_widget.set_title("收盘日评")
        # 周报
        self.weekly_report_widget = ModuleWidget(self)
        # self.weekly_report_widget.setFixedSize(370, 300)
        self.weekly_report_widget.set_title("研究周报")

        # 根据当前时间显示日报还是周报
        current_day = datetime.today()
        week = current_day.weekday()
        current_time = current_day.time().strftime("%H:%M")
        if week < 4 or (week == 4 and current_time < "16:00"):
            modules_layout.addWidget(self.daily_report_widget, 1, 1)
            self.weekly_report_widget.hide()
        else:
            modules_layout.addWidget(self.weekly_report_widget, 1, 1)
            self.daily_report_widget.hide()

        # # 月季报告
        # self.monthly_report_widget = ModuleWidget(self)
        # # self.monthly_report_widget.setFixedSize(370, 300)
        # self.monthly_report_widget.set_title("月季报告")
        # modules_layout.addWidget(self.monthly_report_widget, 1, 1)
        #
        # # 月季报告
        # self.annual_report_widget = ModuleWidget(self)
        # # self.annual_report_widget.setFixedSize(370, 300)
        # self.annual_report_widget.set_title("年度报告")
        # modules_layout.addWidget(self.annual_report_widget, 1, 2)

        right_layout.addLayout(modules_layout)

        content_layout.addLayout(right_layout)

        layout.addLayout(content_layout)
        self.setLayout(layout)
        self.left_menu.setObjectName("LeftMenuList")
        self.setStyleSheet(
            "#LeftMenuList{border:none;color:rgb(254,254,254);font-size:14px;"
            "background-color:rgb(233,26,46);}"
            "#LeftMenuList::item{padding:5px 0 5px 0px}"
            "#LeftMenuList::item:selected{background-color:rgb(255,255,255);color:rgb(0,0,0);}"
        )
