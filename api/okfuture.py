#!/usr/bin/env python
from api.okcoin import OKCoinBase
from settings import config
from utils import common
from utils.log_helper import init_logger


class OKFuture(OKCoinBase):
    plt_info = {
        'prefix': 'https://www.okcoin.com/api/v1',
        'fiat': 'usd'
    }
    PRECISION = 2
    CONTRACT_USD = 100

    def __init__(self, contract_type, trade_fiat):
        super(OKFuture, self).__init__(self.plt_info)
        self.contract_type = contract_type
        self.trade_fiat = trade_fiat
        self.update_usd_cny_rate()

    # noinspection PyAttributeOutsideInit
    def update_usd_cny_rate(self):
        if self.trade_fiat != self.fiat_type:
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
        final = common.to_decimal(buy)
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
        # print(asks_bids)
        converted = [[common.to_decimal(price * self.rate, self.PRECISION), amount] for price, amount in
                     asks_bids]
        return converted

    def api_trades(self):
        pass

    def future_index(self):
        paylad = {
            'symbol': self.coin_type + '_' + self.fiat_type
        }
        res = self._setup_request('future_index', paylad)
        # better <= real
        return common.to_decimal(res['future_index'])

    def minimal_trade_amount(self):
        return common.to_decimal(self.CONTRACT_USD / self.future_index())

    def api_userinfo(self):
        res = self._private_request('future_userinfo', None)
        return res

    def api_position(self):
        payload = {
            'symbol': self.coin_type + '_' + self.fiat_type,
            'contract_type': self.contract_type
        }
        res = self._private_request('future_position', payload)
        return res

    def api_userinfo_4fix(self):
        res = self._private_request('future_userinfo_4fix', None)
        return res

    # future_type=1 will return full
    def api_future_position_4fix(self, future_type=1):
        payload = {
            'symbol': self.coin_type + '_' + self.fiat_type,
            'contract_type': self.contract_type,
            'type': future_type
        }
        res = self._private_request('future_position_4fix', payload)
        return res

    def api_trade(self, future_type, price, amount, level_rate):
        payload = {
            'symbol': self.coin_type + '_' + self.fiat_type,
            'contract_type': self.contract_type,
            'price': price,
            'amount': amount,
            'type': future_type,
            'match_price': 0,
            'level_rate': level_rate
        }
        res = self._private_request('future_trade', payload)
        return res

    def open_long(self, price, amount, level_rate=config.OKCOIN_LEVERAL_RATE):
        res = self.api_trade(1, price, amount, level_rate)
        return res

    def open_short(self, price, amount, level_rate=config.OKCOIN_LEVERAL_RATE):
        res = self.api_trade(2, price, amount, level_rate)
        return res

    def liquidate_long(self, price, amount, level_rate=config.OKCOIN_LEVERAL_RATE):
        res = self.api_trade(3, price, amount, level_rate)
        return res

    def liquidate_short(self, price, amount, level_rate=config.OKCOIN_LEVERAL_RATE):
        res = self.api_trade(4, price, amount, level_rate)
        return res

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
    okfuture = OKFuture('this_week', 'cny')
    # print(okfuture.ask1(), okfuture.bid1())
    # print(okfuture.ask_bid_list(5))
    # print(okfuture.future_index())
    # print(okfuture.minimal_trade_amount())
    # print(okfuture.api_userinfo())
    # print(okfuture.api_position())
    print(okfuture.api_userinfo_4fix())
    # print(okfuture.api_future_position_4fix())
    # print(okfuture.open_long(2115, 0.01))
    # print(okfuture.api_cancel(123456))
