#!/usr/bin/env python

from PySide import QtCore

from asset_info import AssetInfo
import common
import config

# TODO ensure that amount of BTC in a limited range; invoked when
# - cancel/trade fails
# - exiting
# TODO display asset_info regularly
# TODO report the net income when exiting

class AssetMonitor(QtCore.QThread):
    notify_update_asset = QtCore.Signal(list)
    _logger = common.setup_logger()

    def __init__(self, plt_list):
        super(AssetMonitor, self).__init__()
        self.plt_list = plt_list
        self.running = False

    def run(self, *args, **kwargs):
        while self.running:
            AssetMonitor._logger.debug("[Monitor] Notify")
            asset_list = [AssetInfo(plt) for plt in self.plt_list]
            self.notify_update_asset.emit(asset_list)
            QtCore.QThread.sleep(config.monitor_interval_seconds)
