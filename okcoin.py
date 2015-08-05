#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import hashlib
import os
import sys

import requests

from plt_api import Platform
import common
import config
from order_info import OrderInfo


class OKCoinAPI(Platform):
    lower_bound_dict = {
        'btc': 0.01,
        'ltc': 0.1
    }
    _logger = common.get_logger()
    trade_cancel_api_list = ['cancel_order', 'trade']
    common_headers = {
        'user-agent': common.USER_AGENT,
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    def __init__(self, info):
        super(OKCoinAPI, self).__init__(info)
        self.lower_bound =  OKCoinAPI.lower_bound_dict[self.coin_type]
        self.symbol = info['symbol']
        self.api_public = ['ticker', 'depth', 'trades']
        self.api_private = ['userinfo', 'trade', 'batch_trade', 'cancel_order', 'orders', 'order_info']

    def _real_uri(self, api_type):
        path = '/' + api_type + '.do'
        return self.get_url(path)

    def _sign(self, params):
        sign = ''
        for key in sorted(params.keys()):
            sign += key + '=' + str(params[key]) + '&'
        data = sign + 'secret_key=' + self.key['secret']
        sign = hashlib.md5(data.encode("utf8")).hexdigest().upper()
        return sign

    def _setup_request(self, api_type, params, data=None):
        """  the basic request function, also called by _private_request
        :param api_type:
        :param params:
        :param data:
        :return:
        """

        def _request_impl():
            r = None
            if api_type in self.api_public:
                r = requests.request('get', self._real_uri(api_type), params=params, headers=OKCoinAPI.common_headers,
                                     timeout=config.TIMEOUT, verify=True)
            elif api_type in self.api_private:
                # TODO data => js string?
                r = requests.request('post', self._real_uri(api_type), data=data, params=params,
                                     headers=OKCoinAPI.common_headers, timeout=config.TIMEOUT, verify=True)
            else:
                OKCoinAPI._logger.critical('api_type [{}] not supported'.format(api_type))
                os._exit(1)
            # OKCoinAPI._logger.debug(r.url)
            # TODO should consider exception
            res = r.json()
            # OKCoinAPI._logger.warning('response={}'.format(res))
            if res is None or res is {}:
                raise common.NULLResponseError(
                    'NULLResponseError: Response is empty/{} for api_type={}'.format(api_type))
            return res

        try:
            response_data = _request_impl()
            return response_data
        except Exception as e:
            if common.is_retry_exception(e):
                return common.handle_retry(e, _request_impl)
            else:
                common.handle_exit(e)

    ### public api

    def api_ticker(self):
        payload = {
            'symbol': self.coin_type + '_' + self.symbol
        }
        res = self._setup_request('ticker', payload)
        return res

    def ask1(self):
        ticker = self.api_ticker()
        sell = ticker['ticker']['sell']
        sell = common.to_decimal(sell)
        return sell

    def bid1(self):
        ticker = self.api_ticker()
        buy = ticker['ticker']['buy']
        buy = common.to_decimal(buy)
        return buy

    def api_depth(self, length=2):
        assert (1 <= length <= 200)
        payload = {
            'symbol': self.coin_type + '_' + self.symbol,
            'size': length,
            'merge': 0
        }
        res = self._setup_request('depth', payload)
        return res

    def ask_bid_list(self, length=2):
        data = self.api_depth(length)
        while data == {}:
            data = self.api_depth(length)
        asks = sorted(data['asks'], key=lambda ask: ask[0], reverse=True)
        bids = sorted(data['bids'], key=lambda bid: bid[0], reverse=True)
        # assert (asks[-1][0] + config.minor_diff >= bids[0][0])
        asks_bids = asks + bids
        return asks_bids

    def api_trades(self, since=None):
        payload = {
            'symbol': self.coin_type + '_' + self.symbol
        }
        if since is not None:
            payload['since'] = since
        res = self._setup_request('trades', payload)
        return res

    ### private api

    def _private_request(self, api_type, param_dict):
        params = {'api_key': self.key['api']}
        if param_dict is not None:
            params.update(param_dict)
        params['sign'] = self._sign(params)
        response_data = self._setup_request(api_type, None, params)
        result_status = response_data['result']
        if result_status is False:
            OKCoinAPI._logger.critical(
                'ERROR: api_type={}, response_data={}'.format(api_type, response_data))
            if api_type not in OKCoinAPI.trade_cancel_api_list:
                common.send_msg('error during request')
                # noinspection PyProtectedMember
                os._exit(1)
        return response_data

    def api_userinfo(self):
        res = self._private_request('userinfo', None)
        return res

    def api_trade(self, trade_dict):
        params = {
            'symbol': self.coin_type + '_' + self.symbol
        }
        params.update(trade_dict)
        if 'price' in params:
            # if params['price'] is not None:
            assert (0 < common.to_decimal(params['price']) <= 1000000)
        res = self._private_request('trade', params)
        return res

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
            return config.INVALID_ORDER_ID
        else:
            return data['order_id']

    def buy_market(self, mo_amount):
        OKCoinAPI._logger.debug('OKCoinAPI.buy_market with {}'.format(mo_amount))
        return self.trade('buy_market', mo_amount, None)

    def sell_market(self, mo_amount):
        assert (mo_amount >= OKCoinAPI.lower_bound)
        OKCoinAPI._logger.debug('OKCoinAPI.sell_market with amount {}'.format(mo_amount))
        return self.trade('sell_market', None, mo_amount)

    def api_cancel_order(self, order_id):
        params = {
            'symbol': self.coin_type + '_' + self.symbol,
            'order_id': order_id
        }
        res = self._private_request('cancel_order', params)
        return res

    def cancel(self, order_id):
        """
        return whether cancel succeeds or not
        """
        data = self.api_cancel_order(order_id)
        return data['result']

    def api_order_info(self, order_id):
        params = {
            'symbol': self.coin_type + '_' + self.symbol,
            'order_id': order_id
        }
        res = self._private_request('order_info', params)
        return res

    def order_info(self, order_id):
        try:
            response = self.api_order_info(order_id)
            info = response['orders'][0]
            catalog = info['type']
            remaining_amount = info['amount'] - info['deal_amount']
            order_info = OrderInfo(catalog, remaining_amount)
            return order_info
        except Exception as e:
            OKCoinAPI._logger.critical('ERROR: exception="{}", response={}'.format(e, response))
            common.send_msg('okcoin order error')
            # noinspection PyProtectedMember
            os._exit(1)

    def assets(self):
        funds = self.api_userinfo()['info']['funds']
        l = [
            [common.to_decimal(funds['freezed'][self.symbol]), common.to_decimal(funds['free'][self.symbol])],
            [common.to_decimal(funds['freezed'][self.coin_type]), common.to_decimal(funds['free'][self.coin_type])]
        ]
        return l


class OKCoinCN(OKCoinAPI):
    def __init__(self):
        super(OKCoinCN, self).__init__(config.okcoin_cn_info)
        self.key = common.get_key_from_data('OKCoinCN')


class OKCoinCOM(OKCoinAPI):
    def __init__(self):
        super(OKCoinCOM, self).__init__(config.okcoin_com_info)
        self.key = common.get_key_from_data('OKCoinCOM')


if __name__ == '__main__':
    common.init_logger()
    okcoin_cn = OKCoinCN()
    # okcoin_cn.coin_type = 'ltc'
    # print(okcoin_cn.lower_bound)
    # print(okcoin_cn.ask_bid_list(2))
    # print(okcoin_cn.assets())
    # order_id = okcoin_cn.trade('buy', 1, 1)
    # order_id = okcoin_cn.trade('sell', 100, 1)
    # print(order_id)
    # order_info = okcoin_cn.order_info(order_id)
    # print(order_info)
    # okcoin_cn.cancel(order_id)
    # okcoin_cn.cancel(123456)
