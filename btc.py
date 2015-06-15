#!/usr/bin/env python
import logging
import logging.handlers
import logging.config
import os
import errno
from common import setup_logger


class BTC(object):
    def __init__(self, info):
        self.info = info
        self.domain = info['domain']
        self.key = None
        self._btc_rate = None
        self.logger = setup_logger()

    def _real_uri(self, method):
        pass

    def ask_bid_list(self, length):
        pass

    def trade(self, trade_type, price, amount):
        pass

    def cancel(self, order_id):
        pass

    def assets(self):
        pass

    # buy amount is the CNY unit
    def buy_market(self, mo_amount):
        pass

    # sell amount is the BTC unit
    def sell_market(self, mo_amount):
        pass

    def get_url(self, path):
        url = self.domain + path
        # print(url)
        return url
