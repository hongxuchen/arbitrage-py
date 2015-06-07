#!/usr/bin/env python

from __future__ import print_function
import sys

from PySide import QtGui

from bitbays import BitBays
import common
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

    def _fill_table(self, row, col, text):
        item = QtGui.QTableWidgetItem(str(text))
        item.setTextAlignment(2)
        self.asset_okc_table.setItem(row, col, item)

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

    def display_ask_bid(self):
        length = 5
        depth = self.okc.depth()
        assert (len(depth) == length * 2)
        for i in range(len(depth)):
            price = QtGui.QTableWidgetItem(str(depth[i][0]))
            amount = QtGui.QTableWidgetItem(str(depth[i][1]))
            self.okc_ask_bid_table.setItem(i, 0, price)
            self.okc_ask_bid_table.setItem(i, 1, amount)


    def update_info(self):
        self.display_asset()
        self.display_ask_bid()

    def setup_actions(self):
        for checkbox in self.plt_groupbox.findChildren(QtGui.QCheckBox):
            checkbox.stateChanged.connect(self._set_plt)
        self.trade_button.pressed.connect(self.update_info)

    def display_asset(self):
        funds = self.okc.get_funds()
        pending = funds['freezed']
        available = funds['free']
        sum = funds['asset']
        for res in pending, available:
            for k in res:
                res[k] = common.to_decimal(res[k])
        self._fill_table(0, 0, pending['cny'])
        self._fill_table(1, 0, pending['btc'])
        self._fill_table(2, 0, pending['ltc'])
        self._fill_table(0, 1, available['cny'])
        self._fill_table(1, 1, available['btc'])
        self._fill_table(2, 1, available['ltc'])
        self._fill_table(0, 2, pending['cny'] + available['cny'])
        self._fill_table(1, 2, pending['btc'] + available['btc'])
        self._fill_table(2, 2, pending['ltc'] + available['ltc'])


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    widget = ArbitrageUI()
    widget.move(centerized(widget))
    widget.show()
    # widget.display_asset()
    sys.exit(app.exec_())
