#!/usr/bin/env python

import trade_info

class TradeManager(object):
    def __init__(self, trade_info, asset_info):
        self.trade_info = trade_info
        self.api = trade_info.plt
        self.asset_info = asset_info
        assert(self.api == asset_info.api)

    def trade(self):
        pass
