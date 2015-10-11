#!/usr/bin/env python
from utils.asset_info import AssetInfo
from settings import config
from utils import log_helper, common
from utils.order_info import PlatformOrderInfo


class Trader(object):
    _logger = log_helper.get_logger()

    def __init__(self, plt, catalog, price, amount, fiat='cny'):
        """
        :param plt: platform, don't change
        :param catalog: sell/buy, don't change
        :param price: trade price, don't change
        :param amount: trade amount, don't change
        :param fiat: fiat, don't change
        """
        self.plt = plt
        self.coin_type = self.plt.coin_type
        self.fiat = fiat
        self.plt_name = self.plt.__class__.__name__
        assert (catalog in ['sell', 'buy'])
        self.catalog = catalog
        self.amount = amount
        self.price = price
        # initialized with an invalid number
        self.order_id = config.INVALID_ORDER_ID

    def set_order_id(self, order_id):
        self.order_id = order_id

    def regular_trade(self, catalog, price, amount):
        """
        regular trade, may cause pending
        NOTE: only platform is guaranteed to be unchanged
        :return: order_id
        """
        # TradeInfo._logger.debug('BEFORE trade')
        order_id = self.plt.trade(catalog, price, amount)
        Trader._logger.warning(
            'Trade in {:10s}: {:4s} {:10.4f} {:3s} at price {:10.4f} {}, order_id={:d}'.format(
                self.plt_name, catalog, amount, self.coin_type, price, self.fiat, order_id))
        return order_id

    def _asset_afford_trade(self, trade_amount, trade_price):
        """
        test whether there is enough asset to afford trade, catalog is self.catalog
        :param trade_amount:
        :return:
        """
        waited_asset_times = 0
        # NOTE: since we lock the trade, only 1 request needed
        asset_info = AssetInfo.from_api(self.plt)
        if self.catalog == 'sell':
            asset_amount = asset_info.afford_sell_amount()
            if asset_amount >= trade_amount:
                return True
            else:
                return False
        # catalog == 'buy'
        while True:
            asset_amount = asset_info.afford_buy_amount(trade_price)
            if asset_amount >= trade_amount:
                return True
            else:  # asset_amount not enough
                waited_asset_times += 1
                if waited_asset_times > config.ASSET_WAIT_MAX:
                    Trader._logger.critical(
                        '{}: not afford to "{}" after waiting > {} times'.format(
                            self.plt_name, self.catalog, config.ASSET_WAIT_MAX))
                    # TODO should avoid further "not afford"
                    return False
                # adjust to "nearer price"
                # FIXME this conflicts with the currently adjusted arbitrage prices
                trade_price -= (trade_price - self.price) / (config.ASSET_WAIT_MAX + 1)

    # noinspection PyPep8Naming
    def adjust_trade(self):
        """
        this trade ensures that there will be no pending afterwards:
          1. meet the lower_bound limit for each platform
             if amount >= M, regular trade; if amount < M, a bidirectional trade is provided
          2. there will be enough asset for sell(coin) or buy(fiat)
             calculate for current asset
          3. the price is higher for buy or lower for sell
             adjust_price with a certain percentage
        :return: None
        """
        M = self.plt.lower_bound
        # no trading amount
        assert self.amount >= config.MINOR_DIFF
        # if self.amount < config.minor_diff:
        #     TradeInfo._logger.info('{}: trading amount = 0, exit adjust_trade'.format(self.plt_name))
        #     return
        # config.minor_diff <= self.amount
        # self.amount does not change inside
        if self.amount < M:
            trade_amount = self.amount + M
            trade_catalog = self.catalog
            trade_price = common.adjust_price(trade_catalog, self.price)
            afford_info = self._asset_afford_trade(trade_amount, trade_price)
            # TODO: check whether needing to run in different threads
            if afford_info:
                Trader._logger.warning('{} bi-directional adjust_trade'.format(self.plt_name))
                # trade1, must succeed
                self.regular_trade(trade_catalog, trade_price, trade_amount)
                # trade2, must succeed in principle
                # may fail in practice since reverse_price is too hxigh to buy with existing fiat (although not true)
                reverse_amount = M
                reverse_catalog = common.reverse_catalog(trade_catalog)
                reverse_price = common.adjust_price(reverse_catalog, self.price)
                # TODO: may fail, should handle
                order_id = self.regular_trade(reverse_catalog, reverse_price, reverse_amount)
                if order_id == config.INVALID_ORDER_ID:
                    Trader._logger.critical(
                        'Failed reverse at {} during bi-directional trade, to be adjusted by monitor'.format(
                            self.plt_name))
                    return False
                return True  # afford, and bi-directional succeeds
            return False  # not afford for 'self.amount < M'
        else:  # self.amount >= M
            trade_price = common.adjust_price(self.catalog, self.price)
            trade_catalog = self.catalog
            trade_amount = self.amount
            afford_info = self._asset_afford_trade(trade_amount, trade_price)
            if afford_info:
                Trader._logger.warning('{} single adjust_trade'.format(self.plt_name))
                # trade must succeed
                self.regular_trade(trade_catalog, trade_price, trade_amount)
                return True
            return False  # not afford for 'self.amount >= M'

    # do nothing if order invalid
    def cancel(self):
        if self.order_id != config.INVALID_ORDER_ID:
            Trader._logger.warning('{:10s} cancel order_id={}'.format(self.plt_name, self.order_id))
            return self.plt.cancel(self.order_id)

    def get_order_info(self):
        # NOTE: workaround if order failed, copy catalog, remaining is self.amount
        if self.order_id == config.INVALID_ORDER_ID:
            return PlatformOrderInfo(self.order_id, self.catalog, self.amount)
        else:
            return self.plt.order_info(self.order_id)

    def __repr__(self):
        trade_info = '{:>10}: {:4s} {:>10.4f} {:3s}, Price {:>10.2f} {:3s}' \
            .format(self.plt_name, self.catalog, self.amount, self.coin_type, self.price, self.fiat)
        if self.order_id != -1:
            order_info = '{:<d}'.format(self.order_id)
            trade_info += ',\torder_id=' + order_info
        trade_info += ';'
        return trade_info
