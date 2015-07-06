#!/usr/bin/env python
from __future__ import print_function
import hashlib
import hmac
import urllib
import sys
from datetime import datetime
import time
import calendar

import requests

from btc import BTC
import common
import config
from order_info import OrderInfo


class BitBays(BTC):
    _logger = common.setup_logger()
    fmt = '%Y/%m/%d %H:%M:%S'
    catalog_dict = {
        0: 'buy',
        1: 'sell'
    }
    lower_bound = 0.001

    def __init__(self):
        super(BitBays, self).__init__(config.bitbays_info)
        self.symbol = config.bitbays_info['symbol']
        self.key = common.get_key_from_file('BitBays')
        self._btc_rate = None
        self._user_data = None
        self._counter = int(time.time() * 1000)
        self.api_public = ['ticker', 'trades', 'depth']
        self.api_private = ['info', 'orders', 'transactions', 'trade', 'cancel', 'order']
        self._orders_info = {}

    def _nonce(self):
        self._counter += 1
        return self._counter

    def _sign(self, params):
        return hmac.new(self.key['secret'], params, digestmod=hashlib.sha512).hexdigest()

    def _post_param(self, payload):
        params = {
            'Key': self.key['api'],
            'Sign': self._sign(urllib.urlencode(payload))
        }
        return params

    def _real_uri(self, method):
        return self.get_url('/' + method + '/')

    def _setup_request(self, method, params=None, data=None):
        try:
            r = None
            if method in self.api_public:
                r = requests.get(self._real_uri(method), params=params)
            elif method in self.api_private:
                r = requests.post(self._real_uri(method), data=data, headers=params)
            else:
                BitBays._logger.critical('method [{}] not supported'.format(method))
                sys.exit(1)
            # BitBays._logger.debug(r.url)
            return r
        except Exception as e:
            BitBays._logger.critical(e)
            sys.exit(1)

    def api_ticker(self):
        payload = {
            'market': 'btc_' + self.symbol
        }
        r = self._setup_request('ticker', params=payload)
        data = r.json()
        return data

    def ask1(self):
        ticker = self.api_ticker()
        sell = ticker['result']['sell']
        sell = common.to_decimal(sell)
        return sell

    def ask_bid_list(self, length=2):
        assert (1 <= length <= 50)
        payload = {
            'market': 'btc_' + self.symbol
        }
        r = self._setup_request('depth', params=payload)
        data = r.json()['result']
        asks = sorted(data['asks'], key=lambda ask: ask[0], reverse=True)[-length:]
        bids = sorted(data['bids'], key=lambda bid: bid[0], reverse=True)[:length]
        assert (asks[-1][0] > bids[0][0])
        asks_bids = asks + bids
        # BitBays._logger.debug(asks_bids)
        return asks_bids

    # all my trades
    def api_trades(self):
        payload = {
            'market': 'btc_' + self.symbol
        }
        r = self._setup_request('trades', params=payload)
        data = r.json()
        return data

    # trade operations
    def api_trade(self, order):
        payload = {
            'market': 'btc_' + self.symbol,
            'order_type': 0,  # limit order
            'nonce': self._nonce()
        }
        payload.update(order)
        assert (payload['order_type'] in [0, 1])
        assert (payload['op'] in ['buy', 'sell'])
        params = self._post_param(payload)
        r = self._setup_request('trade', params, payload)
        data = r.json()
        return data

    def trade(self, op_type, price, amount):
        trade_dict = {
            'op': op_type,
            'price': str(price),
            'amount': str(amount)
        }
        data = self.api_trade(trade_dict)
        if str(data['status']).startswith('4'):
            BitBays._logger.critical("ERROR: {}".format(data['message']))
            sys.exit(1)
        order_id = data['result']['id']
        return order_id

    def _market_trade(self, op_type, mo_amount):
        trade_dict = {
            'order_type': 1,
            'op': op_type,
            'mo_amount': mo_amount
        }
        data = self.api_trade(trade_dict)
        return data

    def buy_market(self, mo_amount):
        BitBays._logger.debug('BitBays.buy_market with amount {}'.format(mo_amount))
        return self._market_trade('buy', mo_amount)

    def sell_market(self, mo_amount):
        BitBays._logger.debug('BitBays.sell_market with amount {}'.format(mo_amount))
        return self._market_trade('sell', mo_amount)

    def api_cancel(self, order_id):
        payload = {
            'id': order_id,
            'nonce': self._nonce()
        }
        params = self._post_param(payload)
        r = self._setup_request('cancel', params, payload)  #
        data = r.json()
        return data

    def api_order_info(self, order_id):
        payload = {
            'id': order_id,
            'nonce': self._nonce()
        }
        params = self._post_param(payload)
        r = self._setup_request('order', params, payload)
        data = r.json()
        return data

    def cancel(self, order_id):
        BitBays._logger.info('canceling order {}...'.format(order_id))
        data = self.api_cancel(order_id)
        return data

    def cancel_all(self, catalog=2):
        if catalog & 1 == 1:
            BitBays._logger.info('cancelling buy orders')
            buy = self.api_orders(0)['result']
            if buy is not None:
                for t in buy:
                    self.api_cancel(t['buy'])
        if (catalog >> 1) & 1 == 1:
            BitBays._logger.info('cancelling sell orders')
            sell = self.api_orders(1)['result']
            if sell is not None:
                for t in sell:
                    self.api_cancel(t['id'])

    @staticmethod
    def _get_timestamp(time_str, fmt):
        date_obj = datetime.strptime(time_str, fmt).timetuple()
        timestamp = calendar.timegm(date_obj)
        ts2 = time.mktime(date_obj)
        now = time.time()
        return timestamp

    def order_info(self, order_id):
        info = self.api_order_info(order_id)['result']
        create_time = BitBays._get_timestamp(info['created_at'], BitBays.fmt)
        now = time.time()
        amount = 0.0
        if 'amount_total' in info:
            amount = info['amount_total']
        elif 'mo_amount' in info:
            amount = info['mo_amount']
        remaining_amount = common.to_decimal(amount) - common.to_decimal(info['amount_done'])
        catalog = BitBays.catalog_dict[info['catalog']]
        return OrderInfo(catalog, remaining_amount, create_time)

    def api_user_info(self):
        payload = {
            'nonce': self._nonce()
        }
        params = self._post_param(payload)
        r = self._setup_request('info', params, payload)
        return r.json()

    def api_orders(self, catalog, status=0):
        payload = {
            'market': 'btc_' + self.symbol,
            'catalog': catalog,
            'status': status,
            'count': 20,
            'nonce': self._nonce()
        }
        assert (catalog in [0, 1])
        if catalog == 0:
            payload['order'] = 'DESC'
        else:
            payload['order'] = 'ASC'
        params = self._post_param(payload)
        r = self._setup_request('orders', params, payload)
        js = r.json()
        return js

    def api_transactions(self, catalog):
        payload = {
            'market': 'btc_' + self.symbol,
            'catalog': catalog,
            'count': 20,
            'nonce': self._nonce()
        }
        assert (catalog in [0, 1])
        if catalog == 0:
            payload['order'] = 'DESC'
        else:
            payload['order'] = 'ASC'
        params = self._post_param(payload)
        r = self._setup_request('transactions', params, payload)
        js = r.json()
        return js

    def assets(self):
        info = self.api_user_info()['result']['wallet']
        l = [
            [common.to_decimal(info[self.symbol]['lock']), common.to_decimal(info[self.symbol]['avail'])],
            [common.to_decimal(info['btc']['lock']), common.to_decimal(info['btc']['avail'])]
        ]
        return l


if __name__ == '__main__':
    bitbays = BitBays()
    # order_id = bitbays.trade('sell', 10000, 0.001)
    # limit order id
    # res = bitbays.order_info(order_id)
    # print(res)
    order_id = bitbays.trade('buy', 10, 0.001)
    print(order_id)
    order_info = bitbays.order_info(order_id)
    print(order_info)
    # res = bitbays.buy_market(0.01)
    # print(res)
    # order_id = 44036603
    # res = bitbays.order_info(order_id)
    # res = bitbays.sell_market(0.001)
    # print(res)
