#!/usr/bin/env python

from __future__ import print_function
import sys

from PySide import QtGui

import arbitrage_consumer
import arbitrage_producer
import asset_monitor
from bitbays import BitBays
import common
import config
from itbit import ItBitAPI
from okcoin import OKCoinCN
from ui_common import centerized
import ui_main_win
import ui_asset_table
import ui_selections
import ui_settings
from ui_trading_viewer import TradingViewer

select_plt_dict = {
    'OKCoinCN': OKCoinCN,
    'BitBays': BitBays,
    'ItBit': ItBitAPI
}


class ArbitrageUI(ui_main_win.Ui_MainWin):
    def __init__(self, length=5):
        super(ArbitrageUI, self).__init__()
        self.depth_length = length
        self.init_gui()
        self.worklist = []
        self.producer = arbitrage_producer.ArbitrageProducer(self.plt_list, self.worklist, config.fiat)
        self.consumer = arbitrage_consumer.ArbitrageConsumer(self.worklist)
        # self.display_latest_asset()
        self.monitor = asset_monitor.AssetMonitor(self.plt_list)
        self.running = False
        self.setup_actions()

    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'message', 'are you sure to quit?',
                                           QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            if self.running:
                self.stop_trade()
            event.accept()
        else:
            event.ignore()

    def init_gui(self):
        self.setWindowTitle('Arbitrage')
        main_layout = QtGui.QHBoxLayout()
        ### left
        widget1 = QtGui.QWidget()
        layout1 = QtGui.QVBoxLayout()
        available_plt = common.get_key_from_file('Available')
        enabled_plt = common.get_key_from_file('Enabled')
        self.plt_list = [select_plt_dict[plt]() for plt in enabled_plt]
        assert (len(self.plt_list) == 2)
        self.plt_groupbox = ui_selections.SelectGB(available_plt, enabled_plt)
        layout1.addWidget(self.plt_groupbox)
        self.settings_groupbox = ui_settings.SettingGB()
        layout1.addWidget(self.settings_groupbox)
        self.trade_button = QtGui.QPushButton('Arbitrage')
        layout1.addWidget(self.trade_button)
        widget1.setLayout(layout1)
        ### right
        widget2 = QtGui.QWidget()
        layout2 = QtGui.QVBoxLayout()
        self.asset_table_list = []
        for i in range(len(self.plt_list) + 1):
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

    def report_trade(self):
        pass

    def stop_trade(self):
        self.running = False
        self.producer.running = False
        self.producer.wait()
        self.consumer.running = False
        self.consumer.wait()
        self.monitor.running = False
        self.monitor.wait()
        self.trade_button.setText('Arbitrage')

    def start_trade(self):
        self.running = True
        self.producer.running = True
        self.producer.start()
        self.consumer.running = True
        self.consumer.start()
        self.monitor.running = True
        self.monitor.start()
        self.trade_button.setText('Stop')

    def apply_trade(self):
        if not self.running:
            self.start_trade()
        else:
            self.stop_trade()
            self.report_trade()

    def update_plt(self):
        sender = self.sender()
        assert (isinstance(sender, QtGui.QCheckBox))
        assert (not sender.isTristate())
        self.plt[sender.text()] = sender.isChecked()
        # true_list = [k for (k, v) in self.plt.iteritems() if v is True]
        # print(true_list)

    def setup_actions(self):
        for checkbox in self.plt_groupbox.findChildren(QtGui.QCheckBox):
            checkbox.stateChanged.connect(self.update_plt)
        self.trade_button.pressed.connect(self.apply_trade)
        self.producer.notify_asset.connect(self.display_asset_summary)
        self.monitor.notify_update_asset.connect(self.display_asset_summary)
        self.producer.notify_trade.connect(self.display_arbitrage)

    # TODO display nicely
    def display_arbitrage(self, arbitrage_info):
        self.trade_viewer.append(str(arbitrage_info))

    def display_asset_summary(self, asset_info_list):
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
