#!/usr/bin/env python

from __future__ import print_function

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
        arbitrage.adjust_pending()

    def consume(self):
        for arbitrage in self.arbitrage_queue:
            seconds = time.time() - arbitrage.time
            if seconds < config.PENDING_SECONDS:
                sleep_milliseconds = int((config.PENDING_SECONDS - seconds) * 1000)
                ArbitrageConsumer._logger.info('[Consmumer] sleep for {:4d}ms'.format(sleep_milliseconds))
                QtCore.QThread.msleep(sleep_milliseconds)
            ArbitrageConsumer._logger.info('[Consumer] consuming')
            if ArbitrageConsumer.need_adjust(arbitrage):
                self.adjust(arbitrage)
            assert arbitrage.done
            self.arbitrage_queue.remove(arbitrage)

    def run(self):
        while self.running or self.arbitrage_queue:
            ArbitrageConsumer._logger.debug('[Consumer] run')
            if not self.arbitrage_queue:
                ArbitrageConsumer._logger.debug(
                    '[Consumer] queue empty, sleep for {:d}ms'.format(config.CONSUMER_SLEEP_MILLISECONS))
                QtCore.QThread.msleep(config.CONSUMER_SLEEP_MILLISECONS)
            else:
                self.consume()


if __name__ == '__main__':
    p1 = BitBays()
    p2 = OKCoinCN()
    amount = 0.01
