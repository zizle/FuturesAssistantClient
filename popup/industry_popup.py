# _*_ coding:utf-8 _*_
# @File  : industry_popup.py
# @Time  : 2020-09-03 20:30
# @Author: zizle
""" 行业数据的弹窗U组件 """
import json
from datetime import datetime, timedelta
import pandas as pd
from xlsxwriter.exceptions import FileCreateError
from PyQt5.QtWidgets import (qApp, QDesktopWidget, QDialog, QWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QLabel,
                             QPushButton, QSplitter, QLineEdit, QSpinBox, QComboBox, QGroupBox, QTableWidget, QCheckBox,
                             QListWidget, QListWidgetItem, QTableWidgetItem, QHeaderView, QMenu, QMessageBox,
                             QFileDialog, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal, QMargins, QUrl
from PyQt5.QtGui import QBrush, QColor, QIntValidator, QPalette
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtNetwork import QNetworkRequest
from PyQt5.QtWebChannel import QWebChannel
from widgets.path_edit import FolderPathLineEdit
from widgets.loading import LoadingCover
from channels.chart import ChartOptionChannel
from utils.client import get_client_uuid, get_user_token
from utils.constant import BLUE_STYLE_HORIZONTAL_STYLE
from .message import InformationPopup
from settings import BASE_DIR, SERVER_API, logger
from widgets import OperateButton
from apis.industry import SheetAPI
from apis.industry.sheet import UpdateSheetRows, GetChartSheetColumns
from apis.industry.charts import SaveComparesThread

""" 配置更新文件夹 """


class UpdateFolderPopup(QDialog):
    """ 更新数据的文件夹配置 """
    successful_signal = pyqtSignal(str)

    def __init__(self, variety_en, variety_text, group_id, group_text, *args, **kwargs):
        super(UpdateFolderPopup, self).__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.variety_en = variety_en
        self.group_id = group_id

        self.setWindowTitle("配置「" + variety_text + "」的更新路径")

        main_layout = QGridLayout()

        main_layout.addWidget(QLabel("品种:", self), 0, 0)
        main_layout.addWidget(QLabel(variety_text, self), 0, 1)

        main_layout.addWidget(QLabel("组别:"), 1, 0)
        main_layout.addWidget(QLabel(group_text), 1, 1)

        main_layout.addWidget(QLabel('类型:', self), 2, 0)
        self.custom_index = QCheckBox(self)
        self.custom_index.setText('日期序列数据')
        self.custom_index.setCheckState(Qt.Checked)
        main_layout.addWidget(self.custom_index, 2, 1)

        main_layout.addWidget(QLabel("路径:"), 3, 0)
        self.folder_edit = FolderPathLineEdit(self)
        main_layout.addWidget(self.folder_edit, 3, 1)

        self.confirm_button = QPushButton("确定", self)
        self.confirm_button.clicked.connect(self.confirm_current_folder)
        main_layout.addWidget(self.confirm_button, 4, 1, alignment=Qt.AlignRight)

        self.setLayout(main_layout)
        self.setMinimumWidth(370)
        self.setFixedHeight(155)

    def confirm_current_folder(self):
        """ 确定当前配置 """
        # 发起配置的请求
        folder_path = self.folder_edit.text()
        if not folder_path:
            return
        is_dated = 1 if self.custom_index.checkState() else 0
        body_data = {
            "client": get_client_uuid(),
            "folder_path": folder_path,
            "variety_en": self.variety_en,
            "group_id": self.group_id,
            "is_dated": is_dated
        }
        network_manager = getattr(qApp, "_network")
        url = SERVER_API + "industry/user-folder/"
        request = QNetworkRequest(QUrl(url))
        request.setHeader(QNetworkRequest.ContentTypeHeader, "application/x-www-form-urlencoded")
        request.setRawHeader("Authorization".encode("utf-8"), get_user_token().encode("utf-8"))
        reply = network_manager.post(request, json.dumps(body_data).encode("utf-8"))
        reply.finished.connect(self.create_update_folder_reply)

        """ 本地保存(为了更新好处理和用户重新安装程序也存在这个配置,2020-09-29采用线上服务器保存)
        # 打开sqlite3进行数据的保存
        folder_path = self.folder_edit.text()
        if not folder_path:
            return
        insert_data = [get_client_uuid(), self.variety_en, self.group_id, folder_path]
        db_path = os.path.join(BASE_DIR, "dawn/local_data.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT CLIENT,VARIETY_EN,GROUP_ID FROM UPDATE_FOLDER "
            "WHERE CLIENT=? AND VARIETY_EN=? AND GROUP_ID=?;",
            (insert_data[0], insert_data[1], insert_data[2])
        )
        if cursor.fetchone():  # 更新
            cursor.execute(
                "UPDATE UPDATE_FOLDER SET FOLDER=? "
                "WHERE CLIENT=? AND VARIETY_EN=? AND GROUP_ID=?;",
                (insert_data[3], insert_data[0], insert_data[1], insert_data[2])
            )
        else:  # 新建
            cursor.execute(
                "INSERT INTO UPDATE_FOLDER (CLIENT,VARIETY_EN,GROUP_ID,FOLDER) "
                "VALUES (?,?,?,?);",
                insert_data
            )
        conn.commit()
        cursor.close()
        conn.close()
        self.successful_signal.emit("调整配置成功!")
        """

    def create_update_folder_reply(self):
        """ 创建更新文件价返回 """
        reply = self.sender()
        if reply.error():
            self.successful_signal.emit("调整配置失败了!")
        else:
            data = json.loads(reply.readAll().data().decode('utf8'))
            self.successful_signal.emit(data.get('message', '调整配置成功!'))
        reply.deleteLater()


""" 显示数据表内容支持修改 """


class SheetWidgetPopup(QDialog):
    def __init__(self, sheet_id, *args, **kwargs):
        super(SheetWidgetPopup, self).__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.header_keys = None
        self.sheet_id = sheet_id
        layout = QVBoxLayout()
        header_widget = QWidget(self)
        header_lt = QHBoxLayout(self)
        header_lt.setContentsMargins(0, 0, 0, 0)
        self.declare_label = QLabel(
            '双击要修改的数据单元格后,写入新的数据,再点击对应行最后的确认按钮(√)进行修改,一次只能修改一行数据(编号日期不支持修改)。右侧按钮支持修改完再统一更新', self)
        header_lt.addWidget(self.declare_label)

        self.all_update_button = QPushButton('确定更新', self)
        self.all_update_button.setFocusPolicy(Qt.NoFocus)
        self.all_update_button.clicked.connect(self.update_all_edit_rows)
        header_lt.addWidget(self.all_update_button)
        header_lt.addStretch()

        header_widget.setLayout(header_lt)

        layout.addWidget(header_widget)

        self.value_table = QTableWidget(self)
        self.value_table.horizontalHeader().hide()
        self.value_table.verticalHeader().hide()
        self.value_table.cellChanged.connect(self.append_edit_row)
        layout.addWidget(self.value_table)

        self.loading_cover = LoadingCover(self)  # 在此实现才能遮住之前的控件
        self.resize(1080, 600)
        self.loading_cover.resize(self.width(), self.height())
        self.loading_cover.hide()

        self.setLayout(layout)

        self.declare_label.setObjectName('declareLabel')
        self.setStyleSheet(
            '#declareLabel{color:rgb(233,66,66);font-size:12px}'
        )

        self.get_current_sheet_values()

        self.edit_rows = []
        self.update_thread = UpdateSheetRows(self)
        self.update_thread.finished.connect(self.reset_thread_data)
        self.update_thread.update_signal.connect(self.update_rows_result)

    def reset_thread_data(self):
        self.update_thread.set_sheet_id(0)
        self.update_thread.set_rows([])

    def resizeEvent(self, event):
        super(SheetWidgetPopup, self).resizeEvent(event)
        self.loading_cover.resize(self.width(), self.height())

    def update_all_edit_rows(self):
        # 更新所有编辑过的行
        if len(self.edit_rows) < 1:
            return
        self.update_thread.set_sheet_id(self.sheet_id)
        self.update_thread.set_rows(self.edit_rows)
        self.update_thread.start()

    def update_rows_result(self, msg):
        print(msg)
        QMessageBox.information(self, '提示', msg)
        # 关闭变化信号
        self.value_table.cellChanged.disconnect()
        for row_item in self.edit_rows:
            for col in range(self.value_table.columnCount()):
                item = self.value_table.item(row_item['row_index'], col)
                if item:
                    item.setBackground(QBrush(QColor(255, 255, 255)))
        # 清空待更新数据
        self.edit_rows.clear()
        # 开启变化信息
        self.value_table.cellChanged.connect(self.append_edit_row)

    def append_edit_row(self, row, col):
        item = self.value_table.item(row, col)
        if not item:
            return

        value_obj = {'row_index': row}

        for col, key in enumerate(self.header_keys):
            value_item = self.value_table.item(row, col)
            if key == 'id':
                if row > 0:
                    value_obj[key] = int(value_item.text())
                else:
                    value_obj[key] = 1
            else:
                value_obj[key] = value_item.text()

        is_new = True
        for d_item in self.edit_rows:
            if d_item['id'] == value_obj['id']:
                d_item.update(value_obj)
                is_new = False
        if is_new:
            self.edit_rows.append(value_obj)

        item.setBackground(QBrush(QColor(220, 220, 220)))

        # print('待更新:')
        # for i in self.edit_rows:
        #     print(i)

    def get_current_sheet_values(self):
        """ 获取当前表的数据 """
        self.loading_cover.show()
        url = SERVER_API + 'sheet/{}/'.format(self.sheet_id)
        network_manager = getattr(qApp, '_network')
        reply = network_manager.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(self.sheet_values_reply)

    def sheet_values_reply(self):
        """ 得到数据表 """
        reply = self.sender()
        if reply.error():
            logger.error('获取具体表数据错误了{}'.format(reply.error()))
        else:
            data = json.loads(reply.readAll().data().decode('utf8'))
            self.show_value_to_table(data['sheet_values'])
        reply.deleteLater()
        self.loading_cover.hide()

    def show_value_to_table(self, sheet_values):
        """ 将数据显示到表格中 """
        if not sheet_values:
            return
        self.value_table.cellChanged.disconnect()
        first_row = sheet_values[0]
        value_keys = list(first_row.keys())
        if self.header_keys is not None:
            del self.header_keys
            self.header_keys = None
        self.header_keys = value_keys.copy()
        self.value_table.setColumnCount(len(value_keys) + 1)
        self.value_table.horizontalHeader().setSectionResizeMode(len(value_keys), QHeaderView.ResizeToContents)
        self.value_table.setRowCount(len(sheet_values))
        for row, row_item in enumerate(sheet_values):
            for col, col_key in enumerate(value_keys):
                if col == 0:
                    value = '%05d' % row_item[col_key]
                    if row == 0:
                        value = '编号'
                else:
                    value = str(row_item[col_key])
                item = QTableWidgetItem(value)
                if col in [0, 1]:  # 前两列不可编辑
                    item.setFlags(Qt.ItemIsEditable)
                item.setTextAlignment(Qt.AlignCenter)
                self.value_table.setItem(row, col, item)
                if col == len(value_keys) - 1:
                    # 修改按钮
                    button = OperateButton('media/icons/confirm_btn.png', 'media/icons/confirm_btn.png', self)
                    setattr(button, 'row_index', row)
                    button.clicked.connect(self.modify_sheet_row_value)
                    self.value_table.setCellWidget(row, col + 1, button)
        self.value_table.cellChanged.connect(self.append_edit_row)

    def modify_sheet_row_value(self):
        """ 修改一行数据 """
        button = self.sender()
        current_row = getattr(button, 'row_index')
        row_values = self.get_row_values(current_row)
        if not row_values:
            return
        # 发起请求修改数据
        url = SERVER_API + 'sheet/{}/record/{}/'.format(self.sheet_id, row_values['id'])
        request = QNetworkRequest(QUrl(url))
        request.setRawHeader('Authorization'.encode('utf8'), get_user_token().encode('utf8'))
        network_manager = getattr(qApp, '_network')
        reply = network_manager.put(request, json.dumps(row_values).encode('utf8'))
        reply.finished.connect(self.modify_row_value_reply)

    def modify_row_value_reply(self):
        """ 修改一行数据返回 """
        reply = self.sender()
        if reply.error():
            p = InformationPopup('修改失败:{}'.format(reply.error()), self)
        else:
            data = json.loads(reply.readAll().data().decode('utf8'))
            p = InformationPopup(data['message'], self)
        p.exec_()
        reply.deleteLater()

    def get_row_values(self, current_row):
        """ 获取行数据 """
        row_values = {}
        for col, col_key in enumerate(self.header_keys):
            item = self.value_table.item(current_row, col)
            if current_row == 0 and col_key == 'id':
                row_values[col_key] = 1
            else:
                row_values[col_key] = int(item.text()) if col == 0 else item.text()
        return row_values


""" 图形配置选项 """


class OptionWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(OptionWidget, self).__init__(*args, **kwargs)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(QMargins(0, 0, 0, 0))

        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("标题:", self))
        self.title_edit = QLineEdit(self)
        self.title_edit.setPlaceholderText("图形标题(保存配置时必填)")
        title_layout.addWidget(self.title_edit)
        title_layout.addWidget(QLabel("大小:", self))
        self.title_fontsize = QSpinBox(self)
        self.title_fontsize.setMinimum(10)
        self.title_fontsize.setMaximum(100)
        self.title_fontsize.setValue(22)
        title_layout.addWidget(self.title_fontsize)
        main_layout.addLayout(title_layout)

        x_axis = QHBoxLayout()
        x_axis.addWidget(QLabel("横轴:", self))
        self.x_axis_combobox = QComboBox(self)
        self.x_axis_combobox.setMinimumWidth(150)
        x_axis.addWidget(self.x_axis_combobox)
        x_axis.addStretch()
        main_layout.addLayout(x_axis)

        x_format = QHBoxLayout()
        x_format.addWidget(QLabel("格式:", self))
        self.date_length = QComboBox(self)
        self.date_length.addItem('年-月-日', 10)
        self.date_length.addItem('年-月', 7)
        self.date_length.addItem('年', 4)
        self.date_length.setMinimumWidth(150)
        x_format.addWidget(self.date_length)
        x_format.addStretch()
        main_layout.addLayout(x_format)

        add_indicator = QGroupBox("点击选择添加指标", self)
        self.indicator_list = QListWidget(self)
        add_indicator_layout = QVBoxLayout()
        add_indicator.setLayout(add_indicator_layout)
        add_indicator_layout.addWidget(self.indicator_list)

        # 添加指标的按钮
        button_layout = QGridLayout()
        indicator_button1 = QPushButton("左轴线型", self)
        setattr(indicator_button1, "axis_index", 0)
        setattr(indicator_button1, "chart", "line")
        indicator_button1.clicked.connect(self.selected_indicator)
        button_layout.addWidget(indicator_button1, 0, 0)
        indicator_button2 = QPushButton("左轴柱型", self)
        setattr(indicator_button2, "axis_index", 0)
        setattr(indicator_button2, "chart", "bar")
        indicator_button2.clicked.connect(self.selected_indicator)
        button_layout.addWidget(indicator_button2, 1, 0)
        indicator_button3 = QPushButton("右轴线型", self)
        setattr(indicator_button3, "axis_index", 1)
        setattr(indicator_button3, "chart", "line")
        indicator_button3.clicked.connect(self.selected_indicator)
        button_layout.addWidget(indicator_button3, 0, 1)
        indicator_button4 = QPushButton("右轴柱型", self)
        setattr(indicator_button4, "axis_index", 1)
        setattr(indicator_button4, "chart", "bar")
        indicator_button4.clicked.connect(self.selected_indicator)
        button_layout.addWidget(indicator_button4, 1, 1)
        add_indicator_layout.addLayout(button_layout)
        main_layout.addWidget(add_indicator)

        current_indicator = QGroupBox("双击删除已选指标", self)
        current_indicator_layout = QVBoxLayout()
        current_indicator.setLayout(current_indicator_layout)
        self.current_indicator_list = QListWidget(self)
        self.current_indicator_list.itemDoubleClicked.connect(self.remove_selected_indicator)  # 移除已选指标
        self.current_indicator_list.itemClicked.connect(self.change_check_state)  # 修改去0选项
        current_indicator_layout.addWidget(self.current_indicator_list)
        main_layout.addWidget(current_indicator)

        # 水印
        graphic_layout = QHBoxLayout()
        graphic_layout.setSpacing(1)
        self.has_graphic = QCheckBox(self)
        self.has_graphic.setText("添加水印")
        self.water_graphic = QLineEdit(self)
        self.water_graphic.setText("瑞达期货研究院")
        graphic_layout.addWidget(self.has_graphic)
        graphic_layout.addWidget(self.water_graphic)
        graphic_layout.addStretch()
        main_layout.addLayout(graphic_layout)
        # 取数范围
        range_layout = QHBoxLayout()
        range_layout.setSpacing(1)
        self.start_year = QComboBox(self)
        self.end_year = QComboBox(self)
        self.range_check = QCheckBox(self)
        self.range_check.setText("取数范围")
        range_layout.addWidget(self.range_check)
        range_layout.addWidget(self.start_year)
        middle_label = QLabel("至", self)
        middle_label.setContentsMargins(QMargins(2, 0, 2, 0))
        range_layout.addWidget(middle_label)
        range_layout.addWidget(self.end_year)
        range_layout.addStretch()
        main_layout.addLayout(range_layout)

        other_layout = QHBoxLayout()
        tip_label = QLabel("勾选时,范围0表示不限制.", self)
        tip_label.setStyleSheet("color:rgb(180,60,60);max-height:15px")
        other_layout.addWidget(tip_label)
        self.more_dispose_button = QPushButton("更多配置", self)
        other_layout.addWidget(self.more_dispose_button, alignment=Qt.AlignRight)
        main_layout.addLayout(other_layout)

        draw_layout = QHBoxLayout()
        self.chart_drawer = QPushButton('确认绘图', self)
        setattr(self.chart_drawer, "chart_type", "normal")
        draw_layout.addWidget(self.chart_drawer)
        self.season_drawer = QPushButton('季节图表', self)
        setattr(self.season_drawer, "chart_type", "season")
        draw_layout.addWidget(self.season_drawer)
        main_layout.addLayout(draw_layout)

        self.setLayout(main_layout)

    def selected_indicator(self):
        """ 选择指标准备绘图 """
        current_indicator = self.indicator_list.currentItem()
        sender_button = self.sender()
        if not current_indicator:
            return
        indicator_column = current_indicator.data(Qt.UserRole)
        indicator_text = current_indicator.text()
        axis_index = getattr(sender_button, "axis_index")
        chart_type = getattr(sender_button, "chart")
        button_text = sender_button.text()
        indicator_params = {
            "column_index": indicator_column,
            "axis_index": axis_index,
            "chart_type": chart_type,
            "chart_name": indicator_text,
            "contain_zero": 1
        }
        # 重复指标和类型不再添加了
        for item_at in range(self.current_indicator_list.count()):
            item = self.current_indicator_list.item(item_at)
            exist_list = item.data(Qt.UserRole)
            if exist_list == indicator_params:
                return
        # 已选指标内添加指标
        selected_indicator_item = QListWidgetItem("(数据含0) " + indicator_text + " = " + button_text)
        selected_indicator_item.setCheckState(Qt.Unchecked)
        selected_indicator_item.setData(Qt.UserRole, indicator_params)
        self.current_indicator_list.addItem(selected_indicator_item)

    def remove_selected_indicator(self, _):
        """ 删除已选的指标 """
        current_row = self.current_indicator_list.currentRow()
        item = self.current_indicator_list.takeItem(current_row)
        del item

    @staticmethod
    def change_check_state(item):
        """ 修改item的去0选项"""
        text = item.text()
        if item.checkState():
            suffix_text = text[:6].replace("去", "含")
            indicator_params = item.data(Qt.UserRole)
            indicator_params["contain_zero"] = 1
            item.setCheckState(Qt.Unchecked)
        else:
            suffix_text = text[:6].replace("含", "去")
            indicator_params = item.data(Qt.UserRole)
            indicator_params["contain_zero"] = 0
            item.setCheckState(Qt.Checked)
        item.setData(Qt.UserRole, indicator_params)  # 重新设置item的Data
        text = suffix_text + text[6:]
        item.setText(text)

    def get_base_option(self):
        """ 图形的基本配置 """
        # typec表示图形的类型，single单表绘制,compose组合表,calculate计算绘制
        option = dict()
        # 标题
        option["typec"] = "single"
        option["title"] = {
            "text": self.title_edit.text().strip(),
            "font_size": self.title_fontsize.value()
        }
        # x轴
        option["x_axis"] = {
            "column_index": self.x_axis_combobox.currentData(),
            "date_length": self.date_length.currentData()
        }
        # y轴
        option["y_axis"] = [
            {"type": "value", "name": ""}
        ]
        # 数据序列
        series_data = []
        for item_at in range(self.current_indicator_list.count()):
            item = self.current_indicator_list.item(item_at)
            item_data = item.data(Qt.UserRole)
            if item_data["axis_index"] == 1 and len(option["y_axis"]) == 1:  # 如果有右轴添加右轴
                option["y_axis"].append({"type": "value", "name": ""})
            series_data.append(item_data)
        option["series_data"] = series_data

        option["watermark"] = ""
        if self.has_graphic.isChecked():
            option["watermark"] = self.water_graphic.text().strip()
        option["start_year"] = "0"
        option["end_year"] = "0"
        if self.range_check.isChecked():
            option["start_year"] = self.start_year.currentText()
            option["end_year"] = self.end_year.currentText()
        return option


