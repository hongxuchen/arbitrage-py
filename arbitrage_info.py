#!/usr/bin/env python
from __future__ import print_function
import time

from bitbays import BitBays
import common
import config
from okcoin import OKCoinCN
from trade_info import TradeInfo


class ArbitrageInfo(object):
    _logger = common.setup_logger()

    def __init__(self, trade_pair, time):
        """
        :param trade_pair: a TradeInfo pair, (buy, sell)
        :param time:
        :return:
        """
        self.trade_pair = trade_pair
        self.time = time

    def process_trade(self):
        """
        inital trading, this guarantees that the asset is enough
        :return:
        """
        ArbitrageInfo._logger.warning('Arbitrage Start')
        for trade in self.trade_pair:
            order_id = trade.regular_trade(trade.catelog, trade.price, trade.amount)
            trade.set_order_id(order_id)

    @staticmethod
    def normalize_trade_pair_strategy1(trade_pair):
        """
        :return: trade pair, first's lower_bound is smaller
        """
        t1 = trade_pair[0]
        t2 = trade_pair[1]
        p1 = t1.plt
        p2 = t2.plt
        if p1.lower_bound < p2.lower_bound:
            return t1, t2
        else:
            return t2, t1

    @staticmethod
    def normalize_trade_pair_strategy2(trade_pair, catelog):
        """
        This strategy requires to request each plt once
        :return: trade pair, first is preferred
        """
        t1 = trade_pair[0]
        t2 = trade_pair[1]
        p1 = t1.plt
        p2 = t2.plt
        if catelog == 'buy':  # buy lower
            p1_ask = p1.ask1()
            p2_ask = p2.ask1()
            if p1_ask < p2_ask:
                return t1, t2
            else:
                return t2, t1
        else:  # sell, sell higher
            p1_bid = p1.bid1()
            p2_bid = p2.bid2()
            if p1_bid > p2_bid:
                return t1, t2
            else:
                return t2, t1

    def seconds_since_trade(self):
        return time.time() - self.time

    def get_adjust_info(self):
        """
        if finding pending, cancel order ASAP; cancel failure means no pending!
        since trade_pair is of (buy, sell), this returns the *buy* amount
        :return: None if adjust not needed; otherwise (catelog, amount)
        """
        remaining_list = []
        for trade in self.trade_pair:
            order_info = trade.get_order_info()
            if order_info.has_pending():
                cancel_status = trade.cancel()
                if cancel_status is False:
                    order_info.remaining_amount = 0.0
            remaining_list.append(order_info.remaining_amount)
        amount = remaining_list[0] - remaining_list[1]
        # A1: buy remaining, A2: sell remaining
        # if A < 0, bought more, should sell; if A >= 0, sold more, should buy
        ArbitrageInfo._logger.warning(
            'A1={:<10.4f}, A2={:<10.4f}, A={:<10.4f}'.format(remaining_list[0], remaining_list[1], amount))
        if amount < -config.minor_diff:
            trade_catelog = 'sell'
        elif amount > config.minor_diff:
            trade_catelog = 'buy'
        else:
            return None
        trade_amount = abs(amount)
        return trade_catelog, trade_amount

    # noinspection PyPep8Naming
    def adjust_pending(self):
        adjust_res = self.get_adjust_info()
        if adjust_res is None:
            return
        trade_catelog, trade_amount = adjust_res[0], adjust_res[1]
        t1, t2 = self.normalize_trade_pair_strategy1(self.trade_pair)
        trade_plt = t1.plt
        trade_price = t1.price
        # not really care about the EXACT price
        new_t1 = TradeInfo(trade_plt, trade_catelog, trade_price, trade_amount)
        common.MUTEX.acquire(True)  # blocking
        ArbitrageInfo._logger.info('[Consumer] acquire lock')
        t1_adjust_status = new_t1.adjust_trade()
        if t1_adjust_status is False:
            trade_plt = t2.plt
            trade_price = t2.price
            new_t2 = TradeInfo(trade_plt, trade_catelog, trade_price, trade_amount)
            # TODO more code review here
            t2_adjust_status = new_t2.adjust_trade()
            # should be rather rare case
            if t2_adjust_status is False:
                ArbitrageInfo._logger.critical('CRITAL: [{}, {}] cannot adjust'.format(t1.plt_name, t2.plt_name))
                # TODO may need to use monitor here
        ArbitrageInfo._logger.info('[Consumer] adjust done, release lock')
        common.MUTEX.release()

    def __repr__(self):
        t1 = self.trade_pair[0]
        t2 = self.trade_pair[1]
        a1 = t1.amount
        a2 = t2.amount
        assert abs(a1 - a2) < config.minor_diff
        trade_amount = a1
        if t1.catelog == 'buy':
            buy_trade = t1
            sell_trade = t2
        else:  # sell
            assert t2.catelog == 'buy'
            buy_trade = t2
            sell_trade = t1
        return 'Amount={:<10.4f}; {:10s} buys {:10.4f} {:3s}; {:10s} sells {:10.4f} {:3s}'.format(
            trade_amount,
            buy_trade.plt_name, buy_trade.price, buy_trade.fiat,
            sell_trade.plt_name, sell_trade.price, sell_trade.fiat)


if __name__ == '__main__':
    okcoin = OKCoinCN()
    bitbays = BitBays()
    ok_trade = TradeInfo(okcoin, 'buy', 10, 0.01)
    bb_trade = TradeInfo(bitbays, 'sell', 10000, 0.01)
    trade_pair = ok_trade, bb_trade
    now = time.time()
    arbitrage = ArbitrageInfo(trade_pair, now)
    print(arbitrage)
    # arbitrage.process_trade()
    # if arbitrage.has_pending():
    #     arbitrage.adjust_pending()
    # assert arbitrage.done
    # print(arbitrage)
