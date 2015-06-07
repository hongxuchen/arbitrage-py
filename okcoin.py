#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from collections import OrderedDict
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
        # print("DATA=",data)
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

    def userinfo(self):
        params = {'api_key': self.key['api']}
        params['sign'] = self._sign(params)
        # print(params)
        r = self._setup_request('userinfo', None, params)
        # print(r.content)
        js = r.json()
        # print(js)
        if js['result'] is False:
            print('api error')
            sys.exit(1)
        return js

    # need to ensure that the rate is only computed once
    # if in future using 'ltc', self._currency_rate should be a tuple
    # TODO make configurable
    def currency_rate(self):
        payload = {
            'symbol': 'btc_' + self.symbol
        }
        r = self._setup_request('ticker', payload)
        rate_str = float(r.json()['ticker']['last'])
        return common.to_decimal(rate_str, config.precision)

    def depth(self, size=5, should_merge=0):
        assert (5 <= size <= 200)
        payload = {
            'symbol': 'btc_' + self.symbol,
            'size': size,
            'merge': should_merge
        }
        r = self._setup_request('depth', payload)
        data = r.json()
        asks = sorted(data['asks'], key=lambda ask: ask[0], reverse=True)
        bids = sorted(data['bids'], key=lambda bid: bid[0])
        # print(asks)
        # print(bids)
        assert(asks[-1][0] > bids[0][0])
        return asks + bids

    def trades(self, since=None):
        payload = {
            'symbol': 'btc_' + self.symbol
        }
        if since is not None:
            payload['since'] = since
        r = self._setup_request('trades', payload)
        return r.json()

    def kline(self, ktype='15min', size=10, since=None):
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

    def lend_depth(self, symbol='btc_cny'):
        if symbol not in ['btc_cny', 'cny']:
            print('illegal symbol')
            sys.exit(1)
        payload = {
            'symbol': symbol
        }
        r = self._setup_request('lend_depth', params=payload)
        return r.json()

    def get_funds(self):
        funds = self.userinfo()['info']['funds']
        return funds

    def get_coin(self, currency, status):
        try:
            raw_str = self.get_funds()[status][currency]
            return common.to_decimal(raw_str, config.precision)
        except:
            print(
                'funds[{}][{}] not exists'.format(
                    status,
                    currency),
                file=sys.stderr)
            return 0


    def dump(self):
        record = {'btc': self.get_coin('btc', 'free') +
                         self.get_coin('btc', 'freezed') +
                         self.get_coin('btc', 'union_fund'),
                  self.symbol: self.get_coin(self.symbol, 'free') +
                               self.get_coin(self.symbol, 'freezed')}
        record = OrderedDict(record)

        total = common.to_decimal(self.get_funds()['asset']['total'], config.precision)

        record['rate'] = self.currency_rate()
        record['total_' + self.symbol] = total
        record['total_btc'] = total / self.currency_rate()

        for k in record:
            print('{:10s} {:10.4f}'.format(k, record[k]))
        print()


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
    # info = okcoin_cn.userinfo(False)
    # print(info)
    # print(okcoin_cn.trades())
    # print(okcoin_cn.kline())
    # print(okcoin_cn.lend_depth())
    # okcoin_cn.dump()
    print(okcoin_cn.depth(5))
    # okcoin_com = OKCoinCOM()
    # okcoin_com.dump()
    # print('okcoin_com:  btc/usd={:.4f}'.format(okcoin_com.currency_rate()))
    # print('okcoin_cn:   btc/cny={:.4f}'.format(okcoin_cn.currency_rate()))
    # print('yahoo:       usd/cny={:.4f}'.format(common.get_usd_cny_rate()))
    # print('okcoin:      usd/cny={:.4f}'.format(okcoin_cn.currency_rate() / okcoin_com.currency_rate()))
