#!/usr/bin/env python

from PySide import QtCore

from bitbays import BitBays
import common
import config
from okcoin import OKCoinCN


class ArbitrageMonitor(QtCore.QObject):
    _logger = common.setup_logger()

    def __init__(self, api, order_id):
        '''
        :param api: btc.BTC
        :param order_id:
        :param args:
        :param kwargs:
        :return:
        '''
        super(ArbitrageMonitor, self).__init__()
        self.api = api
        self.order_id = order_id
        self.pending = True

    def get_order_info(self):
        order_info = self.api.order_info(self.order_id)
        ArbitrageMonitor._logger.debug('ORDER_INFO:{}'.format(order_info))
        return order_info

    def adjust_price(self):
        order_info = self.get_order_info()
        remaining = order_info.remaining_amount
        if remaining < config.minor_diff:
            self.pending = False
            return
        if order_info.seconds_since_created() > config.max_pending_seconds:
            self.api.cancel(self.order_id)
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
            ArbitrageMonitor._logger.debug("adjust_price")
            if order_info.catalog == 'buy':
                mo_amount = mo_amount * self.api.ask1()
                self.api.buy_market(mo_amount)
            else:
                self.api.sell_market(mo_amount)

    def run(self):
        while self.pending:
            self.adjust_price()
        ArbitrageMonitor._logger.debug('finished inside')


if __name__ == '__main__':
    api = BitBays()
    # api = OKCoinCN()
    # config.lower_bound = 0.003
    amount = 0.001
    order_id = api.trade('sell', 10000, amount)
    monitor = ArbitrageMonitor(api, order_id)
    monitor.start()
    monitor.wait()
    print('\nanother......')
    order_id = api.trade('buy', 1, amount)
    monitor = ArbitrageMonitor(api, order_id)
    monitor.start()
    monitor.wait()
    print('finished outside')
