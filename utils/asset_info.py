#!/usr/bin/env python

from api.huobi import HuoBi
from api.okcoin import OKCoinCN


class AssetInfo(object):
    def __init__(self, plt_name, coin_type, fiat, coin):
        self.plt_name = plt_name
        self.coin_type = coin_type
        self.fiat_pending, self.fiat_avail = fiat
        self.coin_pending, self.coin_avail = coin

    @classmethod
    def from_api(cls, plt):
        asset_raw_list = plt.assets()
        plt_name = plt.plt_name
        coin_type = plt.coin_type
        fiat, coin = asset_raw_list
        return cls(plt_name, coin_type, fiat, coin)

    @classmethod
    def from_sum(cls, plt_list):
        plt_name = 'ALL'
        coin_type = plt_list[0].coin_type
        assert (all(coin_type == plt.coin_type for plt in plt_list))
        fiat = [sum([p.fiat_pending for p in plt_list]), sum(p.fiat_avail for p in plt_list)]
        coin = [sum([p.coin_pending for p in plt_list]), sum(p.coin_avail for p in plt_list)]
        return cls(plt_name, coin_type, fiat, coin)

    def converted_fiat(self, price):
        return self.total_coin() * price + self.total_fiat()

    def converted_coin(self, price):
        return self.total_fiat() / price + self.total_coin()

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
    huobi = HuoBi()
    asset_okcoin = AssetInfo.from_api(okcoin)
    asset_huobi = AssetInfo.from_api(huobi)
    asset_total = AssetInfo.from_sum([asset_huobi, asset_okcoin])
    for asset in [asset_okcoin, asset_huobi, asset_total]:
        print(asset)
