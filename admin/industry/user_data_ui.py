# _*_ coding:utf-8 _*_
# @File  : user_data_ui.py
# @Time  : 2020-09-03 14:08
# @Author: zizle

""" 用户数据维护 (产业数据库) """
import json

from PyQt5.QtWidgets import (QWidget, QSplitter, QHBoxLayout, QVBoxLayout, QListWidget, QTabWidget, QLabel, QComboBox,
                             QPushButton, QTableWidget, QAbstractItemView, QFrame, QLineEdit, QCheckBox, QHeaderView,
                             QProgressBar, QTabBar, QStylePainter, QStyleOptionTab, QStyle, QFormLayout, QDateEdit,
                             QTableWidgetItem, qApp, QMessageBox)
from PyQt5.QtGui import QDoubleValidator, QPalette, QColor, QBrush
from PyQt5.QtCore import QMargins, Qt, pyqtSignal, QDate, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtNetwork import QNetworkRequest, QNetworkAccessManager
from settings import SERVER_API

from apis.industry.sheet import SwapSheetSorted
from apis.industry.charts import SwapChartSorted


class HorizontalTabBar(QTabBar):
    """ 自定义竖向文字显示的tabBar """
    def paintEvent(self, event):
        painter = QStylePainter(self)
        option = QStyleOptionTab()
        painter.begin(self)
        for index in range(self.count()):
            self.initStyleOption(option, index)
            tabRect = self.tabRect(index)
            tabRect.moveLeft(4)
            painter.drawControl(QStyle.CE_TabBarTabShape, option)
            painter.drawText(tabRect, Qt.AlignVCenter | Qt.TextDontClip, self.tabText(index))
        painter.end()


class ConfigSourceUI(QWidget):
    def __init__(self, *args, **kwargs):
        super(ConfigSourceUI, self).__init__(*args, **kwargs)
        self.is_updating = False  # 标记是否正在执行更新
        self.current_button = None

        # 更新数据的线程
        self.updating_thread = None

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(QMargins(0, 1, 0, 2))
        opt_layout = QHBoxLayout()
        opt_layout.addWidget(QLabel("品种:", self))
        self.variety_combobox = QComboBox(self)
        self.variety_combobox.setMinimumWidth(80)
        opt_layout.addWidget(self.variety_combobox)

        opt_layout.addWidget(QLabel("数据组:", self))
        self.group_combobox = QComboBox(self)
        self.group_combobox.setMinimumWidth(100)
        opt_layout.addWidget(self.group_combobox)

        # 新增数据组
        self.new_group_button = QPushButton("新建组?", self)
        self.new_group_button.clicked.connect(self.to_create_new_group)
        opt_layout.addWidget(self.new_group_button)

        # 新增组的编辑框
        self.new_group_edit = QLineEdit(self)
        self.new_group_edit.setFixedWidth(120)
        self.new_group_edit.setPlaceholderText("新组名称?")
        self.new_group_edit.hide()
        opt_layout.addWidget(self.new_group_edit)

        # 新增组确定按钮
        self.confirm_group_button = QPushButton("确定", self)
        self.confirm_group_button.hide()
        opt_layout.addWidget(self.confirm_group_button)

        # 信息提示
        self.tips_message = QLabel(self)
        self.tips_message.setObjectName("messageLabel")
        opt_layout.addWidget(self.tips_message)

        # 更新数据的进度条
        self.updating_process = QProgressBar(self)
        self.updating_process.hide()
        self.updating_process.setFixedHeight(15)
        opt_layout.addWidget(self.updating_process)
        opt_layout.addStretch()

        self.new_config_button = QPushButton('调整配置', self)
        opt_layout.addWidget(self.new_config_button)
        main_layout.addLayout(opt_layout)

        self.config_table = QTableWidget(self)
        self.config_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.config_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.config_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.config_table.setFocusPolicy(Qt.NoFocus)
        self.config_table.setFrameShape(QFrame.NoFrame)
        self.config_table.setAlternatingRowColors(True)
        self.config_table.setColumnCount(7)
        self.config_table.setHorizontalHeaderLabels(["编号", "品种", "组别", "日期序列", "更新路径", "操作", "删除配置"])
        self.config_table.verticalHeader().hide()
        self.config_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.config_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.config_table.setWordWrap(True)
        main_layout.addWidget(self.config_table)

        self.config_table.setObjectName('configsTable')

        tips = "<p>1 点击右上角'更新配置'按钮，配置当前品种当前数据组更新文件所在的文件夹.</p>" \
               "<p>1-1 非日期序列的文件夹路径显示为绿色;日期系列为金黄色." \
               "<p>2 '点击更新'让系统读取文件夹内的数据表自动上传.</p>" \
               "<p>2-1 文件夹内表格格式:</p>" \
               "<p>第1行：万得导出的表第一行不动;自己创建的表第一行须留空;</p>" \
               "<p>第2行：数据表表头;</p>" \
               "<p>第3行：不做限制,可填入单位等,也可直接留空.</p>" \
               "<p>第4行：1 日期序列的数据起始行,第一列为【日期】类型,非日期的行系统不会做读取.</p>" \
               "<p>第4行：2 非日期序列的数据起始行,数据列格式不做要求.</p>" \
               "<p>特别注意: 文件内以`Sheet`开头的表将不做读取.即不进行命名的表系统是忽略的."

        tips_label = QLabel(tips, self)
        tips_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        tips_label.setWordWrap(True)
        tips_label.setObjectName("tipLabel")
        main_layout.addWidget(tips_label)

        self.setLayout(main_layout)
        self.config_table.horizontalHeader().setStyleSheet(
            "QHeaderView::section{background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,"
            "stop:0 #49aa54, stop: 0.48 #49cc54,stop: 0.52 #49cc54, stop:1 #49aa54);"
            "border:1px solid rgb(201,202,202);border-left:none;"
            "min-height:25px;min-width:40px;font-weight:bold;};"
        )

        self.setStyleSheet(
            "#tipLabel{font-size:15px;color:rgb(180,100,100)}"
            "#configsTable{background-color:rgb(240,240,240);"
            "selection-background-color:qlineargradient(x1:0,y1:0, x2:0, y2:1,"
            "stop:0 #cccccc,stop:0.5 white,stop:0.6 white,stop: 1 #cccccc);"
            "alternate-background-color:rgb(245,250,248);}"
            "#operateButton{border:none;}#operateButton:hover{color:rgb(233,66,66)}"
        )

    def to_create_new_group(self):
        """ 显示新增组 """
        if self.new_group_edit.isHidden():
            self.new_group_edit.show()
        else:
            self.new_group_edit.hide()
        if self.confirm_group_button.isHidden():
            self.confirm_group_button.show()
        else:
            self.confirm_group_button.hide()

    def hide_create_new_group(self):
        """ 隐藏新增组 """
        self.new_group_edit.hide()
        self.new_group_edit.clear()
        self.confirm_group_button.hide()


