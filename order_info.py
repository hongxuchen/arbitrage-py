#!/usr/bin/env python
import config


class OrderInfo(object):
    def __init__(self, catalog, remaining_amount):
    # def __init__(self, catalog, remaining_amount, create_time):
        assert (catalog in ['buy', 'sell'])
        self.catalog = catalog
        self.remaining_amount = remaining_amount
        # self.create_time = create_time

    # def seconds_since_created(self):
    #     now = time.time()
    #     return now - self.create_time

    def has_pending(self):
        return self.remaining_amount > config.minor_diff

    def __repr__(self):
        return 'catalog: {}, remaining: {:6f}'.format(self.catalog, self.remaining_amount)
        # return 'catalog: {}, remaining: {:6f}, seconds_since_created: {:6f}' \
        #     .format(self.catalog, self.remaining_amount, self.seconds_since_created())
