#!/usr/bin/env python
from __future__ import print_function
import time

from bitbays import BitBays
from okcoin import OKCoinCN


class TradeInfo(object):
    INVALID_ORDER_ID = -1

    def __init__(self, plt, trade_type, price, amount, fiat='cny'):
        self.plt = plt
        assert (trade_type in ['sell', 'buy'])
        self.type = trade_type
        self.amount = amount
        self.price = price
        self.fiat = fiat
        self.order_id = TradeInfo.INVALID_ORDER_ID  # to be accomplished

    def set_order_id(self, order_id):
        self.order_id = order_id

    def __repr__(self):
        plt_name = self.plt.__class__.__name__
        trade_info = '{:>10}: {} {:>10.4f} btc, Price {:>10.2f} {}' \
            .format(plt_name, self.type, self.amount, self.price, self.fiat)
        if self.order_id != -1:
            order_info = '{:<d}'.format(self.order_id)
            trade_info += ',\torder_id=' + order_info
        trade_info += ';'
        return trade_info

    def __str__(self):
        return self.__repr__()


class ArbitrageInfo(object):
    def __init__(self, trade_pair, time):
        self.trade_pair = trade_pair
        self.time = time
        self.pending = False

    def seconds_since_trade(self):
        return time.time() - self.time

    def process_trade(self):
        for trade in self.trade_pair:
            order_id = trade.plt.trade(trade.type, trade.price, trade.amount)
            trade.set_order_id(order_id)

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
    print(arbitrage)
