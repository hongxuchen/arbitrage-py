#!/usr/bin/env python

from collections import deque
from settings import config


def frange(start, end, step):
    while start < end:
        yield start
        start += step


class Recollector(object):
    """
    use to keep lightweight information during arbitrage; updated by Monitor, visible to Producer
    """
    HISTORY = 7

    def __init__(self):
        self.asset_changes = deque(maxlen=self.HISTORY)

    def push_back(self, asset_change):
        self.asset_changes.append(asset_change)

    def balanced(self, coin_type):
        last_changes = list(self.asset_changes)[-self.HISTORY / 2:]
        if len(last_changes) == 0:
            return True
        return all([abs(change) < config.exceed_max_dict[coin_type] for change in last_changes])


if __name__ == '__main__':
    ss = Recollector()
    for i in frange(-1.0, 1.0, 0.2):
        ss.push_back(i)
    print(ss.balanced('btc'))
