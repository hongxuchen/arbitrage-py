#!/usr/bin/env python

from __future__ import print_function


class TradeInfo(object):
    def __init__(self, plt, trade_type, price, amount, fiat='cny'):
        self.plt = plt
        assert (trade_type in ['sell', 'buy'])
        self.type = trade_type
        self.amount = amount
        self.price = price
        self.fiat = fiat

    def __repr__(self):
        plt_name = self.plt.__class__.__name__
        return '{:>10}: {} {} btc at Price {}{}'.format(plt_name, self.type, self.amount, self.price, self.fiat)

    def __str__(self):
        return self.__repr__()
