# _*_ coding:utf-8 _*_
# ---------------------------
# Python_Version 3.6.3
# Author: zizle
# Created: 2020-05-18
# ---------------------------

import fitz
import chardet
import requests
from PyQt5.QtWidgets import qApp, QWidget, QLabel, QFrame, QScrollArea,QVBoxLayout, QDialog, QScrollBar, QDesktopWidget, QGraphicsDropShadowEffect
from PyQt5.QtGui import QPixmap, QIcon, QImage, QPalette, QColor
from PyQt5.QtCore import Qt, QMargins, QUrl, pyqtSignal
from PyQt5.QtNetwork import QNetworkRequest
from popup.message import InformationPopup
from utils.constant import HORIZONTAL_SCROLL_STYLE, VERTICAL_SCROLL_STYLE


# PDF文件内容直显
class PDFContentShower(QScrollArea):
    def __init__(self, file, *args, **kwargs):
        super(PDFContentShower, self).__init__(*args, **kwargs)
        self.file = file
        # auth doc type
        # scroll
        # self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        # content
        self.page_container = QWidget(self)
        self.page_container.setLayout(QVBoxLayout(self))
        self.page_container.setObjectName('pageContainer')
        # initial data
        self.add_pages()
        # add to show
        self.setWidget(self.page_container)

        # 设置滚动条样式
        with open("media/ScrollBar.qss", "rb") as fp:
            content = fp.read()
            encoding = chardet.detect(content) or {}
            content = content.decode(encoding.get("encoding") or "utf-8")
        self.setStyleSheet(content + 'QScrollArea{border:none;}')

    def add_pages(self):
        # 请求文件
        if not self.file:
            message_label = QLabel('没有文件.')
            self.page_container.layout().addWidget(message_label)
            return
        try:
            response = requests.get(self.file)
            doc = fitz.Document(filename='a', stream=response.content)
        except Exception as e:
            message_label = QLabel('获取文件内容失败.\n{}'.format(e))
            self.page_container.layout().addWidget(message_label)
            return
        for page_index in range(doc.pageCount):
            page = doc.loadPage(page_index)
            page_label = QLabel()
            # page_label.setMinimumSize(self.width() - 20, self.height())  # 设置label大小
            # show PDF content
            zoom_matrix = fitz.Matrix(1.5, 1.5)  # 图像缩放比例
            pagePixmap = page.getPixmap(
                matrix=zoom_matrix,
                alpha=False)
            imageFormat = QImage.Format_RGB888  # get image format
            pageQImage = QImage(
                pagePixmap.samples,
                pagePixmap.width,
                pagePixmap.height,
                pagePixmap.stride,
                imageFormat)  # init QImage
            page_map = QPixmap()
            page_map.convertFromImage(pageQImage)
            page_label.setPixmap(page_map)
            page_label.setScaledContents(True)  # pixmap resize with label
            self.page_container.layout().addWidget(page_label)


# 含阴影的pdf页内容显示label
class PageLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super(PageLabel, self).__init__(*args)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setOffset(1, 1)
        shadow.setColor(QColor(150, 150, 150))
        shadow.setBlurRadius(15)
        self.setGraphicsEffect(shadow)


