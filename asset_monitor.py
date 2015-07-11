#!/usr/bin/env python

from PySide import QtCore

from asset_info import AssetInfo
import common
import config

# TODO ensure that amount of BTC in a limited range; invoked when
# - cancel/trade fails
# - exiting

class AssetMonitor(QtCore.QThread):
    notify_update_asset = QtCore.Signal(list)
    notify_asset_change = QtCore.Signal(str)
    _logger = common.setup_logger()

    def __init__(self, plt_list):
        super(AssetMonitor, self).__init__()
        self.plt_list = plt_list
        self.running = False

    def get_asset_list(self):
        return [AssetInfo(plt) for plt in self.plt_list]

    def asset_change_report(self, original_asset_list):
        asset_list = self.get_asset_list()
        btc, original_btc = 0.0, 0.0
        fiat, original_fiat = 0.0, 0.0
        for asset in asset_list:
            btc += asset.total_btc()
            fiat += asset.total_fiat()
        for original in original_asset_list:
            original_btc += original.total_btc()
            original_fiat += original.total_fiat()
        change_str = 'Asset Change: {:10.4f}btc, {:10.4f}cny'.format(btc - original_btc, fiat - original_fiat)
        AssetMonitor._logger.warning(change_str)
        return change_str

    def run(self, *args, **kwargs):
        original_asset_list = self.get_asset_list()
        self.notify_update_asset.emit(original_asset_list)
        while self.running:
            QtCore.QThread.sleep(config.monitor_interval_seconds)
            AssetMonitor._logger.debug("[Monitor] Notify")
            asset_list = self.get_asset_list()
            self.notify_update_asset.emit(asset_list)
        report = self.asset_change_report(original_asset_list)
        self.notify_asset_change.emit(report)
