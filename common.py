#!/usr/bin/env python

from __future__ import print_function
import decimal
import threading
import math
import requests

import config
import logging_conf


def synchronized(lock):
    """ Synchronization decorator. """

    def wrap(f):
        def new_func(*args, **kw):
            lock.acquire()
            try:
                return f(*args, **kw)
            finally:
                lock.release()

        return new_func

    return wrap


def get_usd_cny_rate():
    r = requests.get("http://finance.yahoo.com/d/quotes.csv?e=.csv&f=sl1d1t1&s=USDCNY=X", timeout=config.TIMEOUT)
    return decimal.Decimal(r.text.split(",")[1])


def to_decimal(value_str, precision=config.DISPLAY_PRECISION):
    return round(float(value_str), precision)


def reverse_catalog(original_catalog):
    assert (original_catalog in ['buy', 'sell'])
    if original_catalog == 'buy':
        return 'sell'
    else:  # sell
        return 'buy'


def round_price(price, precision=config.HuoBi_Price_Precision):
    return round(price, precision)


def adjust_price(trade_catalog, price):
    logging_conf.get_logger().info('trade_catalog={}, price={}'.format(trade_catalog, price))
    assert (trade_catalog in ['buy', 'sell'])
    if trade_catalog == 'buy':
        new_price = price * (1 + config.ADJUST_PERCENTAGE)
    else:  # sell
        new_price = price * (1 - config.ADJUST_PERCENTAGE)
    return round_price(new_price)


def adjust_amount(trade_amount, precision=config.TRADE_PRECISION):
    return math.floor(trade_amount * (10 ** precision)) / (10 ** precision)


MUTEX = threading.Lock()
SIGNAL = None

if __name__ == '__main__':
    logging_conf.init_logger()
