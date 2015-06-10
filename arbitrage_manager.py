#!/usr/bin/env python
from asset_info import AssetInfo
from trade_info import TradeInfo


class TradeManager(object):
    def __init__(self, asset_info_list):
        self.asset_info_list = asset_info_list

    def do_trade(self, trade_info):
        plt = trade_info.plt
        for asset_info in self.asset_info_list:
            if plt == asset_info.plt:
                data = plt.trade(trade_info.type, trade_info.price, trade_info.amount)
                # return data


if __name__ == '__main__':
    from okcoin import OKCoinCN
    from bitbays import BitBays

    okcoin_cn = OKCoinCN()
    asset_info_list = []
    # assets = okcoin_cn.assets()
    # asset_info_list.append(AssetInfo(assets))
    asset_info_list.append(AssetInfo(okcoin_cn))
    bitbays_cn = BitBays()
    # assets = bitbays_cn.assets()
    # asset_info_list.append(AssetInfo(assets))
    asset_info_list.append(AssetInfo(bitbays_cn))
    for asset_info in asset_info_list:
        print(asset_info)
    trade_manager = TradeManager(asset_info_list)
    trade_info = TradeInfo(okcoin_cn, 'buy', 1, 0.01)
    trade_manager.do_trade(trade_info)
    trade_info = TradeInfo(bitbays_cn, 'sell', 10000, 0.01)
    trade_manager.do_trade(trade_info)
