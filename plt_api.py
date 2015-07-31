#!/usr/bin/env python


class Platform(object):
    def __init__(self, info):
        self.domain = info['domain']
        self.key = None

    def _real_uri(self, api_type):
        pass

    def ask1(self):
        '''
        :return: ask1 price
        '''
        pass

    def bid1(self):
        '''
        :return: bid1 price
        '''
        pass

    def ask_bid_list(self, length):
        '''
        :param length: length of ask, bid
        :return: a single ask/bid list
        '''
        pass

    def trade(self, trade_type, price, amount):
        '''
        :param trade_type: sell/buy
        :param price:
        :param amount:
        :return: order id; if failed, return an invalid id
        '''
        pass

    def cancel(self, order_id):
        '''
        :param order_id:
        :return: True/False
        '''
        pass

    def assets(self):
        '''
        :return:
        '''
        pass

    # unused
    def buy_market(self, mo_amount):
        '''
        :param mo_amount: fiat unit
        :return:
        '''
        pass

    # sell amount is the BTC unit
    # unused
    def sell_market(self, mo_amount):
        '''
        :param mo_amount: btc unit
        :return:
        '''
        pass

    def order_info(self, order_id):
        '''
        :param order_id: order id
        :return: an OrderInfo instance
        '''
        pass

    def get_url(self, path):
        url = self.domain + path
        return url
