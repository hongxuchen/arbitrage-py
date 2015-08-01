#!/usr/bin/env python
from email.mime.text import MIMEText
from operator import itemgetter
import smtplib
import threading
import time

import concurrent.futures

import config as config
from asset_info import AssetInfo
from bitbays import BitBays
import common
from okcoin import OKCoinCN
from trade_info import TradeInfo


class AssetMonitor(threading.Thread):
    _logger = common.get_logger()

    def __init__(self, plt_list):
        super(AssetMonitor, self).__init__()
        self.plt_list = plt_list
        self.original_asset_list = []
        self.running = False
        self.btc_exceed_counter = 0
        self.old_btc_change_amount = 0.0
        self.old_fiat_change_amount = 0.0
        self.failed_counter = 0
        self.last_notifier_time = time.time()

    def get_asset_list(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            assets = executor.map(lambda plt: AssetInfo(plt), self.plt_list)
        asset_list = list(assets)
        return asset_list

    @staticmethod
    def report_asset(asset_list):
        asset_logger = common.get_asset_logger()
        report_template = '{:10s} btc={:<10.4f}, cny={:<10.4f}'
        all_btc = 0.0
        all_fiat = 0.0
        for asset in asset_list:
            plt_btc, plt_fiat = asset.total_btc(), asset.total_fiat()
            all_btc += plt_btc
            all_fiat += plt_fiat
            asset_logger.info(report_template.format(asset.plt_name, plt_btc, plt_fiat))
        asset_logger.info(report_template.format('ALL', all_btc, all_fiat))

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
    def report_asset_changes(btc, fiat):
        report = 'Asset Change: {:10.4f}btc, {:10.4f}cny'.format(btc, fiat)
        common.get_asset_logger().warning(report)

    @staticmethod
    def send_msg(report):
        # print('sending email')
        emailing_info = common.get_key_from_data('Emailing')
        sender = emailing_info['sender']
        receiver = emailing_info['receiver']
        server = emailing_info['server']
        msg = MIMEText(report)
        msg['Subject'] = 'Asset Change Report'
        msg['From'] = sender
        msg['To'] = receiver
        session = smtplib.SMTP(server)
        session.sendmail(sender, [receiver], msg.as_string())
        session.quit()

    def try_notify_asset_changes(self, btc, fiat):
        report = 'Asset Change: {:10.4f}btc, {:10.4f}cny'.format(btc, fiat)
        now = time.time()
        # config.EMAILING_INTERVAL_SECONDS = 8
        if now - self.last_notifier_time >= config.EMAILING_INTERVAL_SECONDS:
            AssetMonitor._logger.warning('notifying asset changes via email')
            self.send_msg(report)
            self.last_notifier_time = now

    def _get_plt_price_list(self, catelog):
        if catelog == 'buy':
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                ask1_list = list(executor.map(lambda plt: plt.ask1(), self.plt_list))
            pack = zip(self.plt_list, ask1_list)
            return sorted(pack, key=itemgetter(1))
        else:  # sell
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                bid1_list = list(executor.map(lambda plt: plt.bid1(), self.plt_list))
            pack = zip(self.plt_list, bid1_list)
            return sorted(pack, key=itemgetter(1), reverse=True)

    def btc_update_handler(self, btc_change_amount, is_last):
        # only when exceeds
        if btc_change_amount > config.BTC_DIFF_MAX:
            if is_last:  # make sure will sell
                self.btc_exceed_counter = config.BTC_EXCEED_COUNTER + 2
            # update counter
            if self.old_btc_change_amount < config.MINOR_DIFF:
                self.btc_exceed_counter = 1
            else:
                self.btc_exceed_counter += 1
            AssetMonitor._logger.warning(
                '[Monitor] exceed_counter={}, old_btc_changes={:<10.4f}, current={:<10.4f}'.format(
                    self.btc_exceed_counter, self.old_btc_change_amount, btc_change_amount))
            # test whether trade is needed
            if self.btc_exceed_counter > config.BTC_EXCEED_COUNTER:
                trade_catelog = 'sell'
            else:
                return True  # no trade
        elif btc_change_amount < -config.BTC_DIFF_MAX:
            if is_last:  # make sure we will buy
                self.btc_exceed_counter = -(config.BTC_EXCEED_COUNTER + 2)
            # update counter
            AssetMonitor._logger.warning(
                '[Monitor] exceed_counter={}, old_btc_changes={:<10.4f}, current={:<10.4f}'.format(
                    self.btc_exceed_counter, self.old_btc_change_amount, btc_change_amount))
            if self.old_btc_change_amount > -config.MINOR_DIFF:
                self.btc_exceed_counter = -1
            else:
                self.btc_exceed_counter -= 1
            # test whether trade is needed
            if self.btc_exceed_counter < -config.BTC_EXCEED_COUNTER:
                trade_catelog = 'buy'
            else:
                return True  # no trade
        else:  # -config.BTC_DIFF_MAX <= btc_change_amount <= config.BTC_DIFF_MAX
            self.btc_exceed_counter = 0
            return True  # no trade
        ### adjust trade; FIXME should guarantee no btc change when stop
        adjust_status = self.adjust_trade(trade_catelog, btc_change_amount)
        ## reset after trade
        self.old_btc_change_amount = 0.0
        self.btc_exceed_counter = 0
        return adjust_status

    def adjust_trade(self, trade_catelog, btc_change_amount):
        adjust_status = True
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
            AssetMonitor._logger.warning('[Monitor] FAILED adjust at {}'.format(monitor_t1.plt_name))
            # second try
            trade_plt, trade_price = plt_price_list[1]
            monitor_t2 = TradeInfo(trade_plt, trade_catelog, trade_price, trade_amount)
            AssetMonitor._logger.warning('[Monitor] adjust at {}'.format(monitor_t2.plt_name))
            t2_res = monitor_t2.adjust_trade()
            if t2_res is False:
                AssetMonitor._logger.critical(
                    '[Monitor] FAILED adjust for [{}, {}]'.format(monitor_t1.plt_name, monitor_t2.plt_name))
                adjust_status = False  # only when both False
        return adjust_status

    def asset_update_handler(self, is_last):
        # handle btc changes
        common.MUTEX.acquire(True)
        asset_list = self.get_asset_list()
        btc, fiat = self.get_asset_changes(asset_list)
        status = self.btc_update_handler(btc, is_last)
        common.MUTEX.release()
        ### report
        # NOTE: this report is delayed
        if abs(self.old_btc_change_amount - btc) > config.MINOR_DIFF or abs(
                        self.old_fiat_change_amount - fiat) > config.MINOR_DIFF:
            self.report_asset(asset_list)
            self.report_asset_changes(btc, fiat)
        self.try_notify_asset_changes(btc, fiat)
        ### update old
        self.old_btc_change_amount = btc
        self.old_fiat_change_amount = fiat
        return status

    def run(self, *args, **kwargs):
        # initialize asset
        self.original_asset_list = self.get_asset_list()
        self.old_btc_change_amount = self.get_asset_changes(self.original_asset_list)[0]
        # TODO add asset log
        # update asset info
        while self.running:
            time.sleep(config.MONITOR_INTERVAL_SECONDS)
            adjust_status = self.asset_update_handler(False)  # TODO: return value not used here
            if adjust_status is False:
                self.failed_counter += 1
                if self.failed_counter > config.MONITOR_FAIL_MAX:
                    # FIXME deal with this case
                    pass
        # last adjust
        # FIXME this strategy is fine only when exiting in the order: consumer->monitor
        last_adjust_status = self.asset_update_handler(True)
        if last_adjust_status is False:
            fail_warning = 'last adjust failed, do it yourself!'
            AssetMonitor._logger.warning(fail_warning)


if __name__ == '__main__':
    okcoin_cn = OKCoinCN()
    bitbays = BitBays()
    plt_list = [okcoin_cn, bitbays]
    monitor = AssetMonitor(plt_list)
