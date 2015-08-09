#!/usr/bin/env python

from __future__ import print_function
import threading
import time

from bitbays import BitBays
import common
import config
from okcoin import OKCoinCN


class ArbitrageConsumer(threading.Thread):
    _logger = common.get_logger()

    def __init__(self, adjuster_queue):
        super(ArbitrageConsumer, self).__init__()
        self.adjuster_queue = adjuster_queue

    def consume(self, adjuster):
        ArbitrageConsumer._logger.debug('[C] Consumer')
        seconds = adjuster.seconds_since_arbitrage()
        if seconds < config.PENDING_SECONDS:
            sleep_seconds = config.PENDING_SECONDS - seconds
            ArbitrageConsumer._logger.info('[C] sleep for {:.3f}s'.format(sleep_seconds))
            time.sleep(sleep_seconds)
        adjuster.adjust_pending()

    def run(self):
        while True:
            arbitrage = self.adjuster_queue.get()
            if arbitrage is common.SIGNAL:
                ArbitrageConsumer._logger.debug('[C] Signal')
                break
            self.consume(arbitrage)


if __name__ == '__main__':
    p1 = BitBays()
    p2 = OKCoinCN()
    amount = 0.01
