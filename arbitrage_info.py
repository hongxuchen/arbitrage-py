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

    def process_trade(self):
        """
        inital trading, this guarantees that the asset is enough
        :return:
        """
        ArbitrageInfo._logger.warning('Arbitrage Start')
        for trade in self.trade_pair:
            order_id = trade.regular_trade(trade.catelog, trade.price, trade.amount)
            trade.set_order_id(order_id)

    def normalize_trade_pair(self):
        """
        only 2 platforms; first is trade whose lower_bound is smaller
        :return: trade pair
        """
        ta = self.trade_pair[0]
        tb = self.trade_pair[1]
        ma = ta.plt.lower_bound
        mb = tb.plt.lower_bound
        if ma < mb:
            return ta, tb
        else:
            return tb, ta

    def seconds_since_trade(self):
        return time.time() - self.time

    def get_order_adjust_dict(self):
        """
        if finding pending, cancel order ASAP; cancel failure means no pending!
        NOTE: order_id is useless after this
        :return:
        """
        order_info_dict = {}
        for trade in self.trade_pair:
            order_info = trade.get_order_info()
            if order_info.has_pending():
                cancel_status = trade.cancel()
                if cancel_status is False:
                    order_info.remaining_amount = 0.0
            order_info_dict[trade.plt] = order_info
        return order_info_dict

    # noinspection PyPep8Naming
    def adjust_pending(self):
        adjust_dict = self.get_order_adjust_dict()
        t1, t2 = self.normalize_trade_pair()
        p1, p2 = t1.plt, t2.plt
        O1, O2 = adjust_dict[p1], adjust_dict[p2]
        A1, A2 = O1.remaining_amount, O2.remaining_amount
        M1 = p1.lower_bound
        M2 = p2.lower_bound
        #################################
        # if A2 < M2:
        A = A1 - A2
        # ArbitrageInfo._logger.debug('A2<M2, A1={:<10.4f}, A2={:<10.4f}, A={:<10.4f}'.format(A1, A2, A))
        ArbitrageInfo._logger.warning('A1={:<10.4f}, A2={:<10.4f}, A={:<10.4f}'.format(A1, A2, A))
        if A < -config.minor_diff:
            trade_catelog = common.reverse_catelog(t1.catelog)
        elif A > config.minor_diff:  # A >= 0
            trade_catelog = t1.catelog
        else:
            return
        amount = abs(A)
        # not really care about the EXACT price
        new_t1 = TradeInfo(p1, trade_catelog, t1.price, amount)
        common.MUTEX.acquire(True)  # blocking
        ArbitrageInfo._logger.info('[Consumer] acquire lock')
        t1_adjust_status = new_t1.adjust_trade()
        if t1_adjust_status is False:
            new_t2 = TradeInfo(p2, trade_catelog, t1.price, amount)
            # TODO more code review here
            t2_adjust_status = new_t2.adjust_trade()
            # should be rather rare case
            if t2_adjust_status is False:
                ArbitrageInfo._logger.critical('CRITAL: [{}, {}] cannot adjust'.format(t1.plt_name, t2.plt_name))
                # TODO may need to use monitor here; quite complicated here
        ArbitrageInfo._logger.info('[Consumer] adjust done, release lock')
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