class MoreDisposePopup(QDialog):
    """ 更多配置参数弹窗 """

    def __init__(self, *args, **kwargs):
        super(MoreDisposePopup, self).__init__(*args, **kwargs)
        self.setWindowTitle("更多参数")
        integer_validate = QIntValidator(self)

        main_layout = QVBoxLayout()

        left_label = QLabel('左轴调整:', self)
        left_label.setObjectName("axisTile")
        main_layout.addWidget(left_label)
        left_unit_layout = QHBoxLayout()
        left_unit_layout.setContentsMargins(7, 0, 0, 0)
        left_unit_layout.addWidget(QLabel("名称:", self))
        self.left_name_edit = QLineEdit(self)
        left_unit_layout.addWidget(self.left_name_edit)

        left_unit_layout.addWidget(QLabel("最小值:", self))
        self.left_min_edit = QLineEdit(self)
        self.left_min_edit.setValidator(integer_validate)
        left_unit_layout.addWidget(self.left_min_edit)

        left_unit_layout.addWidget(QLabel("最大值:", self))
        self.left_max_edit = QLineEdit(self)
        self.left_max_edit.setValidator(integer_validate)
        left_unit_layout.addWidget(self.left_max_edit)

        left_unit_layout.addStretch()
        main_layout.addLayout(left_unit_layout)

        right_label = QLabel('右轴调整:', self)
        right_label.setObjectName("axisTile")
        main_layout.addWidget(right_label)
        right_unit_layout = QHBoxLayout()
        right_unit_layout.setContentsMargins(7, 0, 0, 0)
        right_unit_layout.addWidget(QLabel("名称:", self))
        self.right_name_edit = QLineEdit(self)
        right_unit_layout.addWidget(self.right_name_edit)

        right_unit_layout.addWidget(QLabel("最小值:", self))
        self.right_min_edit = QLineEdit(self)
        self.right_min_edit.setValidator(integer_validate)
        right_unit_layout.addWidget(self.right_min_edit)

        right_unit_layout.addWidget(QLabel("最大值:", self))
        self.right_max_edit = QLineEdit(self)
        self.right_max_edit.setValidator(integer_validate)
        right_unit_layout.addWidget(self.right_max_edit)

        right_unit_layout.addStretch()
        main_layout.addLayout(right_unit_layout)

        close_btn = QPushButton("确定", self)
        close_btn.clicked.connect(self.close)
        main_layout.addWidget(close_btn, alignment=Qt.AlignRight)

        self.setLayout(main_layout)
        self.setMaximumWidth(420)
        self.setStyleSheet(
            "#axisTile{padding:3px;font-size:14px;background:rgb(200,220,230);border-radius:3px}"
        )

    def get_more_option(self):
        """ 返回更多参数数据 """
        left_min = int(self.left_min_edit.text()) if self.left_min_edit.text() else None
        left_max = int(self.left_max_edit.text()) if self.left_max_edit.text() else None
        right_min = int(self.right_min_edit.text()) if self.right_min_edit.text() else None
        right_max = int(self.right_max_edit.text()) if self.right_max_edit.text() else None
        return {
            "left_axis": {
                "name": self.left_name_edit.text().strip(),
                "min_value": left_min,
                "max_value": left_max
            },
            "right_axis": {
                "name": self.right_name_edit.text().strip(),
                "min_value": right_min,
                "max_value": right_max
            }
        }


