#!/usr/bin/env python

from __future__ import print_function
import sys

from PySide import QtGui

from bitbays import BitBays
from okcoin import OKCoinCN
import ui_arbitrage


def centerized(widget):
    return QtGui.QDesktopWidget().availableGeometry().center() - widget.frameGeometry().center()


class ArbitrageUI(QtGui.QMainWindow, ui_arbitrage.Ui_arbitrage):
    def __init__(self, parent=None):
        super(ArbitrageUI, self).__init__(parent)
        self.setupUi(self)
        self.okc = OKCoinCN()
        self.bb = BitBays()
        self.plt = {}
        self.setup_actions()

    def _fill_table(self, tbl, row, col, text):
        item = QtGui.QTableWidgetItem(str(text))
        item.setTextAlignment(2)
        tbl.setItem(row, col, item)

    def _set_plt(self):
        sender = self.sender()
        assert (isinstance(sender, QtGui.QCheckBox))
        assert (not sender.isTristate())
        self.plt[sender.text()] = sender.isChecked()
        # true_list = [k for (k, v) in self.plt.iteritems() if v is True]
        # print(true_list)

    def report_abitrage(self):
        pass

    def start_abitrage(self):
        pass

    def stop_abitrage(self):
        self.report_abitrage()

    def update_info(self):
        self.display_asset()
        self.display_ask_bid()

    def setup_actions(self):
        for checkbox in self.plt_groupbox.findChildren(QtGui.QCheckBox):
            checkbox.stateChanged.connect(self._set_plt)
        self.trade_button.pressed.connect(self.update_info)

    def display_ask_bid(self):
        length = 5
        okc_depth = self.okc.depth(length)
        assert (len(okc_depth) == length * 2)
        for i in range(len(okc_depth)):
            price = QtGui.QTableWidgetItem(str(okc_depth[i][0]))
            amount = QtGui.QTableWidgetItem(str(okc_depth[i][1]))
            self.ask_bid_table.setItem(i, 0, price)
            self.ask_bid_table.setItem(i, 1, amount)
        bb_depth = self.bb.depth()
        assert (len(bb_depth) == length * 2)
        for i in range(len(bb_depth)):
            price = QtGui.QTableWidgetItem(str(bb_depth[i][0]))
            amount = QtGui.QTableWidgetItem(str(bb_depth[i][1]))
            self.ask_bid_table.setItem(i, 2, price)
            self.ask_bid_table.setItem(i, 3, amount)

    def display_asset(self):
        okc_assets = self.okc.asset_list()
        bb_assets = self.bb.asset_list()
        tbl_asset_list = [
            (self.asset_okc_table, okc_assets),
            (self.asset_bb_table, bb_assets)
        ]
        for tbl, asset in tbl_asset_list:
            for i in range(len(okc_assets)):
                self._fill_table(tbl, i, 0, asset[i][0])
                self._fill_table(tbl, i, 1, asset[i][1])
                self._fill_table(tbl, i, 2, asset[i][0] + asset[i][1])


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    widget = ArbitrageUI()
    widget.move(centerized(widget))
    widget.show()
    # widget.display_asset()
    sys.exit(app.exec_())
