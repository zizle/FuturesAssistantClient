# _*_ coding:utf-8 _*_
# ---------------------------
# Python_Version 3.6.3
# Author: zizle
# Created: 2020-05-18
# ---------------------------
import sys
from os import environ
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QCoreApplication, Qt
import pandas
from PyQt5.QtWebEngineWidgets import QWebEngineView
from frames import WelcomePage, ClientMainApp
from utils.hooks import exception_hook

# 去除警告
# Warning: QT_DEVICE_PIXEL_RATIO is deprecated. Instead use:
#    QT_AUTO_SCREEN_SCALE_FACTOR to enable platform plugin controlled per-screen factors.
#    QT_SCREEN_SCALE_FACTORS to set per-screen factors.
#    QT_SCALE_FACTOR to set the application global scale factor.
environ["QT_DEVICE_PIXEL_RATIO"] = "0"
environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
environ["QT_SCREEN_SCALE_FACTORS"] = "1"
environ["QT_SCALE_FACTOR"] = "1"


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
sys.excepthook = exception_hook
sys.exit(app.exec_())
