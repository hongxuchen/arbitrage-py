#!/usr/bin/env python
import config

from okcoin import OKCoinCN
from bitbays import BitBays

# it does not recognize fiat, just for amount

class AssetInfo(object):
    def __init__(self, plt):
        self.plt = plt
        self.asset_raw_list = plt.assets()
        assert (len(self.asset_raw_list) == 2)
        [self.fiat_pending, self.fiat_avail] = self.asset_raw_list[0]
        [self.btc_pending, self.btc_avail] = self.asset_raw_list[1]

    def has_pending_fiat(self):
        return self.fiat_pending > config.MINOR_DIFF

    def has_pending_btc(self):
        return self.btc_pending > config.MINOR_DIFF

    def afford_buy_amount(self, price):
        return self.fiat_avail / price

    def afford_sell_amount(self):
        return self.btc_avail

    def total_btc(self):
        return self.btc_avail + self.btc_pending

    def total_fiat(self):
        return self.fiat_avail + self.fiat_pending

    def __repr__(self):
        plt_name = self.plt.__class__.__name__
        fiat_str = 'fiat : pending={:<10.4f} avail={:<10.4f}'.format(self.fiat_pending, self.fiat_avail)
        btc_str = 'btc  : pending={:<10.4f} avail={:<10.4f}'.format(self.btc_pending, self.btc_avail)
        return plt_name + '\n\t' + fiat_str + '\n\t' + btc_str


if __name__ == '__main__':
    okc = OKCoinCN()
    info1 = AssetInfo(okc)
    print(info1)
    bb = BitBays()
    info2 = AssetInfo(bb)
    print(info2)
    print(info1.total_btc() + info2.total_btc())
    print(info1.total_fiat() + info2.total_fiat())
