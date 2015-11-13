#!/usr/bin/env python

from utils import plt_helper


class Platform(object):
    def __init__(self, info):
        """
        :param info: the platform information dict
        a platform should specify 'fiat', 'prefix'; 'public_prefix' is optional
        :return:
        """
        self.coin_type = plt_helper.get_key_from_data('CoinType')
        self.fiat_type = info['fiat']
        self.prefix = info['prefix']
        if 'public_prefix' in info:
            self.public_prefix = info['public_prefix']
        self.key = plt_helper.get_key_from_data(self.plt_name)

    @property
    def plt_name(self):
        return self.__class__.__name__

    def ask1(self):
        """
        :return: ask1 price
        """
        pass

    def bid1(self):
        """
        :return: bid1 price
        """
        pass

    def ask_bid_list(self, length):
        """
        :param length: length of ask, bid
        :return: a single ask/bid list
        """
        pass

    def trade(self, trade_type, price, amount):
        """
        :param trade_type: sell/buy
        :param price:
        :param amount:
        :return: order id; if failed, return an invalid id
        """
        pass

    def cancel(self, order_id):
        """
        :param order_id:
        :return: True/False
        """
        pass

    def assets(self):
        """
        :return:
        """
        pass

    # unused
    def buy_market(self, mo_amount):
        """
        :param mo_amount: fiat unit
        :return:
        """
        pass

    # unused
    def sell_market(self, mo_amount):
        """
        :param mo_amount: coin unit
        :return:
        """
        pass

    def order_info(self, order_id):
        """
        :param order_id: order id
        :return: a PlatformOrderInfo instance
        """
        pass
