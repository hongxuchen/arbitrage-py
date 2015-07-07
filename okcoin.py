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
from order_info import OrderInfo


class OKCoinAPI(BTC):
    _logger = common.setup_logger()
    headers = {
        'user-agent': config.USER_AGENT,
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    def __init__(self, info):
        super(OKCoinAPI, self).__init__(info)
        self.symbol = info['symbol']
        self.api_public = ['ticker', 'depth', 'trades', 'kline', 'lend_depth']
        self.api_private = ['userinfo', 'trade', 'batch_trade', 'cancel_order', 'orders', 'order_info']

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
        """  the basic request function, also called by _private_request
        :param method:
        :param params:
        :param data:
        :return:
        """

        def request_impl():
            r = None
            if method in self.api_public:
                r = requests.request('get', self._real_uri(method), params=params, headers=OKCoinAPI.headers)
            elif method in self.api_private:
                # TODO data => json string?
                r = requests.request('post', self._real_uri(method), data=data, params=params,
                                     headers=OKCoinAPI.headers)
            else:
                OKCoinAPI._logger.critical('method [{}] not supported'.format(method))
                sys.exit(1)
            return r

        try:
            r = request_impl()
            # OKCoinAPI._logger.debug(r.url)
            if r is None:
                OKCoinAPI._logger.critical('ERROR: return None for params={}, data={}'.format(params, data))
                # FIXME terminate safely
                sys.exit(1)
            return r
        except config.retry_except_tuple as e:
            common.handle_retry(e, OKCoinAPI, request_impl)
        except config.exit_except_tuple as e:
            common.handle_exit(e, OKCoinAPI)
        except Exception as e:
            common.handle_exit(e, OKCoinAPI)

    ### public api

    def api_ticker(self):
        payload = {
            'symbol': 'btc' + self.symbol
        }
        r = self._setup_request('ticker', payload)
        return r.json()

    def ask1(self):
        ticker = self.api_ticker()
        sell = ticker['ticker']['sell']
        sell = common.to_decimal(sell)
        return sell

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
        # OKCoinAPI._logger.debug(data)
        asks = sorted(data['asks'], key=lambda ask: ask[0], reverse=True)
        bids = sorted(data['bids'], key=lambda bid: bid[0], reverse=True)
        assert (asks[-1][0] > bids[0][0])
        asks_bids = asks + bids
        # OKCoinAPI._logger.debug(asks_bids)
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
        assert (r is not None)
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
        if 'price' in params:
            # if params['price'] is not None:
            assert (0 < common.to_decimal(params['price']) <= 1000000)
        r = self._private_request('trade', params)
        data = r.json()
        return data

    def trade(self, trade_type, price, amount):
        assert (trade_type in ['buy', 'sell', 'buy_market', 'sell_market'])
        trade_dict = {
            'type': trade_type
        }
        if price:
            trade_dict['price'] = str(price)
        if amount:
            trade_dict['amount'] = str(amount)

        data = self.api_trade(trade_dict)
        if data['result'] is False:
            OKCoinAPI._logger.critical(data)
            sys.exit(1)
        return data['order_id']

    def buy_market(self, mo_amount):
        OKCoinAPI._logger.debug('OKCoinAPI.buy_market with {}'.format(mo_amount))
        return self.trade('buy_market', mo_amount, None)

    def sell_market(self, mo_amount):
        assert (mo_amount >= config.lower_bound)
        OKCoinAPI._logger.debug('OKCoinAPI.sell_market with amount {}'.format(mo_amount))
        return self.trade('sell_market', None, mo_amount)

    def api_batch_trade(self, trade_dict):
        pass

    def api_cancel_order(self, order_id):
        params = {
            'symbol': 'btc_' + self.symbol,
            'order_id': order_id
        }
        r = self._private_request('cancel_order', params)
        return r.json()

    def cancel(self, order_id):
        OKCoinAPI._logger.info('canceling order {}...'.format(order_id))
        data = self.api_cancel_order(order_id)
        return data

    def api_order_info(self, order_id):
        params = {
            'symbol': 'btc_' + self.symbol,
            'order_id': order_id
        }
        r = self._private_request('order_info', params)
        return r.json()

    def order_info(self, order_id):
        # orders = self.api_order_info(order_id)
        # print(orders)
        info = self.api_order_info(order_id)['orders'][0]
        catalog = info['type']
        remaining_amount = info['amount'] - info['deal_amount']
        # create_time = info['create_date'] / 1000.0
        # order_info = OrderInfo(catalog, remaining_amount, create_time)
        order_info = OrderInfo(catalog, remaining_amount)
        return order_info

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
    lower_bound = 0.01

    def __init__(self):
        super(OKCoinCN, self).__init__(config.okcoin_cn_info)
        self.key = common.get_key_from_file('OKCoinCN')


class OKCoinCOM(OKCoinAPI):
    def __init__(self):
        super(OKCoinCOM, self).__init__(config.okcoin_com_info)
        self.key = common.get_key_from_file('OKCoinCOM')


status_dict = {
    -1: 'cancelled',
    0: 'unfilled',
    1: 'partially filled',
    2: 'fully filled',
    4: 'cancel request in process'
}

if __name__ == '__main__':
    okcoin_cn = OKCoinCN()
    while True:
        print(okcoin_cn.ask_bid_list(2))
        print(okcoin_cn.assets())
        # res = okcoin_cn.api_trade(trade_dict)
        # order_id = okcoin_cn.trade('buy', 10, 0.01)
        # res = okcoin_cn.order_info(order_id)
        # print(res)
