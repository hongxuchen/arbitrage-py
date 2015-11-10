#!/usr/bin/env python

from arbitrage import monitor, consumer, producer
from arbitrage.stats import Statistics
from utils import log_helper, plt_helper
# FIXME it's better to import dynamically
# noinspection PyUnresolvedReferences
from api.bitbays import BitBays
# noinspection PyUnresolvedReferences
from api.huobi import HuoBi
# noinspection PyUnresolvedReferences
from api.okcoin import OKCoinCN

try:
    # noinspection PyPep8Naming
    import Queue as queue
except ImportError:
    # noinspection PyUnresolvedReferences
    import queue
try:
    # noinspection PyShadowingBuiltins
    input = raw_input
except NameError:
    pass


class Driver(object):
    def __init__(self):
        log_helper.init_logger()
        enabled_plt = plt_helper.get_key_from_data('Enabled')
        self.plt_list = [eval(plt)() for plt in enabled_plt]
        self.adjuster_enabled = plt_helper.get_key_from_data('Enable_Adjuster')
        stats = Statistics()
        if self.adjuster_enabled:
            self.adjuster_queue = queue.Queue()
            self.producer = producer.Producer(self.plt_list, self.adjuster_queue, stats)
            self.consumer = consumer.Consumer(self.adjuster_queue, stats)
        else:
            self.producer = producer.Producer(self.plt_list, None, stats)
        self.monitor = monitor.Monitor(self.plt_list, stats)
        self.running = False

    def start_trade(self):
        self.producer.running = True
        self.producer.start()
        if self.adjuster_enabled:
            self.consumer.start()
        self.monitor.running = True
        self.monitor.start()

    def stop_trade(self):
        log_helper.get_logger().warning('[D] stopping Producer')
        self.producer.running = False
        self.producer.join()
        if self.adjuster_enabled:
            log_helper.get_logger().warning('[D] stopping Consumer')
            self.consumer.join()
        log_helper.get_logger().warning('[D] stopping monitor')
        self.monitor.running = False
        self.monitor.join()

    def main_run(self):
        log_helper.get_logger().info('=' * 80)
        log_helper.get_logger().warning('[D] start trade')
        driver.start_trade()
        try:
            while True:
                value = input()
                if value.startswith('q'):
                    break
        except KeyboardInterrupt:
            pass
        finally:
            log_helper.get_logger().warning('[D] stop trade')
            self.stop_trade()


if __name__ == '__main__':
    driver = Driver()
    driver.main_run()
