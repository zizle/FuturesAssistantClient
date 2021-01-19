# _*_ coding:utf-8 _*_
# @File  : rich_edit.py
# @Time  : 2021-01-19 10:00
# @Author: zizle

from PyQt5.QtWidgets import (QMainWindow, QTextEdit, QToolBar, QPushButton, QComboBox,
                             QFontComboBox, QColorDialog, QMenu, )
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QBrush, QColor, QIcon, QPixmap, QPalette, QTextCharFormat, QTextCursor


class RichTextEdit(QMainWindow):
    """ 富文本编辑控件 """
    # 字体大小字典
    FONT_SIZE = {
        '42.0': '初号', '36.0': '小初',
        '26.0': '一号', '24.0': '小一',
        '22.0': '二号', '18.0': '小二',
        '16.0': '三号', '15.0': '小三',
        '14.0': '四号', '12.0': '小四',
        '10.5': '五号', '9.0': '小五',
        '7.5': '六号', '6.5': '小六',
        '5.5': '七号', '5': '八号',
        '8': '8', '9': '9',
        '10': '10', '11': '11',
        '12': '12', '14': '14',
        '16': '16', '18': '18',
        '20': '20', '22': '22',
        '24': '24', '26': '26',
        '28': '28', '36': '36',
        '48': '48', '72': '72',
    }

    def __init__(self, *args, **kwargs):
        super(RichTextEdit, self).__init__(*args, **kwargs)
        self.current_font_size = 10.5   # 默认字体大小(小五)
        self.current_font_family = 'Arial'  # 默认字体
        self.recently_font_color = ['#000000', '#C00000', '#FFC000', '#FFFF00', '#92D050']   # 最近使用的字体颜色
        self.recently_font_bg_color = ['#FFFFFF', '#C00000', '#FFC000', '#FFFF00', '#92D050']         # 最近使用的字体背景色

        """ 工具栏 """
        self.tool_bar = QToolBar(self)
        self.tool_bar.setMovable(False)
        first_separator = self.tool_bar.addSeparator()
        # 加粗
        self.font_bold_action = self.tool_bar.addAction(QIcon(QIcon('media/rich_text/bold.png')), '')
        self.font_bold_action.triggered.connect(self.change_font_bold)
        # 斜体
        self.font_italic_action = self.tool_bar.addAction(QIcon('media/rich_text/italic.png'), '')
        self.font_italic_action.triggered.connect(self.change_font_italic)
        # 下划线
        self.font_underline_action = self.tool_bar.addAction(QIcon('media/rich_text/underline.png'), '')
        self.font_underline_action.triggered.connect(self.change_font_underline)
        # 左对齐
        self.left_action = self.tool_bar.addAction(QIcon('media/rich_text/left.png'), '')
        self.left_action.triggered.connect(lambda: self.change_row_alignment('left'))
        # 中间对齐
        self.center_action = self.tool_bar.addAction(QIcon('media/rich_text/center.png'), '')
        self.center_action.triggered.connect(lambda: self.change_row_alignment('center'))
        # 右对齐
        self.right_action = self.tool_bar.addAction(QIcon('media/rich_text/right.png'), '')
        self.right_action.triggered.connect(lambda: self.change_row_alignment('right'))
        # # 两边对齐
        # self.left_right_action = self.tool_bar.addAction(QIcon('icons/left_right.png'), '')
        # self.left_right_action.triggered.connect(lambda: self.change_row_alignment('left_right'))

        # 字体选择
        self.font_selector = QFontComboBox(self)
        self.font_selector.setMaximumWidth(60)
        self.tool_bar.insertWidget(first_separator, self.font_selector)
        # 字体大小选择
        self.font_size_selector = QComboBox(self)
        [self.font_size_selector.addItem(self.FONT_SIZE[key], key) for key in self.FONT_SIZE.keys()]  # 添加选项
        self.font_size_selector.setCurrentText('五号')  # 默认五号
        self.font_size_selector.currentIndexChanged.connect(self.change_font_size)  # 字体选择信号
        self.tool_bar.insertWidget(first_separator, self.font_size_selector)
        # 字体颜色控制
        self.font_color_selector = QPushButton('A', self)
        self.font_color_selector.setToolTip('字体颜色')
        self.font_color_selector.setFixedSize(30, 21)
        self.update_recently_colors(color_type='font_color')

        self.tool_bar.insertWidget(first_separator, self.font_color_selector)
        # 字体背景色控制
        self.font_bg_color_selector = QPushButton('A', self)
        self.font_bg_color_selector.setToolTip('字体背景色')
        self.font_bg_color_selector.setFixedSize(30, 21)
        self.update_recently_colors(color_type='font_bg_color')
        self.tool_bar.insertWidget(first_separator, self.font_bg_color_selector)

        self.addToolBar(Qt.TopToolBarArea, self.tool_bar)

        # 编辑框
        self.text_edit = QTextEdit(self)
        self.setCentralWidget(self.text_edit)

        self.tool_bar.setObjectName('toolBar')
        self.setStyleSheet(
            "#toolBar{spacing:2px}"
        )
        # 设置初始字体和大小
        init_font = QFont()
        init_font.setPointSize(self.current_font_size)
        init_font.setFamily(self.current_font_family)
        self.text_edit.setFont(init_font)
        # 字体选择改变的信号
        self.font_selector.activated.connect(self.change_font)

    def update_recently_colors(self, color_type):
        """ 更新最近使用颜色 """
        if color_type == 'font_color':
            # 更新最近使用字体色
            colors = self.recently_font_color
            color_button = self.font_color_selector
            button_style = 'border:1px solid rgb(220,220,220);'
            if colors:
                button_style = 'border:1px solid rgb(220,220,220);color:{}'.format(colors[0])
        elif color_type == 'font_bg_color':
            # 更新最近使用字体背景色
            colors = self.recently_font_bg_color
            color_button = self.font_bg_color_selector
            button_style = 'border:1px solid rgb(220,220,220);'
            if colors:
                button_style = 'border:1px solid rgb(220,220,220);background-color:{}'.format(colors[0])
        else:
            return
        old_menu = color_button.menu()
        if old_menu:
            old_menu.deleteLater()  # 删除原按钮
        menu = QMenu()
        for color_item in colors:
            pix = QPixmap('media/rich_text/color_icon.png')
            # bitmap = pix.createMaskFromColor(QColor(210,120,100))
            pix.fill(QColor(color_item))
            # pix.setMask(bitmap)
            ico = QIcon(pix)
            action = menu.addAction(ico, color_item)
            action.triggered.connect(lambda: self.change_current_color(color_type))
        # 添加更多选项
        more_action = menu.addAction(QIcon('media/rich_text/more.png'), '更多颜色')
        more_action.triggered.connect(lambda: self.select_more_color(color_type))
        color_button.setStyleSheet(button_style)
        color_button.setMenu(menu)

    def select_more_color(self, color_type):
        """ 选择更多的颜色 """
        color = QColorDialog.getColor(parent=self, title='选择颜色')  # 不选默认为黑色
        color_str = color.name()
        # 改变对应颜色情况
        self.set_current_color(color_str.upper(), color_type)

    def change_current_color(self, color_type):
        """ 改变当前字体或字体背景的颜色 """
        action = self.sender()
        color = action.text()
        self.set_current_color(color, color_type)

    def set_current_color(self, color, color_type):

        if color_type == 'font_color':
            colors = self.recently_font_color
        elif color_type == 'font_bg_color':
            colors = self.recently_font_bg_color
        else:
            return
        if color in colors:
            color_index = colors.index(color)
            colors.insert(0, colors.pop(color_index))  # 将颜色插入到起始
        else:
            # 将颜色第一个替换掉
            colors[0] = color
        # 更新当前颜色
        self.update_recently_colors(color_type)

        if color_type == 'font_color':
            # 改变字体颜色
            self.change_font_color(colors[0])
        if color_type == 'font_bg_color':
            # 改变字体背景颜色
            self.change_font_bg_color(colors[0])

    def update_font(self):
        """ 改变字体 """
        current_font = QFont()
        current_font.setFamily(self.current_font_family)
        current_font.setPointSize(self.current_font_size)
        tc = self.text_edit.textCursor()
        font_format = self.text_edit.currentCharFormat()
        font_format.setFont(current_font)
        tc.mergeCharFormat(font_format)

    def change_font(self, index):
        """ 字体选择改变 """
        self.current_font_family = self.font_selector.currentFont().family()
        self.update_font()

    def change_font_size(self):
        """ 字体大小选择信号 """
        self.current_font_size = float(self.font_size_selector.currentData())
        self.update_font()

    def change_font_color(self, color):
        """ 改变字体颜色 """
        tc = self.text_edit.textCursor()
        font_format = self.text_edit.currentCharFormat()
        font_format.setForeground(QBrush(QColor(color)))
        tc.mergeCharFormat(font_format)

    def change_font_bg_color(self, color):
        """ 改变字体背景颜色 """
        tc = self.text_edit.textCursor()
        font_format = self.text_edit.currentCharFormat()
        font_format.setBackground(QBrush(QColor(color)))
        tc.mergeCharFormat(font_format)

    def change_font_italic(self):
        """ toggle斜体 """
        tc = self.text_edit.textCursor()
        font_format = self.text_edit.currentCharFormat()
        font_format.setFontItalic(not font_format.fontItalic())
        tc.mergeCharFormat(font_format)

    def change_font_bold(self):
        """ toggle粗体 """
        tc = self.text_edit.textCursor()
        font_format = self.text_edit.currentCharFormat()
        current_font = font_format.font()
        current_font.setBold(not current_font.bold())
        current_font.setFamily(self.current_font_family)
        current_font.setPointSize(self.current_font_size)
        font_format.setFont(current_font)
        tc.mergeCharFormat(font_format)

    def change_font_underline(self):
        """ toggle下划线 """
        tc = self.text_edit.textCursor()
        font_format = self.text_edit.currentCharFormat()
        font_format.setFontUnderline(not font_format.fontUnderline())
        tc.mergeCharFormat(font_format)

    def change_row_alignment(self, alignment: str):
        """ toggle对齐方式 """
        if alignment == 'left':
            self.text_edit.setAlignment(Qt.AlignLeft)
        elif alignment == 'right':
            self.text_edit.setAlignment(Qt.AlignRight)
        elif alignment == 'center':
            self.text_edit.setAlignment(Qt.AlignHCenter)
        # elif alignment == 'left_right':
        #     self.text_edit.setAlignment(Qt.AlignAbsolute)
        else:
            return

    def clear(self):
        self.text_edit.clear()

    def toHtml(self):
        return self.text_edit.toHtml()

    def setHtml(self, html):
        self.text_edit.setHtml(html)


