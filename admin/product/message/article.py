# _*_ coding:utf-8 _*_
# @File  : article.py
# @Time  : 2021-05-31 11:21
# @Author: zizle


# 分析文章
import datetime

from PyQt5.QtCore import Qt, QFile, QUrl
from PyQt5.QtNetwork import QNetworkRequest
from PyQt5.QtWidgets import qApp, QWidget, QVBoxLayout, QLabel, QTableWidget, QRadioButton, \
    QHBoxLayout, QTabWidget, QLineEdit, QPushButton, QDateTimeEdit, QComboBox, QTableWidgetItem

from widgets import FilePathLineEdit, Paginator
from popup.message import InformationPopup
from settings import SERVER_API
from utils.client import get_user_token
from utils.multipart import generate_multipart_data
from apis.product.analysis_article import GetAnalysisArticle
from apis.variety import VarietyAPI


class ProductArticle(QWidget):
    def __init__(self, *args, **kwargs):
        super(ProductArticle, self).__init__(*args, **kwargs)
        lt = QVBoxLayout(self)
        container = QTabWidget(self)
        lt.addWidget(container)
        self.setLayout(lt)

        # 当前管理
        manager_widget = QWidget(self)
        manager_lt = QVBoxLayout(manager_widget)
        manager_widget.setLayout(manager_lt)
        self.paginator = Paginator()
        self.paginator.setParent(manager_widget)
        self.paginator.setFixedHeight(30)
        manager_lt.addWidget(self.paginator, alignment=Qt.AlignRight)

        self.article_table = QTableWidget(manager_widget)
        manager_lt.addWidget(self.article_table)

        container.addTab(manager_widget, '管理')

        # 新增 #########################
        self.create_widget = QWidget(container)
        create_lt = QVBoxLayout()
        self.create_widget.setLayout(create_lt)
        container.addTab(self.create_widget, '新增')

        # 日期
        self.time_widget = QWidget(self)
        time_lt = QHBoxLayout(self.time_widget)
        self.time_widget.setLayout(time_lt)
        time_lt.addWidget(QLabel('时间：', self))
        self.create_time = QDateTimeEdit(self.time_widget)
        self.create_time.setDateTime(datetime.datetime.now())
        self.create_time.setCalendarPopup(True)
        self.create_time.setDisplayFormat('yyyy-MM-dd HH:mm:ss')
        time_lt.addWidget(self.create_time)
        time_lt.addStretch()
        create_lt.addWidget(self.time_widget)

        # 类型
        self.type_widget = QWidget(self)
        type_lt = QHBoxLayout(self.type_widget)
        self.type_widget.setLayout(type_lt)

        type_label = QLabel('类型：', self)
        type_lt.addWidget(type_label)

        self.pdf_radio = QRadioButton('PDF文件', self)
        self.pdf_radio.setChecked(True)
        self.pdf_radio.toggled.connect(self.pdf_toggled)
        type_lt.addWidget(self.pdf_radio)
        self.html_radio = QRadioButton('网址', self)
        self.html_radio.toggled.connect(self.web_toggled)
        type_lt.addWidget(self.html_radio)

        type_lt.addStretch()
        create_lt.addWidget(self.type_widget)

        # 关联品种
        self.variety_widget = QWidget(self)
        variety_lt = QHBoxLayout(self.variety_widget)
        variety_lt.addWidget(QLabel('品种：', self.variety_widget))
        self.variety_combobox = QComboBox(self.variety_widget)
        self.variety_combobox.currentTextChanged.connect(self.selected_variety_changed)
        variety_lt.addWidget(self.variety_combobox)
        variety_lt.addWidget(QLabel('已选：', self.variety_widget))
        self.selected_variety = QLabel(self.variety_widget)
        variety_lt.addWidget(self.selected_variety)
        self.clear_selected_variety = QPushButton('清空', self.variety_widget)
        self.clear_selected_variety.setCursor(Qt.PointingHandCursor)
        self.clear_selected_variety.setFlat(True)
        self.clear_selected_variety.clicked.connect(self.clear_variety)
        variety_lt.addWidget(self.clear_selected_variety)
        variety_lt.addStretch()
        create_lt.addWidget(self.variety_widget)

        # 标题
        self.title_widget = QWidget(self)
        title_lt = QHBoxLayout(self.title_widget)
        self.title_widget.setLayout(title_lt)
        title_lt.addWidget(QLabel('标题：', self.title_widget))
        self.title_edit = QLineEdit(self.title_widget)
        self.title_edit.setPlaceholderText('输入文章的标题')
        title_lt.addWidget(self.title_edit)
        create_lt.addWidget(self.title_widget)

        # pdf文件选择
        self.pdf_widget = QWidget(self)
        pdf_lt = QHBoxLayout(self.pdf_widget)
        self.pdf_widget.setLayout(pdf_lt)
        self.pdf_label = QLabel('PDF：', self.pdf_widget)
        pdf_lt.addWidget(self.pdf_label)

        self.pdf_file_edit = FilePathLineEdit(self.pdf_widget)
        pdf_lt.addWidget(self.pdf_file_edit)

        pdf_lt.addStretch()
        create_lt.addWidget(self.pdf_widget)

        # 网址录入
        self.url_widget = QWidget(self)
        url_lt = QHBoxLayout(self.url_widget)
        self.url_widget.setLayout(url_lt)
        self.url_label = QLabel('网址：', self.url_widget)
        url_lt.addWidget(self.url_label)

        self.url_edit = QLineEdit(self)
        self.url_edit.setPlaceholderText('PDF文件和网址仅选择的会生效')
        url_lt.addWidget(self.url_edit)
        create_lt.addWidget(self.url_widget)
        url_lt.addStretch()

        # 确定添加
        self.push_article = QPushButton('确定添加', self)
        self.push_article.clicked.connect(self.create_body_data)
        create_lt.addWidget(self.push_article, alignment=Qt.AlignLeft)

        create_lt.addStretch()

        self.url_label.hide()
        self.url_edit.hide()

        self.network_manager = getattr(qApp, '_network')

        self.get_article_thread = GetAnalysisArticle(self)
        self.get_article_thread.article_reply.connect(self.get_article_reply)
        self.get_article_thread.start()

        self.variety_api = VarietyAPI(self)
        self.variety_api.varieties_sorted.connect(self.variety_reply)
        self.variety_api.get_variety_en_sorted()

        self.relative_variety = []

    def pdf_toggled(self, f):
        self.pdf_label.setVisible(f)
        self.pdf_file_edit.setVisible(f)

    def web_toggled(self, f):
        self.url_label.setVisible(f)
        self.url_edit.setVisible(f)

    def selected_variety_changed(self):
        v = self.variety_combobox.currentData()
        if v in self.relative_variety:
            return
        self.relative_variety.append(v)
        self.selected_variety.setText(','.join(self.relative_variety))

    def clear_variety(self):
        self.relative_variety.clear()
        self.selected_variety.setText('')

    def create_body_data(self):
        title = self.title_edit.text().strip()
        t = 'pdf' if self.pdf_radio.isChecked() else 'web'
        file_url = self.pdf_file_edit.text().strip()
        web_url = self.url_edit.text().strip()
        if not title or (not file_url and not web_url):
            return
        if web_url and not web_url.startswith('http'):
            p = InformationPopup('请输入正确的链接地址', self)
            p.exec_()
            return
        if len(self.relative_variety) < 1:
            p = InformationPopup('请选择品种', self)
            p.exec_()
            return
        self.push_article.setEnabled(False)

        file_dict = {}
        if t == 'pdf':
            # 文件信息
            file = QFile(file_url)
            file.open(QFile.ReadOnly)
            file_dict = {"file": file}
        # 其他信息
        text_dict = {
            'create_time': self.create_time.text(),
            'title': title,
            'web_url': web_url,
            'variety': ','.join(self.relative_variety)
        }
        multipart_data = generate_multipart_data(text_dict, file_dict)
        url = SERVER_API + 'article/analysis/'
        request = QNetworkRequest(QUrl(url))
        request.setRawHeader("Authorization".encode("utf-8"), get_user_token(raw=True).encode("utf-8"))
        reply = self.network_manager.post(request, multipart_data)
        reply.finished.connect(self.create_article_reply)
        multipart_data.setParent(reply)

    def create_article_reply(self):
        self.push_article.setEnabled(True)
        reply = self.sender()
        if reply.error():
            pop = InformationPopup('添加失败!', self)
        else:
            pop = InformationPopup('添加成功!', self)
        pop.exec_()
        reply.deleteLater()

    def variety_reply(self, data):
        self.variety_combobox.clear()
        for variety_item in data.get('varieties', []):
            self.variety_combobox.addItem(variety_item['variety_name'], variety_item['variety_en'])

    def get_article_reply(self, data):
        self.paginator.setTotalPages(data['total_page'])
        self.paginator.setCurrentPage(data['page'])

        articles = data.get('articles', [])
        self.article_table.clear()
        self.article_table.setRowCount(len(articles))
        col_keys = ['varieties', 'title', 'create_date']
        self.article_table.setColumnCount(len(col_keys))
        self.article_table.setHorizontalHeaderLabels(['品种', '标题', '创建日期'])
        for row, row_item in enumerate(articles):
            for col, k in enumerate(col_keys):
                item = QTableWidgetItem(str(row_item[k]))
                if col == 0:
                    item.setData(Qt.UserRole, row_item)
                self.article_table.setItem(row, col, item)
