#!/usr/bin/env python

from __future__ import print_function
import sys

from PySide import QtGui

from bitbays import BitBays
import common
from itbit import ItBitAPI
from okcoin import OKCoinCN
from ui_common import centerized
import ui_main_win
import ui_ask_bid_table
import ui_asset_table
import ui_selections
import ui_settings

select_api_dict = {
    'OKCoinCN': OKCoinCN,
    'BitBays': BitBays,
    'ItBit': ItBitAPI
}


class ArbitrageUI(QtGui.QMainWindow, ui_main_win.Ui_MainWindow):
    def __init__(self, length=5, parent=None):
        super(ArbitrageUI, self).__init__(parent)
        self.setupUi(self)
        self.depth_length = length
        self.init_gui()
        self.setup_actions()

    def init_gui(self):
        main_layout = QtGui.QHBoxLayout()
        ### left
        gp1 = QtGui.QGroupBox()
        layout1 = QtGui.QVBoxLayout()
        available_plt = common.get_key_from_file('Available')
        enabled_plt = common.get_key_from_file('Enabled')
        self.plt_api_list = [select_api_dict[plt_api]() for plt_api in enabled_plt]
        self.plt_groupbox = ui_selections.SelectGB(available_plt, enabled_plt)
        layout1.addWidget(self.plt_groupbox)
        self.settings_groupbox = ui_settings.SettingGB()
        layout1.addWidget(self.settings_groupbox)
        self.trade_button = QtGui.QPushButton('Start')
        layout1.addWidget(self.trade_button)
        gp1.setLayout(layout1)
        ### right
        gp2 = QtGui.QGroupBox()
        layout2 = QtGui.QVBoxLayout()
        self.asset_table_list = []
        for plt_api in self.plt_api_list:
            tbl = ui_asset_table.AssetTable(plt_api)
            self.asset_table_list.append(tbl)
            layout2.addWidget(tbl)
        self.ask_bid_table = ui_ask_bid_table.AskBidTable(self.plt_api_list, self.depth_length, self)
        layout2.addWidget(self.ask_bid_table)
        gp2.setLayout(layout2)
        ### all
        main_layout.addWidget(gp1)
        main_layout.addWidget(gp2)
        central = QtGui.QWidget()
        central.setLayout(main_layout)
        self.setCentralWidget(central)

    def update_plt(self):
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
        # self.display_asset()
        self.display_ask_bid()

    def setup_actions(self):
        for checkbox in self.plt_groupbox.findChildren(QtGui.QCheckBox):
            checkbox.stateChanged.connect(self.update_plt)
        self.trade_button.pressed.connect(self.update_info)

    #TODO distinguish init and update
    def display_ask_bid(self):
        api_num = len(self.plt_api_list)
        for api_index in range(api_num):
            # rest api
            trade_depth = self.plt_api_list[api_index].depth(self.depth_length)
            for ask_bid_index in range(self.depth_length * 2):
                price = QtGui.QTableWidgetItem(str(trade_depth[ask_bid_index][0]))
                self.ask_bid_table.setItem(ask_bid_index, 2*api_index, price)
                amount = QtGui.QTableWidgetItem(str(trade_depth[ask_bid_index][1]))
                self.ask_bid_table.setItem(ask_bid_index, 2*api_index+1, amount)

    def display_asset(self):
        for tbl in self.asset_table_list:
            tbl.display()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    widget = ArbitrageUI(3)
    widget.move(centerized(widget))
    widget.show()
    # widget.display_asset()
    sys.exit(app.exec_())
