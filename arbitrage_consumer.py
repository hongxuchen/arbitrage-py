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

    def __init__(self, arbitrage_list):
        super(ArbitrageConsumer, self).__init__()
        self.running = False
        # FIXME change to Queue
        self.arbitrage_queue = arbitrage_list

    def consume(self):
        for arbitrage in self.arbitrage_queue:
            seconds = time.time() - arbitrage.time
            # note: the size of queue may be > 1 and subsequent element may sleep too much
            # but may not be a big problem since the sleep time is for all elem in queue
            if seconds < config.PENDING_SECONDS:
                sleep_seconds = config.PENDING_SECONDS - seconds
                ArbitrageConsumer._logger.info('[Consmumer] sleep for {:4d}ms'.format(sleep_seconds))
                time.sleep(sleep_seconds)
            ArbitrageConsumer._logger.info('[Consumer] consuming')
            arbitrage.adjust_pending()
            self.arbitrage_queue.remove(arbitrage)

    def run(self):
        while self.running or self.arbitrage_queue:
            ArbitrageConsumer._logger.debug('[Consumer] run')
            if not self.arbitrage_queue:
                ArbitrageConsumer._logger.debug(
                    '[Consumer] queue empty, sleep for {:d}s'.format(config.CONSUMER_SLEEP_SECONS))
                time.sleep(config.CONSUMER_SLEEP_SECONS)
            else:
                self.consume()


if __name__ == '__main__':
    p1 = BitBays()
    p2 = OKCoinCN()
    amount = 0.01
