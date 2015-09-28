#!/usr/bin/env python
from settings import config


class OrderInfo(object):
    def __init__(self, catalog, remaining_amount):
        assert (catalog in ['buy', 'sell'])
        self.catalog = catalog
        self.remaining_amount = remaining_amount

    def has_pending(self):
        return self.remaining_amount > config.MINOR_DIFF

    def __repr__(self):
        return 'catalog: {}, remaining: {:10.4f}'.format(self.catalog, self.remaining_amount)


# TODO merge with OrderInfo
class PlatformOrderInfo(object):
    """
    abstract class for storing order info from platform
    """

    def __init__(self, order_id, catalog, remaining):
        self.catalog = catalog
        self.order_id = order_id
        self.remaining = remaining

    def __repr__(self):
        return 'id={:<15d} catalog={:<4s} remaining={:<10.4f}'.format(self.order_id, self.catalog, self.remaining)
