#!/usr/bin/env python

from __future__ import print_function
import time

# this class is used to help deal with the remaining pending order
class OrderInfo(object):
    def __init__(self, catalog, remaining_amount, create_time):
        assert(catalog in ['buy', 'sell'])
        self.catalog = catalog
        self.remaining_amount = remaining_amount
        self.create_time = create_time

    def seconds_since_created(self):
        now = time.time()
        return now - self.create_time

    def __str__(self):
        return 'catalog: {}, remaining: {:6f}, seconds_since_created: {:6f}' \
            .format(self.catalog, self.remaining_amount, self.seconds_since_created())


if __name__ == '__main__':
    order_info = OrderInfo('buy', 0.02, 1434270483)
    print(order_info)
