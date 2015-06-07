#!/usr/bin/env python

from __future__ import print_function
import hashlib
import hmac
import json
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
            # print(r.url)
            return r
        except Exception as e:
            print(e)
            sys.exit(1)

    def btc_rate(self):
        r = self._setup_request('ticker')
        js = r.json()
        return common.to_decimal(js['result']['last'])

    def depth(self):
        r = self._setup_request('depth')
        js = r.json()
        return js

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
            'market': 'btc_usd'
        }
        r = self._setup_request('trades', params=payload)
        js = r.json()
        return js

    # trade operations
    def trade(self, order):
        payload = {
            'market': 'btc_usd',
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
        r = self._setup_request('cancel', params, payload) #
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
            'market': 'btc_usd',
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
            'market': 'btc_usd',
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

    def dump_buy_sell(self):
        self.print_js(self.transactions(0))
        self.print_js(self.transactions(1))


    def asset(self):
        asset = {}
        info = self.user_info()
        wallet = info['result']['wallet']
        fund = self.user_info()['result']['fund']['arbitrage']
        asset['wallet_asset'] = wallet['usd'], wallet['btc']
        asset['fund_asset'] = fund['usd']['avail'], fund['btc']['avail']
        return asset

    def print_js(self, json_data):
        print(json.dumps(json_data, indent=2))


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
        # print(date_obj)
        # print(now)
        # FIXME error
        return (now - date_obj).seconds


    def dump(self):
        print('btc_rate: {}'.format(bitbays.btc_rate()))
        asset = self.asset()
        usd = common.to_decimal(asset['wallet_asset'][0]['avail']), common.to_decimal(
            asset['wallet_asset'][0]['lock']), common.to_decimal(asset['fund_asset'][0])
        btc = common.to_decimal(asset['wallet_asset'][1]['avail']), common.to_decimal(
            asset['wallet_asset'][1]['lock']), common.to_decimal(asset['fund_asset'][1])
        print('{:5}{:>15}{:>15}{:>15}'.format(' ', 'avail', 'lock', 'fund'))
        print('{:5}{:>15f}{:>15f}{:>15f}'.format('usd', usd[0], usd[1], usd[2]))
        print('{:5}{:>15f}{:>15f}{:>15f}'.format('btc', btc[0], btc[1], btc[2]))
        import operator

        acc = lambda t: reduce(operator.add, t, 0)
        print('usd->btc {:>15f}'.format(acc(usd) / self.btc_rate()))
        print('btc----> {:>15f}'.format(acc(btc)))


    def my_trade(self, op, price, amount):
        order = {
            'op': op,
            'price': str(price),
            'amount': str(amount)
        }
        return self.trade(order)

    def smart_trade(self, bound):
        print(self.get_ask_bid())
        wallet = self.user_info()['result']['wallet']
        available = {
            'usd': common.to_decimal(wallet['usd']['avail']),
            'btc': common.to_decimal(wallet['btc']['avail'])
        }
        lock = {
            'usd': common.to_decimal(wallet['usd']['lock']),
            'btc': common.to_decimal(wallet['btc']['lock'])
        }
        if available['btc'] + lock['btc'] >= 1:
            assert ( available['usd'] + lock['usd'] < 100)
            if available['btc'] >= 1:
                print('selling', bound[1], available['btc'])
                self.my_trade('sell', bound[1], available['btc'])
            else:
                assert (lock['btc'] >= 1)
                # print('locked [btc]')
        else:
            assert (available['btc'] + lock['btc'] < 1)
            if available['usd'] > 100:
                print('buying', bound[0], available['usd'])
                amount = available['usd']/bound[0]
                trade_info = self.my_trade('buy', bound[0], amount)
                print(trade_info)
            else:
                assert (lock['usd'] > 100)
                # print('locked [usd]')

    def ask_bid_query(self, duration=10):
        old = None
        new = None
        while True:
            new = bitbays.get_ask_bid()
            if new != old:
                old = new
                print(new)
            time.sleep(duration)


if __name__ == '__main__':
    init()
    bitbays = BitBays()
    bitbays.ask_bid_query()
    # bitbays.smart_trade([234, 235])
    # print(bitbays.current_trade(0), bitbays.current_trade(1))
