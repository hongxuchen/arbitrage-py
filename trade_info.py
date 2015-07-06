#!/usr/bin/env python
from asset_info import AssetInfo
import common
import config


class TradeInfo(object):
    INVALID_ORDER_ID = -1
    _logger = common.setup_logger()

    def __init__(self, plt, catelog, price, amount, fiat='cny'):
        """
        :param plt: platform, don't change
        :param catelog: sell/buy, don't change
        :param price: trade price, don't change
        :param amount: trade amount, don't change
        :param fiat: fiat, don't change
        """
        self.plt = plt
        self.plt_name = self.plt.__class__.__name__
        assert (catelog in ['sell', 'buy'])
        self.catelog = catelog
        self.amount = amount
        self.price = price
        self.fiat = fiat
        # initialized with an invalid number
        self.order_id = TradeInfo.INVALID_ORDER_ID  # to be accomplished

    def set_order_id(self, order_id):
        self.order_id = order_id

    def regular_trade(self, catelog, price, amount):
        """
        regular trade, may cause pending
        :return: order_id
        """
        TradeInfo._logger.debug(
            'BEFORE, {:10s}: {:4s} {:10.4f} btc at price {:10.4f} cny'.format(self.plt_name, catelog, amount,
                                                                           price))
        order_id = self.plt.trade(catelog, price, amount)
        TradeInfo._logger.debug(
            'AFTER,  {:10s}: {:4s} {:10.4f} btc at price {:10.4f} cny, order_id={:d}'.format(self.plt_name, catelog,
                                                                                             amount,
                                                                                             price, order_id))
        return order_id

    def _asset_afford_trade(self, trade_amount, trade_price):
        """
        test whether there is enough asset to afford trade, catelog is self.catelog
        :param trade_amount:
        :return:
        """
        # trade_price = common.adjust_price(self.catelog, self.price)
        waited_asset_times = 0
        while True:
            ### request here
            asset_info = AssetInfo(self.plt)
            if self.catelog == 'buy':
                asset_amount = asset_info.afford_buy_amount(trade_price)
            else:  # sell
                asset_amount = asset_info.afford_sell_amount()
            if asset_amount >= trade_amount:
                return True
            else:
                waited_asset_times += 1
                # FIXME this is a BUG
                if waited_asset_times >= config.ASSET_WAIT_MAX:
                    TradeInfo._logger.debug(
                        '{}: not afford to "{}" after waiting {} times'.format(self.plt_name, self.catelog,
                                                                               config.ASSET_WAIT_MAX))
                    return False

    # noinspection PyPep8Naming
    def adjust_trade(self):
        """
        this trade ensures that there will be no pending afterwards:
          1. meet the lower_bound limit for each platform
             if amount >= M, regular trade; if amount < M, a bidirectional trade is provided
          2. there will be enough asset for sell(BTC) or buy(fiat/CNY)
             calculate for current asset
          3. the price is higher for buy or lower for sell
             adjust_price with a certain percentage
        :return: None
        """
        M = self.plt.__class__.lower_bound
        # no trading amount
        if self.amount < config.minor_diff:
            TradeInfo._logger.debug('{}: trading amount = 0, exit adjust_trade'.format(self.plt_name))
            return
        # config.minor_diff <= self.amount
        wait_for_asset_times = 0
        # self.amount does not change inside
        if self.amount < M:
            trade_amount = self.amount + M
            trade_catelog = self.catelog
            trade_price = common.adjust_price(trade_catelog, self.price)
            if self._asset_afford_trade(trade_amount, trade_price):
                TradeInfo._logger.debug('bi-directional adjust_trade, waited {:d} times'.format(wait_for_asset_times))
                # FIXME: it has data race problem with arbitrage thread, but no error within itself if single thread
                # trade1, must succeed
                self.regular_trade(trade_catelog, trade_price, trade_amount)
                # trade2, must succeed
                reverse_amount = M
                reverse_catelog = common.reverse_catelog(trade_catelog)
                reverse_price = common.adjust_price(reverse_catelog, self.price)
                self.regular_trade(reverse_catelog, reverse_price, reverse_amount)
        else:  # self.amount >= M
            trade_price = common.adjust_price(self.catelog, self.price)
            trade_catelog = self.catelog
            trade_amount = self.amount
            if self._asset_afford_trade(trade_amount, trade_price):
                # trade must succeed
                TradeInfo._logger.debug(
                    '{} single adjust_trade, waited {:d} times'.format(self.plt_name, wait_for_asset_times))
                self.regular_trade(trade_catelog, trade_price, trade_amount)

    def cancel(self):
        if self.order_id != -1:
            self.plt.cancel(self.order_id)

    def get_order_info(self):
        return self.plt.order_info(self.order_id)

    def __repr__(self):
        trade_info = '{:>10}: {} {:>10.4f} btc, Price {:>10.2f} {}' \
            .format(self.plt_name, self.catelog, self.amount, self.price, self.fiat)
        if self.order_id != -1:
            order_info = '{:<d}'.format(self.order_id)
            trade_info += ',\torder_id=' + order_info
        trade_info += ';'
        return trade_info
