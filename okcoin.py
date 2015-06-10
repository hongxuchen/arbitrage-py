#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import hashlib
import sys
import datetime

import requests

from btc import BTC
import common
import config


class OKCoinAPI(BTC):
    def __init__(self, info):
        super(OKCoinAPI, self).__init__(info)
        self.symbol = info['symbol']

        self.api_public = ['ticker', 'depth', 'trades', 'kline', 'lend_depth']
        self.api_private = ['userinfo', 'trade', 'batch_trade', 'cancel_order', 'orders']

    def _real_uri(self, method):
        path = '/' + method + '.do'
        return self.get_url(path)

    def _sign(self, params):
        sign = ''
        for key in sorted(params.keys()):
            sign += key + '=' + str(params[key]) + '&'
        data = sign + 'secret_key=' + self.key['secret']
        sign = hashlib.md5(data.encode("utf8")).hexdigest().upper()
        return sign

    def _setup_request(self, method, params, data=None):
        try:
            r = None
            if method in self.api_public:
                r = requests.request('get', self._real_uri(method), params=params)
            elif method in self.api_private:
                r = requests.request('post', self._real_uri(method), data=data, params=params)
            else:
                print('method [{}] not supported'.format(method))
                sys.exit(1)
            # print(r.status_code, r.url)
            return r
        except Exception as e:
            print(e)
            sys.exit(1)

    def _userinfo(self):
        params = {'api_key': self.key['api']}
        params['sign'] = self._sign(params)
        r = self._setup_request('userinfo', None, params)
        js = r.json()
        if js['result'] is False:
            print('api error')
            sys.exit(1)
        return js

    def depth(self, length=2):
        assert (1 <= length <= 200)
        payload = {
            'symbol': 'btc_' + self.symbol,
            'size': length,
            'merge': 0
        }
        r = self._setup_request('depth', payload)
        data = r.json()
        asks = sorted(data['asks'], key=lambda ask: ask[0], reverse=True)
        bids = sorted(data['bids'], key=lambda bid: bid[0], reverse=True)
        # print(asks)
        # print(bids)
        assert (asks[-1][0] > bids[0][0])
        return asks + bids

    def _trades(self, since=None):
        payload = {
            'symbol': 'btc_' + self.symbol
        }
        if since is not None:
            payload['since'] = since
        r = self._setup_request('trades', payload)
        return r.json()

    def _kline(self, ktype='15min', size=10, since=None):
        payload = {
            'symbol': 'btc_' + self.symbol,
            'size': size,
            'type': ktype
        }
        if since is not None:
            payload['since'] = since
        else:
            yesterday = datetime.date.today() - datetime.timedelta(1)
            payload['since'] = yesterday.strftime('%s')
        r = self._setup_request('kline', payload)
        return r.json()

    def _lend_depth(self, symbol='btc_cny'):
        if symbol not in ['btc_cny', 'cny']:
            print('illegal symbol')
            sys.exit(1)
        payload = {
            'symbol': symbol
        }
        r = self._setup_request('lend_depth', params=payload)
        return r.json()

    def asset_list(self):
        funds = self._userinfo()['info']['funds']
        l = [
            [common.to_decimal(funds['freezed'][self.symbol]), common.to_decimal(funds['free'][self.symbol])],
            [common.to_decimal(funds['freezed']['btc']), common.to_decimal(funds['free']['btc'])]
        ]
        return l


class OKCoinCN(OKCoinAPI):
    def __init__(self):
        super(OKCoinCN, self).__init__(config.okcoin_cn_info)
        self.key = common.get_key_from_file('OKCoinCN')


class OKCoinCOM(OKCoinAPI):
    def __init__(self):
        super(OKCoinCOM, self).__init__(config.okcoin_com_info)
        self.key = common.get_key_from_file('OKCoinCOM')


if __name__ == '__main__':
    okcoin_cn = OKCoinCN()
    print(okcoin_cn.depth(5))
