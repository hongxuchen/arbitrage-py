#!/usr/bin/env python
import sys

from PySide import QtGui

from asset_info import AssetInfo

from bitbays import BitBays
from okcoin import OKCoinCN
import ui_asset_table
from ui_common import centerized


class AssetWidget(QtGui.QWidget):
    def __init__(self, enabled_plt):
        super(AssetWidget, self).__init__()
        layout = QtGui.QVBoxLayout()
        policy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.setSizePolicy(policy)
        self.asset_table_list = []
        plt_names = [plt.__class__.__name__ for plt in enabled_plt]
        all_names = plt_names + ['Total']
        for name in all_names:
            gp = QtGui.QGroupBox()
            tbl = ui_asset_table.AssetTable()
            self.asset_table_list.append(tbl)
            tbl_layout = QtGui.QVBoxLayout()
            tbl_layout.addWidget(tbl)
            gp.setLayout(tbl_layout)
            gp.setTitle(name)
            layout.addWidget(gp)
        self.setLayout(layout)

    def display_asset(self, asset_info_list):
        asset_raw_list_list = []
        # zip len is smaller of the two
        for tbl, asset_info in zip(self.asset_table_list, asset_info_list):
            asset_raw = asset_info.asset_raw_list
            tbl.display_asset(asset_raw)
            asset_raw_list_list.append(asset_raw)
        sum_tbl_index = len(self.asset_table_list) - 1
        sum_asset_tbl = self.asset_table_list[sum_tbl_index]
        sum_asset_raw = []
        for i in range(len(asset_raw_list_list[0])):
            sum_asset_instance = []
            for j in range(len(asset_raw_list_list[0][0])):
                sum_asset_instance.append(asset_raw_list_list[0][i][j] + asset_raw_list_list[1][i][j])
            sum_asset_raw.append(sum_asset_instance)
        sum_asset_tbl.display_asset(sum_asset_raw)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    plt_list = [OKCoinCN(), BitBays()]
    asset_list = [AssetInfo(plt) for plt in plt_list]
    asset_gp = AssetWidget(plt_list)
    asset_gp.move(centerized(asset_gp))
    asset_gp.show()
    asset_gp.display_asset(asset_list)
    sys.exit(app.exec_())
