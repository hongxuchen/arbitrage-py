#!/usr/bin/env python
import config

from okcoin import OKCoinCN
from bitbays import BitBays

# it does not recognize fiat, just for amount

class AssetInfo(object):
    def __init__(self, plt):
        self.plt = plt
        asset_list = plt.assets()
        assert (len(asset_list) == 2)
        [self.fiat_pending, self.fiat_avail] = asset_list[0]
        [self.btc_pending, self.btc_avail] = asset_list[1]

    def has_pending_fiat(self):
        return self.fiat_pending > config.minor_diff

    def afford_buy_amount(self, price):
        return self.fiat_avail / price

    def afford_sell_amount(self):
        return self.btc_avail

    def has_pending_btc(self):
        return self.btc_pending > config.minor_diff

    def __str__(self):
        plt_name = self.plt.__class__.__name__
        fiat_str = 'fiat : pending={:<10} avail={:<10}'.format(self.fiat_pending, self.fiat_avail)
        btc_str = 'btc  : pending={:<10} avail={:<10}'.format(self.btc_pending, self.btc_avail)
        return plt_name + '\n' + fiat_str + '\n' + btc_str


if __name__ == '__main__':
    okc = OKCoinCN()
    asset_info = AssetInfo(okc)
    print(asset_info)
    bb = BitBays()
    asset_info = AssetInfo(bb)
    print(asset_info)
    print(asset_info.has_pending_btc())
    print(asset_info.has_pending_fiat())
