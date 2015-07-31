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
from ui_asset_widget import AssetWidget
from ui_common import centerized
import ui_main_win
import ui_selections
from ui_trading_viewer import TradingViewer

select_plt_dict = {
    'OKCoinCN': OKCoinCN,
    'BitBays': BitBays,
    'ItBit': ItBitAPI
}


class ArbitrageUI(ui_main_win.Ui_MainWin):
    _logger = common.get_logger()

    def __init__(self):
        super(ArbitrageUI, self).__init__()
        common.init_logger()
        self.init_gui()
        self.worklist = []
        self.producer = arbitrage_producer.ArbitrageProducer(self.plt_list, self.worklist, config.fiat)
        self.consumer = arbitrage_consumer.ArbitrageConsumer(self.worklist)
        self.monitor = asset_monitor.AssetMonitor(self.plt_list)
        self.running = False
        self.setup_actions()

    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'message', 'Really quit?',
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
        available_plt = common.get_key_from_data('Available')
        enabled_plt = common.get_key_from_data('Enabled')
        self.plt_list = [select_plt_dict[plt]() for plt in enabled_plt]
        assert (len(self.plt_list) == 2)
        self.plt_groupbox = ui_selections.SelectGB(available_plt, enabled_plt)
        layout1.addWidget(self.plt_groupbox)
        # self.settings_groupbox = ui_settings.SettingGB()
        # layout1.addWidget(self.settings_groupbox)
        self.trade_button = QtGui.QPushButton('Arbitrage')
        layout1.addWidget(self.trade_button)
        widget1.setLayout(layout1)
        ### right
        widget2 = QtGui.QWidget()
        layout2 = QtGui.QVBoxLayout()
        self.asset_widget = AssetWidget(self.plt_list)
        layout2.addWidget(self.asset_widget)
        self.trade_viewer = TradingViewer()
        layout2.addWidget(self.trade_viewer)
        widget2.setLayout(layout2)
        ### all
        main_layout.addWidget(widget1)
        main_layout.addWidget(widget2)
        central = QtGui.QWidget()
        central.setLayout(main_layout)
        self.setCentralWidget(central)

    def stop_trade(self):
        self.running = False
        ArbitrageUI._logger.info('waiting producer')
        self.producer.running = False
        self.producer.wait()
        ArbitrageUI._logger.info('waiting consumer')
        self.consumer.running = False
        self.consumer.wait()
        ArbitrageUI._logger.info('waiting monitor')
        self.monitor.running = False
        self.monitor.wait()
        self.trade_button.setText('Arbitrage')

    def start_trade(self):
        # requests.packages.urllib3.disable_warnings()
        self.running = True
        ArbitrageUI._logger.info('start producer')
        self.producer.running = True
        self.producer.start()
        ArbitrageUI._logger.info('start consumer')
        self.consumer.running = True
        self.consumer.start()
        ArbitrageUI._logger.info('start monitor')
        self.monitor.running = True
        self.monitor.start()
        self.trade_button.setText('Stop')

    def apply_trade(self):
        if not self.running:
            self.start_trade()
        else:
            self.stop_trade()

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
        self.monitor.notify_update_asset.connect(self.display_asset)
        self.producer.notify_trade.connect(self.log_arbitrage)
        self.monitor.notify_asset_change.connect(self.log_asset_change)

    def log_arbitrage(self, arbitrage_info):
        self.trade_viewer.append(str(arbitrage_info))

    def log_asset_change(self, asset_report):
        self.trade_viewer.append(asset_report)

    def display_asset(self, asset_info_list):
        self.asset_widget.display_asset(asset_info_list)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    widget = ArbitrageUI()
    widget.move(centerized(widget))
    widget.show()
    sys.exit(app.exec_())
