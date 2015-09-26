#!/usr/bin/env python

from huobi import HuoBi
from okcoin import OKCoinCN


class AssetInfo(object):
    def __init__(self, plt_name, coin_type, fiat, coin):
        self.plt_name = plt_name
        self.coin_type = coin_type
        self.fiat_pending, self.fiat_avail = fiat
        self.coin_pending, self.coin_avail = coin

        # [self.fiat_pending, self.fiat_avail] = asset_raw_list[0]
        # [self.coin_pending, self.coin_avail] = asset_raw_list[1]

    @classmethod
    def from_api(cls, plt):
        asset_raw_list = plt.assets()
        plt_name = plt.__class__.__name__
        coin_type = plt.coin_type
        fiat, coin = asset_raw_list
        return cls(plt_name, coin_type, fiat, coin)

    @classmethod
    def from_sum(cls, p1, p2):
        plt_name = 'ALL'
        assert (p1.coin_type == p2.coin_type)
        coin_type = p1.coin_type
        fiat = [p1.fiat_pending + p2.fiat_pending, p1.fiat_avail + p2.fiat_avail]
        coin = [p1.coin_pending + p2.coin_pending, p1.coin_avail + p2.coin_avail]
        return cls(plt_name, coin_type, fiat, coin)

    def afford_buy_amount(self, price):
        return self.fiat_avail / price

    def afford_sell_amount(self):
        return self.coin_avail

    def total_coin(self):
        return self.coin_avail + self.coin_pending

    def total_fiat(self):
        return self.fiat_avail + self.fiat_pending

    def __repr__(self):
        fiat_str = 'fiat: pending={:<10.4f} avail={:<10.4f}'.format(self.fiat_pending, self.fiat_avail)
        coin_str = '{:4s}: pending={:<10.4f} avail={:<10.4f}'.format(self.coin_type, self.coin_pending, self.coin_avail)
        return self.plt_name + '\n\t' + fiat_str + '\n\t' + coin_str


if __name__ == '__main__':
    okcoin = OKCoinCN()
    # info1 = AssetInfo(okc)
    # print(info1)
    # bb = BitBays()
    # info2 = AssetInfo(bb)
    # print(info2)
    # print(info1.total_coin() + info2.total_coin())
    # print(info1.total_fiat() + info2.total_fiat())
    huobi = HuoBi()
    asset_okcoin = AssetInfo.from_api(okcoin)
    asset_huobi = AssetInfo.from_api(huobi)
    asset_total = AssetInfo.from_sum(asset_huobi, asset_okcoin)
    for asset in [asset_okcoin, asset_huobi, asset_total]:
        print(asset)
