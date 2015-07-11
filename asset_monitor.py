#!/usr/bin/env python

from PySide import QtCore

from asset_info import AssetInfo
from bitbays import BitBays
import common
import config

# TODO ensure that amount of BTC in a limited range; invoked when
# - cancel/trade fails
# - exiting
from okcoin import OKCoinCN


class AssetMonitor(QtCore.QThread):
    notify_update_asset = QtCore.Signal(list)
    notify_asset_change = QtCore.Signal(str)
    _logger = common.setup_logger()

    def __init__(self, plt_list):
        super(AssetMonitor, self).__init__()
        self.plt_list = plt_list
        self.change_info = None
        self.original_asset_list = []
        self.running = False

    def get_asset_list(self):
        return [AssetInfo(plt) for plt in self.plt_list]

    def get_asset_changes(self):
        asset_list = self.get_asset_list()
        btc, original_btc = 0.0, 0.0
        fiat, original_fiat = 0.0, 0.0
        for original in self.original_asset_list:
            original_btc += original.total_btc()
            original_fiat += original.total_fiat()
        for asset in asset_list:
            btc += asset.total_btc()
            fiat += asset.total_fiat()
        return btc - original_btc, fiat - original_fiat

    def handle_asset_changes(self, trade_plt):
        if self.change_info is None:
            btc, fiat = self.get_asset_changes()
        else:
            btc, fiat = self.change_info
        self.handle_asset_changes_impl(trade_plt, btc, fiat)
        self.change_info = None

    # FIXME the amouont should be specified by the failed trade
    @staticmethod
    def handle_asset_changes_impl(plt, btc, fiat):
        if btc > config.minor_diff:
            catelog = 'sell'
            price = plt.bid1()  # find "buyer"
        elif btc < -config.minor_diff:
            catelog = 'buy'
            price = plt.ask1()  # find "seller"
        else:
            return
        # must always succeed
        adjust_price = common.adjust_price(catelog, price)
        AssetMonitor._logger.warning(
            '[Monitor]: {} {}btc at {}cny [{}]'.format(catelog, abs(btc), adjust_price, plt.__class__.__name__))
        plt.trade(catelog, adjust_price, btc)

    def run(self, *args, **kwargs):
        # initialize asset
        self.original_asset_list = self.get_asset_list()
        self.notify_update_asset.emit(self.original_asset_list)
        # update asset
        while self.running:
            QtCore.QThread.sleep(config.monitor_interval_seconds)
            AssetMonitor._logger.debug("[Monitor] Notify")
            asset_list = self.get_asset_list()
            self.notify_update_asset.emit(asset_list)
        # report net income
        self.change_info = self.get_asset_changes()
        report = 'Asset Change: {:10.4f}btc, {:10.4f}cny'.format(self.change_info[0], self.change_info[1])
        AssetMonitor._logger.warning(report)
        self.notify_asset_change.emit(report)


if __name__ == '__main__':
    okcoin_cn = OKCoinCN()
    bitbays = BitBays()
    plt_list = [okcoin_cn, bitbays]
    monitor = AssetMonitor(plt_list)
    # monitor.change_info = [0.0155, 0]
    # monitor.handle_asset_changes(okcoin_cn)
