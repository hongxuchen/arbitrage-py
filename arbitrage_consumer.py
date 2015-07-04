#!/usr/bin/env python

from PySide import QtCore

from bitbays import BitBays
import common
import config
from okcoin import OKCoinCN


class ArbitrageConsumer(QtCore.QThread):
    _logger = common.setup_logger()

    def __init__(self, arbitrage_list):
        super(ArbitrageConsumer, self).__init__()
        self.running = False
        self.queue = arbitrage_list

    def _get_order_info(self, order_id):
        order_info = self.plt_list.order_info(order_id)
        ArbitrageConsumer._logger.debug('ORDER_INFO:{}'.format(order_info))
        return order_info

    ### only remove self.arbitrage_list item
    def consume(self):
        for q in self.queue:
            # TODO
            pass

    def AdjustTrade(self):
        pass


    def run(self):
        while self.running:
            self.consume()


if __name__ == '__main__':
    plt = BitBays()
    # plt = OKCoinCN()
    # config.lower_bound = 0.003
    amount = 0.001
    order_id = plt.trade('sell', 10000, amount)
