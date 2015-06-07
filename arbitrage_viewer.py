#!/usr/bin/env python

from __future__ import print_function
import sys
from bitbays import BitBays
from okcoin import OKCoinCN
import ui_arbitrage
from PySide import QtGui
import os


def centerized(widget):
    return QtGui.QDesktopWidget().availableGeometry().center() - widget.frameGeometry().center()

class ArbitrageUI(QtGui.QMainWindow, ui_arbitrage.Ui_arbitrage):
    def __init__(self, parent=None):
        super(ArbitrageUI, self).__init__(parent)
        self.setupUi(self)
        self.okc = OKCoinCN()
        self.bb = BitBays()

    def display_asset(self):
        table = self.asset_okc_table
        info = self.okc.userinfo()
        print(info)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    widget = ArbitrageUI()
    widget.move(centerized(widget))
    widget.show()
    widget.display_asset()
    sys.exit(app.exec_())
