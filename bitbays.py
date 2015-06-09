#!/usr/bin/env python

from __future__ import print_function
import hashlib
import hmac
import urllib
import sys
from datetime import datetime
import time

import requests
from colorama import *

from btc import BTC
import common
import config


class BitBays(BTC):
    fmt = '%Y/%m/%d %H:%M:%S'

    def __init__(self):
        super(BitBays, self).__init__(config.bitbays_info)
        self.symbol = config.bitbays_info['symbol']
        self.key = common.get_key_from_file('BitBays')
        self._btc_rate = None
        self._user_data = None
        self._counter = int(time.time() * 1000)
        self.api_public = ['ticker', 'trades', 'depth']
        self.api_private = ['info', 'orders', 'transactions', 'trade', 'cancel']
        self._orders = {}

    def _nonce(self):
        self._counter += 1
        return self._counter

    def _sign(self, params):
        return hmac.new(self.key['secret'], params, digestmod=hashlib.sha512).hexdigest()

    def _post_param(self, payload):
        # print('ENCODING=', urllib.urlencode(payload))
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
                print('method [{}] not supported'.format(method))
                sys.exit(1)
            self.logger.debug(r.url)
            return r
        except Exception as e:
            print(e)
            sys.exit(1)

    def btc_rate(self):
        r = self._setup_request('ticker')
        js = r.json()
        return common.to_decimal(js['result']['last'])

    def depth(self, length=2):
        assert (1 <= length <= 50)
        payload = {
            'market': 'btc_' + self.symbol
        }
        r = self._setup_request('depth', params=payload)
        data = r.json()['result']
        asks = sorted(data['asks'], key=lambda ask: ask[0], reverse=True)[-length:]
        bids = sorted(data['bids'], key=lambda bid: bid[0], reverse=True)[:length]
        assert (asks[-1][0] > bids[0][0])
        self.logger.debug(asks)
        self.logger.debug(bids)
        return asks + bids

    # global
    def get_ask_bid(self):
        depth = self.depth()['result']
        asks = depth['asks']
        bids = depth['bids']
        asks = sorted(asks, key=lambda ask: ask[0])
        bids = sorted(bids, key=lambda bid: bid[0], reverse=True)
        return '{:40s} {:40s}'.format(str(asks[0]), str(bids[0]))

    # all my trades
    def trades(self):
        payload = {
            'market': 'btc_' + self.symbol
        }
        r = self._setup_request('trades', params=payload)
        js = r.json()
        return js

    # trade operations
    def trade(self, order):
        payload = {
            'market': 'btc_' + self.symbol,
            'order_type': 0,
            'nonce': self._nonce()
        }
        payload.update(order)
        params = self._post_param(payload)
        r = self._setup_request('trade', params, payload)
        js = r.json()
        return js

    def cancel(self, id):
        print('canceling order {}...'.format(id))
        payload = {
            'id': id,
            'nonce': self._nonce()
        }
        params = self._post_param(payload)
        r = self._setup_request('cancel', params, payload)  #
        js = r.json()
        return js

    def cancel_all(self, catalog=2):
        if catalog & 1 == 1:
            print('cancelling buy orders')
            buy = self.orders(0)['result']
            if buy is not None:
                for t in buy:
                    self.cancel(t['buy'])
        if (catalog >> 1) & 1 == 1:
            print('cancelling sell orders')
            sell = self.orders(1)['result']
            if sell is not None:
                for t in sell:
                    self.cancel(t['id'])

    @staticmethod
    def _order_info(order):
        create_time = BitBays.get_timestamp(order['created_at'], BitBays.fmt)
        # update_time = BitBaysAPI.get_timestamp(order['updated_at'], BitBaysAPI.fmt)
        order_id = order['id']
        price = common.to_decimal(order['price'])
        amount = common.to_decimal(order['amount_total'])
        return (create_time, order_id, price, amount)

    def get_orders_info(self):
        buy = self.orders(0)['result']
        buy_list = []
        if buy is not None:
            for t in buy:
                buy_list.append(BitBays._order_info(t))
            self._orders['buy'] = buy_list
        sell = self.orders(1)['result']
        sell_list = []
        if sell is not None:
            for t in sell:
                sell_list.append(BitBays._order_info(t))
            self._orders['sell'] = sell_list
        return self._orders

    def user_info(self):
        if self._user_data is None:
            payload = {
                'nonce': self._nonce()
            }
            params = self._post_param(payload)
            r = self._setup_request('info', params, payload)
            self._user_data = r.json()
        return self._user_data

    def orders(self, catalog, status=0):
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

    def transactions(self, catalog):
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
        info = self.user_info()
        wallet = info['result']['wallet']
        # my_logger.debug_logger.debug(wallet)
        return wallet

    def asset_list(self):
        info = self.user_info()['result']['wallet']
        l = [
            [common.to_decimal(info[self.symbol]['lock']), common.to_decimal(info[self.symbol]['avail'])],
            [common.to_decimal(info['btc']['lock']), common.to_decimal(info['btc']['avail'])]
        ]
        return l

    def current_trade(self, op):
        trade_jsdata = self.orders(op)
        trade_list = []
        for r in trade_jsdata['result']:
            created_at = r['created_at']
            updated_at = r['updated_at']
            sell_id = r['id']
            amount = common.to_decimal(r['amount_total'])
            price = common.to_decimal(r['price'])
            created_duration = BitBays.get_timestamp(created_at, BitBays.fmt)
            # current = (sell_id, created_duration, prince, amount)
            current = (price, amount)
            trade_list.append(current)
        return trade_list

    @staticmethod
    def get_timestamp(time_str, fmt):
        now = datetime.utcnow()
        date_obj = datetime.strptime(time_str, fmt)
        # FIXME error
        return (now - date_obj).seconds

    def my_trade(self, op, price, amount):
        order = {
            'op': op,
            'price': str(price),
            'amount': str(amount)
        }
        return self.trade(order)


if __name__ == '__main__':
    init()
    bitbays = BitBays()
    # bitbays.depth()
    bitbays.assets()
