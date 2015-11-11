#!/usr/bin/env python

import threading
import time
import concurrent.futures
from arbitrage.adjuster import Adjuster
from arbitrage.trader import Trader
from settings import config
from utils import common, plt_helper, log_helper, excepts
from utils.asset_info import AssetInfo


class Producer(threading.Thread):
    _logger = log_helper.get_logger()
    coin_type = plt_helper.get_key_from_data('CoinType')
    diff_dict = config.diff_dict[coin_type]

    # stateless
    def __init__(self, plt_list, adjuster_queue, stats, recollector):
        super(Producer, self).__init__()
        self.plt_list = plt_list
        if adjuster_queue is not None:
            self.adjuster_enabled = True
            self.adjuster_queue = adjuster_queue
        else:
            self.adjuster_enabled = False
        self.running = False
        self.min_amount = max(plt_list[0].lower_bound, plt_list[1].lower_bound)
        self.stats = stats
        self.recollector = recollector

    def run(self):
        while self.running:
            time.sleep(config.sleep_seconds)
            Producer._logger.debug('[P] Producer')
            self.process_arbitrage()
        if self.adjuster_enabled:
            self.adjuster_queue.put(common.SIGNAL)

    @staticmethod
    def _handle_failed_order(trade_pair):
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            assets = list(executor.map(lambda t: AssetInfo.from_api(t.plt), trade_pair))
        asset_str = '[asset info]\n'
        for asset in assets:
            asset_str += str(asset) + '\n'
        trade_str = '[trade info]\n'
        for trader in trade_pair:
            trade_str += str(trader) + '\n'
        err_msg = 'msg: Found non-existent Order ID Error\n' + asset_str + '\n' + trade_str
        excepts.send_msg(err_msg, 'Error', 'plain')

    @staticmethod
    def process_trade(trade_pair):
        """
        inital trading, this guarantees that the asset is enough
        TODO: ensure this trade MUST succeed
        :param trade_pair:
        :return:
        """
        Producer._logger.warning('[P] Arbitrage Start')
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            order_ids = executor.map(lambda t: t.regular_trade(t.catalog, t.price, t.amount), trade_pair)
        for trade, order_id in zip(trade_pair, order_ids):
            if order_id == config.INVALID_ORDER_ID:
                Producer._handle_failed_order(trade_pair)
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

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            asset_info = executor.map(lambda plt: AssetInfo.from_api(plt), self.plt_list)
        Producer._logger.debug('[P] asset_info obtained')
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
            amount = min(config.upper_bound[Producer.coin_type],
                         ask_a_amount * config.AMOUNT_PERCENT,
                         bid_b_amount * config.AMOUNT_PERCENT,
                         plt_a_buy_amount,
                         plt_b_sell_amount)
            amount = max(self.min_amount, amount)
            amount = common.adjust_amount(amount)
            return amount

        final_amount = amount_refine()

        Producer._logger.debug('[P] amount obtained')

        # case 1: no trade
        if final_amount - self.min_amount < config.MINOR_DIFF:
            self.stats.insufficient_num += 1
            Producer._logger.info('[P] arbitrage cancelled, insufficient amount')
            return False

        # case 2: trade
        self.stats.arbitrage_num += 1
        buy_trade = Trader(plt_a, 'buy', ask_a_adjust_price, final_amount)  # buy at plt_a
        sell_trade = Trader(plt_b, 'sell', bid_b_adjust_price, final_amount)  # sell at plt_b
        # (buy, sell)
        trade_pair = (buy_trade, sell_trade)
        now = time.time()
        Producer._logger.debug('[P] trade_pair obtained')
        # trade, and get order_id
        Producer.process_trade(trade_pair)
        Producer._logger.info('[P] arbitrage done')
        if self.adjuster_enabled:
            adjuster = Adjuster(trade_pair, now)
            self.adjuster_queue.put(adjuster)
        return True

    def try_arbitrage(self, ask_list, bid_list, i):
        """
        arbitrage necssary condition
        ask_a, bid_b are of [price, amount]
        :param i:
        :param bid_list:
        :param ask_list:
        :return:
        """

        ask_a, bid_b = ask_list[i], bid_list[1 - i]
        plt_name_a, plt_name_b = self.plt_list[i].plt_name, self.plt_list[1 - i].plt_name

        arbitrage_diff = Producer.diff_dict[plt_name_a][plt_name_b]
        # try buying at plt_a, sell at plt_b
# if for most of the time, price(plt_a) < price(plt_b),  we need to make
# 1. diff_a_b=arbitrage_diff[plt_a][plt_b] bigger
# 2. diff_b_a=arbitrage_diff[plt_b][plt_a] smaller       
# ideally diff_a_b==diff_b_a, so in this trend, diff_a_b > diff_b_a
# EXAMPLE: when  price(HuoBi) < price(OKCoinCN), plt_a == HuoBi, plt_b == OKCoinCN
#          in config.py, we should make diff_dict[HuoBi][OKCoinCN] > diff_dict[OKCoinCN][HuoBi]
        if ask_a[0] + arbitrage_diff < bid_b[0]:
            self.stats.trade_chance += 1
            Producer._logger.debug('[P] Arbitrage chance: {} {}'.format(ask_a, bid_b))

            with common.MUTEX:
                Producer._logger.debug('[P] LOCK acquired')
                self.arbitrage_impl(i, ask_list[i], bid_list[1 - i])
            Producer._logger.debug('[P] LOCK released')
            return True
        else:
            return False

    def process_arbitrage(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            info_list = list(executor.map(lambda plt: plt.ask_bid_list(1), self.plt_list))
        Producer._logger.debug('[P] ask_bid_list obtained')
        length = len(info_list[0])

        ask_list = [info[length / 2 - 1] for info in info_list]
        bid_list = [info[length / 2] for info in info_list]
        # FIXME redundant for CoinType
        if not self.recollector.balanced(plt_helper.get_key_from_data("CoinType")):
            Producer._logger.debug('[P] wait for ImBalanced')
            self.stats.wait_imbalanced += 1
            return False
        for i in range(2):
            if self.try_arbitrage(ask_list, bid_list, i):
                return True
        return False
