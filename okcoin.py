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
    _logger = common.setup_logger()
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
                OKCoinAPI._logger.critical('method [{}] not supported'.format(method))
                sys.exit(1)
            # OKCoinAPI._logger.debug(r.url)
            return r
        except Exception as e:
            OKCoinAPI._logger.critical(e)
            sys.exit(1)

    ### public api

    def api_ticker(self):
        payload = {
            'symbol': 'btc' + self.symbol
        }
        r = self._setup_request('ticker', payload)
        return r.json()

    def api_depth(self, length=2):
        assert (1 <= length <= 200)
        payload = {
            'symbol': 'btc_' + self.symbol,
            'size': length,
            'merge': 0
        }
        r = self._setup_request('depth', payload)
        return r.json()

    def ask_bid_list(self, length=2):
        data = self.api_depth(length)
        asks = sorted(data['asks'], key=lambda ask: ask[0], reverse=True)
        bids = sorted(data['bids'], key=lambda bid: bid[0], reverse=True)
        assert (asks[-1][0] > bids[0][0])
        asks_bids = asks + bids
        OKCoinAPI._logger.debug(asks_bids)
        return asks_bids

    def api_trades(self, since=None):
        payload = {
            'symbol': 'btc_' + self.symbol
        }
        if since is not None:
            payload['since'] = since
        r = self._setup_request('trades', payload)
        return r.json()

    def api_kline(self, ktype='15min', size=10, since=None):
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

    def api_lend_depth(self, symbol='btc_cny'):
        if symbol not in ['btc_cny', 'cny']:
            OKCoinAPI._logger.critical('illegal symbol')
            sys.exit(1)
        payload = {
            'symbol': symbol
        }
        r = self._setup_request('lend_depth', params=payload)
        return r.json()

    ### private api

    def _private_request(self, api_type, param_dict):
        params = {'api_key': self.key['api']}
        if param_dict is not None:
            params.update(param_dict)
        params['sign'] = self._sign(params)
        # print(params)
        r = self._setup_request(api_type, None, params)
        return r

    def api_userinfo(self):
        r = self._private_request('userinfo', None)
        data = r.json()
        if data['result'] is False:
            OKCoinAPI._logger.critical('api error')
            sys.exit(1)
        return data

    def api_trade(self, trade_dict):
        params = {
            'symbol': 'btc_' + self.symbol
        }
        params.update(trade_dict)
        assert (0 < common.to_decimal(params['price']) <= 1000000)
        r = self._private_request('trade', params)
        data = r.json()
        return data

    def trade(self, trade_type, price, amount):
        trade_dict = {
            'type': trade_type,
            'price': str(price),
            'amount': str(amount)
        }
        data = self.api_trade(trade_dict)
        if data['result'] is False:
            OKCoinAPI._logger.critical(data)
            sys.exit(1)
        return data

    def api_batch_trade(self, trade_dict):
        pass

    def api_cancel_order(self, order_id):
        params = {
            'symbol': 'btc_' + self.symbol
        }
        params.update(order_id)
        r = self._private_request('cancel_order', params)
        return r.json()

    def cancel(self, order_id):
        data = self.api_cancel_order(order_id)
        return data

    def api_order_history(self):
        pass

    def api_withdraw(self):
        pass

    def api_cancel_withdraw(self):
        pass

    def api_order_fee(self):
        pass

    def assets(self):
        funds = self.api_userinfo()['info']['funds']
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
    print(okcoin_cn.assets())
    trade_dict = {
        'type': 'buy',
        'price': '1',
        'amount': '0.01'
    }
    trade_dict = {
        'type': 'sell',
        'price': '10000',
        'amount': '0.1'
    }
    res = okcoin_cn.api_trade(trade_dict)
    print(res)
