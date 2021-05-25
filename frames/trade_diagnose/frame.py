# _*_ coding:utf-8 _*_
# @File  : frame.py
# @Time  : 2021-03-26 10:20
# @Author: zizle

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from widgets import LoadingCover

from frames.trade_diagnose import pages
from frames.trade_diagnose.threads import HandleSourceThread


class TradeDiagnose(QWidget):
    # pid为页面id，负数表示不跳转页面是根节点菜单，整数表示页面索引
    MENUS = [
        {'pid': -1, 'name': '账户概况', 'logo': '', 'children': [
            # {'pid': 0, 'name': '数据概览', 'logo': ''}, 0为导入数据页
            {'pid': 1, 'name': '原始数据', 'logo': ''},
            {'pid': 2, 'name': '账户基本统计', 'logo': ''},  # 诊断分析
        ]},
        {'pid': -2, 'name': '交易分析', 'logo': '', 'children': [
            {'pid': 3, 'name': '手数-金额', 'logo': ''},
            {'pid': 4, 'name': '日内与隔夜', 'logo': ''},
            {'pid': 5, 'name': '交易费用', 'logo': ''},
        ]},
        {'pid': -3, 'name': '盈亏分析', 'logo': '', 'children': [
            {'pid': 6, 'name': '净值图', 'logo': ''},
            {'pid': 7, 'name': '品种盈亏分析', 'logo': ''},
        ]},
        {'pid': -4, 'name': '风控分析', 'logo': '', 'children': [
            {'pid': 8, 'name': '账户风控', 'logo': ''},
        ]}
    ]

    def __init__(self, *args, **kwargs):
        super(TradeDiagnose, self).__init__(*args, **kwargs)
        self.resize(1200, 700)
        layout = QHBoxLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        layout.setSpacing(0)
        self.splitter = QSplitter(self)
        # 左侧是个tree
        self.tree_list = QTreeWidget(self)
        self.tree_list.setMinimumWidth(100)
        self.tree_list.setMaximumWidth(220)
        self.tree_list.header().hide()
        self.tree_list.setFrameShape(QFrame.NoFrame)
        # tree的样式
        self.tree_list.setObjectName('treeWidget')
        # 右侧是个显示窗
        self.stacked = QStackedWidget(self)
        self.stacked.setObjectName('stacked')

        self.splitter.addWidget(self.tree_list)
        self.splitter.addWidget(self.stacked)
        self.splitter.setHandleWidth(1)

        self.setStyleSheet(
            '#treeWidget{background-color:rgb(159, 205, 254);border-right:1px solid #555}'
            '#treeWidget::item{margin: 5px}'
            '#stacked{background-color:rgb(159, 205, 254)}'
        )

        # 添加菜单目录，添加各窗口
        # 添加菜单
        bold_font = QFont()
        bold_font.setBold(True)
        for parent_item in self.MENUS:
            root_item = QTreeWidgetItem()
            root_item.setText(0, parent_item["name"])
            setattr(root_item, "pid", parent_item["pid"])
            root_item.setIcon(0, QIcon(parent_item["logo"]))
            root_item.setFont(0, bold_font)
            root_item.setForeground(0, QBrush(QColor(8, 111, 199)))
            self.tree_list.addTopLevelItem(root_item)
            for child_item in parent_item["children"]:
                child = QTreeWidgetItem(root_item)
                child.setText(0, child_item["name"])
                setattr(child, "pid", child_item["pid"])
                child.setIcon(0, QIcon(child_item["logo"]))
                child.setForeground(0, QBrush(QColor(255, 255, 255)))
                root_item.addChild(child)
        # 各窗口
        self.load_data_page = None  # 导入数据窗口
        self.source_view = None  # 处理后的原始数据
        self.base_view = None  # 基本数据
        self.hands_price_view = None  # 交易分析 - 手数金额
        self.pass_night_view = None  # 交易分析 - 日内隔夜
        self.exchange_charge_view = None  # 交易分析 - 交易费用
        self.net_value_view = None  # 净值图
        self.variety_profit_view = None  # 品种盈亏分析
        self.risk_control_view = None  # 风控分析 - 账户风控

        # 左侧菜单点击事件
        self.tree_list.expandAll()
        self.tree_list.itemClicked.connect(self.left_menu_selected)
        self.current_pid = None

        # 弹窗提消息
        self.tip_popup = LoadingCover(self)
        self.tip_popup.show(text='正在加载模块...')
        layout.addWidget(self.splitter)
        self.setLayout(layout)
        # 处理原始数据的线程
        self.thread_ = None
        self.source_data = None

    def resizeEvent(self, event):
        super(TradeDiagnose, self).resizeEvent(event)
        self.tip_popup.resize(self.width(), self.height())

    def clear_current_thread(self):
        # 删除当前的线程
        if self.thread_:
            del self.thread_
            self.thread_ = None

    def left_menu_selected(self, tree_item):
        if tree_item.childCount():
            if tree_item.isExpanded():
                tree_item.setExpanded(False)
            else:
                tree_item.setExpanded(True)
            self.current_pid = None
        elif tree_item.parent():
            self.current_pid = getattr(tree_item, "pid")
        else:
            self.current_pid = None

        self.changed_page()

    def changed_page(self):
        if self.current_pid is None:
            return
        if not self.source_data:
            QMessageBox.information(self, '提示', '请导入原始数据后再进行诊断...')
            return
        if self.current_pid == 1: # 原始数据
            self.stacked.setCurrentIndex(self.current_pid)
            return
        # 根据页面处理需要显示的数据并进行显示
        if self.current_pid == 2:  # 基本指标
            self.show_base_view_data()

        elif self.current_pid == 3:  # 交易分析 - 手数金额
            self.show_hands_price()

        elif self.current_pid == 4: # 交易分析 - 日内与隔夜
            self.show_pass_night()

        elif self.current_pid == 5:  # 交易分析 - 交易费用
            self.show_exchange_charge()

        elif self.current_pid == 6:  # 盈亏分析 - 净值图
            self.show_net_value()

        elif self.current_pid == 7:  # 盈亏分析 - 品种盈亏分析
            self.show_variety_profit()

        elif self.current_pid == 8:
            self.show_account_risk()  # 风控分析 - 账户风控

        else:
            return
        self.stacked.setCurrentIndex(self.current_pid)

    def set_all_pages(self):
        # 设置添加各页面的GUI
        # 导入数据
        self.load_data_page = pages.LoadDataWidget(self)
        self.load_data_page.load_button.clicked.connect(self.loading_source_data)
        self.stacked.addWidget(self.load_data_page)
        # 原始数据
        self.source_view = pages.SourceViewWidget(self)
        self.stacked.addWidget(self.source_view)
        # 基础数据
        self.base_view = pages.BaseViewWidget(self)
        self.base_view.finished.connect(self.tip_popup.hide)
        self.stacked.addWidget(self.base_view)
        # 交易分析 - 手数金额
        self.hands_price_view = pages.HandsPriceWidget(self)
        self.hands_price_view.finished.connect(self.tip_popup.hide)
        self.stacked.addWidget(self.hands_price_view)
        # 交易分析 - 日内隔夜
        self.pass_night_view = pages.PassNightWidget(self)
        self.pass_night_view.finished.connect(self.tip_popup.hide)
        self.stacked.addWidget(self.pass_night_view)
        # 交易分析 - 交易费用
        self.exchange_charge_view = pages.ExchangeChargeWidget(self)
        self.exchange_charge_view.finished.connect(self.tip_popup.hide)
        self.stacked.addWidget(self.exchange_charge_view)
        # 盈亏分析 - 净值图
        self.net_value_view = pages.NetValueWidget(self)
        self.net_value_view.finished.connect(self.tip_popup.hide)
        self.stacked.addWidget(self.net_value_view)
        # 盈亏分析- 品种盈亏分析
        self.variety_profit_view = pages.VarietyProfitWidget(self)
        self.variety_profit_view.finished.connect(self.tip_popup.hide)
        self.stacked.addWidget(self.variety_profit_view)
        # 风控分析 - 账户风控
        self.risk_control_view = pages.RiskControlWidget(self)
        self.risk_control_view.finished.connect(self.tip_popup.hide)
        self.stacked.addWidget(self.risk_control_view)

        self.tip_popup.hide()

    def loading_source_data(self):
        # 导入数据的逻辑
        if self.load_data_page is None:
            return
        bill_t = self.load_data_page.bill_type
        # 弹窗选择文件夹
        files, _ = QFileDialog.getOpenFileNames(self, '选择文件夹', 'C:/Users/Administrator/Desktop/账单数据/日账单(逐日盯市)', '*.xls')
        # 保存原始数据
        self.tip_popup.show('正在处理数据')
        self.clear_current_thread()
        self.thread_ = HandleSourceThread(bill_type=bill_t, files=files)
        self.thread_.finished.connect(self.thread_.deleteLater)
        self.thread_.error_break.connect(self.handle_source_error)
        self.thread_.handle_finished.connect(self.has_got_source_data)
        self.thread_.start()

    def handle_source_error(self, e):
        QMessageBox.warning(self, '错误', e)
        self.tip_popup.hide()

    def has_got_source_data(self, source):
        # 得到原始数据
        self.source_data = source
        self.source_view.show_source_data(self.source_data['account'], self.source_data['trade_detail'])
        self.tip_popup.hide()
        self.stacked.setCurrentIndex(1)  # 跳转到原始数据页

    def show_base_view_data(self):
        # 显示基础数据
        self.tip_popup.show(text='正在处理数据,请稍后...')
        self.base_view.handle_base_data(self.source_data['account'], self.source_data['trade_detail'])

    def show_hands_price(self):
        # 显示交易分析 - 金额手数分析
        self.tip_popup.show(text='正在处理数据,请稍后...')
        self.hands_price_view.handle_data(self.source_data['trade_detail'])

    def show_pass_night(self):
        # 显示交易分析 - 日内与隔夜
        self.tip_popup.show(text='正在处理数据,请稍后...')
        self.pass_night_view.handle_data(self.source_data['trade_detail'])

    def show_exchange_charge(self):
        # 显示交易分析 - 交易费用
        self.tip_popup.show(text='正在处理数据,请稍后...')
        self.exchange_charge_view.handle_data(self.source_data['account'])

    def show_net_value(self):
        # 盈亏分析 - 净值图
        self.tip_popup.show(text='正在处理数据,请稍后...')
        self.net_value_view.handle_data(self.source_data['account'])

    def show_variety_profit(self):
        # 盈亏分析 - 品种盈亏分析
        self.tip_popup.show(text='正在处理数据,请稍后...')
        self.variety_profit_view.handle_data(self.source_data['trade_detail'])

    def show_account_risk(self):
        # 风控分析 - 账户风控
        self.tip_popup.show(text='正在处理数据,请稍后...')
        self.risk_control_view.handle_data(self.source_data['account'], self.source_data['trade_detail'])


    # def show_sum_profit_rate(self):
    #     # 显示累计收益率页面及数据
    #     self.tip_popup.show(text='正在处理数据，请稍后...')
    #     self.profit_view.handle_profit_data(self.source_data['account'])
    #
    # def show_net_profits(self):
    #     # 显示累计净利润页面及数据
    #     self.tip_popup.show(text='正在处理数据，请稍后...')
    #     self.net_profits.handle_net_profits(self.source_data['account'])
    #
    # def show_sum_variety_profit(self):
    #     # 显示累计品种盈亏页面及数据
    #     self.tip_popup.show(text='正在处理数据，请稍后...')
    #     self.sum_variety_profit.handle_sum_variety_profit(self.source_data['exchange'])
    #
    # def show_risk_percent(self):
    #     # 显示风险度
    #     self.tip_popup.show(text='正在处理数据，请稍后...')
    #     self.risk_view.handle_risk_percent(self.source_data['account'])
    #
    # def show_variety_percent(self):
    #     # 显示品种交易额数据(各品种交易额饼图,交易手数饼图)
    #     self.tip_popup.show(text='正在处理数据，请稍后...')
    #     self.variety_view.handle_variety_percent(self.source_data['exchange'])
    #
    # def show_shmore_percent(self):
    #     # 显示多空盈亏统计数
    #     self.tip_popup.show(text='正在处理数据，请稍后...')
    #     self.shmore_view.handle_short_more(self.source_data['exchange'])
