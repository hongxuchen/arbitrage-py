# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './main_win.ui'
#
# Created: Mon Jun  8 15:34:13 2015
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui


class Ui_MainWin(QtGui.QMainWindow):
    def __init__(self):
        super(Ui_MainWin, self).__init__()
        self.setObjectName("self")
        self.resize(800, 600)
        self.centralwidget = QtGui.QWidget(self)

        self.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 19))
        self.menubar.setObjectName("menubar")
        self.menuSettings = QtGui.QMenu(self.menubar)

        self.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(self)

        self.setStatusBar(self.statusbar)
        self.menubar.addAction(self.menuSettings.menuAction())
