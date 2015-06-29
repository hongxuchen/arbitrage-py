#!/usr/bin/env python

from PySide import QtCore

from bitbays import BitBays
import common
import config
from okcoin import OKCoinCN


class ArbitrageConsumer(QtCore.QThread):
    _logger = common.setup_logger()

    def __init__(self, arbitrage_list, api, parent=None):
        super(ArbitrageConsumer, self).__init__(parent)
        self.api = api
        self.pending = True
        self.running = False
        self.queue = arbitrage_list

    def _get_order_info(self, order_id):
        order_info = self.api.order_info(order_id)
        ArbitrageConsumer._logger.debug('ORDER_INFO:{}'.format(order_info))
        return order_info

    def consume(self):
        for q in self.queue:
            # TODO
            pass

    def adjust_price(self, order_id):
        order_info = self._get_order_info(order_id)
        remaining = order_info.remaining_amount
        if remaining < config.minor_diff:
            self.pending = False
            return
        if order_info.seconds_since_created() > config.max_pending_seconds:
            self.api.cancel(order_id)
            self.pending = False
            # normal case, all remaining should be used to trade
            if remaining >= config.lower_bound:
                mo_amount = remaining
            # should use lower_bound
            elif remaining >= config.lower_bound * config.lower_rate:
                mo_amount = config.lower_bound
            # discard, simply cancel
            else:
                return
            ArbitrageConsumer._logger.debug("adjust_price")
            # TODO

    def run(self):
        while self.running:
            self.consume()


if __name__ == '__main__':
    api = BitBays()
    # api = OKCoinCN()
    # config.lower_bound = 0.003
    amount = 0.001
    order_id = api.trade('sell', 10000, amount)
    monitor = ArbitrageConsumer(api, order_id)
    monitor.start()
    monitor.wait()
    print('\nanother......')
    order_id = api.trade('buy', 1, amount)
    monitor = ArbitrageConsumer(api, order_id)
    monitor.start()
    monitor.wait()
    print('finished outside')
