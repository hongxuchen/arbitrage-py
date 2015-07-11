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
        ArbitrageInfo._logger.warning('Arbitrage Start')
        for trade in self.trade_pair:
            trade_price = common.adjust_arbitrage_price(trade.catelog, trade.price)
            order_id = trade.regular_trade(trade.catelog, trade_price, trade.amount)
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

    # FIXME decide how to cancel correctly
    def _cancel_orders(self):
        succeed_list = []
        for trade in self.trade_pair:
            status = trade.cancel()
            succeed_list.append(status)
        return succeed_list

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
        cancel_status_list = self._cancel_orders()
        t1, t2 = self.normalize_trade_pair()
        # ArbitrageInfo._logger.debug('Adjust Pair: {} {}'.format(t1, t2))
        p1, p2 = t1.plt, t2.plt
        O1, O2 = self._order_dict[p1], self._order_dict[p2]
        A1, A2 = O1.remaining_amount, O2.remaining_amount
        if cancel_status_list[0] is False:
            A1 = 0.0
        if cancel_status_list[1] is False:
            A2 = 0.0
        M1 = p1.__class__.lower_bound
        M2 = p2.__class__.lower_bound
        #################################
        # if A2 < M2:
        A = A1 - A2
        # ArbitrageInfo._logger.debug('A2<M2, A1={:<10.4f}, A2={:<10.4f}, A={:<10.4f}'.format(A1, A2, A))
        ArbitrageInfo._logger.info('A1={:<10.4f}, A2={:<10.4f}, A={:<10.4f}'.format(A1, A2, A))
        if A < 0:
            trade_catelog = common.reverse_catelog(t1.catelog)
        else:  # A >= 0
            trade_catelog = t1.catelog
        new_t1 = TradeInfo(p1, trade_catelog, t1.price, abs(A))
        common.MUTEX.acquire(True)  # blocking
        TradeInfo._logger.info('[Consumer] acquire lock')
        new_t1.adjust_trade()
        TradeInfo._logger.info('[Consumer] adjust done, release lock')
        common.MUTEX.release()
        # else:  # A2 >= M2:
        #     ArbitrageInfo._logger.debug('A2>=M2, A1={:<10.4f}, A2={:<10.4f}'.format(A1, A2))
        ##    FIXME this may introduce bug since one of new_t1, new_t2 may be canceled
        # new_t1 = TradeInfo(p1, t1.catelog, t1.price, A1)
        # new_t2 = TradeInfo(p2, t2.catelog, t2.price, A2)
        # config.MUTEX.acquire(True)  # blocking
        # new_t1.adjust_trade()
        # new_t2.adjust_trade()
        # config.MUTEX.release()
        #################################
        ### post-condition
        self.done = True

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
        return 'Amount={}, {:10s} buy at {:10.4f}, {:10s} sell at {:10.4f}'.format(
            buy_trade.plt_name, buy_trade.price, sell_trade.plt_name, sell_trade.price)


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
