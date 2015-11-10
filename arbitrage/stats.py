#!/usr/bin/env python


class Statistics(object):
    def __init__(self):
        self.reset()

    # noinspection PyAttributeOutsideInit
    def reset(self):
        self.trade_chance = 0
        self.wait_imbalanced = 0
        self.insufficient_num = 0
        self.arbitrage_num = 0
        self.adjust_num = 0
        self.monitor_num = 0

    def __repr__(self):
        return self.__dict__.__repr__()


if __name__ == '__main__':
    stats = Statistics()
    print(stats)
