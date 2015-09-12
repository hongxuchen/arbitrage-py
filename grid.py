#!/usr/bin/env python
import random
import time
import common
import config
import grid_conf
from grid_order import GridOrderInfo
from okcoin import OKCoinCN


class Grid(object):
    _logger = common.get_logger()

    def __init__(self, plt):
        self.plt = plt
        self.lower_bound = grid_conf.grid_range[0]
        self.upper_bound = grid_conf.grid_range[1]
        self.size = (self.upper_bound - self.lower_bound) / grid_conf.order_diff + 1
        self.buy_orders = [None] * self.size
        self.sell_orders = [None] * self.size
        self.amount = grid_conf.order_amount

    def single_trade(self, catalog, price):
        now = int(time.time())
        order_id = random.randint(1, 100)
        if order_id != config.INVALID_ORDER_ID:
            grid_order = GridOrderInfo(order_id, catalog, now)
            if catalog == 'buy':
                index = int(round((price - self.lower_bound) / grid_conf.order_diff))
            else:
                index = int(round(price - self.lower_bound - grid_conf.buy_sell_diff) / grid_conf.order_diff)
            assert (self.buy_orders[index] is None)
            self.buy_orders[index] = grid_order
            self._logger.warning("index={:03d}, {}".format(index, grid_order))
        else:
            print("error")

    def init(self):
        for i in xrange(self.size):
            price = self.lower_bound + grid_conf.order_diff * i
            self.single_trade('buy', price)

    def find_bought_list(self):
        pass

    def find_sold_list(self):
        pass

    def run_main(self):
        while True:
            bought_list = self.find_bought_list()
            for to_sell in bought_list:
                amount = to_sell.


if __name__ == '__main__':
    common.init_logger()
    okcoin = OKCoinCN()
    grid = Grid(okcoin)
    grid.init()
