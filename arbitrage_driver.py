#!/usr/bin/env python

from chbtc import CHBTC
from huobi import HuoBi
from itbit import ItBitAPI
import logging_conf
from okcoin import OKCoinCN
from bitbays import BitBays
import arbitrage_consumer
import arbitrage_producer
import arbitrage_monitor
import plt_conf

select_plt_dict = {
    'OKCoinCN': OKCoinCN,
    'BitBays': BitBays,
    'ItBit': ItBitAPI,
    'HuoBi': HuoBi,
    'CHBTC': CHBTC
}

try:
    import Queue as queue
except ImportError:
    import queue
try:
    # noinspection PyShadowingBuiltins
    input = raw_input
except NameError:
    pass


class Driver(object):
    def __init__(self):
        logging_conf.init_logger()
        enabled_plt = plt_conf.get_key_from_data('Enabled')
        self.plt_list = [select_plt_dict[plt]() for plt in enabled_plt]
        self.adjuster_enabled = plt_conf.get_key_from_data('Enable_Adjuster')
        if self.adjuster_enabled:
            self.adjuster_queue = queue.Queue()
            self.producer = arbitrage_producer.Producer(self.plt_list, self.adjuster_queue)
            self.consumer = arbitrage_consumer.Consumer(self.adjuster_queue)
        else:
            self.producer = arbitrage_producer.Producer(self.plt_list, None)
        self.monitor = arbitrage_monitor.Monitor(self.plt_list)
        self.running = False

    def start_trade(self):
        self.producer.running = True
        self.producer.start()
        if self.adjuster_enabled:
            self.consumer.start()
        self.monitor.running = True
        self.monitor.start()

    def stop_trade(self):
        logging_conf.get_logger().warning('[D] stopping Producer')
        self.producer.running = False
        self.producer.join()
        if self.adjuster_enabled:
            logging_conf.get_logger().warning('[D] stopping Consumer')
            self.consumer.join()
        logging_conf.get_logger().warning('[D] stopping monitor')
        self.monitor.running = False
        self.monitor.join()

    def main_run(self):
        logging_conf.get_logger().info('=' * 80)
        logging_conf.get_logger().warning('[D] start trade')
        driver.start_trade()
        try:
            while True:
                value = input()
                if value == 'q':
                    break
        except KeyboardInterrupt:
            pass
        finally:
            logging_conf.get_logger().warning('[D] stop trade')
            self.stop_trade()


if __name__ == '__main__':
    driver = Driver()
    driver.main_run()
