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
        self.setWindowTitle('Arbitrage')
        self.arbitrage_worker = ArbitrageWorker(self.plt_api_list, 'cny')
        self.setup_actions()

    def apply_trade(self):
        if self.arbitrage_worker.running is False:
            self.arbitrage_worker.running = True
            self.arbitrage_worker.start()
            self.trade_button.setText('stop')
        else:
            self.arbitrage_worker.running = False
            self.arbitrage_worker.quit()
            self.trade_button.setText('Trade')

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
        self.trade_button = QtGui.QPushButton('Trade')
        layout1.addWidget(self.trade_button)
        widget1.setLayout(layout1)
        ### right
        widget2 = QtGui.QWidget()
        layout2 = QtGui.QVBoxLayout()
        self.asset_table_list = []
        for i in range(len(self.plt_api_list) + 1):
            tbl = ui_asset_table.AssetTable()
            self.asset_table_list.append(tbl)
            layout2.addWidget(tbl)
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

    def setup_actions(self):
        for checkbox in self.plt_groupbox.findChildren(QtGui.QCheckBox):
            checkbox.stateChanged.connect(self.update_plt)
        self.trade_button.pressed.connect(self.apply_trade)
        self.arbitrage_worker.notify_trade.connect(self.display_trade)
        self.arbitrage_worker.notify_asset.connect(self.display_asset)

    def display_trade(self, trading_list):
        for trade in trading_list:
            self.trade_viewer.append(str(trade))
        self.trade_viewer.append('\n')

    def display_asset(self, asset_info_list):
        asset_raw_list_list = []
        for tbl, asset_info in zip(self.asset_table_list, asset_info_list):
            asset_raw = asset_info.asset_raw_list
            tbl.display_asset(asset_raw)
            asset_raw_list_list.append(asset_raw)
        sum_asset_tbl = self.asset_table_list[2]
        sum_asset_raw = []
        for i in range(len(asset_raw_list_list[0])):
            sum_asset_instance = []
            for j in range(len(asset_raw_list_list[0][0])):
                sum_asset_instance.append(asset_raw_list_list[0][i][j] + asset_raw_list_list[1][i][j])
            sum_asset_raw.append(sum_asset_instance)
        sum_asset_tbl.display_asset(sum_asset_raw)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    widget = ArbitrageUI(2)
    widget.move(centerized(widget))
    widget.show()
    sys.exit(app.exec_())
