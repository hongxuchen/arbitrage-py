#!/usr/bin/env python

from __future__ import print_function
import sys

from PySide import QtGui

from arbitrage_thread import ArbitrageWorker
from bitbays import BitBays
import common
from itbit import ItBitAPI
from okcoin import OKCoinCN
from ui_common import centerized
import ui_main_win
import ui_asset_table
import ui_selections
import ui_settings
from ui_trading_viewer import TradingViewer

select_api_dict = {
    'OKCoinCN': OKCoinCN,
    'BitBays': BitBays,
    'ItBit': ItBitAPI
}


class ArbitrageUI(ui_main_win.Ui_MainWin):
    def __init__(self, length=5):
        super(ArbitrageUI, self).__init__()
        self.depth_length = length
        self.init_gui()
        self.arbitrage_worker = ArbitrageWorker(self.plt_api_list, 'cny')
        self.setup_actions()

    def apply_trade(self):
        self.arbitrage_worker.start()

    def init_gui(self):
        main_layout = QtGui.QHBoxLayout()
        ### left
        widget1 = QtGui.QWidget()
        layout1 = QtGui.QVBoxLayout()
        available_plt = common.get_key_from_file('Available')
        enabled_plt = common.get_key_from_file('Enabled')
        self.plt_api_list = [select_api_dict[plt_api]() for plt_api in enabled_plt]
        self.plt_groupbox = ui_selections.SelectGB(available_plt, enabled_plt)
        layout1.addWidget(self.plt_groupbox)
        self.settings_groupbox = ui_settings.SettingGB()
        layout1.addWidget(self.settings_groupbox)
        self.trade_button = QtGui.QPushButton('trade')
        layout1.addWidget(self.trade_button)
        widget1.setLayout(layout1)
        ### middle
        widget2 = QtGui.QWidget()
        layout2 = QtGui.QVBoxLayout()
        self.asset_table_list = []
        for plt_api in self.plt_api_list:
            tbl = ui_asset_table.AssetTable(plt_api)
            self.asset_table_list.append(tbl)
            layout2.addWidget(tbl)
        # self.ask_bid_table = ui_ask_bid_table.AskBidTable(self.plt_api_list, self.depth_length, self)
        # layout2.addWidget(self.ask_bid_table)
        self.trade_viewer = TradingViewer()
        layout2.addWidget(self.trade_viewer)
        # widget2.setMinimumWidth(config.ui_tbl_col_width * 5)
        widget2.setLayout(layout2)
        ### all
        main_layout.addWidget(widget1)
        main_layout.addWidget(widget2)
        # main_layout.addWidget(self.trade_viewer)
        central = QtGui.QWidget()
        central.setLayout(main_layout)
        self.setCentralWidget(central)

    def update_plt(self):
        sender = self.sender()
        assert (isinstance(sender, QtGui.QCheckBox))
        assert (not sender.isTristate())
        # self.plt[sender.text()] = sender.isChecked()
        # true_list = [k for (k, v) in self.plt.iteritems() if v is True]
        # print(true_list)

    def report_abitrage(self):
        pass

    def start_abitrage(self):
        pass

    def stop_abitrage(self):
        self.report_abitrage()

    def update_info(self):
        pass
        # self.display_asset()
        # self.display_ask_bid()

    def setup_actions(self):
        for checkbox in self.plt_groupbox.findChildren(QtGui.QCheckBox):
            checkbox.stateChanged.connect(self.update_plt)
        self.trade_button.pressed.connect(self.apply_trade)
        self.arbitrage_worker.notify.connect(self.display_trade)

    def display_trade(self, trading_list):
        for trade in trading_list:
            self.trade_viewer.append(str(trade))
        self.trade_viewer.append('\n')

    # TODO distinguish init and update
    def display_ask_bid(self, tbl):
        api_num = len(self.plt_api_list)
        for api_index in range(api_num):
            # rest api
            trade_depth = self.plt_api_list[api_index].depth(self.depth_length)
            for ask_bid_index in range(self.depth_length * 2):
                price = QtGui.QTableWidgetItem(str(trade_depth[ask_bid_index][0]))
                tbl.setItem(ask_bid_index, 2 * api_index, price)
                amount = QtGui.QTableWidgetItem(str(trade_depth[ask_bid_index][1]))
                tbl.setItem(ask_bid_index, 2 * api_index + 1, amount)

    def display_asset(self):
        for tbl in self.asset_table_list:
            tbl.display()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    widget = ArbitrageUI(2)
    widget.move(centerized(widget))
    widget.show()
    sys.exit(app.exec_())