# PDF文件内容弹窗
class PDFContentPopup(QDialog):

    def __init__(self, title, file, *args, **kwargs):
        super(PDFContentPopup, self).__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowFlags(Qt.Dialog)
        self.file = file
        self.file_name = title
        # auth doc type
        self.setWindowTitle(title)
        available_size = QDesktopWidget().availableGeometry()  # 用户的桌面信息,来改变自身窗体大小
        available_width, available_height = available_size.width(), available_size.height()
        self.resize(available_width * 0.7, available_height * 0.72)
        # self.download = QPushButton("下载PDF", self)
        # self.download.setIcon(QIcon('media/download-file.png'))
        self.setWindowIcon(QIcon("media/reader.png"))
        # scroll
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setContentsMargins(QMargins(0, 0, 0, 0))
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # # content
        # self.page_container = QWidget(self)
        # container_layout = QVBoxLayout()  # 页面布局
        # # 计算大小(设置了label范围890-895)
        # container_layout.setContentsMargins(QMargins(10, 10, 10, 10))  # 右边 页面距离10
        # self.page_container.setLayout(container_layout)
        layout = QVBoxLayout()  # 主布局
        layout.setContentsMargins(QMargins(0, 0, 0, 0))

        # add to show
        # scroll_area.setWidget(self.page_container)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.horizontalScrollBar().setStyleSheet(HORIZONTAL_SCROLL_STYLE)
        self.scroll_area.verticalScrollBar().setStyleSheet(VERTICAL_SCROLL_STYLE)
        # self.scroll_area.verticalScrollBar().hide()
        # add layout
        # layout.addWidget(self.download, alignment=Qt.AlignLeft)
        self.scroll_area.setFixedWidth(925)  # 固定宽度保持居中，且显示清晰
        layout.addWidget(self.scroll_area, alignment=Qt.AlignHCenter)
        self.scroll_bar = QScrollBar(Qt.Vertical, self)
        self.scroll_bar.setStyleSheet(VERTICAL_SCROLL_STYLE)
        self.scroll_bar.setMaximumWidth(10)
        self.setLayout(layout)
        # initial data
        self.add_pages()
        self.scroll_bar.valueChanged.connect(self.scroll_value_changed)  # 自定义的变化随之原滚动变化
        self.scroll_area.verticalScrollBar().valueChanged.connect(self.custom_scroller)  # 原滚动变化带动自定义的变化
        self.setObjectName("pdfPopup")
        self.scroll_area.setStyleSheet("scrollArea")
        self.setStyleSheet(
            "#pdfPopup,#pageContainer{background-color:rgb(230,230,230)}"
            "#scrollArea{background-color:rgb(150,20,230)}"
        )

    def resizeEvent(self, event):
        self.scroll_bar.setMinimumHeight(self.height())
        self.scroll_bar.move(self.width() - 10, 0)

    def scroll_value_changed(self, value):
        self.scroll_area.verticalScrollBar().setValue(value)

    def custom_scroller(self, value):
        self.scroll_bar.setValue(value)

    def add_pages(self):
        # 请求文件
        if not self.file:
            p = InformationPopup('请传入文件资源网络路径', self)
            p.exec_()
            return
        # 异步获取文件内容
        network_manager = getattr(qApp, "_network")
        reply = network_manager.get(QNetworkRequest(QUrl(self.file)))
        reply.finished.connect(self.add_paf_pages)

    def add_paf_pages(self):
        page_container = QWidget(self)   # 页面容器
        page_container.setObjectName("pageContainer")
        container_layout = QVBoxLayout()
        # container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(15)
        container_layout.setAlignment(Qt.AlignHCenter)
        reply = self.sender()
        if reply.error():
            p = InformationPopup('获取文件内容失败：{}'.format(reply.error()), self)
            p.exec_()
            return
        else:
            content = reply.readAll().data()
            doc = fitz.Document(filename=self.file_name, stream=content)
        reply.deleteLater()
        for page_index in range(doc.pageCount):
            page = doc.loadPage(page_index)
            page_label = PageLabel(self)
            # 设置label大小:宽-左侧距离10-右侧距离10-右侧滚东条10
            # show PDF content
            zoom_matrix = fitz.Matrix(1.5, 1.5)  # 图像缩放比例 (893-894)
            pagePixmap = page.getPixmap(
                matrix=zoom_matrix,
                alpha=False)
            if pagePixmap.width >= 895:
                page_label.setFixedWidth(895)
            elif pagePixmap.width < 890:
                page_label.setFixedWidth(890)
            else:
                page_label.setFixedWidth(pagePixmap.width)  # 只有设置这个宽度才会清晰
            image_format = QImage.Format_RGB888  # get image format
            page_image = QImage(
                pagePixmap.samples,
                pagePixmap.width,
                pagePixmap.height,
                pagePixmap.stride,
                image_format)  # init QImage
            page_map = QPixmap()
            page_map.convertFromImage(page_image)
            page_label.setPixmap(page_map)
            page_label.setScaledContents(True)  # pixmap resize with label
            container_layout.addWidget(page_label)
        doc.close()
        page_container.setLayout(container_layout)
        self.scroll_area.setWidget(page_container)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_bar.setMinimum(self.scroll_area.verticalScrollBar().minimum())
        self.scroll_bar.setMaximum(self.scroll_area.verticalScrollBar().maximum())
        self.scroll_bar.setPageStep(self.scroll_area.verticalScrollBar().pageStep())


