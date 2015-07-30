#!/usr/bin/env python

import sys

from PySide import QtGui

from asset_info import AssetInfo
from okcoin import OKCoinCN
from ui_common import centerized, fill_table


class AssetTable(QtGui.QTableWidget):
    def __init__(self, parent=None):
        super(AssetTable, self).__init__(parent)
        row_list = ['CNY', 'BTC']
        col_list = ['Pending', 'Available', 'Sum']
        len_row_list = len(row_list)
        len_col_list = len(col_list)
        self.setRowCount(len_row_list)
        self.setColumnCount(len_col_list)
        self.setHorizontalHeaderLabels(col_list)
        self.setVerticalHeaderLabels(row_list)

    def display_asset(self, asset_raw_list):
        for i in range(len(asset_raw_list)):
            fill_table(self, i, 0, asset_raw_list[i][0])
            fill_table(self, i, 1, asset_raw_list[i][1])
            fill_table(self, i, 2, asset_raw_list[i][0] + asset_raw_list[i][1])


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    plt = OKCoinCN()
    widget = AssetTable()
    asset_info = AssetInfo(plt)
    widget.move(centerized(widget))
    widget.show()
    widget.display_asset(asset_info.asset_raw_list)
    sys.exit(app.exec_())
