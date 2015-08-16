#!/usr/bin/env python

from huobi import HuoBi


class AssetInfo(object):
    def __init__(self, plt):
        self.plt = plt
        self.coin_type = self.plt.coin_type
        self.plt_name = self.plt.__class__.__name__
        self.asset_raw_list = plt.assets()
        [self.fiat_pending, self.fiat_avail] = self.asset_raw_list[0]
        [self.coin_pending, self.coin_avail] = self.asset_raw_list[1]

    def afford_buy_amount(self, price):
        return self.fiat_avail / price

    def afford_sell_amount(self):
        return self.coin_avail

    def total_coin(self):
        return self.coin_avail + self.coin_pending

    def total_fiat(self):
        return self.fiat_avail + self.fiat_pending

    def __repr__(self):
        plt_name = self.plt.__class__.__name__
        fiat_str = 'fiat: pending={:<10.4f} avail={:<10.4f}'.format(self.fiat_pending, self.fiat_avail)
        coin_str = '{:4s}: pending={:<10.4f} avail={:<10.4f}'.format(self.coin_type, self.coin_pending, self.coin_avail)
        return plt_name + '\n\t' + fiat_str + '\n\t' + coin_str


if __name__ == '__main__':
    # okc = OKCoinCN()
    # info1 = AssetInfo(okc)
    # print(info1)
    # bb = BitBays()
    # info2 = AssetInfo(bb)
    # print(info2)
    # print(info1.total_coin() + info2.total_coin())
    # print(info1.total_fiat() + info2.total_fiat())
    huobi = HuoBi()
    while True:
        asset_info = AssetInfo(huobi)
        print(asset_info)
        print(asset_info.afford_sell_amount())
        print(asset_info.afford_buy_amount(12))