class ChartWidget(QWidget):
    """ 图形显示控件 """
    save_option_signal = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(ChartWidget, self).__init__(*args, *kwargs)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(QMargins(0, 0, 0, 0))

        self.chart_container = QWebEngineView(self)
        self.chart_container.setContextMenuPolicy(Qt.NoContextMenu)
        self.chart_container.load(QUrl("file:///html/charts/custom_chart.html"))  # 加载页面
        # 设置与页面信息交互的通道
        channel_qt_obj = QWebChannel(self.chart_container.page())  # 实例化qt信道对象,必须传入页面参数
        self.contact_channel = ChartOptionChannel()  # 页面信息交互通道
        self.chart_container.page().setWebChannel(channel_qt_obj)
        channel_qt_obj.registerObject("pageContactChannel", self.contact_channel)  # 信道对象注册信道，只能注册一个

        main_layout.addWidget(self.chart_container)

        other_layout = QHBoxLayout()
        self.decipherment_edit = QLineEdit(self)
        self.decipherment_edit.setPlaceholderText("此处填写对图形的文字解读(非必填)")
        other_layout.addWidget(self.decipherment_edit)

        self.private_check = QCheckBox(self)
        self.private_check.setText("仅自己可见")
        other_layout.addWidget(self.private_check)

        save_button = QPushButton("保存图形", self)
        save_menu = QMenu(save_button)
        self.chart_action = save_menu.addAction("普通图形")
        setattr(self.chart_action, "chart_type", "normal")
        self.chart_action.triggered.connect(self.save_chart_option)
        self.season_action = save_menu.addAction("季节图形")
        setattr(self.season_action, "chart_type", "season")
        self.season_action.triggered.connect(self.save_chart_option)
        save_button.setMenu(save_menu)
        other_layout.addWidget(save_button)
        main_layout.addLayout(other_layout)

        self.setLayout(main_layout)

    def save_chart_option(self):
        """ 保存当前的图形配置 """
        action = self.sender()
        normal = getattr(action, "chart_type")
        self.save_option_signal.emit(normal)

    def show_chart(self, chart_type, option, values, headers):
        """ 显示图形
        option:(json字符串)基础的图形配置,
        values:(json字符串)用于绘图的数据
        """
        self.contact_channel.chartSource.emit(chart_type, option, values, headers)