# PDF文件内容直接显示
class PDFContentWidget(QWidget):
    file_loaded = pyqtSignal(bool)

    def __init__(self, title, file, *args, **kwargs):
        super(PDFContentWidget, self).__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowFlags(Qt.Dialog)
        self.file = file
        self.file_name = title
        # auth doc type
        self.setWindowTitle(title)
        available_size = QDesktopWidget().availableGeometry()  # 用户的桌面信息,来改变自身窗体大小
        available_width, available_height = available_size.width(), available_size.height()
        self.resize(available_width * 0.7, available_height * 0.72)
        # self.download = QPushButton("下载PDF", self)
        # self.download.setIcon(QIcon('media/download-file.png'))
        self.setWindowIcon(QIcon("media/reader.png"))
        # scroll
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setContentsMargins(QMargins(0, 0, 0, 0))
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # # content
        # self.page_container = QWidget(self)
        # container_layout = QVBoxLayout()  # 页面布局
        # # 计算大小(设置了label范围890-895)
        # container_layout.setContentsMargins(QMargins(10, 10, 10, 10))  # 右边 页面距离10
        # self.page_container.setLayout(container_layout)
        layout = QVBoxLayout()  # 主布局
        layout.setContentsMargins(QMargins(0, 0, 0, 0))

        # add to show
        # scroll_area.setWidget(self.page_container)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.horizontalScrollBar().setStyleSheet(HORIZONTAL_SCROLL_STYLE)
        self.scroll_area.verticalScrollBar().setStyleSheet(VERTICAL_SCROLL_STYLE)
        # self.scroll_area.verticalScrollBar().hide()
        # add layout
        # layout.addWidget(self.download, alignment=Qt.AlignLeft)
        self.scroll_area.setFixedWidth(925)  # 固定宽度保持居中，且显示清晰
        layout.addWidget(self.scroll_area, alignment=Qt.AlignHCenter)
        self.scroll_bar = QScrollBar(Qt.Vertical, self)
        self.scroll_bar.setStyleSheet(VERTICAL_SCROLL_STYLE)
        self.scroll_bar.setMaximumWidth(10)
        self.setLayout(layout)
        # initial data
        self.add_pages()
        self.scroll_bar.valueChanged.connect(self.scroll_value_changed)  # 自定义的变化随之原滚动变化
        self.scroll_area.verticalScrollBar().valueChanged.connect(self.custom_scroller)  # 原滚动变化带动自定义的变化
        self.setObjectName("pdfPopup")
        self.scroll_area.setStyleSheet("scrollArea")
        self.setStyleSheet(
            "#pdfPopup,#pageContainer{background-color:rgb(255,255,255)}"
            "#scrollArea{background-color:rgb(255,255,255)}"
        )

        self.error_message = '获取文件内容失败了!'

    def resizeEvent(self, event):
        self.scroll_bar.setMinimumHeight(self.height())
        self.scroll_bar.move(self.width() - 10, 0)

    def scroll_value_changed(self, value):
        self.scroll_area.verticalScrollBar().setValue(value)

    def custom_scroller(self, value):
        self.scroll_bar.setValue(value)

    def add_pages(self):
        # 请求文件
        if not self.file:
            self.clear()
            return
        # 异步获取文件内容
        network_manager = getattr(qApp, "_network")
        reply = network_manager.get(QNetworkRequest(QUrl(self.file)))
        reply.finished.connect(self.add_pdf_pages)

    def add_pdf_pages(self):
        page_container = QWidget(self)   # 页面容器
        page_container.setObjectName("pageContainer")
        container_layout = QVBoxLayout()
        # container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(15)
        container_layout.setAlignment(Qt.AlignHCenter)
        reply = self.sender()
        if reply.error():
            error_label = QLabel(self.error_message, self)
            error_label.setAlignment(Qt.AlignCenter)
            self.scroll_area.setWidget(error_label)
            self.scroll_area.setWidgetResizable(True)
            self.scroll_bar.hide()
            self.file_loaded.emit(False)
            return
        else:
            content = reply.readAll().data()
            doc = fitz.Document(filename=self.file_name, stream=content)
        reply.deleteLater()
        for page_index in range(doc.pageCount):
            page = doc.loadPage(page_index)
            page_label = PageLabel(self)
            # 设置label大小:宽-左侧距离10-右侧距离10-右侧滚东条10
            # show PDF content
            zoom_matrix = fitz.Matrix(1.5, 1.5)  # 图像缩放比例 (893-894)
            pagePixmap = page.getPixmap(
                matrix=zoom_matrix,
                alpha=False)
            if pagePixmap.width >= 895:
                page_label.setFixedWidth(895)
            elif pagePixmap.width < 890:
                page_label.setFixedWidth(890)
            else:
                page_label.setFixedWidth(pagePixmap.width)  # 只有设置这个宽度才会清晰
            image_format = QImage.Format_RGB888  # get image format
            page_image = QImage(
                pagePixmap.samples,
                pagePixmap.width,
                pagePixmap.height,
                pagePixmap.stride,
                image_format)  # init QImage
            page_map = QPixmap()
            page_map.convertFromImage(page_image)
            page_label.setPixmap(page_map)
            page_label.setScaledContents(True)  # pixmap resize with label
            container_layout.addWidget(page_label)
        doc.close()
        page_container.setLayout(container_layout)
        self.scroll_area.setWidget(page_container)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_bar.setMinimum(self.scroll_area.verticalScrollBar().minimum())
        self.scroll_bar.setMaximum(self.scroll_area.verticalScrollBar().maximum())
        self.scroll_bar.setPageStep(self.scroll_area.verticalScrollBar().pageStep())
        self.scroll_bar.show()
        self.file_loaded.emit(True)

    def clear(self):
        self.scroll_area.setWidget(QWidget(self))
        self.scroll_area.setWidgetResizable(True)
        self.scroll_bar.hide()

    def set_file(self, filename, filepath):
        print(filepath)
        self.clear()
        self.file_name = filename
        self.file = filepath
        self.add_pages()

    def set_error_message(self, message):
        self.error_message = message
