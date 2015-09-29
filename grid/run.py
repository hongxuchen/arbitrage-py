#!/usr/bin/env python

import time
import sys

from utils.asset_info import AssetInfo
from utils import common
from settings import config
from slot import GridInstance, GridSlot
from utils import log_helper


class Grid(object):
    _logger = log_helper.get_logger()
    grid_min, grid_max = config.grid_range

    def __init__(self, plt):
        self.plt = plt
        self.orders_recorder = {
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

        slot_list = self.orders_recorder[catalog]
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

    def _make_order(self, catalog, price, grid_slot=None):
        order_id = self.plt.trade(catalog, price, config.grid_order_amount)
        if grid_slot is None:
            found, index = self._find_slot_index(catalog, price)
            if found:
                grid_slot = self.orders_recorder[catalog][index]
            else:
                grid_slot = GridSlot(catalog, price)
                self.orders_recorder[catalog].insert(index, grid_slot)
        grid_slot.append_order(order_id)
        instance = GridInstance(catalog, int(time.time()), config.grid_order_amount)
        self.order_instance_dict[order_id] = instance

    # TODO should provide an option for this since NOT always should cancel
    # FIXME if we use local time and don't persistent it, we HAVE to cancel all
    def cancel_all_orders(self):
        """
        cancel all orders finally
        :return:
        """
        for order_id in self.order_instance_dict:
            # TODO may fail, but not serious
            self.plt.cancel(order_id)
        self.orders_recorder = dict()
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

    def _cleanup_orders(self, order_list, slot):
        for order_id in order_list:
            del self.order_instance_dict[order_id]
            slot.remove(order_id)

    def _reset_slot_orders(self, slot):
        for order_id in slot.order_id_list:
            del self.order_instance_dict[order_id]
        slot.order_id_list = []

    # TODO may fail; batch cancel
    def cancel_slot_orders(self, slot):
        for order_id in slot.order_id_list:
            self.plt.cancel(order_id)

    @staticmethod
    def grid_reverse_price(current_catalog, price):
        if current_catalog == 'buy':
            reverse_price = price + config.grid_buy_sell_diff
        else:
            assert (current_catalog == 'sell')
            reverse_price = price - config.grid_buy_sell_diff
        return reverse_price

    def _handle_slot(self, slot, global_pending_list):
        """
        :param slot:
        :param global_pending_list:
        :return:
        """

        def timeout(order_instance, now):
            return now - order_instance.start_time > config.grid_cancel_duration

        slot_pending_list = [order_id for order_id in slot.order_id_list if order_id in global_pending_list]
        slot_finished_list = [order_id for order_id in slot.order_id_list if order_id not in global_pending_list]
        total_remaining = sum(self.order_instance_dict[order_id].remaining for order_id in global_pending_list)
        lower_bound = self.plt.lower_bound_dict[self.plt.coin_type]
        if len(slot_pending_list) == 0 or total_remaining < lower_bound:
            self._reset_slot_orders(slot)
            reverse_catalog = common.reverse_catalog(slot.catalog)
            reverse_price = self.grid_reverse_price(slot.catalog, slot.price)
            self._make_order(reverse_catalog, reverse_price)
        else:  # has pending and total_remaining >= lower_bound
            now = int(time.time())
            has_timeout = any(timeout(self.order_instance_dict[order_id], now) for order_id in slot_pending_list)
            # has >= 1 timeout, cancel all; order one
            if config.AVOID_TIMEOUT and has_timeout:
                self.cancel_slot_orders(slot)
                self._reset_slot_orders(slot)
                self._make_order(slot.catalog, slot.price, slot)
            else:  # if no timeouts, deal with finished
                self._cleanup_orders(slot, slot_finished_list)

    def local_orders_handler(self):
        """
        deal with pending order timeouts, this works in "orders_recorder"
        :return:
        """
        pending_id_list = self.update_pending_orders()
        for catalog in self.orders_recorder:
            for slot in self.orders_recorder[catalog]:
                self._handle_slot(slot, pending_id_list)

    def init_grid(self):
        """
        initialize (buy) grid
        :return:
        """
        price = self.grid_max
        size = (self.grid_max - self.grid_min) / config.grid_price_diff
        asset = AssetInfo.from_api(self.plt)
        to_consume = (
                     self.grid_max + self.grid_min + config.grid_price_diff) / 2.0 * size * config.grid_order_amount
        if asset.fiat_avail < to_consume:
            self._logger.critical("cannot afford to buy, avail={}, to_consume={}".format(asset.fiat_avail, to_consume))
            sys.exit(1)
        while price > self.grid_min:
            self._make_order('buy', price)
            price -= config.grid_price_diff

    def run_main(self):
        try:
            while True:
                time.sleep(config.sleep_seconds)
        except KeyboardInterrupt:
            pass
        if config.grid_cancel_all:
            self.cancel_all_orders()


if __name__ == '__main__':
    log_helper.init_logger()
