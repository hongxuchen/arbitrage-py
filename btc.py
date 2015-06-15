#!/usr/bin/env python
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

    def ask1(self):
        pass

    def ask_bid_list(self, length):
        '''
        :param length: length of ask, bid
        :return: a single ask/bid list
        '''
        pass

    def trade(self, trade_type, price, amount):
        '''
        :param trade_type:
        :param price:
        :param amount:
        :return:
        '''
        pass

    def cancel(self, order_id):
        '''
        :param order_id:
        :return:
        '''
        pass

    def assets(self):
        '''
        :return:
        '''
        pass

    def buy_market(self, mo_amount):
        '''
        :param mo_amount: fiat unit
        :return:
        '''
        pass

    # sell amount is the BTC unit
    def sell_market(self, mo_amount):
        '''
        :param mo_amount: btc unit
        :return:
        '''
        pass

    def order_info(self, order_id):
        '''
        :param order_id: order id
        :return: a OrderInfo instance
        '''
        pass

    def get_url(self, path):
        url = self.domain + path
        # print(url)
        return url
