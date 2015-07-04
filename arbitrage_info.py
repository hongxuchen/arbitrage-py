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
        '''
        :param plt: platform, don't change
        :param catelog: sell/buy, don't change
        :param price: trade price, don't change
        :param amount: trade amount, don't change
        :param fiat: fiat, don't change
        '''
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

    def regular_trade(self):
        return self.plt.trade(self.catelog, self.price, self.amount)

    def get_price_and_afford(self):
        asset_info = AssetInfo(self.plt)
        if self.catelog == 'buy':
            trade_price = self.price * (1 + config.adjust_percentage)
            asset_amount = asset_info.afford_buy_amount(trade_price)
        else:  # self.catelog == 'sell'
            trade_price = self.price * (1 - config.adjust_percentage)
            asset_amount = asset_info.afford_sell_amount()
        return trade_price, asset_amount

    # it is ensured that this trade MUST succeed
    def adjust_trade(self):
        M = self.plt.__class__.lower_bound
        # no trading amount
        if self.amount < config.minor_diff:
            return
        wait_for_asset_times = 0
        # conflicts with self.amount >= M, do not change
        while self.amount < M:
            trade_price, asset_amount = self.get_price_and_afford()
            if asset_amount > self.amount + M:
                TradeInfo._logger.debug('bi-directional adjust_trade, waited {:d} times'.format(wait_for_asset_times))
                # trade1, must succeed
                self.plt.trade(self.catelog, trade_price, self.amount + M)
                # trade2, must succeed
                # FIXME: it has data race problem with arbitrage thread
                reverse_catelog = common.reverse_catelog(self.catelog)
                reverse_price = common.adjust_price(reverse_catelog, self.price)
                self.plt.trade(reverse_catelog, reverse_price, M)
            else:
                wait_for_asset_times += 1
                if wait_for_asset_times > config.ASSET_WAIT_MAX:
                    return
        if self.amount >= M:
            TradeInfo._logger.debug('single adjust_trade')
            trade_price, asset_amount = self.get_price_and_afford()
            self.plt.trade(self.catelog, trade_price, asset_amount)

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
    def __init__(self, trade_pair, time):
        self.trade_pair = trade_pair
        self.time = time
        self.pending = False
        self.min_plt = None
        self._order_dict = []
        self.done = False

    ### initial trading
    def process_trade(self):
        for trade in self.trade_pair:
            order_id = trade.regular_trade()
            trade.set_order_id(order_id)

    def normalize_trade_pair(self):
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

    def cancel_orders(self):
        for trade in self.trade_pair:
            trade.cancel()

    def init_order_dict(self):
        self._order_dict = []
        for trade in self.trade_pair:
            order_info = trade.get_order_info()
            self._order_dict.append(order_info)
        return self._order_dict

    def has_pending(self):
        self.init_order_dict()
        for order in self._order_dict:
            if order.has_pending():
                return True
        # no remaining amount, done
        self.done = True
        return False

    # adjust after finding has_pending
    # self._order_dict has been initialized
    def adjust(self):
        self.cancel_orders()
        t1, t2 = self.normalize_trade_pair()
        p1, p2 = t1.plt, t2.plt
        O1, O2 = self._order_dict[p1], self._order_dict[p2]
        A1, A2 = O1.remaining_amount, O2.remaining_amount
        M1 = p1.__class__.lower_bound
        M2 = p2.__class__.lower_bound
        if A2 < M2:
            A = A1 - A2
            if A < 0:
                trade_catelog = common.reverse_catelog(t1.catelog)
            else:
                trade_catelog = t1.catelog
            new_t1 = TradeInfo(p1, trade_catelog, t1.price, A)
            new_t1.adjust_trade()
        else:  # A2 >= M2:
            new_t1 = TradeInfo(p1, t1.type, t1.price, A1)
            new_t1.adjust_trade()
            new_t2 = TradeInfo(p2, t2.type, t2.price, A2)
            new_t2.adjust_trade()
        ### post-condition
        self.done = True

    @staticmethod
    def adjust_trade(self):
        pass

    def __repr__(self):
        trade_info = ''
        for trade in self.trade_pair:
            trade_info += str(trade) + ' '
        seconds = '{:10.2f}s ago'.format(time.time() - self.time)
        return trade_info + seconds


if __name__ == '__main__':
    okcoin = OKCoinCN()
    bitbays = BitBays()
    amount = 0.01
    ok_trade = TradeInfo(okcoin, 'buy', 1000, amount)
    bb_trade = TradeInfo(bitbays, 'sell', 3000, amount)
    trade_pair = ok_trade, bb_trade
    now = time.time()
    arbitrage = ArbitrageInfo(trade_pair, now)
    print(arbitrage)
    arbitrage.process_trade()
    print(arbitrage.init_order_dict())
    print(arbitrage)
    arbitrage.cancel_orders()