class DisposeChartPopup(QDialog):
    """ 配置图形json信息进行绘图或保存 """

    def __init__(self, variety_en, sheet_id, *args, **kwargs):
        super(DisposeChartPopup, self).__init__(*args, **kwargs)
        self.source_dataframe = None
        self.is_dated = 1

        # 更多配置弹窗
        self.more_dispose_popup = MoreDisposePopup(self)
        self.more_dispose_popup.close()

        # 初始化大小
        available_size = QDesktopWidget().availableGeometry()  # 用户的桌面信息,来改变自身窗体大小
        available_width, available_height = available_size.width(), available_size.height()
        self.resize(available_width * 0.70, available_height * 0.72)

        self.setAttribute(Qt.WA_DeleteOnClose)

        self.variety_en = variety_en
        self.sheet_id = sheet_id

        main_layout = QHBoxLayout()
        main_splitter = QSplitter(self)
        main_layout.addWidget(main_splitter)  # 套layout自动改变大小

        self.option_widget = OptionWidget(self)
        # self.option_widget.resize(self.width() * 0.4, self.height())
        self.option_widget.more_dispose_button.clicked.connect(self.show_more_dispose)
        main_splitter.addWidget(self.option_widget)

        chart_sheet_splitter = QSplitter(self)
        chart_sheet_splitter.setOrientation(Qt.Vertical)

        self.chart_widget = ChartWidget(self)
        self.chart_widget.save_option_signal.connect(self.save_option_to_server)  # 链接保存图形的信号
        chart_sheet_splitter.addWidget(self.chart_widget)

        self.sheet_table = QTableWidget(self)
        # self.sheet_table.resize(self.width() * 0.6, self.height() * 0.4)
        self.sheet_table.verticalHeader().hide()
        chart_sheet_splitter.addWidget(self.sheet_table)

        # chart_sheet_splitter.setStretchFactor(0, 4)
        # chart_sheet_splitter.setStretchFactor(1, 6)
        chart_sheet_splitter.setSizes([self.height() * 0.6, self.height() * 0.4])
        main_splitter.addWidget(chart_sheet_splitter)

        main_splitter.setSizes([self.width() * 0.35, self.width() * 0.65])
        # main_splitter.setStretchFactor(0, 4)
        # main_splitter.setStretchFactor(1, 6)

        self.setLayout(main_layout)

        # 遮罩层
        self.cover_widget = LoadingCover(self)
        self.cover_widget.resize(self.width(), self.height())

        self._get_sheet_values()

        self.sheet_table.horizontalHeader().setStyleSheet(
            "QHeaderView::section{background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,"
            "stop:0 #bbbbbb, stop: 0.5 #eeeeee,stop: 0.6 #eeeeee, stop:1 #bbbbbb);"
            "border:1px solid rgb(201,202,202);border-left:none;"
            "min-height:25px;min-width:40px;font-weight:bold;font-size:13px};"
        )

        self.option_widget.chart_drawer.clicked.connect(self.preview_chart_with_option)  # 在右侧图形窗口显示图形信号
        self.option_widget.season_drawer.clicked.connect(self.preview_chart_with_option)  # 季节图形

    def resizeEvent(self, event):
        super(DisposeChartPopup, self).resizeEvent(event)
        self.cover_widget.resize(self.width(), self.height())

    def _get_sheet_values(self):
        """ 获取数据表的源数据 """
        network_manager = getattr(qApp, "_network")
        url = SERVER_API + "sheet/{}/".format(self.sheet_id)
        reply = network_manager.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(self.sheet_values_reply)

    def set_range_enabled(self, enable):
        self.option_widget.range_check.setEnabled(enable)
        self.option_widget.start_year.setEnabled(enable)
        self.option_widget.end_year.setEnabled(enable)

    def remove_season_chart(self, enable):
        self.option_widget.season_drawer.setEnabled(enable)
        self.chart_widget.season_action.setEnabled(enable)

    def sheet_values_reply(self):
        reply = self.sender()
        if reply.error():
            logger.error("用户获取数据表源数据失败:{}".format(reply.error()))
        else:
            data = reply.readAll().data()
            data = json.loads(data.decode("utf-8"))
            self.cover_widget.show(text="正在处理数据 ")
            is_dated = data['is_dated']
            # 处理取数范围可用与否
            if not is_dated:
                self.set_range_enabled(False)
                self.remove_season_chart(False)
            self.is_dated = is_dated
            # 使用pandas处理数据到弹窗相应参数中
            self.handler_sheet_values(data["sheet_values"])

    def handler_sheet_values(self, values):
        """ pandas处理数据到弹窗相应参数中 """
        value_df = pd.DataFrame(values)
        if value_df.iloc[2:].empty:  # 从第3行起取数,为空
            logger.error("该数据表最多存在3行数据,遂取绘图数据失败!")
            self.cover_widget.hide()
            return
        self.source_dataframe = value_df.copy()  # 将源数据复制一份关联到窗口(用于作图)
        sheet_headers = value_df.iloc[:1].to_numpy().tolist()[0]  # 取表头
        sheet_headers.pop(0)  # 删掉id列
        col_index_list = ["id", ]
        for i, header_item in enumerate(sheet_headers):  # 根据表头生成数据选择项
            col_index = "column_{}".format(i)
            self.option_widget.x_axis_combobox.addItem(header_item, col_index)  # 添加横轴选项
            indicator_item = QListWidgetItem(header_item)
            indicator_item.setData(Qt.UserRole, col_index)
            self.option_widget.indicator_list.addItem(indicator_item)  # 填入指标选择框
            col_index_list.append(col_index)
        # 根据最值填入起终值的范围
        max_date = value_df.iloc[2:]["column_0"].max()  # 取日期最大值
        min_date = value_df.iloc[2:]["column_0"].min()  # 取日期最小值
        self.option_widget.start_year.clear()
        self.option_widget.end_year.clear()
        self.option_widget.start_year.addItem("0")
        self.option_widget.end_year.addItem("0")
        for year in range(int(min_date[:4]), int(max_date[:4]) + 1):
            self.option_widget.start_year.addItem(str(year))
            self.option_widget.end_year.addItem(str(year))

        sheet_headers.insert(0, "编号")  # 还原id列

        table_show_df = value_df.iloc[1:]
        if self.is_dated:  # 日期序列做排序
            table_show_df = table_show_df.sort_values(by="column_0")
        table_show_df.reset_index(inplace=True)  # 重置索引,让排序生效(赋予row正确的值)
        self.sheet_table.setColumnCount(len(sheet_headers))
        self.sheet_table.setHorizontalHeaderLabels(sheet_headers)
        self.sheet_table.setRowCount(table_show_df.shape[0])
        self.sheet_table.horizontalHeader().setDefaultSectionSize(150)
        self.sheet_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.sheet_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        for row, row_item in table_show_df.iterrows():  # 遍历数据(填入表格显示)
            for col, col_key in enumerate(col_index_list):
                # print(row_item[col_key], end=' ')
                item = QTableWidgetItem(str(row_item[col_key]))
                item.setTextAlignment(Qt.AlignCenter)
                if col < 2:
                    item.setFlags(Qt.ItemIsEditable)  # ID,日期不可编辑
                    item.setForeground(QBrush(QColor(60, 60, 60)))
                self.sheet_table.setItem(row, col, item)
            # print()
        self.cover_widget.hide()

    def show_more_dispose(self):
        """ 更多的配置参数 """
        self.more_dispose_popup.exec_()

    def save_option_to_server(self, chart_type):
        """ 保存图形的配置到服务器 """
        chart_option = self.get_chart_option()  # 作图配置
        chart_option["chart_category"] = chart_type  # 图表类型(普通图形:normal,季节图形:season)
        title = chart_option["title"]["text"]
        if not title:
            QMessageBox.information(self, "提示", "请填写图形标题!")
            return
        is_private = 1 if self.chart_widget.private_check.checkState() else 0
        json_option = {
            "title": title,
            "variety_en": self.variety_en,
            "decipherment": self.chart_widget.decipherment_edit.text().strip(),
            "is_private": is_private,
            "option": chart_option.copy()
        }
        network_manager = getattr(qApp, "_network")
        url = SERVER_API + "sheet/{}/chart/".format(self.sheet_id)
        request = QNetworkRequest(QUrl(url))
        user_token = get_user_token()
        request.setRawHeader("Authorization".encode("utf-8"), user_token.encode("utf-8"))
        reply = network_manager.post(request, json.dumps(json_option).encode("utf-8"))
        reply.finished.connect(self.save_option_reply)

    def save_option_reply(self):
        """ 保存配置返回 """
        reply = self.sender()
        if reply.error():
            QMessageBox.information(self, "失败", "保存配置失败!")
            logger.error("用户保存图形配置失败:{}".format(reply.error()))
        else:
            QMessageBox.information(self, "成功", "保存配置成功!")
        reply.deleteLater()

    def preview_chart_with_option(self):
        """ 在当前窗口预览显示图形 """
        chart_button = self.sender()
        chart_type = getattr(chart_button, "chart_type")
        # print("作图类型:\n", chart_type)
        chart_option = self.get_chart_option()  # 作图配置
        chart_source_json, sheet_headers = self.get_chart_source_json(chart_type, chart_option, self.source_dataframe)
        # print("作图配置:\n", chart_option)
        # print("作图源数据:\n", chart_source_json)
        # print("作图的表头:\n", sheet_headers)
        # 将数据和配置传入echarts绘图
        self.chart_widget.show_chart(
            chart_type, json.dumps(chart_option), json.dumps(chart_source_json), json.dumps(sheet_headers)
        )

    def get_chart_option(self):
        """ 获取图形的配置 """
        base_option = self.option_widget.get_base_option()  # 作图基本配置
        more_option = self.more_dispose_popup.get_more_option()  # 作图更多配置
        # 将更多配置添加入基本配置中
        y_axis = base_option["y_axis"]
        # 左轴
        left_more_op = more_option["left_axis"]
        y_axis[0]["name"] = left_more_op["name"]
        if left_more_op["min_value"]:
            y_axis[0]["min"] = left_more_op["min_value"]
        if left_more_op["max_value"]:
            y_axis[0]["max"] = left_more_op["max_value"]
        # 右轴
        if len(y_axis) > 1:
            right_more_op = more_option["right_axis"]
            y_axis[1]["name"] = right_more_op["name"]
            if right_more_op["min_value"]:
                y_axis[1]["min"] = right_more_op["min_value"]
            if right_more_op["max_value"]:
                y_axis[1]["max"] = right_more_op["max_value"]

        return base_option

    @staticmethod
    def replace_zero_to_line(data_str):
        """ 替换0为-"""
        try:
            value = float(data_str)
        except Exception:
            return '-'
        else:
            return '-' if value == 0 else data_str

    def get_chart_source_json(self, chart_type, base_option, source_dataframe):
        """ 处理出绘图的最终数据 """
        # 取得数据的头
        sheet_headers = source_dataframe.iloc[:1].to_dict(orient="records")[0]
        values_df = source_dataframe.iloc[2:]
        # 取最大值和最小值
        start_year = base_option["start_year"]
        end_year = base_option["end_year"]
        if start_year > "0":
            start_date = str(start_year) + "-01-01"
            # 切出大于开始日期的数据
            values_df = values_df[values_df["column_0"] >= start_date]
        if end_year > "0":
            # 切出小于结束日期的数据
            end_date = str(end_year) + "-12-31"  # 含结束年份end_year + 1
            values_df = values_df[values_df["column_0"] <= end_date]
        # 数据是否去0处理
        for series_item in base_option["series_data"]:
            column_index = series_item["column_index"]
            contain_zero = series_item["contain_zero"]
            if not contain_zero:  # 数据不含0,去0处理
                # 数据去0的话替换为'-' 使其在echarts中不会被作出图形点(在echarts配置中直接连接空数据)
                values_df[column_index] = values_df[column_index].apply(self.replace_zero_to_line)
                # 以下的去0方式较单一,0.00就无法去除,且数据会被裁剪
                # values_df = values_df[values_df[column_index] != "0"]
                # values_df = values_df[values_df[column_index] != "0.0"]  # 去除计算出来是0.0的数据
        # 日期序列进行排序
        if self.is_dated:
            values_df = values_df.sort_values(by="column_0")  # 最后进行数据从小到大的时间排序
        # table_show_df.reset_index(inplace=True)  # 重置索引,让排序生效(赋予row正确的值。可不操作,转为json后,索引无用处了)
        #
        # 普通图形返回结果数据
        if chart_type == "normal":
            # 日期序列处理横轴的格式
            if self.is_dated:
                date_length = base_option["x_axis"]["date_length"]
                values_df["column_0"] = values_df["column_0"].apply(lambda x: x[:date_length])
            values_json = values_df.to_dict(orient="record")
        elif chart_type == "season":  # 季节图形将数据分为{year1: values1, year2: values2}型
            values_json = self.get_season_chart_source(values_df.copy())
        else:
            values_json = []
        return values_json, sheet_headers

    def get_season_chart_source(self, source_df):
        """ 获取季节图形的作图源数据 """
        target_values = dict()  # 保存最终数据的字典
        target_values["xAxisData"] = self.generate_days_of_year()
        # 获取column_0的最大值和最小值
        min_date = source_df["column_0"].min()
        max_date = source_df["column_0"].max()
        start_year = int(min_date[:4])
        end_year = int(max_date[:4])
        for year in range(start_year, end_year + 1):
            # 获取当年的第一天和最后一天
            current_first = str(year) + "-01-01"
            current_last = str(year) + "-12-31"
            # 从data frame中取本年度的数据并转为列表字典格式
            current_year_df = source_df[
                (source_df["column_0"] >= current_first) & (source_df["column_0"] <= current_last)]
            current_year_df["column_0"] = current_year_df["column_0"].apply(lambda x: x[5:])
            # target_values[str(year)] = current_year_df.to_dict(orient="record")
            target_values[str(year)] = current_year_df.to_dict(orient="record")
        return target_values

    @staticmethod
    def generate_days_of_year():
        """ 生成一年的每一月每一天 """
        days_list = list()
        start_day = datetime.strptime("2020-01-01", "%Y-%m-%d")
        end_day = datetime.strptime("2020-12-31", "%Y-%m-%d")
        while start_day <= end_day:
            days_list.append(start_day.strftime("%m-%d"))
            start_day += timedelta(days=1)
        return days_list


