# _*_ coding:utf-8 _*_
# @File  : variety_data.py
# @Time  : 2020-09-03 8:29
# @Author: zizle
import json

from PyQt5.QtGui import QIcon, QCursor
from PyQt5.QtWidgets import qApp, QTableWidgetItem, QMenu, QHeaderView
from PyQt5.QtNetwork import QNetworkRequest, QNetworkAccessManager
from PyQt5.QtCore import Qt, QUrl
from settings import SERVER_API, logger
from utils.client import get_user_token
from popup.sheet_charts import SheetChartsPopup, ChartPopup
from popup.industry_popup import DisposeChartPopup
from popup.message import WarningPopup, InformationPopup
from widgets import OperateButton
from .variety_data_ui import VarietyDataUI


class VarietyData(VarietyDataUI):
    def __init__(self, variety_en=None, *args, **kwargs):
        super(VarietyData, self).__init__(*args, **kwargs)
        self.variety_en = variety_en
        self.variety_tree.left_mouse_clicked.connect(self.selected_variety_event)
        # 双击数据库下的条目
        self.sheet_table.doubleClicked.connect(self.popup_show_chart_sheet)
        if variety_en is None:
            # 默认显示股指的数据
            self._get_variety_sheets("GP")
            # 默认加载主页显示的图形
            self._load_default_page()
        else:
            self._get_variety_sheets(variety_en)
            self._load_variety_charts(variety_en)

        # 右击事件
        self.sheet_table.right_mouse_clicked.connect(self.sheet_table_right_mouse)
        # 渲染我的图形库
        self.tab.tabBar().tabBarClicked.connect(self.enter_tab)

    def enter_tab(self, tab_index):
        if self.variety_en is None:
            self.my_charts.chart_container.setHtml("<div style='color:#de2020'>您还未指定品种!左侧选择品种后查看图形。</div>")
        if tab_index == 2 and self.variety_en is not None:
            self.render_my_charts()

    def render_my_charts(self):
        # 请求当前用户的图形并进行渲染和管理表格填充
        user_token = get_user_token(raw=True)
        url = SERVER_API + "variety/{}/chart/?is_own=1&render=1&token={}&category=0".format(self.variety_en, user_token)
        self.my_charts.chart_container.load(QUrl(url))
        # 加载管理的表格数据
        self.get_my_charts_to_manager()

    def get_my_charts_to_manager(self):
        user_token = get_user_token(raw=True)
        network_manager = getattr(qApp, "_network", QNetworkAccessManager(self))
        url = SERVER_API + "variety/{}/chart/?is_own=1&token={}&category={}".format(self.variety_en, user_token, 0)
        request = QNetworkRequest(QUrl(url))
        request.setRawHeader("Authorization".encode("utf-8"), user_token.encode("utf-8"))
        reply = network_manager.get(request)
        reply.finished.connect(self.variety_charts_reply)

    def variety_charts_reply(self):
        reply = self.sender()
        if reply.error():
            logger.error("用户获取自己的品种的数据图形信息失败:{}".format(reply.error()))
        else:
            data = reply.readAll().data()
            data = json.loads(data.decode("utf-8"))
            self.show_variety_charts(data["data"])
        reply.deleteLater()

    def show_variety_charts(self, charts_list):
        self.my_charts.chart_table.clear()
        self.my_charts.chart_table.setColumnCount(4)
        self.my_charts.chart_table.setHorizontalHeaderLabels(["创建日期", "标题", '图形', '删除'])
        self.my_charts.chart_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.my_charts.chart_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.my_charts.chart_table.setRowCount(len(charts_list))
        for row, row_item in enumerate(charts_list):
            item0 = QTableWidgetItem(row_item["create_time"])
            item0.setData(Qt.UserRole, row_item['id'])
            item0.setTextAlignment(Qt.AlignCenter)
            self.my_charts.chart_table.setItem(row, 0, item0)
            item1 = QTableWidgetItem(row_item["title"])
            item1.setTextAlignment(Qt.AlignCenter)
            self.my_charts.chart_table.setItem(row, 1, item1)
            # 图形
            item2_button = OperateButton("media/icons/chart.png", "media/icons/chart_hover.png",self.my_charts.chart_table)
            setattr(item2_button, "row_index", row)
            item2_button.clicked.connect(self.show_current_chart)
            self.my_charts.chart_table.setCellWidget(row, 2, item2_button)
            item3_button = OperateButton("media/icons/delete.png", "media/icons/delete_hover.png", self)
            setattr(item3_button, "row_index", row)
            item3_button.clicked.connect(self.user_delete_chart)
            self.my_charts.chart_table.setCellWidget(row, 3, item3_button)

    def show_current_chart(self):
        """ 显示当前的图形 """
        current_row = getattr(self.sender(), "row_index")
        chart_id = self.my_charts.chart_table.item(current_row, 0).data(Qt.UserRole)
        chart_name = self.my_charts.chart_table.item(current_row, 1).text()
        popup = ChartPopup(chart_id, self)
        popup.setWindowTitle(chart_name)
        popup.show()

    def user_delete_chart(self):
        """ 用户删除图形"""
        sender_button = self.sender()
        current_row = getattr(sender_button, "row_index")
        chart_id = self.my_charts.chart_table.item(current_row, 0).data(Qt.UserRole)
        warning = WarningPopup("确定删除这张图形吗?删除后将不可恢复!", self)
        warning.set_data({"chart_id": chart_id})
        warning.confirm_operate.connect(self.confirm_delete_chart)
        warning.exec_()

    def confirm_delete_chart(self, data):
        """ 确定删除数据图形 """
        chart_id = data["chart_id"]
        url = SERVER_API + "chart/{}/".format(chart_id)
        request = QNetworkRequest(QUrl(url))
        request.setRawHeader("Authorization".encode('utf-8'), get_user_token().encode("utf-8"))
        network_manager = getattr(qApp, "_network")
        reply = network_manager.deleteResource(request)
        reply.finished.connect(self.delete_chart_reply)

    def delete_chart_reply(self):
        """ 删除图形返回 """
        reply = self.sender()
        if reply.error():
            m = "删除图形失败了{}".format(reply.error)
        else:
            m = "删除成功!"
        p = InformationPopup(m, self)
        p.exec_()
        self.render_my_charts()  # 重新加载图形

    def sheet_table_right_mouse(self):
        r_menu = QMenu(self)
        chart_action = r_menu.addAction('我要绘图')
        chart_action.setIcon(QIcon('media/icons/chart.png'))
        chart_action.triggered.connect(self.to_draw_custom_chart)
        r_menu.exec_(QCursor.pos())

    def _load_default_page(self):
        """ 加载主页默认页面 """
        url = SERVER_API + "industry/chart/"
        self.chart_container.load(QUrl(url))

    def selected_variety_event(self, variety_id, group_text, variety_en):
        """ 选择了某个品种事件 """
        self._get_variety_sheets(variety_en)
        self._load_variety_charts(variety_en)
        self.variety_en = variety_en
        if self.tab.currentIndex() == 2:
            self.render_my_charts()

    def _load_variety_charts(self, variety_en):
        """ 加载品种下的所有数据图 """
        uset_token = get_user_token().split(' ')[1]
        url = SERVER_API + "variety/{}/chart/?render=1&is_petit=1&token={}".format(variety_en, uset_token)
        self.chart_container.load(QUrl(url))

    def _get_variety_sheets(self, variety_en):
        """ 获取当前品种下的数据表 """
        network_manager = getattr(qApp, "_network")
        user_token = get_user_token()
        url = SERVER_API + "variety/{}/sheet/".format(variety_en)
        request = QNetworkRequest(QUrl(url))
        request.setRawHeader("Authorization".encode("utf-8"), user_token.encode("utf-8"))
        reply = network_manager.get(request)
        reply.finished.connect(self.variety_sheets_reply)

    def variety_sheets_reply(self):
        """ 请求到品种数据表 """
        reply = self.sender()
        if reply.error():
            logger.error("产业数据库主页获取数据表失败:{}".format(reply.error()))
        else:
            data = reply.readAll().data()
            data = json.loads(data.decode("utf-8"))
            # 过滤掉私有的数据表
            sheets = list(filter(lambda x: False if x.get('is_private', None) else True, data['sheets']))
            self.sheet_table_show_contents(sheets)

    def sheet_table_show_contents(self, sheets):
        """ 数据列表显示 """
        self.sheet_table.clearContents()
        self.sheet_table.setRowCount(len(sheets))
        for row, row_item in enumerate(sheets):
            item0 = QTableWidgetItem(str(row + 1))
            item0.setData(Qt.UserRole, {"sheet_id": row_item["id"], "sheet_variety": row_item['variety_en']})
            item0.setTextAlignment(Qt.AlignCenter)
            self.sheet_table.setItem(row, 0, item0)

            item1 = QTableWidgetItem(row_item["sheet_name"])
            item1.setToolTip('双击查看数据,右键自定义作图')
            item1.setTextAlignment(Qt.AlignCenter)
            self.sheet_table.setItem(row, 1, item1)

            item2 = QTableWidgetItem(row_item["min_date"])
            item2.setTextAlignment(Qt.AlignCenter)
            self.sheet_table.setItem(row, 2, item2)

            item3 = QTableWidgetItem(row_item["max_date"])
            item3.setTextAlignment(Qt.AlignCenter)
            self.sheet_table.setItem(row, 3, item3)

            item4_button = OperateButton("media/icons/chart.png", "media/icons/chart_hover.png", self)
            setattr(item4_button, "row_index", row)
            item4_button.clicked.connect(self.show_sheet_charts)
            self.sheet_table.setCellWidget(row, 4, item4_button)

    def popup_show_chart_sheet(self):
        """ 弹窗显示某个表下的所有图形和表数据"""
        self.show_sheet_charts(self.sheet_table.currentRow())

    def show_sheet_charts(self, current_row=False):
        """ 弹窗显示某个表下的所有图形和表数据 """
        if current_row is False:
            current_row = getattr(self.sender(), "row_index")
        sheet_data = self.sheet_table.item(current_row, 0).data(Qt.UserRole)
        sheet_id = sheet_data.get('sheet_id', None)
        if not sheet_id:
            return
        sheet_name = self.sheet_table.item(current_row, 1).text()
        popup = SheetChartsPopup(sheet_id, 0, self)
        popup.setWindowTitle(sheet_name)
        popup.exec_()

    def to_draw_custom_chart(self):
        """ 弹窗，用户绘图 """
        current_row = self.sheet_table.currentRow()
        if current_row < 0:
            return
        sheet_data = self.sheet_table.item(current_row, 0).data(Qt.UserRole)
        sheet_id = sheet_data.get('sheet_id', None)
        variety_en = sheet_data.get('sheet_variety', None)
        if not sheet_id or not variety_en:
            return
        sheet_name = self.sheet_table.item(current_row, 1).text()
        # 弹窗绘图
        chart_popup = DisposeChartPopup(variety_en, sheet_id, self)
        chart_popup.setWindowTitle(sheet_name)
        chart_popup.chart_widget.private_check.setChecked(Qt.Checked)
        chart_popup.chart_widget.private_check.hide()
        chart_popup.exec_()
