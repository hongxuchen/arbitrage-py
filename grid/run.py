#!/usr/bin/env python
from itertools import chain

# how to get finished

import time
import sys

from utils.asset_info import AssetInfo
import conf
from settings import config
from slot import OrderInstance, GridSlot
from utils import log_helper
from api.okcoin import OKCoinCN


def finished_order_handler(order_instance):
    """
    :param order_instance:
    :return:
    """
    pass


def cancel_order(order_instance):
    """
    should deal with slot and order_instance_dict
    this only deal with 'timeout' unfinished order
    :param order_instance:
    :return:
    """
    pass


class Grid(object):
    _logger = log_helper.get_logger()
    lower_bound = conf.grid_range[0]
    upper_bound = conf.grid_range[1]
    grid_diff = conf.grid_diff
    amount = conf.order_amount
    batch_check_num = conf.batch_check_num

    def __init__(self, plt):
        self.plt = plt
        self.order_recorder = {
            'buy': [],
            'sell': []
        }
        self.order_instance_dict = dict()

    def _find_slot_index(self, catalog, price):
        """
        :param catalog:
        :param price:
        :return: if find, return (True,index); otherwise, return (False, index); True/False indicates found or not
        """

        slot_list = self.order_recorder[catalog]
        for i in xrange(len(slot_list)):
            if abs(slot_list[i].price - price) < config.MINOR_DIFF:
                return True, i
            # DESC
            if catalog == 'buy' and price - slot_list[i].price > config.MINOR_DIFF:
                return False, i
            # ASC
            elif catalog == 'sell' and slot_list[i].price - price > config.MINOR_DIFF:
                return False, i
        return False, len(slot_list)

    def _make_order(self, catalog, price):
        order_id = self.plt.trade(catalog, price, self.amount)
        # print(order_id)
        found, index = self._find_slot_index(catalog, price)
        if found:
            grid_slot = self.order_recorder[catalog][index]
        else:
            grid_slot = GridSlot(price)
            self.order_recorder[catalog].insert(index, grid_slot)
        grid_slot.append_order(order_id)
        instance = OrderInstance(catalog, int(time.time()), self.amount)
        self.order_instance_dict[order_id] = instance

    # TODO should provide an option for this since NOT always should cancel
    def cancel_all_orders(self):
        """
        cancel all orders finally
        :return:
        """
        for order_id in self.order_instance_dict:
            # TODO may fail, but not serious
            self.plt.cancel(order_id)
        self.order_recorder = dict()
        self.order_instance_dict = dict()


    def update_pending_orders(self):
        pending_id_list = []
        pending_dict = self.plt.pending_orders()
        for catalog in pending_dict:
            for pending in pending_dict[catalog]:
                pending_id = pending.order_id
                pending_id_list.append(pending_id)
                grid_order = self.order_instance_dict[pending_id]
                grid_order.set_remaining(pending.remaining)
        return pending_id_list

    def local_orders_handler(self):
        """
        deal with pending order timeouts, this works in "orders_recorder"
        :return:
        """
        pending_id_list = self.update_pending_orders()
        for catalog in self.order_recorder:
            for slot in self.order_recorder[catalog]:
                for order_id in slot.order_id_list:
                    if order_id not in pending_id_list:
                        self.finished_list_handler(order_id)
                    else:
                        pass

    def init_grid(self):
        """
        initialize (buy) grid
        :return:
        """
        price = self.upper_bound
        size = (self.upper_bound - self.lower_bound) / self.grid_diff
        asset = AssetInfo.from_api(self.plt)
        to_consume = (self.upper_bound + self.lower_bound + self.grid_diff) / 2.0 * size * self.amount
        if asset.fiat_avail < to_consume:
            self._logger.critical("cannot afford to buy, avail={}, to_consume={}".format(asset.fiat_avail, to_consume))
            sys.exit(1)
        while price > self.lower_bound:
            self._make_order('buy', price)
            price -= self.grid_diff

    def dump_order_info(self):
        for catalog in self.order_recorder:
            print(catalog)
            order_list = self.order_recorder[catalog]
            for slot in order_list:
                print(slot)

    def finished_list_handler(self, order_id):
        pass


if __name__ == '__main__':
    log_helper.init_logger()
    okcoin = OKCoinCN()
    print(okcoin.pending_orders())
    # grid = Grid(okcoin)
    # grid.init_grid()
    # grid.dump_orders()
    # grid.cancel_all()
