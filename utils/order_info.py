#!/usr/bin/env python
# -*- coding: utf-8 -*-

from settings import config


# TODO merge with OrderInfo
class PlatformOrderInfo(object):
    """
    abstract class for storing order info from platform
    """

    def __init__(self, order_id, catalog, remaining):
        self.catalog = catalog
        self.order_id = order_id
        self.remaining_amount = remaining

    def has_pending(self):
        return self.remaining_amount > config.MINOR_DIFF

    def __repr__(self):
        return 'id={:<15d} catalog={:<4s} remaining={:<10.4f}'.format(self.order_id, self.catalog, self.remaining_amount)
