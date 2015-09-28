#!/usr/bin/env python
from utils import log_helper


class OrderInstance(object):
    def __init__(self, catalog, start_time, remaining):
        self.catalog = catalog
        self.start_time = start_time
        self.remaining = remaining

    def set_remaining(self, remaining):
        self.remaining = remaining

    def __repr__(self):
        return "catalog={:<4s}, start_time={}".format(self.catalog, self.start_time)


class GridSlot(object):
    _logger = log_helper.get_logger()

    def __init__(self, price):
        self.price = price
        self.order_id_list = []

    def append_order(self, order_instance):
        self.order_id_list.append(order_instance)

    def __repr__(self):
        order_list_str = '\n'.join([str(order) for order in self.order_id_list])
        return 'price={}\n{}'.format(self.price, order_list_str)
