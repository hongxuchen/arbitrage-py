#!/usr/bin/env python
import common
import logging_conf
from order_info import OrderInfo
import order_info


class OrderInstance(object):
    def __init__(self, plt, order_id, start_time):
        self.plt = plt
        self.order_id = order_id
        self.start_time = start_time

    def get_remaining(self):
        order_info = self.plt.order_info(self.order_id)
        return order_info.remaining_amount

    def __repr__(self):
        return "order_id={:<10d}, start_time={}".format(self.order_id, self.start_time)


class GridSlot(object):
    _logger = logging_conf.get_logger()

    def __init__(self, price):
        self.price = price
        self.order_list = []

    def append_order(self, order_instance):
        self.order_list.append(order_instance)

    def get_order_list(self):
        return [order.order_id for order in self.order_list]

    # TODO: batch cancel
    def cancel_orders(self):
        self._logger.info("cancel order for slot={}".format(self.price))
        for order in self.order_list:
            order_id = order.order_id
            self._logger.info("cancel order: {}".format(order_id))
            order.plt.cancel(order_id)

    def __repr__(self):
        order_list_str = '\n'.join([str(order) for order in self.order_list])
        return 'price={}\n{}'.format(self.price, order_list_str)
