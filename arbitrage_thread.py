#!/usr/bin/env python

from PySide import QtCore

from asset_info import AssetInfo
import config
from trade_info import TradeInfo


class ArbitrageWorker(QtCore.QThread):
    notify = QtCore.Signal(list)

    def __init__(self, plt_list, symbol):
        super(ArbitrageWorker, self).__init__()
        self.plt_list = plt_list
        self.symbol = symbol

    # used each time we run; producer
    def update_ask_bid_info(self):
        self._info_list = []
        for plt in self.plt_list:
            self._info_list.append(plt.depth())  # request here

    def update_asset_info_list(self):
        self._asset_info_list = []
        for plt in self.plt_list:
            asset_info = AssetInfo(plt)  # request here
            self._asset_info_list.append(asset_info)

    # do arbitrage
    def arbitrage_trade(self):
        info = self.arbitrage_info()
        if info is not None:
            self.notify.emit(info)
            print(info)

    def do_trade(self, trading_info):
        print(trading_info)

    # keep doing
    def run(self, *args, **kwargs):
        while True:
            self.arbitrage_trade()

    # arbitrage necssary condition
    # ask_a, bid_b are of [price, amount]
    @staticmethod
    def can_arbitrage(ask_a, bid_b):
        return ask_a[0] < bid_b[0]

    # ask_a, bid_b are of [price, amount]
    @staticmethod
    def amount_refine(ask_a, bid_b, asset_info_a, asset_info_b):
        plt_a_buy_amount = asset_info_a.afford_buy_amount(ask_a[1])
        plt_b_sell_amount = asset_info_b.afford_sell_amount()
        amount = min(config.upper_bound, ask_a[1], bid_b[1], plt_a_buy_amount, plt_b_sell_amount)
        amount = float('{:.4f}'.format(amount))
        amount = max(config.lower_bound, amount)
        return amount

    # the consumer that "uses" the info
    def arbitrage_info(self):
        self.update_ask_bid_info()
        self.update_asset_info_list()
        assert (len(self._info_list) == 2)
        assert (len(self._info_list[0]) == len(self._info_list[1]))
        length = len(self._info_list[0])
        assert (length % 2 == 0)
        assert (len(self._asset_info_list) == 2)

        # collect ask, bid info
        ask_list = []
        bid_list = []
        ask1_bid1_list = []
        for i in range(2):  # len(self._info_list)
            info = self._info_list[i]
            ask_list.append(info[length / 2])
            bid_list.append(info[length / 2 + 1])

        # if can arbitrage, return trade pair
        for i in range(2):  # len(self._info_list)
            ask_a = ask_list[i]  # a
            bid_b = bid_list[1 - i]  # the oposite, b
            if self.can_arbitrage(ask_a, bid_b):
                ask_a_price = ask_a[0]
                bid_b_price = bid_b[0]
                plt_a = self.plt_list[i]
                plt_b = self.plt_list[1 - i]
                asset_info_a = self._asset_info_list[i]
                asset_info_b = self._asset_info_list[1 - i]
                amount = self.amount_refine(ask_a, bid_b, asset_info_a, asset_info_b)
                if amount - config.lower_bound < config.minor_diff:
                    return None
                buy_trade = TradeInfo(plt_a, 'buy', ask_a_price, amount)  # buy at plt_a
                sell_trade = TradeInfo(plt_b, 'sell', bid_b_price, amount)  # sell at plt_b
                return buy_trade, sell_trade
        return None
