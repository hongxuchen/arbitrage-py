#!/usr/bin/env python

import time
import math
import threading

import concurrent.futures

from asset_info import AssetInfo
import common
import config
from arbitrage_info import ArbitrageInfo
from trade_info import TradeInfo


class ArbitrageProducer(threading.Thread):
    _logger = common.get_logger()

    ### stateless
    def __init__(self, plt_list, arbitrage_list, symbol, parent=None):
        super(ArbitrageProducer, self).__init__(parent)
        self.plt_list = plt_list
        self.arbitrage_queue = arbitrage_list
        self.symbol = symbol
        self.running = False
        self.lower_bound = max(plt_list[0].lower_bound, plt_list[1].lower_bound)

    def run(self):
        while self.running:
            ArbitrageProducer._logger.debug('[Producer] run')
            self.process_arbitrage()

    def arbitrage_impl(self, i, ask_a, bid_b):
        """
        :param i: the index of platform for buy; 1-i index of platform for sell
        :param ask_a: platform a ask info, [price, amount]
        :param bid_b: platform b bid info, [price, amount]
        :return:
        """
        plt_a = self.plt_list[i]
        plt_b = self.plt_list[1 - i]
        ask_a_price, ask_a_amount = ask_a[0], ask_a[1]
        bid_b_price, bid_b_amount = bid_b[0], bid_b[1]

        ## lock here
        common.MUTEX.acquire(True)
        ArbitrageProducer._logger.info('[Producer] acquire lock')
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            asset_info = executor.map(lambda plt: AssetInfo(plt), self.plt_list)
        asset_info_list = list(asset_info)
        # asset_info_list = [AssetInfo(plt) for plt in self.plt_list]
        asset_info_a = asset_info_list[i]
        asset_info_b = asset_info_list[1 - i]

        # ask_a_price < bid_b_price
        price_diff = bid_b_price - ask_a_price
        ask_a_adjust_price = ask_a_price + price_diff / 3
        bid_b_adjust_price = bid_b_price - price_diff / 3

        def amount_refine():
            plt_a_buy_amount = asset_info_a.afford_buy_amount(ask_a_adjust_price) - config.ASSET_FOR_TRAID_DIFF
            plt_b_sell_amount = asset_info_b.afford_sell_amount() - config.ASSET_FOR_TRAID_DIFF
            amount = min(config.UPPER_BOUND, ask_a_amount, bid_b_amount, plt_a_buy_amount, plt_b_sell_amount)
            amount = math.floor(amount * (10 ** config.TRADE_PRECISION)) / (10 ** config.TRADE_PRECISION)
            amount = max(self.lower_bound, amount)
            return amount

        amount = amount_refine()
        if amount - self.lower_bound < config.MINOR_DIFF:
            ArbitrageProducer._logger.info('[Producer] insufficient amount, release lock')
            common.MUTEX.release()
            return False
        ArbitrageProducer._logger.debug(asset_info_a)
        ArbitrageProducer._logger.debug(asset_info_b)
        buy_trade = TradeInfo(plt_a, 'buy', ask_a_adjust_price, amount)  # buy at plt_a
        sell_trade = TradeInfo(plt_b, 'sell', bid_b_adjust_price, amount)  # sell at plt_b
        # (buy, sell)
        trade_pair = (buy_trade, sell_trade)
        now = time.time()
        arbitrage_info = ArbitrageInfo(trade_pair, now)
        arbitrage_info.process_trade()
        ArbitrageProducer._logger.info('[Producer] arbitrage done, release lock')
        common.MUTEX.release()
        self.arbitrage_queue.append(arbitrage_info)
        return True

    def try_arbitrage(self, ask_list, bid_list, i):
        """
        arbitrage necssary condition
        ask_a, bid_b are of [price, amount]
        :return:
        """

        def get_plt_name(plt):
            return plt.__class__.__name__

        ask_a, bid_b = ask_list[i], bid_list[1 - i]
        plt_name_a, plt_name_b = get_plt_name(self.plt_list[i]), get_plt_name(self.plt_list[1 - i])

        arbitrage_diff = config.diff_dict[plt_name_a][plt_name_b]
        if ask_a[0] + arbitrage_diff < bid_b[0]:
            ArbitrageProducer._logger.debug('[Producer] Arbitrage chance: {} {}'.format(ask_a, bid_b))
            self.arbitrage_impl(i, ask_list[i], bid_list[1 - i])
            return True
        else:
            return False

    def process_arbitrage(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            self._info_list = list(executor.map(lambda plt: plt.ask_bid_list(1), self.plt_list))
        length = len(self._info_list[0])

        ask_list = [info[length / 2 - 1] for info in self._info_list]
        bid_list = [info[length / 2] for info in self._info_list]

        for i in range(2):
            if self.try_arbitrage(ask_list, bid_list, i):
                return True
        return False
