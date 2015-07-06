#!/usr/bin/env python
from __future__ import print_function
import time

from asset_info import AssetInfo
from bitbays import BitBays
import common
import config
from okcoin import OKCoinCN


class TradeInfo(object):
    INVALID_ORDER_ID = -1
    _logger = common.setup_logger()

    def __init__(self, plt, catelog, price, amount, fiat='cny'):
        """
        :param plt: platform, don't change
        :param catelog: sell/buy, don't change
        :param price: trade price, don't change
        :param amount: trade amount, don't change
        :param fiat: fiat, don't change
        """
        self.plt = plt
        assert (catelog in ['sell', 'buy'])
        self.catelog = catelog
        self.amount = amount
        self.price = price
        self.fiat = fiat
        # initialized with an invalid number
        self.order_id = TradeInfo.INVALID_ORDER_ID  # to be accomplished

    def set_order_id(self, order_id):
        self.order_id = order_id

    @staticmethod
    def regular_trade(plt, catelog, price, amount):
        """
        regular trade, may cause pending
        :return: order_id
        """
        order_id = plt.trade(catelog, price, amount)
        TradeInfo._logger.debug(
            'regular_trade {}: {} {} btc at price {} cny, order_id={:d}'.format(plt.__class__.__name__, catelog, amount,
                                                                                price, order_id))
        return order_id

    def _asset_afford_trade(self, trade_amount, trade_price):
        """
        test whether there is enough asset to afford trade, catelog is self.catelog
        :param trade_amount:
        :return:
        """
        # trade_price = common.adjust_price(self.catelog, self.price)
        waited_asset_times = 0
        while True:
            ### request here
            asset_info = AssetInfo(self.plt)
            if self.catelog == 'buy':
                asset_amount = asset_info.afford_buy_amount(trade_price)
            else:  # sell
                asset_amount = asset_info.afford_sell_amount()
            if asset_amount >= trade_amount:
                return True
            else:
                waited_asset_times += 1
                if waited_asset_times >= config.ASSET_WAIT_MAX:
                    TradeInfo._logger.debug(
                        'asset cannot afford trading after waiting {} times'.format(config.ASSET_WAIT_MAX))
                    return False

    # noinspection PyPep8Naming
    def adjust_trade(self):
        """
        this trade ensures that there will be no pending afterwards:
          1. meet the lower_bound limit for each platform
             if amount >= M, regular trade; if amount < M, a bidirectional trade is provided
          2. there will be enough asset for sell(BTC) or buy(fiat/CNY)
             calculate for current asset
          3. the price is higher for buy or lower for sell
             adjust_price with a certain percentage
        :return: None
        """
        M = self.plt.__class__.lower_bound
        # no trading amount
        if self.amount < config.minor_diff:
            return
        # config.minor_diff <= self.amount
        wait_for_asset_times = 0
        # conflicts with self.amount >= M, do not change
        if self.amount < M:
            trade_amount = self.amount + M
            trade_catelog = self.catelog
            trade_price = common.adjust_price(trade_catelog, self.price)
            if self._asset_afford_trade(trade_amount, trade_price):
                TradeInfo._logger.debug('bi-directional adjust_trade, waited {:d} times'.format(wait_for_asset_times))
                # trade1, must succeed
                TradeInfo.regular_trade(self.plt, trade_catelog, trade_price, trade_amount)
                # trade2, must succeed
                # FIXME: it has data race problem with arbitrage thread
                reverse_amount = M
                reverse_catelog = common.reverse_catelog(trade_catelog)
                reverse_price = common.adjust_price(reverse_catelog, self.price)
                TradeInfo.regular_trade(self.plt, reverse_catelog, reverse_price, reverse_amount)
        else:  # self.amount >= M
            trade_price = common.adjust_price(self.catelog, self.price)
            trade_catelog = self.catelog
            trade_amount = self.amount
            if self._asset_afford_trade(trade_amount, trade_price):
                # trade must succeed
                TradeInfo._logger.debug('single adjust_trade, waited {:d} times'.format(wait_for_asset_times))
                TradeInfo.regular_trade(self.plt, trade_catelog, trade_price, trade_amount)

    def cancel(self):
        if self.order_id != -1:
            self.plt.cancel(self.order_id)

    def get_order_info(self):
        return self.plt.order_info(self.order_id)

    def __repr__(self):
        plt_name = self.plt.__class__.__name__
        trade_info = '{:>10}: {} {:>10.4f} btc, Price {:>10.2f} {}' \
            .format(plt_name, self.catelog, self.amount, self.price, self.fiat)
        if self.order_id != -1:
            order_info = '{:<d}'.format(self.order_id)
            trade_info += ',\torder_id=' + order_info
        trade_info += ';'
        return trade_info


class ArbitrageInfo(object):
    _logger = common.setup_logger()

    def __init__(self, trade_pair, time):
        self.trade_pair = trade_pair
        self.time = time
        self.done = False

    ### initial trading
    def process_trade(self):
        ArbitrageInfo._logger.debug('Arbitrage Start')
        for trade in self.trade_pair:
            order_id = TradeInfo.regular_trade(trade.plt, trade.catelog, trade.price, trade.amount)
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
            if A < 0:
                trade_catelog = common.reverse_catelog(t1.catelog)
            else:  # A >= 0
                trade_catelog = t1.catelog
            new_t1 = TradeInfo(p1, trade_catelog, t1.price, A)
            new_t1.adjust_trade()
        else:  # A2 >= M2:
            # FIXME this may introduce bug since one of new_t1, new_t2 may be canceled
            new_t1 = TradeInfo(p1, t1.catelog, t1.price, A1)
            new_t1.adjust_trade()
            new_t2 = TradeInfo(p2, t2.catelog, t2.price, A2)
            new_t2.adjust_trade()
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
