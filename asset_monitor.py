#!/usr/bin/env python

from PySide import QtCore

from asset_info import AssetInfo
import common
import config


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