class SheetTable(QTableWidget):
    """ 用户数据表显示控件 """
    right_mouse_clicked = pyqtSignal()
    cell_changed_signal = pyqtSignal(bool)
    to_set_row_buttons = pyqtSignal(int, dict)

    def __init__(self, *args, **kwargs):
        super(SheetTable, self).__init__(*args, **kwargs)
        self.drag_row = -1
        self.drag_widget = None

        self.can_show_drag = False

    def init_drag_widget(self):
        if self.drag_widget is not None and isinstance(self.drag_widget, QWidget):
            self.drag_widget.deleteLater()
            self.drag_widget = None
        self.drag_widget = QWidget(self)
        p = self.drag_widget.palette()
        p.setColor(QPalette.Background, QColor(0, 200, 100))
        self.drag_widget.setPalette(p)
        self.drag_widget.setAutoFillBackground(True)

        self.drag_widget.resize(self.width(), 30)
        self.drag_widget.hide()
        self.can_show_drag = False

    def mouseMoveEvent(self, event) -> None:
        row, col = self.indexAt(event.pos()).row(), self.indexAt(event.pos()).column()
        if col == 0:
            self.drag_widget.move(0, event.pos().y())
            if self.can_show_drag:
                self.drag_widget.show()
            # 设置当前行的背景色
            self.set_row_bg_color(row, QColor(254, 163, 86))
            # 还原上下行的背景色
            color1 = QColor(240, 240, 240) if (row + 1) % 2 == 0 else QColor(245,250,248)  # 偶数行
            color2 = QColor(240, 240, 240) if (row - 1) % 2 == 0 else QColor(245,250,248)  # 偶数行
            self.set_row_bg_color(row + 1, color1)
            self.set_row_bg_color(row - 1, color2)
        else:
            self.init_drag_widget()
            self.drag_row = -1

    def set_row_bg_color(self, row, color):
        if row < 0:
            return
        for col in range(self.columnCount()):
            item = self.item(row, col)
            if item:
                item.setBackground(QBrush(color))

    def mousePressEvent(self, event):
        if event.buttons() == Qt.RightButton:
            self.right_mouse_clicked.emit()
        if event.buttons() == Qt.LeftButton:
            row, col = self.indexAt(event.pos()).row(), self.indexAt(event.pos()).column()
            cur_item = self.item(row, col)
            if col == 0 and cur_item:
                self.cell_changed_signal.emit(False)  # 关掉单元格变化
                self.init_drag_widget()
                drag_row_data = cur_item.data(Qt.UserRole)  # 获取数据
                self.set_drag_data_on_widget(drag_row_data)
                # 记录老数据行号
                self.drag_row = row
        super(SheetTable, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:

        if self.drag_row >= 0:
            row, col = self.indexAt(event.pos()).row(), self.indexAt(event.pos()).column()
            # 还原当前行背景色
            self.set_row_bg_color(row, QColor(255, 255, 255))
            # 插入目标位置
            row_data = getattr(self.drag_widget, 'row_data', None)
            if row_data and row >= 0 and self.drag_row != row:
                # 异步请求更改排序,然后插入数据
                swap_thread = SwapSheetSorted()
                swap_thread.finished.connect(swap_thread.deleteLater)
                # 取目标数据
                if self.drag_row > row and row > 0:
                    to_id = self.item(row - 1, 0).text()
                else:
                    to_id = self.item(row, 0).text()
                move_id = row_data['id']
                # 组织数据，发起网络请求
                body_data = {
                    "move_id": move_id,
                    "to_id": to_id,
                }
                swap_thread.set_body_data(body_data)
                swap_thread.start()

                self.removeRow(self.drag_row)
                self.insert_row_data(row, row_data)
                self.selectRow(row)
        self.init_drag_widget()
        # 还原信号
        self.cell_changed_signal.emit(True)  # 关掉单元格变化
        super(SheetTable, self).mouseReleaseEvent(event)

    def insert_row_data(self, row, row_item):
        self.insertRow(row)
        item0 = QTableWidgetItem("%04d" % row_item["id"])
        item0.setTextAlignment(Qt.AlignCenter)
        item0.setToolTip('创建者:{}'.format(row_item["creator"]))
        # item0.setData(Qt.UserRole, {"is_dated": row_item['is_dated']})
        item0.setData(Qt.UserRole, row_item)
        self.setItem(row, 0, item0)

        item1 = QTableWidgetItem(row_item["create_date"])
        item1.setTextAlignment(Qt.AlignCenter)
        self.setItem(row, 1, item1)

        date_index = '是' if row_item['is_dated'] else '否'
        item2 = QTableWidgetItem(date_index)
        item2.setTextAlignment(Qt.AlignCenter)
        self.setItem(row, 2, item2)

        item3 = QTableWidgetItem(row_item["sheet_name"])
        item3.setTextAlignment(Qt.AlignCenter)
        self.setItem(row, 3, item3)

        item4 = QTableWidgetItem(row_item["update_date"])
        item4.setTextAlignment(Qt.AlignCenter)
        self.setItem(row, 4, item4)

        item5 = QTableWidgetItem(row_item["update_by"])
        item5.setTextAlignment(Qt.AlignCenter)
        self.setItem(row, 5, item5)

        update_count = row_item["update_count"]
        item6 = QTableWidgetItem(str(update_count))
        item6.setTextAlignment(Qt.AlignCenter)
        item6.setForeground(QBrush(QColor(233, 66, 66))) if update_count > 0 else item6.setForeground(
            QBrush(QColor(66, 66, 66)))
        self.setItem(row, 6, item6)

        check = Qt.Checked if row_item["is_private"] else Qt.Unchecked
        item9 = QTableWidgetItem("私有")
        item9.setCheckState(check)
        self.setItem(row, 9, item9)

        self.to_set_row_buttons.emit(row, row_item)
        
    def get_sep_button(self):
        button = QPushButton(self.drag_widget)
        button.setFocusPolicy(Qt.NoFocus)
        button.setFixedWidth(1)
        return button

    def set_drag_data_on_widget(self, row_data):  # 请参照user_data.py的函数show_variety_sheets里的取数方法
        col_widths = []
        for col in range(self.columnCount()):
            col_widths.append(self.columnWidth(col))

        drag_layout = QHBoxLayout(self.drag_widget)
        drag_layout.setContentsMargins(0, 0, 0, 0)
        drag_layout.setSpacing(0)
        label1 = QLabel("%04d" % row_data["id"], self.drag_widget)
        label1.setMinimumWidth(col_widths[0])
        label1.setAlignment(Qt.AlignCenter)
        drag_layout.addWidget(label1)

        drag_layout.addWidget(self.get_sep_button())

        label2 = QLabel(str(row_data['create_date']), self.drag_widget)
        label2.setMinimumWidth(col_widths[1])
        label2.setAlignment(Qt.AlignCenter)
        drag_layout.addWidget(label2)

        drag_layout.addWidget(self.get_sep_button())

        text = '是' if row_data['is_dated'] else '否'
        label3 = QLabel(text, self.drag_widget)
        label3.setMinimumWidth(col_widths[2])
        label3.setAlignment(Qt.AlignCenter)
        drag_layout.addWidget(label3)
        drag_layout.addWidget(self.get_sep_button())

        label4 = QLabel(str(row_data['sheet_name']), self.drag_widget)
        label4.setMinimumWidth(col_widths[3])
        label4.setAlignment(Qt.AlignCenter)
        drag_layout.addWidget(label4)
        drag_layout.addWidget(self.get_sep_button())

        label5 = QLabel(str(row_data['update_date']), self.drag_widget)
        label5.setMinimumWidth(col_widths[4])
        label5.setAlignment(Qt.AlignCenter)
        drag_layout.addWidget(label5)
        drag_layout.addWidget(self.get_sep_button())

        label6 = QLabel(str(row_data['update_by']), self.drag_widget)
        label6.setMinimumWidth(col_widths[5])
        label6.setAlignment(Qt.AlignCenter)
        drag_layout.addWidget(label6)
        drag_layout.addWidget(self.get_sep_button())

        label7 = QLabel(str(row_data['update_count']), self.drag_widget)
        label7.setMinimumWidth(col_widths[6])
        label7.setAlignment(Qt.AlignCenter)
        drag_layout.addWidget(label7)
        drag_layout.addWidget(self.get_sep_button())

        drag_layout.addStretch()
        self.drag_widget.setLayout(drag_layout)
        setattr(self.drag_widget, 'row_data', row_data)
        self.can_show_drag = True


class VarietySheetUI(QWidget):
    def __init__(self, *args, **kwargs):
        super(VarietySheetUI, self).__init__(*args, **kwargs)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(QMargins(0, 1, 0, 1))
        opts_layout = QHBoxLayout()
        opts_layout.addWidget(QLabel("品种:", self))
        self.variety_combobox = QComboBox(self)
        self.variety_combobox.setMinimumWidth(80)
        opts_layout.addWidget(self.variety_combobox)

        opts_layout.addWidget(QLabel("数据组:", self))
        self.group_combobox = QComboBox(self)
        self.group_combobox.setMinimumWidth(100)
        opts_layout.addWidget(self.group_combobox)

        # 只看我上传选项
        self.only_me_check = QCheckBox(self)
        self.only_me_check.setText("只看我上传的")
        self.only_me_check.setChecked(True)
        opts_layout.addWidget(self.only_me_check)

        tip_label = QLabel(self)
        tip_label.setText('提示:在第1列范围按住拖动排序!(辅助跨行排序,结果刷新为准.)')
        pal = tip_label.palette()
        pal.setColor(QPalette.WindowText, QColor(233, 66, 66))
        font = tip_label.font()
        font.setPointSize(9)
        tip_label.setFont(font)
        tip_label.setPalette(pal)
        tip_label.setAutoFillBackground(True)
        opts_layout.addWidget(tip_label)
        self.refresh_button = QPushButton('刷新', self)
        opts_layout.addWidget(self.refresh_button)
        opts_layout.addStretch()
        main_layout.addLayout(opts_layout)

        # 搜索框
        self.query_edit = QLineEdit(self)
        self.query_edit.setPlaceholderText('在此输入数据表名称进行检索')
        self.query_edit.setFixedHeight(22)
        main_layout.addWidget(self.query_edit)

        self.sheet_table = SheetTable(self)
        self.sheet_table.setFrameShape(QFrame.NoFrame)
        self.sheet_table.setFocusPolicy(Qt.NoFocus)
        self.sheet_table.verticalHeader().hide()
        self.sheet_table.setEditTriggers(QHeaderView.NoEditTriggers)
        self.sheet_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.sheet_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.sheet_table.verticalHeader().setDefaultSectionSize(25)  # 设置行高(与下行代码同时才生效)
        self.sheet_table.verticalHeader().setMinimumSectionSize(25)
        self.sheet_table.setAlternatingRowColors(True)
        main_layout.addWidget(self.sheet_table)
        self.setLayout(main_layout)
        self.sheet_table.setObjectName("sheetTable")
        self.sheet_table.horizontalHeader().setStyleSheet(
            "QHeaderView::section{background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,"
            "stop:0 #34adf3, stop: 0.5 #ccddff,stop: 0.6 #ccddff, stop:1 #34adf3);"
            "border:1px solid rgb(201,202,202);border-left:none;"
            "min-height:25px;min-width:40px;font-weight:bold;};"
        )
        self.setStyleSheet(
            "#tipLabel{font-size:15px;color:rgb(180,100,100)}"
            "#sheetTable{background-color:rgb(240,240,240);"
            "selection-background-color:qlineargradient(x1:0,y1:0, x2:0, y2:1,"
            "stop:0 #cccccc,stop:0.5 white,stop:0.6 white,stop: 1 #cccccc);"
            "alternate-background-color:rgb(245,250,248);}"
        )


class ChartTable(QTableWidget):
    cell_changed_signal = pyqtSignal(bool)
    to_set_row_buttons = pyqtSignal(int, dict)
    right_mouse_clicked = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(ChartTable, self).__init__(*args, **kwargs)
        self.drag_row = -1
        self.drag_widget = None
        
        self.can_show_drag = False
        
    def init_drag_widget(self):
        if self.drag_widget is not None and isinstance(self.drag_widget, QWidget):
            self.drag_widget.deleteLater()
            self.drag_widget = None
        self.drag_widget = QWidget(self)
        p = self.drag_widget.palette()
        p.setColor(QPalette.Background, QColor(0, 200, 100))
        self.drag_widget.setPalette(p)
        self.drag_widget.setAutoFillBackground(True)
    
        self.drag_widget.resize(self.width(), 30)
        self.drag_widget.hide()
        self.can_show_drag = False

    def get_sep_button(self):
        button = QPushButton(self.drag_widget)
        button.setFocusPolicy(Qt.NoFocus)
        button.setFixedWidth(1)
        return button

    def set_drag_data_on_widget(self, row_data):
        col_widths = []
        for col in range(self.columnCount()):
            col_widths.append(self.columnWidth(col))

        drag_layout = QHBoxLayout(self.drag_widget)
        drag_layout.setContentsMargins(0, 0, 0, 0)
        drag_layout.setSpacing(0)
        label1 = QLabel("%04d" % row_data["id"], self.drag_widget)
        label1.setMinimumWidth(col_widths[0])
        label1.setAlignment(Qt.AlignCenter)
        drag_layout.addWidget(label1)

        drag_layout.addWidget(self.get_sep_button())

        label2 = QLabel(str(row_data['creator']), self.drag_widget)
        label2.setMinimumWidth(col_widths[1])
        label2.setAlignment(Qt.AlignCenter)
        drag_layout.addWidget(label2)

        drag_layout.addWidget(self.get_sep_button())

        label3 = QLabel(str(row_data['create_time']), self.drag_widget)
        label3.setMinimumWidth(col_widths[2])
        label3.setAlignment(Qt.AlignCenter)
        drag_layout.addWidget(label3)

        drag_layout.addWidget(self.get_sep_button())

        label4 = QLabel(str(row_data['title']), self.drag_widget)
        label4.setMinimumWidth(col_widths[3])
        label4.setAlignment(Qt.AlignCenter)
        drag_layout.addWidget(label4)

        drag_layout.addWidget(self.get_sep_button())

        drag_layout.addStretch()
        self.drag_widget.setLayout(drag_layout)
        setattr(self.drag_widget, 'row_data', row_data)
        self.can_show_drag = True

    def set_row_bg_color(self, row, color):
        if row < 0:
            return
        for col in range(self.columnCount()):
            item = self.item(row, col)
            if item:
                item.setBackground(QBrush(color))

    def insert_row_data(self, row, row_item):
        self.insertRow(row)
        item0 = QTableWidgetItem("%04d" % row_item["id"])
        item0.setTextAlignment(Qt.AlignCenter)
        item0.setData(Qt.UserRole, row_item)
        self.setItem(row, 0, item0)

        item1 = QTableWidgetItem(row_item["creator"])
        item1.setTextAlignment(Qt.AlignCenter)
        self.setItem(row, 1, item1)

        item2 = QTableWidgetItem(row_item["create_time"])
        item2.setTextAlignment(Qt.AlignCenter)
        self.setItem(row, 2, item2)

        item3 = QTableWidgetItem(row_item["title"])
        item3.setTextAlignment(Qt.AlignCenter)
        self.setItem(row, 3, item3)
        # 主页
        item7 = QTableWidgetItem()
        if row_item["is_principal"] == "0":
            text = "显示"
            checked = Qt.Unchecked
        elif row_item["is_principal"] == "1":
            text = "审核"
            checked = Qt.PartiallyChecked
        else:
            text = "开启"
            checked = Qt.Checked
        item7.setText(text)
        item7.setCheckState(checked)
        self.setItem(row, 7, item7)

        # 品种页
        item8 = QTableWidgetItem()
        checked = Qt.Checked if row_item["is_petit"] else Qt.Unchecked
        item8.setText("开启")
        item8.setCheckState(checked)
        self.setItem(row, 8, item8)

        # 仅私有可见
        item9 = QTableWidgetItem("私有")
        checked = Qt.Checked if row_item["is_private"] else Qt.Unchecked
        item9.setCheckState(checked)
        self.setItem(row, 9, item9)

        self.to_set_row_buttons.emit(row, row_item)

    def mouseMoveEvent(self, event) -> None:
        row, col = self.indexAt(event.pos()).row(), self.indexAt(event.pos()).column()
        if col == 0:
            self.drag_widget.move(0, event.pos().y())
            if self.can_show_drag:
                self.drag_widget.show()
            # 设置当前行的背景色
            self.set_row_bg_color(row, QColor(254, 163, 86))
            # 还原上下行的背景色
            color1 = QColor(255, 255, 255) if (row + 1) % 2 == 0 else QColor(245, 245, 245)  # 偶数行
            color2 = QColor(255, 255, 255) if (row - 1) % 2 == 0 else QColor(245, 245, 245)  # 偶数行
            self.set_row_bg_color(row + 1, color1)
            self.set_row_bg_color(row - 1, color2)
        else:
            self.init_drag_widget()
            self.drag_row = -1

        super(ChartTable, self).mouseMoveEvent(event)

    def mousePressEvent(self, event) -> None:
        if event.buttons() == Qt.RightButton:
            self.right_mouse_clicked.emit()
        if event.buttons() == Qt.LeftButton:
            row, col = self.indexAt(event.pos()).row(), self.indexAt(event.pos()).column()
            cur_item = self.item(row, col)
            if col == 0 and cur_item:
                self.cell_changed_signal.emit(False)  # 关掉单元格变化
                self.init_drag_widget()
                drag_row_data = cur_item.data(Qt.UserRole)
                self.set_drag_data_on_widget(drag_row_data)
                self.drag_row = row
        super(ChartTable, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if self.drag_row >= 0:
            row, col = self.indexAt(event.pos()).row(), self.indexAt(event.pos()).column()
            self.set_row_bg_color(row, QColor(255, 255, 255))
            # 插入目标位置
            row_data = getattr(self.drag_widget, 'row_data', None)
            if row_data and row >=0 and self.drag_row != row:
                # 异步请求更改排序，然后插入数据
                sort_thread = SwapChartSorted()
                sort_thread.finished.connect(sort_thread.deleteLater)
                move_id = row_data['id']
                if self.drag_row > row and row > 0:
                    to_id = self.item(row - 1, 0).text()
                else:
                    to_id = self.item(row, 0).text()
                body_data = {
                    "move_id": move_id,
                    "to_id": to_id
                }
                sort_thread.set_body_data(body_data)
                sort_thread.start()

                self.removeRow(self.drag_row)
                self.insert_row_data(row, row_data)
                self.selectRow(row)
        self.init_drag_widget()
        self.cell_changed_signal.emit(True)
        super(ChartTable, self).mouseReleaseEvent(event)


class SheetChartUI(QWidget):
    def __init__(self, *args, **kwargs):
        super(SheetChartUI, self).__init__(*args, **kwargs)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(QMargins(0, 1, 0, 1))
        opts_layout = QHBoxLayout()
        opts_layout.addWidget(QLabel("品种:", self))
        self.variety_combobox = QComboBox(self)
        self.variety_combobox.setMinimumWidth(80)
        opts_layout.addWidget(self.variety_combobox)

        # 指定图形类型
        opts_layout.addWidget(QLabel('类型:', self))
        self.category_combobox = QComboBox(self)
        self.category_combobox.addItem('全部', '0')
        self.category_combobox.addItem('普通图形', 'normal')
        self.category_combobox.addItem('季节图形', 'season')
        opts_layout.addWidget(self.category_combobox)

        # 只看我上传选项
        self.only_me_check = QCheckBox(self)
        self.only_me_check.setText("只看我配置的")
        self.only_me_check.setChecked(True)
        opts_layout.addWidget(self.only_me_check)

        tip_label = QLabel(self)
        tip_label.setText('提示:在第1列范围按住拖动排序!(辅助跨行排序,结果刷新为准.)')
        pal = tip_label.palette()
        pal.setColor(QPalette.WindowText, QColor(233, 66, 66))
        font = tip_label.font()
        font.setPointSize(9)
        tip_label.setFont(font)
        tip_label.setPalette(pal)
        tip_label.setAutoFillBackground(True)
        opts_layout.addWidget(tip_label)
        self.refresh_button = QPushButton('刷新', self)
        opts_layout.addWidget(self.refresh_button)

        opts_layout.addStretch()
        main_layout.addLayout(opts_layout)

        # 检索框
        self.query_edit = QLineEdit(self)
        self.query_edit.setPlaceholderText('在此输入图形名称进行检索')
        self.query_edit.setFixedHeight(22)
        main_layout.addWidget(self.query_edit)

        self.chart_table = ChartTable(self)
        self.chart_table.setFrameShape(QFrame.NoFrame)
        self.chart_table.setFocusPolicy(Qt.NoFocus)
        self.chart_table.verticalHeader().hide()
        self.chart_table.setEditTriggers(QHeaderView.NoEditTriggers)
        self.chart_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.chart_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.chart_table.setAlternatingRowColors(True)
        self.chart_table.verticalHeader().setDefaultSectionSize(25)  # 设置行高(与下行代码同时才生效)
        self.chart_table.verticalHeader().setMinimumSectionSize(25)

        self.swap_tab = QTabWidget(self)

        self.swap_tab.setTabBar(HorizontalTabBar())

        self.swap_tab.addTab(self.chart_table, "管\n理")
        self.swap_tab.setDocumentMode(True)
        self.swap_tab.setTabPosition(QTabWidget.East)
        self.chart_container = QWebEngineView(self)
        self.chart_container.setContextMenuPolicy(Qt.NoContextMenu)

        self.swap_tab.addTab(self.chart_container, "全\n览")

        main_layout.addWidget(self.swap_tab)

        self.setLayout(main_layout)
        self.chart_table.setObjectName("chartTable")
        self.chart_table.horizontalHeader().setStyleSheet(
            "QHeaderView::section{background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,"
            "stop:0 #fea356, stop: 0.5 #eeeeee,stop: 0.6 #eeeeee, stop:1 #fea356);"
            "border:1px solid rgb(201,202,202);border-left:none;"
            "min-height:25px;min-width:40px;font-weight:bold;};"
        )
        self.swap_tab.tabBar().setObjectName("tabBar")
        self.setStyleSheet(
            "#tabBar::tab{min-height:75px;}"
            "#tipLabel{font-size:15px;color:rgb(180,100,100)}"
            "#chartTable{background-color:rgb(240,240,240);"
            "selection-background-color:qlineargradient(x1:0,y1:0, x2:0, y2:1,"
            "stop:0 #cccccc,stop:0.5 white,stop:0.6 white,stop: 1 #cccccc);"
            "alternate-background-color:rgb(245,250,248);}"
            "#operateButton{border:none;}#operateButton:hover{color:rgb(233,66,66)}"
        )


# 现货报价数据维护(2021.02.25)
class SpotPriceWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(SpotPriceWidget, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        form_widget = QWidget(self)
        form_layout = QFormLayout()
        self.date_edit = QDateEdit(self)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat('yyyy-MM-dd')
        form_layout.addRow("日期:", self.date_edit)
        self.spot_table = QTableWidget(self)
        self.spot_table.setColumnCount(2)
        self.spot_table.setHorizontalHeaderLabels(['品种', '价格'])
        self.spot_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        form_layout.addRow("数据:", self.spot_table)
        self.submit_button = QPushButton('确定提交', self)
        submit_layout = QHBoxLayout()
        submit_layout.addStretch()
        submit_layout.addWidget(self.submit_button)
        form_layout.addRow("", submit_layout)
        form_widget.setLayout(form_layout)
        form_widget.setMinimumWidth(660)
        layout.addWidget(form_widget, alignment=Qt.AlignHCenter)
        self.setLayout(layout)

        self.date_edit.dateChanged.connect(self.get_spot_prices)
        self.submit_button.clicked.connect(self.submit_spot_prices)

    def set_variety(self, variety_list):
        self.spot_table.clearContents()
        variety_list = list(filter(lambda x: x['variety_en'] not in ['GP', 'GZ', 'WB', 'HG'], variety_list))
        self.spot_table.setRowCount(len(variety_list))
        for row, v_item in enumerate(variety_list):
            item0 = QTableWidgetItem(v_item['variety_name'])
            item0.setData(Qt.UserRole, v_item['variety_en'])
            item1 = QLineEdit(self)
            item1.setValidator(QDoubleValidator(item1))
            self.spot_table.setItem(row, 0, item0)
            self.spot_table.setCellWidget(row, 1, item1)

        # 获取当日现货报价
        self.get_spot_prices()

    def get_spot_prices(self):  # 请求当前日期的现货数据
        current_date = self.date_edit.text().replace('-', '')
        network_manager = getattr(qApp, '_network', QNetworkAccessManager(self))
        url = QUrl(SERVER_API + 'spot-price/')
        url.setQuery("date={}".format(current_date))
        reply = network_manager.get(QNetworkRequest(url))
        reply.finished.connect(self.spot_price_reply)

    def update_spot_price(self, spot_prices):
        spot_prices = {item['variety_en']: item['price'] for item in spot_prices}
        row_count = self.spot_table.rowCount()
        for row in range(row_count):
            variety_en = self.spot_table.item(row, 0).data(Qt.UserRole)
            edit_widget = self.spot_table.cellWidget(row, 1)
            edit_widget.setText(str(spot_prices.get(variety_en, '')))

    def spot_price_reply(self):
        reply = self.sender()
        if not reply.error():
            data = json.loads(reply.readAll().data().decode('utf8'))
            self.update_spot_price(data['data'])
        reply.deleteLater()

    def get_table_data(self):
        data = []
        row_count = self.spot_table.rowCount()
        for row in range(row_count):
            variety_en = self.spot_table.item(row, 0).data(Qt.UserRole)
            edit_widget = self.spot_table.cellWidget(row, 1)
            price_str = edit_widget.text().strip()
            if price_str:
                data.append({'variety_en': variety_en, 'price': float(price_str)})
        return data

    def submit_spot_prices(self):
        data = self.get_table_data()
        print(data)
        # 将数据上传到服务器进行保存
        current_date = self.date_edit.text()
        print(current_date)


class UserDataMaintainUI(QWidget):
    def __init__(self, *args, **kwargs):
        super(UserDataMaintainUI, self).__init__(*args, **kwargs)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(QMargins(0, 0, 0, 0))
        main_splitter = QSplitter(self)

        self.maintain_menu = QListWidget(self)
        main_splitter.addWidget(self.maintain_menu)

        self.maintain_frame = QTabWidget(self)
        self.maintain_frame.setDocumentMode(True)
        self.maintain_frame.tabBar().hide()
        main_splitter.addWidget(self.maintain_frame)

        main_splitter.setStretchFactor(1, 2)
        main_splitter.setStretchFactor(2, 8)
        main_splitter.setHandleWidth(1)

        main_layout.addWidget(main_splitter)
        self.setLayout(main_layout)

        self.maintain_menu.setObjectName('leftList')
        self.setStyleSheet(
            "#leftList{outline:none;border:none;border-right: 1px solid rgb(180,180,180);}"
            "#leftList::item{height:25px;}"
            "#leftList::item:selected{border-left:3px solid rgb(100,120,150);color:#000;background-color:rgb(180,220,230);}"
            "#messageLabel{color:rgb(233,66,66);font-weight:bold}"
        )

        # 实例化3个待显示的界面
        self.source_config_widget = ConfigSourceUI(self)
        self.maintain_frame.addTab(self.source_config_widget, "数据源")

        self.variety_sheet_widget = VarietySheetUI(self)
        self.maintain_frame.addTab(self.variety_sheet_widget, "数据表")

        self.sheet_chart_widget = SheetChartUI(self)

        self.maintain_frame.addTab(self.sheet_chart_widget, "数据图")

        # 实例化现货数据维护界面
        self.spot_price_widget = SpotPriceWidget(self)
        self.maintain_frame.addTab(self.spot_price_widget, "现货数据")
