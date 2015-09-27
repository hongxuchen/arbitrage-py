#!/usr/bin/env python
import settings.config


class OrderInfo(object):
    def __init__(self, catalog, remaining_amount):
        assert (catalog in ['buy', 'sell'])
        self.catalog = catalog
        self.remaining_amount = remaining_amount

    def has_pending(self):
        return self.remaining_amount > settings.config.MINOR_DIFF

    def __repr__(self):
        return 'catalog: {}, remaining: {:10.4f}'.format(self.catalog, self.remaining_amount)
