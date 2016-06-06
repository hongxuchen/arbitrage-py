#!/usr/bin/env python

from api.okcoin import OKCoinBase
from settings import config
from utils import common
from utils.log_helper import init_logger, get_logger


class FutureType(object):
    this_week = "this_week"
    next_week = "next_week"
    quarter = "quarter"


class OKFuture(OKCoinBase):
    plt_info = {
        'prefix': 'https://www.okcoin.com/api/v1',
        'fiat': 'usd'
    }
    PRECISION = 2
    CONTRACT_USD = 100
    _logger = get_logger()

    def __init__(self, contract_type, trade_fiat):
        super(OKFuture, self).__init__(self.plt_info)
        self.contract_type = contract_type
        self.visualable_fiat = trade_fiat
        self.update_usd_cny_rate()

    # noinspection PyAttributeOutsideInit
    def update_usd_cny_rate(self):
        if self.visualable_fiat != self.fiat_type:
            self.rate = self._exchange_rate()
        else:
            self.rate = 1.0

    def _exchange_rate(self):
        res = self._setup_request('exchange_rate', None)
        return common.to_decimal(res['rate'])

    # public api

    def api_ticker(self):
        payload = {
            'symbol': self.coin_type + '_' + self.fiat_type,
            'contract_type': self.contract_type
        }
        res = self._setup_request('future_ticker', payload)
        return res

    def ask1(self):
        ticker = self.api_ticker()
        sell = ticker['ticker']['sell']
        final = common.to_decimal(sell, self.PRECISION)
        return final * self.rate

    def bid1(self):
        ticker = self.api_ticker()
        buy = ticker['ticker']['buy']
        final = common.to_decimal(buy, self.PRECISION)
        return final * self.rate

    def api_depth(self):
        payload = {
            'symbol': self.coin_type + '_' + self.fiat_type,
            'contract_type': self.contract_type
        }
        res = self._setup_request('future_depth', payload)
        return res

    def ask_bid_list(self, length=2):
        assert 2 <= length <= 5
        res = self.api_depth()
        asks = sorted(res['asks'], key=lambda ask: ask[0], reverse=True)[-length:]
        bids = sorted(res['bids'], key=lambda bid: bid[0], reverse=True)[:length]
        asks_bids = asks + bids
        return asks_bids

    def api_trades(self):
        pass

    def future_index(self):
        paylad = {
            'symbol': self.coin_type + '_' + self.fiat_type
        }
        res = self._setup_request('future_index', paylad)
        # better <= real
        return common.to_decimal(res['future_index'])

    def bitcoin_per_cont(self, price):
        return self.CONTRACT_USD / float(price)

    def api_userinfo(self):
        res = self._private_request('future_userinfo', None)
        return res

    # cross-margin
    def api_userinfo_4fix(self):
        res = self._private_request('future_userinfo_4fix', None)
        return res

    # future_type=1 will return full
    # cross-margin
    def api_future_position_4fix(self, future_type=1):
        payload = {
            'symbol': self.coin_type + '_' + self.fiat_type,
            'contract_type': self.contract_type,
            'type': future_type
        }
        res = self._private_request('future_position_4fix', payload)
        return res

    # risk_rate:
    def assets(self):
        userinfo = self.api_userinfo()
        info = userinfo['info'][self.coin_type]
        return info

    def account_rights(self):
        asset = self.assets()
        rights = asset['account_rights']
        return rights

    def api_position(self):
        payload = {
            'symbol': self.coin_type + '_' + self.fiat_type,
            'contract_type': self.contract_type
        }
        res = self._private_request('future_position', payload)
        return res

    def api_trade(self, type_code, price, amount, lever_rate):
        """
        :param type_code:
        :param price: the price is the same as fiat_type ("usd")
        :param amount:
        :param lever_rate:
        :return:
        """
        payload = {
            'symbol': self.coin_type + '_' + self.fiat_type,
            'contract_type': self.contract_type,
            'price': price,
            'amount': amount,
            'type': type_code,
            'match_price': 0,
            'lever_rate': lever_rate
        }
        res = self._private_request('future_trade', payload)
        return res

    def _get_settle_price(self, price):
        return price / self.rate

    def _settle_trade(self, type_code, price, amount, lever_rate):
        settle_price = self._get_settle_price(price)
        future_type_dict = {
            1: "open_long",
            2: "open_short",
            3: "liquidate_long",
            4: "liquidate_short"
        }
        if self.visualable_fiat != self.fiat_type:
            self._logger.warning(
                "{:20s}: price: {:>8.4f}{}({:8.4f}{}) amount={}, lever={:2d}"
                    .format(future_type_dict[type_code], price, self.visualable_fiat, settle_price,
                            self.fiat_type, amount, lever_rate))
        else:
            self._logger.warning("{:20s}: price: {:>8.4f}{}({:8.4f}{}) amount={}, lever={:2d}"
                                 .format(future_type_dict[type_code], price, self.visualable_fiat, amount, lever_rate))
        res = self.api_trade(type_code, settle_price, amount, lever_rate)
        return res

    def open_long(self, price, amount, lever_rate=config.OKCOIN_LEVERAL_RATE):
        return self._settle_trade(1, price, amount, lever_rate)

    def open_short(self, price, amount, lever_rate=config.OKCOIN_LEVERAL_RATE):
        return self._settle_trade(2, price, amount, lever_rate)

    def liquidate_long(self, price, amount, lever_rate=config.OKCOIN_LEVERAL_RATE):
        return self._settle_trade(3, price, amount, lever_rate)

    def liquidate_short(self, price, amount, lever_rate=config.OKCOIN_LEVERAL_RATE):
        return self._settle_trade(4, price, amount, lever_rate)

    def api_cancel(self, order_id):
        payload = {
            'symbol': self.coin_type + '_' + self.fiat_type,
            'order_id': order_id,
            'contract_type': self.contract_type
        }
        res = self._private_request('future_cancel', payload)
        return res


if __name__ == '__main__':
    init_logger()
    okfuture = OKFuture(FutureType.quarter, 'cny')
    # print(okfuture.ask1(), okfuture.bid1())
    price = 400
    print(okfuture.bitcoin_per_cont(price))
    # print(okfuture.ask_bid_list(5))
    # print(okfuture.future_index())
    # print(okfuture.minimal_trade_amount())
    # print(okfuture.api_userinfo())
    # okfuture.account_rights()
    # print(okfuture.api_position())
    # print(okfuture.api_userinfo_4fix())
    # print(okfuture.api_future_position_4fix())
    # print(okfuture.open_long(2115, 0.01))
    # print(okfuture.api_cancel(123456))

    print(price * okfuture.rate)
    order_id = okfuture.open_short(price, 1)
