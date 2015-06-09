#!/usr/bin/env python
import sys

from PySide import QtGui

from bitbays import BitBays
from okcoin import OKCoinCN
from ui_common import centerized


class AskBidTable(QtGui.QTableWidget):
    def __init__(self, plt_api_list, length, parent=None):
        super(AskBidTable, self).__init__(parent)
        self.setRowCount(length * 2)
        plt_num = len(plt_api_list)
        self.setColumnCount(plt_num * 2)
        for i in range(length):
            item_str = 'ask' + str(length - i)
            item = QtGui.QTableWidgetItem(item_str)
            self.setVerticalHeaderItem(i, item)
        for i in range(length, 2 * length):
            item_str = 'bid' + str(i - length + 1)
            item = QtGui.QTableWidgetItem(item_str)
            self.setVerticalHeaderItem(i, item)
        for i in range(plt_num):
            price_item = QtGui.QTableWidgetItem('price ' + str(i + 1))
            self.setHorizontalHeaderItem(2 * i, price_item)
            amount_item = QtGui.QTableWidgetItem('amount ' + str(i + 1))
            self.setHorizontalHeaderItem(2 * i + 1, amount_item)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    api_list = [OKCoinCN(), BitBays()]
    widget = AskBidTable(api_list)
    widget.move(centerized(widget))
    widget.show()
    sys.exit(app.exec_())
