#!/usr/bin/env python

class GridOrderInfo(object):
    def __init__(self, order_id, catalog, start_time):
        self.order_id = order_id
        self.catalog = catalog
        self.start_time = start_time

    def __repr__(self):
        return "order_id={:<10d}, catalog={:4s}, start_time={}".format(self.order_id, self.catalog, self.start_time)
