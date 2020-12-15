# _*_ coding:utf-8 _*_
# @File  : basis_price.py
# @Time  : 2020-08-25 15:01
# @Author: zizle
import os
import json
import pandas as pd
from datetime import datetime
from PyQt5.QtWidgets import qApp, QTableWidgetItem, QPushButton, QAbstractItemView
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtNetwork import QNetworkRequest
from .spot_price_ui import SpotPriceAdminUI
from utils.constant import VARIETY_EN
from settings import SERVER_API, BASE_DIR


def date_converter(column_content):
    """ 时间类型转换器 """
    if isinstance(column_content, datetime):
        return column_content.strftime("%Y%m%d")
    else:
        raise ValueError('TIMEERROR')


class SpotPriceAdmin(SpotPriceAdminUI):
    def __init__(self, *args, **kwargs):
        super(SpotPriceAdmin, self).__init__(*args, **kwargs)
        self.final_data = None   # 最终现货数据
        self.today_str = ""
        self.analysis_button.clicked.connect(self.extract_spot_source_price)  # 提取数据
        self.commit_button.clicked.connect(self.commit_spot_data)             # 上传提交数据

        self.modify_query_button.clicked.connect(self.query_spot_data)        # 查询现货报价数据

    def extract_spot_source_price(self):
        """ 提取现货数据 """
        # 保存到当前属性
        if self.final_data is not None:
            del self.final_data
            self.final_data = None
        current_date = self.current_date.text()
        self.today_str = datetime.strptime(current_date, "%Y-%m-%d").strftime("%Y%m%d")
        # 读取文件
        filepath = os.path.join(BASE_DIR, 'sources/spot_price/{}.xlsx'.format(self.today_str))
        if not os.path.exists(filepath):
            self.tip_label.setText("请放入数据源再进行提取! ")
            return
        # 读取文件
        data_df = pd.read_excel(filepath, thousands=',', converters={0: date_converter})
        # 处理数据
        # date转为时间戳
        data_df['date'] = data_df['date'].apply(lambda x: int(datetime.strptime(x, '%Y%m%d').timestamp()))
        # 获取品种的英文
        data_df['variety_en'] = data_df['variety'].apply(lambda x: VARIETY_EN.get(x, 'VARIETYERROR'))
        # 在表中显示
        value_keys = ['date', 'variety', 'variety_en', 'price']
        spots_price = data_df.to_dict(orient='records')
        self.preview_table.setRowCount(len(spots_price))
        for row, row_item in enumerate(spots_price):
            row_brush = QBrush(QColor(0, 0, 0))
            for col, v_key in enumerate(value_keys):
                value_str = str(row_item[v_key])
                if value_str in ['TIMEERROR', 'VARIETYERROR']:
                    row_brush = QBrush(QColor(233, 0, 0))
                item = QTableWidgetItem(value_str)
                item.setForeground(row_brush)
                self.preview_table.setItem(row, col, item)
        self.final_data = spots_price
        self.tip_label.setText("数据提取完成! ")

    def commit_spot_data(self):
        """ 提交数据 """
        if self.final_data is None:
            self.tip_label.setText("请先提取数据...")
            return
        self.tip_label.setText("正在上传数据到服务器...")
        network_manager = getattr(qApp, "_network")
        url = SERVER_API + "spot-price/?date=" + self.today_str
        request = QNetworkRequest(QUrl(url))
        request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json;charset=utf-8")

        reply = network_manager.post(request, json.dumps(self.final_data).encode("utf-8"))
        reply.finished.connect(self.save_spot_price_reply)

    def save_spot_price_reply(self):
        """ 保存数据返回 """
        reply = self.sender()
        data = reply.readAll().data()
        reply.deleteLater()
        if reply.error():
            self.tip_label.setText("保存{}现货动态数据数据库失败:{}".format(self.today_str, reply.error()))
        else:
            data = json.loads(data.decode("utf-8"))
            self.tip_label.setText(data["message"])
        self.preview_table.clearContents()
        self.preview_table.setRowCount(0)
        self.source_edit.clear()

    def query_spot_data(self):
        """ 查询指定日期现货数据用于修改 """
        query_date = self.modify_date_edit.text()
        query_date_str = datetime.strptime(query_date, "%Y-%m-%d").strftime("%Y%m%d")
        network_manager = getattr(qApp, "_network")
        url = SERVER_API + "spot-price/?date=" + query_date_str

        reply = network_manager.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(self.query_spot_price_reply)

    def query_spot_price_reply(self):
        """ 获取指定日期现货数据返回 """
        reply = self.sender()
        data = reply.readAll().data()
        if reply.error():
            self.modify_tip_label.setText("获取{}现货动态数据失败:\n{}".format(self.modify_date_edit.text(), reply.error()))
        else:
            data = json.loads(data.decode("utf-8"))
            self.modify_tip_label.setText(data["message"])
        reply.deleteLater()
        self.modify_table.clearContents()
        self.modify_table.setRowCount(0)
        for row, row_item in enumerate(data["data"]):
            self.modify_table.insertRow(row)
            item0 = QTableWidgetItem(str(row_item["id"]))
            item1 = QTableWidgetItem(row_item["date"])
            item2 = QTableWidgetItem(row_item["variety_en"])
            item3 = QTableWidgetItem(str(row_item["price"]))
            item4 = QTableWidgetItem(str(row_item["increase"]))
            item0.setTextAlignment(Qt.AlignCenter)
            item1.setTextAlignment(Qt.AlignCenter)
            item2.setTextAlignment(Qt.AlignCenter)
            item3.setTextAlignment(Qt.AlignCenter)
            item4.setTextAlignment(Qt.AlignCenter)
            # ID 日期 品种不支持修改
            item0.setFlags(Qt.ItemIsEditable)
            item0.setForeground(QBrush(QColor(50, 50, 50)))
            item1.setFlags(Qt.ItemIsEditable)
            item1.setForeground(QBrush(QColor(50, 50, 50)))
            item2.setFlags(Qt.ItemIsEditable)
            item2.setForeground(QBrush(QColor(50, 50, 50)))
            self.modify_table.setItem(row, 0, item0)
            self.modify_table.setItem(row, 1, item1)
            self.modify_table.setItem(row, 2, item2)
            self.modify_table.setItem(row, 3, item3)
            self.modify_table.setItem(row, 4, item4)
            m_button = QPushButton("确定", self)
            m_button.setObjectName("modifyButton")
            m_button.setCursor(Qt.PointingHandCursor)
            setattr(m_button, 'row_index', row)
            m_button.clicked.connect(self.modify_row_data)
            self.modify_table.setCellWidget(row, 5, m_button)

    def modify_row_data(self):
        """ 修改数据表的单元格点击 """
        btn = self.sender()
        row = getattr(btn, 'row_index')
        # 获取组织数据
        item = {
            "id": int(self.modify_table.item(row, 0).text()),
            "date": self.modify_table.item(row, 1).text(),
            "variety_en": self.modify_table.item(row, 2).text(),
            "price": float(self.modify_table.item(row, 3).text()),
            "increase": float(self.modify_table.item(row, 4).text())
        }
        network_manager = getattr(qApp, "_network")
        url = SERVER_API + "spot-price/{}/".format(item["id"])

        request = QNetworkRequest(QUrl(url))
        request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json;charset=utf-8")

        reply = network_manager.put(request, json.dumps(item).encode("utf-8"))
        reply.finished.connect(self.modify_spot_price_reply)

    def modify_spot_price_reply(self):
        """ 修改数据返回 """
        reply = self.sender()
        data = reply.readAll().data()
        if reply.error():
            self.modify_tip_label.setText("修改数据失败:\n{}".format(self.modify_date_edit.text(), reply.error()))
        else:
            data = json.loads(data.decode("utf-8"))
            self.modify_tip_label.setText(data["message"])
        reply.deleteLater()
