#!/usr/bin/env python

import time

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
        self.arbitrage_queue = arbitrage_list

    @staticmethod
    def need_adjust(arbitrage_info):
        return arbitrage_info.has_pending()

    def adjust(self, arbitrage):
        seconds = time.time() - arbitrage.time
        arbitrage.adjust_pending()

    ### only remove self.arbitrage_list item
    def consume(self):
        for arbitrage in self.arbitrage_queue:
            seconds = time.time() - arbitrage.time
            if seconds > config.PENDING_SECONDS and ArbitrageConsumer.need_adjust(arbitrage):
                self.adjust(arbitrage)
            # must be done
            assert arbitrage.done
            self.arbitrage_queue.remove(arbitrage)

    def run(self):
        while self.running or self.arbitrage_queue:
            self.consume()


if __name__ == '__main__':
    p1 = BitBays()
    p2 = OKCoinCN()
    amount = 0.01