""" 添加指定表的数据 """


class AddSheetRecordPopup(QDialog):
    def __init__(self, *args, **kwargs):
        super(AddSheetRecordPopup, self).__init__(*args, **kwargs)
        self.sheet_id = None
        self.is_dated = 1

        # 初始化大小
        available_size = QDesktopWidget().availableGeometry()  # 用户的桌面信息,来改变自身窗体大小
        available_width, available_height = available_size.width(), available_size.height()
        self.resize(available_width * 0.70, available_height * 0.72)

        layout = QVBoxLayout()
        self.tip_label = QLabel(self)
        self.tip_label.setText('1.标题`[]`内表示是否为日期序列的数据，日期序列要求同类型才能粘贴数据!'
                               '\n2.【第一行为当前表中最近日期数据】手动添加一行后,在对应位置双击录入数据。'
                               '\n3.使用Ctrl+V粘贴,粘贴后可双击修改,确认无误后点击右侧保存!其中第一列格式需为yyyy-mm-dd\n'
                               '4.移除一行有选中行移除选中行,无选中行移除末尾行。')
        self.tip_label.setStyleSheet('color:rgb(204, 95, 45)')
        layout.addWidget(self.tip_label)
        top_layout = QHBoxLayout()
        self.add_row_button = QPushButton('添加一行', self)
        top_layout.addWidget(self.add_row_button)
        self.remove_row_button = QPushButton('移除一行', self)
        top_layout.addWidget(self.remove_row_button)
        top_layout.addStretch()
        self.save_button = QPushButton('确定保存', self)
        top_layout.addWidget(self.save_button)
        layout.addLayout(top_layout)
        self.paste_table = QTableWidget(self)
        self.paste_table.horizontalHeader().setStyleSheet(BLUE_STYLE_HORIZONTAL_STYLE)
        layout.addWidget(self.paste_table)
        self.setLayout(layout)

        self.sheet_api = SheetAPI(self)
        self.sheet_api.sheet_last_reply.connect(self.last_row_reply)
        self.sheet_api.add_record_reply.connect(self.add_new_reply)

        self.add_row_button.clicked.connect(self.insert_new_row)
        self.remove_row_button.clicked.connect(self.remove_last_row)
        self.save_button.clicked.connect(self.to_save_rows)

    def insert_new_row(self):
        c_row = self.paste_table.rowCount()
        if c_row > 0:
            c_date = self.paste_table.item(c_row - 1, 0).text()
            next_date = self.handle_date_column(c_date)
            if next_date:
                self.paste_table.insertRow(c_row)
                self.paste_table.setItem(c_row, 0, QTableWidgetItem(next_date))
                for col in range(1, self.paste_table.columnCount()):
                    self.paste_table.setItem(c_row, col, QTableWidgetItem())

    def remove_last_row(self):
        row_count = self.paste_table.rowCount()
        if row_count > 1:
            current_row = self.paste_table.currentRow()
            if current_row > 0:
                self.paste_table.removeRow(current_row)
            else:
                self.paste_table.removeRow(row_count - 1)

    def keyPressEvent(self, event) -> None:
        super(AddSheetRecordPopup, self).keyPressEvent(event)
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_V:
            # 处理粘贴板中的数据
            self.handle_clipboard()

    def handle_date_column(self, date_str):
        if self.is_dated:
            try:
                next_date = (datetime.strptime(date_str, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
            except Exception:
                p = InformationPopup('第一列日期格式有误!', self)
                p.exec_()
                return None
            return next_date
        else:
            return date_str

    def handle_value_column(self, value):
        if not value:
            return ''
        try:
            float(value)
        except Exception:
            p = InformationPopup('含非法数据类型!', self)
            p.exec_()
            return None
        return value

    def handle_row_data(self, item):
        if len(item) < 1:
            return []
        try:
            item[0] = datetime.strptime(item[0], '%Y-%m-%d').strftime('%Y-%m-%d')
        except Exception:
            try:
                item[0] = datetime.strptime(item[0], '%Y/%m/%d').strftime('%Y-%m-%d')
            except Exception:
                return []
            else:
                return item
        else:
            return item

    def handle_clipboard(self):
        # 处理粘贴板数据
        clipboard = qApp.clipboard()
        origin_text = clipboard.text()
        # 根据换行符切分数据
        row_list = origin_text.split('\n')
        new_data = []
        for row_text in row_list:
            new_data.append(row_text.split('\t'))
        # 处理一下数据
        if self.is_dated:
            new_data = list(map(self.handle_row_data, new_data))
        new_data = list(filter(lambda x: len(x) > 0, new_data))
        # 填充数据
        col_count = self.paste_table.columnCount()
        for row in new_data:
            row_count = self.paste_table.rowCount()
            self.paste_table.insertRow(row_count)
            if len(row) < col_count:
                row += ['' for _ in range(col_count - len(row))]
            # 添加数据
            for col in range(col_count):
                item = QTableWidgetItem(str(row[col]).replace(',', ''))
                item.setTextAlignment(Qt.AlignCenter)
                self.paste_table.setItem(row_count, col, item)

    def set_sheet_id(self, sheet_id):
        self.sheet_id = sheet_id
        # 获取最新数据行
        self.sheet_api.get_sheet_last(self.sheet_id)

    def last_row_reply(self, data):
        # 显示到表格中且设置不可编辑
        last_row = data.get('last_row', None)
        header_row = data.get('header_row', None)
        self.is_dated = data.get('is_dated', 1)
        if not header_row:
            return
        del header_row['id']
        header_keys = ['column_{}'.format(col) for col in range(len(header_row))]
        self.paste_table.setRowCount(1)
        self.paste_table.setColumnCount(len(header_keys))
        self.paste_table.setHorizontalHeaderLabels([header_row.get(k, '') for k in header_keys])
        for col, key in enumerate(header_keys):
            item = QTableWidgetItem(last_row.get(key, ''))
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(Qt.ItemIsEditable)  # 不可编辑
            item.setForeground(QBrush(QColor(100, 100, 100)))
            self.paste_table.setItem(0, col, item)

    def get_table_new_data(self):
        # 获取表中的新数据
        new_data = []
        is_error = False
        for row in range(1, self.paste_table.rowCount()):
            row_data = []
            for col in range(self.paste_table.columnCount()):
                text = self.paste_table.item(row, col).text().strip()
                if col == 0:
                    if not self.handle_date_column(text):
                        is_error = True
                        break
                else:
                    if self.handle_value_column(text) is None:
                        is_error = True
                        break
                if not is_error:
                    row_data.append(text)
            if row_data:
                new_data.append(row_data)
        return new_data, is_error

    def to_save_rows(self):
        new_data, is_error = self.get_table_new_data()
        if is_error:
            return
        self.sheet_api.save_sheet_new_data(self.sheet_id, new_data)

    def add_new_reply(self, success):
        if success:
            p = InformationPopup('添加新数据成功!', self)
            p.exec_()
            # 清除新数据行
            self.paste_table.setRowCount(1)
        else:
            p = InformationPopup('添加新数据失败!', self)
            p.exec_()


""" 导出指定表数据 """


class ExportSheetPopup(QDialog):
    def __init__(self, sheet_id, *args, **kwargs):
        super(ExportSheetPopup, self).__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.header_keys = None
        self.sheet_id = sheet_id
        layout = QVBoxLayout()

        self.export_button = QPushButton('立即导出', self)
        self.export_button.clicked.connect(self.export_table_data)
        layout.addWidget(self.export_button, alignment=Qt.AlignTop | Qt.AlignLeft)

        # self.declare_label = QLabel(
        #     '双击要修改的数据单元格后,写入新的数据,再点击对应行最后的确认按钮(√)进行修改,一次只能修改一行数据(编号日期不支持修改)。', self)
        # layout.addWidget(self.declare_label, alignment=Qt.AlignTop | Qt.AlignLeft)
        self.value_table = QTableWidget(self)
        self.value_table.horizontalHeader().hide()
        self.value_table.verticalHeader().hide()
        layout.addWidget(self.value_table)

        self.loading_cover = LoadingCover(self)  # 在此实现才能遮住之前的控件
        self.resize(1080, 600)
        self.loading_cover.resize(self.width(), self.height())
        self.loading_cover.hide()

        self.setLayout(layout)

        # self.declare_label.setObjectName('declareLabel')
        # self.setStyleSheet(
        #     '#declareLabel{color:rgb(233,66,66);font-size:12px}'
        # )

        self.get_current_sheet_values()

    def resizeEvent(self, event):
        super(ExportSheetPopup, self).resizeEvent(event)
        self.loading_cover.resize(self.width(), self.height())

    def get_current_sheet_values(self):
        """ 获取当前表的数据 """
        self.loading_cover.show()
        url = SERVER_API + 'sheet/{}/'.format(self.sheet_id)
        network_manager = getattr(qApp, '_network')
        reply = network_manager.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(self.sheet_values_reply)

    def sheet_values_reply(self):
        """ 得到数据表 """
        reply = self.sender()
        if reply.error():
            logger.error('获取具体表数据错误了{}'.format(reply.error()))
        else:
            data = json.loads(reply.readAll().data().decode('utf8'))
            self.show_value_to_table(data['sheet_values'])
        reply.deleteLater()
        self.loading_cover.hide()

    def show_value_to_table(self, sheet_values):
        """ 将数据显示到表格中 """
        if not sheet_values:
            return
        first_row = sheet_values[0]
        value_keys = list(first_row.keys())
        if self.header_keys is not None:
            del self.header_keys
            self.header_keys = None
        self.header_keys = value_keys.copy()
        self.value_table.setColumnCount(len(value_keys))
        self.value_table.setRowCount(len(sheet_values))
        for row, row_item in enumerate(sheet_values):
            for col, col_key in enumerate(value_keys):
                if col == 0:
                    value = '%05d' % row_item[col_key]
                    if row == 0:
                        value = '编号'
                else:
                    value = str(row_item[col_key])
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                self.value_table.setItem(row, col, item)

    def get_value_table_data(self):
        # 获取表格数据
        header_list = []
        value_list = []
        row_count = self.value_table.rowCount()
        col_count = self.value_table.columnCount()
        for header_col in range(1, col_count):
            item_value = self.value_table.item(0, header_col).text()
            header_list.append(item_value)

        for row in range(1, row_count):
            row_list = []
            for col in range(1, col_count):
                item_value = self.value_table.item(row, col).text()
                try:
                    value = datetime.strptime(item_value, '%Y-%m-%d') if col == 0 else float(
                        self.value_table.item(row, col).text().replace(',', ''))
                except ValueError:
                    value = item_value
                row_list.append(value)
            value_list.append(row_list)
        return pd.DataFrame(value_list, columns=header_list)

    def export_table_data(self):
        # 导出表格数据
        sheet_name = self.windowTitle()
        filepath, _ = QFileDialog.getSaveFileName(self, '保存文件', sheet_name, 'EXCEL文件(*.xlsx *.xls)')
        if filepath:
            self.loading_cover.show('正在导出数据,请稍后...')
            # 获取表格数据
            sheet_df = self.get_value_table_data()
            writer = pd.ExcelWriter(filepath, engine='xlsxwriter', datetime_format='YYYY-MM-DD')
            # 多级表头默认会出现一个空行,需改pandas源码,这里不做处理
            sheet_df.to_excel(writer, sheet_name=sheet_name, encoding='utf8', index=False,
                              merge_cells=False)
            work_sheets = writer.sheets[sheet_name]
            book_obj = writer.book
            format_obj = book_obj.add_format({'font_name': 'Arial', 'font_size': 9})
            work_sheets.set_column('A:Z', None, cell_format=format_obj)
            try:
                writer.save()
            except FileCreateError:
                p = InformationPopup('请关闭已打开的文件再进行替换保存!', self)
                p.exec_()
            self.loading_cover.hide()


class SetComparesPopup(QDialog):
    def __init__(self, sid, cid, *args, **kwargs):
        super(SetComparesPopup, self).__init__(*args, **kwargs)
        self.resize(800, 450)
        self.chart_id = cid
        lt = QVBoxLayout(self)
        scroll_widget = QScrollArea(self)

        self.setLayout(lt)

        self.column_widget = QWidget(self)
        self.column_lt = QVBoxLayout()
        self.column_widget.setLayout(self.column_lt)
        scroll_widget.setWidget(self.column_widget)
        scroll_widget.setWidgetResizable(True)
        lt.addWidget(scroll_widget)

        self.confirm_compare_button = QPushButton('保存设置', self)
        self.confirm_compare_button.setFocusPolicy(Qt.NoFocus)
        self.confirm_compare_button.clicked.connect(self.to_save_compares)

        lt.addWidget(self.confirm_compare_button, alignment=Qt.AlignBottom | Qt.AlignRight)

        self.get_columns_thread = GetChartSheetColumns(self)
        self.get_columns_thread.set_sheet_id(sid, self.chart_id)
        self.get_columns_thread.columns_reply.connect(self.sheet_columns_reply)
        self.get_columns_thread.start()

        self.save_compare_thread = SaveComparesThread(self)
        self.save_compare_thread.request_finished.connect(self.save_reply)

        self.compare_obj = {}

    def save_reply(self, data):
        QMessageBox.information(self, '提示', data['message'])

    def to_save_compares(self):
        if len(self.compare_obj) <= 0:
            QMessageBox.information(self, '错误', '至少设置一个对比解读才能保存!')
            return
        self.save_compare_thread.set_body_data(self.compare_obj, self.chart_id)
        self.save_compare_thread.start()

    def sheet_columns_reply(self, reply_data):
        columns = reply_data['columns']
        compares = reply_data['compares']
        print(compares)
        for col_key, col_name in columns.items():
            c_label = QLabel(col_name, self.column_widget)
            pal = c_label.palette()
            pal.setColor(QPalette.Background, QColor(180, 220, 230))
            c_label.setPalette(pal)
            c_label.setAutoFillBackground(True)
            self.column_lt.addWidget(c_label)
            compare = compares.get(col_key, [])
            self.column_lt.addWidget(self.get_column_checks(col_key, compare))
        self.column_lt.addStretch()

    def check_compares(self):
        check = self.sender()
        check_msg = getattr(check, 'data', None)
        if not check_msg:
            return
        # 设置数据
        save_column = self.compare_obj.get(check_msg['column'], [])
        if check.checkState() == Qt.Checked:
            self.compare_obj[check_msg['column']] = list(set(save_column + [check_msg['name']]))
        else:
            # 去除选择
            if save_column:
                save_column.remove(check_msg['name'])
            if not save_column:
                self.compare_obj[check_msg['column']] = []

    def get_column_checks(self, col_key, compare):
        check_widget = QWidget(self.column_widget)
        clt = QHBoxLayout()
        clt.setContentsMargins(10, 0, 0, 0)
        wk = QCheckBox(check_widget)
        setattr(wk, 'data', {'column': col_key, 'name': 'week'})
        wk.setText('环比上周')
        wk.stateChanged.connect(self.check_compares)
        if 'week' in compare:
            wk.setChecked(Qt.Checked)
        clt.addWidget(wk)

        mn = QCheckBox(check_widget)
        mn.setText('环比上月')
        setattr(mn, 'data', {'column': col_key, 'name': 'month'})
        mn.stateChanged.connect(self.check_compares)
        if 'month' in compare:
            mn.setChecked(Qt.Checked)
        clt.addWidget(mn)

        yr = QCheckBox(check_widget)
        yr.setText('去年同期')
        setattr(yr, 'data', {'column': col_key, 'name': 'year'})
        yr.stateChanged.connect(self.check_compares)
        if 'year' in compare:
            yr.setChecked(Qt.Checked)
        clt.addWidget(yr)

        clt.addStretch()
        check_widget.setLayout(clt)
        return check_widget

    def hideEvent(self, event) -> None:
        super(SetComparesPopup, self).hideEvent(event)
        self.deleteLater()
