#!/usr/bin/env python

from __future__ import print_function
from Queue import Empty
import threading
import time

from api.bitbays import BitBays
from settings import config
from utils import common
from utils import log_helper
from api.okcoin import OKCoinCN


class Consumer(threading.Thread):
    _logger = log_helper.get_logger()

    def __init__(self, adjuster_queue):
        super(Consumer, self).__init__()
        self.adjuster_queue = adjuster_queue

    # noinspection PyMethodMayBeStatic
    def consume(self, adjuster):
        Consumer._logger.debug('[C] Consuming')
        seconds = adjuster.seconds_since_arbitrage()
        if seconds < config.PENDING_SECONDS:
            sleep_seconds = config.PENDING_SECONDS - seconds
            Consumer._logger.info('[C] sleep for {:.3f}s'.format(sleep_seconds))
            time.sleep(sleep_seconds)
        adjuster.adjust_pending()

    def run(self):
        while True:
            try:
                arbitrage = self.adjuster_queue.get(timeout=config.CONSUMER_TIMEOUTS)
                if arbitrage is common.SIGNAL:
                    Consumer._logger.debug('[C] Signal')
                    break
                self.consume(arbitrage)
            except Empty:
                pass


if __name__ == '__main__':
    p1 = BitBays()
    p2 = OKCoinCN()
    amount = 0.01
