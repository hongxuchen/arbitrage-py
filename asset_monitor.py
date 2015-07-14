#!/usr/bin/env python

from PySide import QtCore

import config as config
from asset_info import AssetInfo
from bitbays import BitBays
import common


# TODO ensure that amount of BTC in a limited range; invoked when
# - cancel/trade fails
# - exiting
from okcoin import OKCoinCN
from trade_info import TradeInfo


class AssetMonitor(QtCore.QThread):
    notify_update_asset = QtCore.Signal(list)
    notify_asset_change = QtCore.Signal(str)
    _logger = common.setup_logger()

    def __init__(self, plt_list):
        super(AssetMonitor, self).__init__()
        self.plt_list = plt_list
        self.original_asset_list = []
        self.running = False
        self.btc_exceed_counter = 0
        self.old_btc_change_amount = 0.0
        self.old_fiat_change_amount = 0.0

    def get_asset_list(self):
        return [AssetInfo(plt) for plt in self.plt_list]

    def get_asset_changes(self, asset_list):
        btc, original_btc = 0.0, 0.0
        fiat, original_fiat = 0.0, 0.0
        for original in self.original_asset_list:
            original_btc += original.total_btc()
            original_fiat += original.total_fiat()
        for asset in asset_list:
            btc += asset.total_btc()
            fiat += asset.total_fiat()
        return btc - original_btc, fiat - original_fiat

    @staticmethod
    def get_asset_change_report(btc, fiat):
        report = 'Asset Change: {:10.4f}btc, {:10.4f}cny'.format(btc, fiat)
        return report

    def _get_plt_price_list(self, catelog):
        p1 = self.plt_list[0]
        p2 = self.plt_list[1]
        if catelog == 'buy':
            p1_ask1 = p1.ask1()
            p2_ask1 = p2.ask1()
            if p1_ask1 < p2_ask1:
                info = [(p1, p1_ask1), (p2, p2_ask1)]
            else:
                info = [(p2, p2_ask1), (p1, p1_ask1)]
        else:  # sell
            p1_bid1 = p1.bid1()
            p2_bid1 = p2.bid1()
            if p1_bid1 > p2_bid1:
                info = [(p1, p1_bid1), (p2, p2_bid1)]
            else:
                info = [(p2, p2_bid1), (p1, p1_bid1)]
        return info

    def handle_btc_changes(self, btc_change_amount):
        # only when exceeds
        if btc_change_amount > config.BTC_DIFF_MAX:
            # update counter
            AssetMonitor._logger.warning(
                '[Monitor] exceed_counter={}, old_btc_changes={:<10.4f}, current={:<10.4f}'.format(
                    self.old_btc_change_amount, btc_change_amount))
            if self.old_btc_change_amount < config.minor_diff:
                self.btc_exceed_counter = 1
            else:
                self.btc_exceed_counter += 1
            # test whether trade is needed
            if self.btc_exceed_counter > config.BTC_EXCEED_COUNTER:
                trade_catelog = 'sell'
            else:
                return  # no trade
        elif btc_change_amount < -config.BTC_DIFF_MAX:
            # update counter
            AssetMonitor._logger.warning(
                '[Monitor] exceed_counter={}, old_btc_changes={:<10.4f}, current={:<10.4f}'.format(
                    self.btc_exceed_counter, self.old_btc_change_amount, btc_change_amount))
            if self.old_btc_change_amount > -config.minor_diff:
                self.btc_exceed_counter = -1
            else:
                self.btc_exceed_counter -= 1
            # test whether trade is needed
            if self.btc_exceed_counter < -config.BTC_EXCEED_COUNTER:
                trade_catelog = 'buy'
            else:
                return  # no trade
        else:  # -config.BTC_DIFF_MAX <= btc_change_amount <= config.BTC_DIFF_MAX
            self.btc_exceed_counter = 0
            return  # no trade
        ### adjust trade
        AssetMonitor._logger.warning(
            '[Monitor] exceed_counter={}, amount={}'.format(self.btc_exceed_counter, btc_change_amount))
        trade_amount = abs(btc_change_amount)
        plt_price_list = self._get_plt_price_list(trade_catelog)
        ### first try
        trade_plt, trade_price = plt_price_list[0]
        monitor_t1 = TradeInfo(trade_plt, trade_catelog, trade_price, trade_amount)
        AssetMonitor._logger.warning('[Monitor] adjust at {}'.format(monitor_t1.plt_name))
        t1_res = monitor_t1.adjust_trade()
        if t1_res is False:
            # second try
            trade_plt, trade_price = plt_price_list[1]
            monitor_t2 = TradeInfo(trade_plt, trade_catelog, trade_price, trade_amount)
            AssetMonitor._logger.warning('[Monitor] adjust at {}'.format(monitor_t2.plt_name))
            t2_res = monitor_t2.adjust_trade()
            if t2_res is False:
                AssetMonitor._logger.critical(
                    '[Monitor] adjust fails for [{}, {}]'.format(monitor_t1.plt_name, monitor_t2.plt_name))
        self.old_btc_change_amount = 0.0
        self.btc_exceed_counter = 0

    def log_asset_update(self):
        # handle btc changes
        common.MUTEX.acquire(True)
        asset_list = self.get_asset_list()
        btc, fiat = self.get_asset_changes(asset_list)
        self.handle_btc_changes(btc)
        common.MUTEX.release()
        ### report
        # NOTE:this report is delayed
        self.notify_update_asset.emit(asset_list)
        report = self.get_asset_change_report(btc, fiat)
        ### always report on console; notify UI only when change
        AssetMonitor._logger.warning(report)
        if abs(self.old_btc_change_amount - btc) > config.minor_diff or abs(
                        self.old_fiat_change_amount - fiat) > config.minor_diff:
            self.notify_asset_change.emit(report)
        ### update old
        self.old_btc_change_amount = btc
        self.old_fiat_change_amount = fiat

    def run(self, *args, **kwargs):
        # initialize asset
        self.original_asset_list = self.get_asset_list()
        self.old_btc_change_amount = self.get_asset_changes(self.original_asset_list)[0]
        self.notify_update_asset.emit(self.original_asset_list)
        # update asset info
        while self.running:
            QtCore.QThread.sleep(config.monitor_interval_seconds)
            AssetMonitor._logger.debug("[Monitor] Notify")
            self.log_asset_update()


if __name__ == '__main__':
    okcoin_cn = OKCoinCN()
    bitbays = BitBays()
    plt_list = [okcoin_cn, bitbays]
    monitor = AssetMonitor(plt_list)
