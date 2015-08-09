#!/usr/bin/env python

import time
import math
import threading

import concurrent.futures

from asset_info import AssetInfo
import common
import config
from arbitrage_adjuster import Adjuster
from trade_info import TradeInfo


class ArbitrageProducer(threading.Thread):
    _logger = common.get_logger()
    coin_type = common.get_key_from_data('CoinType')
    diff_dict = config.diff_dict[coin_type]

    ### stateless
    def __init__(self, plt_list, adjuster_queue):
        super(ArbitrageProducer, self).__init__()
        self.plt_list = plt_list
        self.adjuster_queue = adjuster_queue
        self.running = False
        self.min_amount = max(plt_list[0].lower_bound, plt_list[1].lower_bound)

    def run(self):
        while self.running:
            time.sleep(config.SLEEP_SECONDS)
            ArbitrageProducer._logger.debug('[P] Producer')
            self.process_arbitrage()
        self.adjuster_queue.put(common.SIGNAL)


    @staticmethod
    def process_trade(trade_pair):
        """
        inital trading, this guarantees that the asset is enough
        TODO: ensure this trade MUST succeed
        :return:
        """
        Adjuster._logger.warning('Arbitrage Start')
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            order_ids = executor.map(lambda t: t.regular_trade(t.catelog, t.price, t.amount), trade_pair)
        for trade, order_id in zip(trade_pair, order_ids):
            if order_id == config.INVALID_ORDER_ID:
                Adjuster._logger.critical('order_id not exists, EXIT')
                # noinspection PyProtectedMember
                os._exit(1)
            trade.set_order_id(order_id)

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
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            asset_info = executor.map(lambda plt: AssetInfo(plt), self.plt_list)
        ArbitrageProducer._logger.info('[P] asset_info got')
        asset_info_list = list(asset_info)
        asset_info_a = asset_info_list[i]
        asset_info_b = asset_info_list[1 - i]

        # ask_a_price < bid_b_price
        price_diff = bid_b_price - ask_a_price
        ask_a_adjust_price = common.round_price(ask_a_price + price_diff / config.PRICE_ROUND)
        bid_b_adjust_price = common.round_price(bid_b_price - price_diff / config.PRICE_ROUND)

        def amount_refine():
            plt_a_buy_amount = asset_info_a.afford_buy_amount(ask_a_adjust_price) - config.ASSET_FOR_TRAID_DIFF
            plt_b_sell_amount = asset_info_b.afford_sell_amount() - config.ASSET_FOR_TRAID_DIFF
            amount = min(config.upper_bound[ArbitrageProducer.coin_type], ask_a_amount, bid_b_amount, plt_a_buy_amount,
                         plt_b_sell_amount)
            amount = math.floor(amount * (10 ** config.TRADE_PRECISION)) / (10 ** config.TRADE_PRECISION)
            amount = max(self.min_amount, amount)
            return amount

        amount = amount_refine()

        ArbitrageProducer._logger.info('[P] amount got')

        # case 1: no trade
        if amount - self.min_amount < config.MINOR_DIFF:
            ArbitrageProducer._logger.info('[P]arbitrage cancelled, insufficient amount')
            return False

        # case 2: trade
        buy_trade = TradeInfo(plt_a, 'buy', ask_a_adjust_price, amount)  # buy at plt_a
        sell_trade = TradeInfo(plt_b, 'sell', bid_b_adjust_price, amount)  # sell at plt_b
        # (buy, sell)
        trade_pair = (buy_trade, sell_trade)
        now = time.time()
        ArbitrageProducer._logger.info('[P] trade_pair got')
        ArbitrageProducer.process_trade(trade_pair)
        ArbitrageProducer._logger.info('[P] arbitrage done')
        adjuster = Adjuster(trade_pair, now)
        self.adjuster_queue.put(adjuster)
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

        arbitrage_diff = ArbitrageProducer.diff_dict[plt_name_a][plt_name_b]
        if ask_a[0] + arbitrage_diff < bid_b[0]:
            ArbitrageProducer._logger.debug('[P] Arbitrage chance: {} {}'.format(ask_a, bid_b))
            with common.MUTEX:
                ArbitrageProducer._logger.info('[P] LOCK acquired')
                self.arbitrage_impl(i, ask_list[i], bid_list[1 - i])
            ArbitrageProducer._logger.info('[P] LOCK released')
            return True
        else:
            return False

    def process_arbitrage(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            info_list = list(executor.map(lambda plt: plt.ask_bid_list(1), self.plt_list))
        ArbitrageProducer._logger.debug('[P] ask_bid_list got')
        length = len(info_list[0])

        ask_list = [info[length / 2 - 1] for info in info_list]
        bid_list = [info[length / 2] for info in info_list]

        for i in range(2):
            if self.try_arbitrage(ask_list, bid_list, i):
                return True
        return False
