#!/usr/bin/env python
from itertools import chain
import time
import sys

from asset_info import AssetInfo
import grid_conf
from grid_order import OrderInstance, GridSlot
import logging_conf
from api.okcoin import OKCoinCN


class Grid(object):
    _logger = logging_conf.get_logger()
    lower_bound = grid_conf.grid_range[0]
    upper_bound = grid_conf.grid_range[1]
    grid_diff = grid_conf.grid_diff
    amount = grid_conf.order_amount
    batch_check_num = grid_conf.batch_check_num

    def __init__(self, plt):
        self.plt = plt
        self.buy_list = []
        self.partial_orders = []

    def init_grid(self):
        price = self.upper_bound
        size = (self.upper_bound - self.lower_bound) / self.grid_diff
        asset = AssetInfo.from_api(self.plt)
        to_consume = (self.upper_bound + self.lower_bound + self.grid_diff) / 2.0 * size * self.amount
        if asset.fiat_avail < to_consume:
            self._logger.critical("cannot afford to buy, avail={}, to_consume={}".format(asset.fiat_avail, to_consume))
            sys.exit(1)
        while price > self.lower_bound:
            order_id = self.plt.trade('buy', price, self.amount)
            now = int(time.time())
            order = OrderInstance(self.plt, order_id, now)
            grid_slot = GridSlot(price)
            grid_slot.append_order(order)
            self.buy_list.append(grid_slot)
            price -= self.grid_diff

    # TODO: should check quickly
    def check_orders(self, order_list):
        should_continue = True
        to_sell_order_list = []
        i = 0
        old_id = 0
        order_id_list = [instance.get_order_list() for instance in order_list]
        flat_order_id_list = list(chain.from_iterable(order_id_list))
        buy_max = len(flat_order_id_list)
        while should_continue and i < buy_max:
            check_size = min(buy_max, self.batch_check_num - i)
            old_id = i
            i += self.batch_check_num

    def bought_handler(self):
        pass

    def cancel_all(self):
        for buy in self.buy_list:
            buy.cancel_orders()


if __name__ == '__main__':
    logging_conf.init_logger()
    okcoin = OKCoinCN()
    grid = Grid(okcoin)
    grid.init_grid()
    # grid.cancel_all()
