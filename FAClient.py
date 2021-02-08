# _*_ coding:utf-8 _*_
# ---------------------------
# Python_Version 3.6.3
# Author: zizle
# Created: 2020-05-18
# ---------------------------
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QCoreApplication, Qt
import pandas
from PyQt5.QtWebEngineWidgets import QWebEngineView
from frames import WelcomePage, ClientMainApp

QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)  # 高分辨率DPI屏幕自动缩放

app = QApplication(sys.argv)
font = QFont()
font.setPointSize(11)
font.setFamily('Arial')
font.setStyleStrategy(QFont.PreferAntialias)
app.setFont(font)
splash = WelcomePage()
splash.show()
splash.get_all_advertisement()  # 在此调用才能真正实现同步化
app.processEvents()  # non-blocking
main_app = ClientMainApp()
main_app.show()
splash.finish(main_app)
sys.exit(app.exec_())
