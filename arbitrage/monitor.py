#!/usr/bin/env python
import threading
import time
from operator import itemgetter
import concurrent.futures
import jinja2
from jinja2.exceptions import TemplateSyntaxError
from api.huobi import HuoBi
from api.okcoin import OKCoinCN
from arbitrage.stats import Statistics
from settings import config
from trader import Trader
from utils import (common, plt_helper, excepts, log_helper)
from utils.asset_info import AssetInfo


class Monitor(threading.Thread):
    _logger = log_helper.get_logger()
    coin_type = plt_helper.get_key_from_data('CoinType')
    exceed_max = config.exceed_max_dict[coin_type]

    def __init__(self, plt_list, stats):
        super(Monitor, self).__init__()
        self.plt_list = plt_list
        self.original_asset_list = []
        self.running = False
        self.coin_exceed_counter = 0
        self.old_coin_changes = 0.0
        self.old_fiat_changes = 0.0
        self.failed_counter = 0
        self.last_notifier_time = time.time()
        self.stats = stats

    # asset

    def get_asset_list(self):
        """
        get asset list, the order is the same as plt list
        :return: list of AssetInfo
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            assets = executor.map(lambda plt: AssetInfo.from_api(plt), self.plt_list)
        asset_list = list(assets)
        return asset_list

    @staticmethod
    def report_asset(asset_list):
        """
        log current each platform's asset, including "ALL"
        :param asset_list: platform's asset info, exluding "ALL"
        :return:
        """
        asset_logger = log_helper.get_asset_logger()
        report_template = '{:10s} ' + Monitor.coin_type + '={:<10.4f}, cny={:<10.4f}'
        total_asset = AssetInfo.from_sum(asset_list)
        # TODO: currently haven't append "ALL"
        for asset in asset_list:
            plt_coin, plt_fiat = asset.total_coin(), asset.total_fiat()
            asset_logger.info(report_template.format(asset.plt_name, plt_coin, plt_fiat))
        plt_coin, plt_fiat = total_asset.total_coin(), total_asset.total_fiat()
        asset_logger.info(report_template.format(total_asset.plt_name, plt_coin, plt_fiat))

    # asset changes

    def get_asset_changes(self, asset_list):
        """
        :param asset_list: platform's asset info, excluding "ALL"
        :return: (coin_change, fiat_change)
        """
        coin, original_coin = 0.0, 0.0
        fiat, original_fiat = 0.0, 0.0
        for original in self.original_asset_list:
            original_coin += original.total_coin()
            original_fiat += original.total_fiat()
        for asset in asset_list:
            coin += asset.total_coin()
            fiat += asset.total_fiat()
        return coin - original_coin, fiat - original_fiat

    @staticmethod
    def report_asset_changes(coin, fiat):
        """
        log asset changes
        :param coin:
        :param fiat:
        :return:
        """
        report = '[M] Asset Change: {:10.4f}{:3s}, {:10.4f}cny'.format(coin, Monitor.coin_type, fiat)
        log_helper.get_asset_logger().warning(report)

    @staticmethod
    def asset_message_render(asset_list, coin_changes, fiat_changes, stats):
        """
        return a templated string for emailing
        :param asset_list:
        :param coin_changes:
        :param fiat_changes:
        :param stats:
        :return:
        """
        for asset in asset_list:
            print(asset)
        assert (len(asset_list) == 2)
        asset_total = AssetInfo.from_sum(asset_list)
        asset_list.append(asset_total)
        coin_price = common.get_coin_price()
        jinja2_env = jinja2.Environment(loader=jinja2.FileSystemLoader(config.res_dir), trim_blocks=True)
        msg = jinja2_env.get_template(config.render_file).render(asset_list=asset_list, coin_changes=coin_changes,
                                                                 fiat_changes=fiat_changes, coin_price=coin_price,
                                                                 language=config.language, stats=stats)
        stats.reset()
        return msg

    def try_notify_asset_changes(self, asset_list, coin_changes, fiat_changes, is_last):
        """
        notify asset changes if proper; this should have no effect but possible emailing

        :param fiat_changes:
        :param coin_changes:
        :param asset_list: asset info, including sumed
        """
        now = time.time()
        if is_last or now - self.last_notifier_time >= config.emailing_interval_seconds:
            if abs(coin_changes) <= self.exceed_max:
                Monitor._logger.info('notifying asset changes via email')
                report = self.asset_message_render(asset_list, coin_changes, fiat_changes, self.stats)
                try:
                    if is_last:
                        excepts.send_msg(report, 'summary', 'html')
                    else:
                        excepts.send_msg(report, 'terminate', 'html')
                except TemplateSyntaxError as e:
                    excepts.send_msg('wrong template, {}'.format(e), 'Error', 'plain')
                self.last_notifier_time = now

    def _get_plt_price_list(self, catalog):
        """
        get the price list for platforms; the final price is sorted according to catalog. i.e.,

        - if catalog is buy, x1<x2<...xn
        - if catalog is sell, x1>x2>...xn

        :param catalog: buy/sell
        :return: list of (plt, price)
        """
        if catalog == 'buy':
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                ask1_list = list(executor.map(lambda plt: plt.ask1(), self.plt_list))
            pack = zip(self.plt_list, ask1_list)
            return sorted(pack, key=itemgetter(1))
        else:  # sell
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                bid1_list = list(executor.map(lambda plt: plt.bid1(), self.plt_list))
            pack = zip(self.plt_list, bid1_list)
            return sorted(pack, key=itemgetter(1), reverse=True)

    def coin_keeper(self, coin_change_amount, is_last):
        """
        keeps the coin amount to be within an allowed range; if exceed range, determine catalog and do adjust trade

        :param coin_change_amount: unbalanced coin amount
        :param is_last: True/False; if True, always do adjust when found unbalanced
        :return: whether the coin has been kept balanced
        """
        # only when exceeds
        if coin_change_amount > Monitor.exceed_max:
            if is_last:  # make sure will sell
                self.coin_exceed_counter = config.COIN_EXCEED_TIMES + 2
            # update counter
            if self.old_coin_changes < config.MINOR_DIFF:
                self.coin_exceed_counter = 1
            else:
                self.coin_exceed_counter += 1
            Monitor._logger.warning(
                '[M] exceed_counter={}, old_coin_changes={:<10.4f}, current={:<10.4f}'.format(
                    self.coin_exceed_counter, self.old_coin_changes, coin_change_amount))
            # test whether trade is needed
            if self.coin_exceed_counter > config.COIN_EXCEED_TIMES:
                trade_catalog = 'sell'
            else:
                return True  # no trade
        elif coin_change_amount < -Monitor.exceed_max:
            if is_last:  # make sure we will buy
                self.coin_exceed_counter = -(config.COIN_EXCEED_TIMES + 2)
            # update counter
            Monitor._logger.warning(
                '[M] exceed_counter={}, old_coin_changes={:<10.4f}, current={:<10.4f}'.format(
                    self.coin_exceed_counter, self.old_coin_changes, coin_change_amount))
            if self.old_coin_changes > -config.MINOR_DIFF:
                self.coin_exceed_counter = -1
            else:
                self.coin_exceed_counter -= 1
            # test whether trade is needed
            if self.coin_exceed_counter < -config.COIN_EXCEED_TIMES:
                trade_catalog = 'buy'
            else:
                return True  # no trade
        else:  # -exceed_max <= coin_change_amount <= exceed_max
            self.coin_exceed_counter = 0
            return True  # no trade
        # keeper
        self.stats.monitor_num += 1
        self._logger.warning('statistics: {}'.format(self.stats))
        trade_amount = common.adjust_amount(coin_change_amount)
        adjust_status = self.adjust_trade(trade_catalog, trade_amount)
        # reset after trade
        self.old_coin_changes = 0.0
        self.coin_exceed_counter = 0
        return adjust_status

    def adjust_trade(self, trade_catalog, coin_change_amount):
        """
        calculate each platform's price, and trade with a adjusted value; return value tells succeed or not
        :param trade_catalog: bug/sell
        :param coin_change_amount: biased coin amount
        :return: True/False
        """
        adjust_status = True
        Monitor._logger.warning(
            '[M] exceed_counter={}, amount={}'.format(self.coin_exceed_counter, coin_change_amount))
        trade_amount = abs(coin_change_amount)
        plt_price_list = self._get_plt_price_list(trade_catalog)
        # first try
        trade_plt, trade_price = plt_price_list[0]
        monitor_t1 = Trader(trade_plt, trade_catalog, trade_price, trade_amount)
        Monitor._logger.warning('[M] adjust at {}'.format(monitor_t1.plt_name))
        t1_res = monitor_t1.adjust_trade()
        if t1_res is False:
            Monitor._logger.warning('[M] FAILED adjust at {}'.format(monitor_t1.plt_name))
            # second try
            trade_plt, trade_price = plt_price_list[1]
            monitor_t2 = Trader(trade_plt, trade_catalog, trade_price, trade_amount)
            Monitor._logger.warning('[M] adjust at {}'.format(monitor_t2.plt_name))
            t2_res = monitor_t2.adjust_trade()
            if t2_res is False:
                Monitor._logger.critical(
                    '[M] FAILED adjust for [{}, {}]'.format(monitor_t1.plt_name, monitor_t2.plt_name))
                adjust_status = False  # only when both False
        return adjust_status

    def asset_update_handler(self, is_last):
        """
        general handler for asset update, do the following things:

        * keep coin amount fixed
        * if asset changed, log asset and changes
        * possible emailing
        * update old changes
        :param is_last: when True always process an adjust
        :return: whether coin keeper succeeds
        """
        # handle coin changes
        with common.MUTEX:
            Monitor._logger.debug('[M] LOCK acquired')
            asset_list = self.get_asset_list()
            Monitor._logger.debug('[M] asset_list obtained')
            coin_changes, fiat_changes = self.get_asset_changes(asset_list)
            status = self.coin_keeper(coin_changes, is_last)
        Monitor._logger.debug('[M] LOCK released')
        # report
        # NOTE: this report is delayed
        if abs(self.old_coin_changes - coin_changes) > config.MINOR_DIFF or abs(
                        self.old_fiat_changes - fiat_changes) > config.MINOR_DIFF:
            self.report_asset(asset_list)
            self.report_asset_changes(coin_changes, fiat_changes)
        # possible emailing
        self.try_notify_asset_changes(asset_list, coin_changes, fiat_changes, is_last)
        # update old
        self.old_coin_changes = coin_changes
        self.old_fiat_changes = fiat_changes
        return status

    def run(self, *args, **kwargs):
        """
        thread entry; while loop run; when exit loop, ensure that the coin amount is still fixed
        """
        # initialize asset
        self.original_asset_list = self.get_asset_list()
        self.report_asset(self.original_asset_list)
        self.old_coin_changes = self.get_asset_changes(self.original_asset_list)[0]
        # update asset info
        while self.running:
            time.sleep(config.MONITOR_INTERVAL_SECONDS)
            Monitor._logger.debug('[M] Monitor')
            adjust_status = self.asset_update_handler(False)
            if adjust_status is False:
                self.failed_counter += 1
                if self.failed_counter > config.monitor_fail_max:
                    report = 'Monitor adjuster failed {} times'.format(self.failed_counter)
                    excepts.send_msg(report, 'Error', 'plain')
        # last adjust
        # NOTE this strategy is fine only when exiting in the order: consumer->monitor
        last_adjust_status = self.asset_update_handler(True)
        if last_adjust_status is False:
            fail_warning = 'last adjust failed, do it yourself!'
            Monitor._logger.warning(fail_warning)


if __name__ == '__main__':
    log_helper.init_logger()
    okcoin_cn = OKCoinCN()
    huobi = HuoBi()
    plt_list = [okcoin_cn, huobi]
    stats = Statistics()
    monitor = Monitor(plt_list, stats)
    asset_list = monitor.get_asset_list()
    monitor.report_asset(asset_list)
    msg = monitor.asset_message_render(asset_list, 3.0, 4.0, stats)
    excepts.send_msg(msg, 'summary', 'html')
