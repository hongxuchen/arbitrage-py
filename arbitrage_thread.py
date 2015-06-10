#!/usr/bin/env python

from PySide import QtCore

from trade_info import TradeInfo


class ArbitrageWorker(QtCore.QThread):
    notify = QtCore.Signal(list)

    def __init__(self, api_list, symbol):
        super(ArbitrageWorker, self).__init__()
        self.api_list = api_list
        self.symbol = symbol

    # used each time we run; producer
    def update_ask_bid_info(self):
        self._info_list = []
        for api in self.api_list:
            self._info_list.append(api.depth())

    # do arbitrage
    def arbitrage_trade(self):
        info = self.arbitrage_info()
        if info is not None:
            self.notify.emit(info)
            print(info)

    def do_trade(self, trading_info):
        pass

    # keep doing
    def run(self, *args, **kwargs):
        while True:
            self.arbitrage_trade()

    # arbitrage condition
    # ask_a, bid_b are of [price, amount]
    @staticmethod
    def should_arbitrage(ask_a, bid_b):
        return ask_a[0] < bid_b[0]

    # ask_a, bid_b are of [price, amount]
    @staticmethod
    def amount_refine(ask_a, bid_b):
        amount = min(50, ask_a[1], bid_b[1])
        amount = max(0.001, amount)
        return amount

    # the consumer that "uses" the info
    def arbitrage_info(self):
        self.update_ask_bid_info()
        assert (len(self._info_list) == 2)
        assert (len(self._info_list[0]) == len(self._info_list[1]))
        length = len(self._info_list[0])
        assert (length % 2 == 0)

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
            if self.should_arbitrage(ask_a, bid_b):
                ask_a_price = ask_a[0]
                bid_b_price = bid_b[0]
                plt_a = self.api_list[i]
                plt_b = self.api_list[1 - i]
                amount = self.amount_refine(ask_a, bid_b)
                buy_trade = TradeInfo(plt_a, 'buy', ask_a_price, amount)
                sell_trade = TradeInfo(plt_b, 'sell', bid_b_price, amount)
                return buy_trade, sell_trade
        return None
