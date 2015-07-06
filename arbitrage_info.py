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
        self.trade_pair = trade_pair
        self.time = time
        self.done = False

    def process_trade(self):
        """
        inital trading, this guarantees that the asset is enough
        :return:
        """
        ArbitrageInfo._logger.debug('Arbitrage Start')
        for trade in self.trade_pair:
            config.MUTEX.acquire(True)  # blocking
            order_id = trade.regular_trade(trade.catelog, trade.price, trade.amount)
            config.MUTEX.release()
            trade.set_order_id(order_id)

    def normalize_trade_pair(self):
        """
        only 2 platforms; first is trade whose lower_bound is smaller
        :return: trade pair
        """
        ta = self.trade_pair[0]
        tb = self.trade_pair[1]
        ma = ta.plt.__class__.lower_bound
        mb = tb.plt.__class__.lower_bound
        if ma < mb:
            return ta, tb
        else:
            return tb, ta

    def seconds_since_trade(self):
        return time.time() - self.time

    def _cancel_orders(self):
        for trade in self.trade_pair:
            trade.cancel()

    def _init_order_dict(self):
        """ self._order_dict is initialized/changed for each adjust
        :return: order dict
        """
        self._order_dict = {}
        for trade in self.trade_pair:
            order_info = trade.get_order_info()
            self._order_dict[trade.plt] = order_info
        return self._order_dict

    def has_pending(self):
        """
        has pending when at least one platform has pending
        need to get order dict for current arbitrage pair
        :return:
        """
        self.done = False
        self._init_order_dict()
        for order in self._order_dict.values():
            if order.has_pending():
                return True
        # no remaining amount, no need to adjust_pending, done
        self.done = True
        return False

    # noinspection PyPep8Naming
    def adjust_pending(self):
        """adjust after finding has_pending; self._order_dict has been initialized
        :return: None
        """
        self._cancel_orders()
        t1, t2 = self.normalize_trade_pair()
        # ArbitrageInfo._logger.debug('Adjust Pair: {} {}'.format(t1, t2))
        p1, p2 = t1.plt, t2.plt
        O1, O2 = self._order_dict[p1], self._order_dict[p2]
        A1, A2 = O1.remaining_amount, O2.remaining_amount
        M1 = p1.__class__.lower_bound
        M2 = p2.__class__.lower_bound
        if A2 < M2:
            A = A1 - A2
            ArbitrageInfo._logger.debug('A2<M2, A1={:<10.4f}, A2={:<10.4f}, A={:<10.4f}'.format(A1, A2, A))
            if A < 0:
                trade_catelog = common.reverse_catelog(t1.catelog)
            else:  # A >= 0
                trade_catelog = t1.catelog
            new_t1 = TradeInfo(p1, trade_catelog, t1.price, A)
            config.MUTEX.acquire(True)  # blocking
            new_t1.adjust_trade()
            config.MUTEX.release()
        else:  # A2 >= M2:
            ArbitrageInfo._logger.debug('A2>=M2, A1={:<10.4f}, A2={:<10.4f}'.format(A1, A2))
            # FIXME this may introduce bug since one of new_t1, new_t2 may be canceled
            new_t1 = TradeInfo(p1, t1.catelog, t1.price, A1)
            new_t2 = TradeInfo(p2, t2.catelog, t2.price, A2)
            config.MUTEX.acquire(True)  # blocking
            new_t1.adjust_trade()
            new_t2.adjust_trade()
            config.MUTEX.release()
        ### post-condition
        self.done = True

    def __repr__(self):
        trade_info = ''
        for trade in self.trade_pair:
            trade_info += str(trade) + ' '
        seconds = '{:10.2f}s ago'.format(time.time() - self.time)
        return trade_info + seconds


if __name__ == '__main__':
    okcoin = OKCoinCN()
    bitbays = BitBays()
    ok_trade = TradeInfo(okcoin, 'buy', 1615, 0.01)
    bb_trade = TradeInfo(bitbays, 'sell', 1635, 0.008)
    trade_pair = ok_trade, bb_trade
    now = time.time()
    arbitrage = ArbitrageInfo(trade_pair, now)
    print(arbitrage)
    arbitrage.process_trade()
    # if arbitrage.has_pending():
    #     arbitrage.adjust_pending()
    # assert arbitrage.done
    print(arbitrage)
