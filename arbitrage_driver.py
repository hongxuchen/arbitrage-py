#!/usr/bin/env python

from chbtc import CHBTC
from huobi import HuoBi
from itbit import ItBitAPI
from okcoin import OKCoinCN
from bitbays import BitBays
import arbitrage_consumer
import arbitrage_producer
import asset_monitor
import common
import config

select_plt_dict = {
    'OKCoinCN': OKCoinCN,
    'BitBays': BitBays,
    'ItBit': ItBitAPI,
    'HuoBi': HuoBi,
    'CHBTC': CHBTC
}


class ArbitrageDriver():
    def __init__(self):
        common.init_logger()
        ### TODO
        enabled_plt = common.get_key_from_data('Enabled')
        self.plt_list = [select_plt_dict[plt]() for plt in enabled_plt]
        self.worklist = []
        self.producer = arbitrage_producer.ArbitrageProducer(self.plt_list, self.worklist, config.fiat)
        self.consumer = arbitrage_consumer.ArbitrageConsumer(self.worklist)
        self.monitor = asset_monitor.AssetMonitor(self.plt_list)
        self.running = False

    def start_trade(self):
        self.running = True
        self.producer.running = True
        self.producer.start()
        self.consumer.running = True
        self.consumer.start()
        self.monitor.running = True
        self.monitor.start()

    def stop_trade(self):
        self.running = False
        common.get_logger().warning('stopping producer')
        self.producer.running = False
        self.producer.join()
        common.get_logger().warning('stopping consumer')
        self.consumer.running = False
        self.consumer.join()
        common.get_logger().warning('stopping monitor')
        self.monitor.running = False
        self.monitor.join()

    def main_run(self):
        common.get_logger().warning('start trade')
        driver.start_trade()
        while True:
            # FIXME only works for python2
            value = raw_input()
            if value == 'q':
                break
        common.get_logger().warning('stop trade')
        self.stop_trade()


if __name__ == '__main__':
    driver = ArbitrageDriver()
    driver.main_run()
