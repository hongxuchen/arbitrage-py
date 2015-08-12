#!/usr/bin/env python

from __future__ import print_function
import hashlib
import os
import sha
import time
import struct
from collections import OrderedDict

import requests

import common
import config
from order_info import OrderInfo
from plt_api import Platform


class CHBTC(Platform):
    lower_bound_dict = {
        'btc': 0.001,
        'ltc': 0.001
    }
    trade_type_map = {
        'buy': 1,
        'sell': 0
    }
    _logger = common.get_logger()
    trade_cancel_api_list = ['order', 'cancelOrder']
    data_domain = config.chbtc_info['data_domain']
    common_headers = {
        'user-agent': common.USER_AGENT
    }

    def __init__(self):
        super(CHBTC, self).__init__(config.chbtc_info)
        self.symbol = config.bitbays_info['symbol']
        self.lower_bound = CHBTC.lower_bound_dict[self.coin_type]
        self.key = common.get_key_from_data('CHBTC')
        self.api_public = ['ticker', 'depth', 'trades']
        self.api_private = ['order', 'cancelOrder', 'getOrder', 'getOrdersNew', 'getOrdersIgnoreTradeType',
                            'getUnfinishedOrdersIgnoreTradeType', 'getAccountInfo']

    def _setup_requests(self, api_type, params=None, data=None):
        def _request_impl():
            r = None
            if api_type in self.api_public:
                if self.coin_type == 'btc':
                    uri = CHBTC.data_domain + api_type
                else:
                    uri = CHBTC.data_domain + 'ltc/' + api_type
                r = requests.get(uri, headers=CHBTC.common_headers, timeout=config.TIMEOUT)
            elif api_type in self.api_private:
                base_uri = self.domain + api_type + '?'
                param_str = self._signed_param(params)
                request_str = base_uri + param_str
                # print(request_str)
                r = requests.get(request_str, timeout=config.TIMEOUT)
            else:
                os._exit(1)
            res_data = r.json()
            if 'code' in res_data:
                code = res_data['code']
                if code == 1000:
                    return res_data
                CHBTC._logger.error(u'CHBTC Error: code={}, msg={}'.format(code, res_data['message']))
                if code in [1001, 1002, 1003, 3002, 3003, 3004, 3005, 3006, 4001, 4002]:
                    raise common.CHBTCExitError('CHBTCExitError: code={}, msg={}'.format(code, res_data['message']))
                elif code in [2001, 2002, 2003, 3001]:
                    CHBTC._logger.warning('ignore error, code={}'.format(code))
                else:
                    raise common.CHBTCRetryError('CHBTCRetryError: code={}, msg={}'.format(code, res_data['message']))
            return res_data

        try:
            res = _request_impl()
            return res
        except Exception as e:
            if common.is_retry_exception(e):
                return common.handle_retry(e, _request_impl)
            else:
                common.handle_exit(e)

    def _private_requests(self, param_dict):
        api_type = param_dict['method']
        res = self._setup_requests(api_type, param_dict)
        return res

    def api_ticker(self):
        return self._setup_requests('ticker')

    def ask1(self):
        ticker = self.api_ticker()
        return common.to_decimal(ticker['ticker']['sell'])

    def bid1(self):
        ticker = self.api_ticker()
        return common.to_decimal(ticker['ticker']['buy'])

    def api_depth(self):
        depth = self._setup_requests('depth')
        return depth

    def ask_bid_list(self, length):
        res = self.api_depth()
        asks = sorted(res['asks'], key=lambda ask: ask[0], reverse=True)[-length:]
        bids = sorted(res['bids'], key=lambda bid: bid[0], reverse=True)[:length]
        asks_bids = asks + bids
        return asks_bids

    def api_trades(self):
        return self._setup_requests('trades')

    def __fill(self, value, lenght, fillByte):
        if len(value) >= lenght:
            return value
        else:
            fillSize = lenght - len(value)
        return value + chr(fillByte) * fillSize

    def __doXOr(self, s, value):
        slist = list(s)
        for index in xrange(len(slist)):
            slist[index] = chr(ord(slist[index]) ^ value)
        return "".join(slist)

    ## TODO use hashlib
    def __digest(self, aValue):
        value = struct.pack("%ds" % len(aValue), aValue)
        h = sha.new()
        h.update(value)
        dg = h.hexdigest()
        return dg

    def __hmacSign(self, aValue, aKey):
        keyb = struct.pack("%ds" % len(aKey), aKey)
        value = struct.pack("%ds" % len(aValue), aValue)
        k_ipad = self.__doXOr(keyb, 0x36)
        k_opad = self.__doXOr(keyb, 0x5c)
        k_ipad = self.__fill(k_ipad, 64, 54)
        k_opad = self.__fill(k_opad, 64, 92)
        m = hashlib.md5()
        m.update(k_ipad)
        m.update(value)
        dg = m.digest()

        m = hashlib.md5()
        m.update(k_opad)
        sub_str = dg[0:16]
        m.update(sub_str)
        dg = m.hexdigest()
        return dg

    def _signed_param(self, param_dict):
        # accesskey_str = 'accesskey=' + self.key['api']
        # del param_dict['method']
        param_list = [l[0] + '=' + str(l[1]) for l in param_dict.items()]
        message_str = '&'.join(param_list)
        sha_secret = self.__digest(self.key['secret'])
        sig = self.__hmacSign(message_str, sha_secret)
        sign_str = 'sign=' + sig
        now = int(time.time() * 1000)
        req_time_str = 'reqTime=' + str(now)
        param_str = '&'.join([message_str] + [sign_str, req_time_str])
        # print(param_str)
        return param_str

    def api_getaccountinfo(self):
        param_dict = OrderedDict()
        param_dict['method'] = 'getAccountInfo'
        param_dict['accesskey'] = self.key['api']
        res = self._private_requests(param_dict)
        return res

    def assets(self):
        user_info = self.api_getaccountinfo()['result']
        fronzen, avail = user_info['frozen'], user_info['balance']
        l = [
            [
                common.to_decimal(fronzen[self.symbol.upper()]['amount']),
                common.to_decimal(avail[self.symbol.upper()]['amount'])],
            [
                common.to_decimal(fronzen[self.coin_type.upper()]['amount']),
                common.to_decimal((avail[self.coin_type.upper()])['amount'])
            ]
        ]
        return l

    def api_trade(self, trade_type, price, amount):
        param_dict = OrderedDict()
        param_dict['method'] = 'order'
        param_dict['accesskey'] = self.key['api']
        param_dict['price'] = str(price)
        param_dict['amount'] = str(amount)
        param_dict['tradeType'] = CHBTC.trade_type_map[trade_type]
        param_dict['currency'] = self.coin_type
        res = self._private_requests(param_dict)
        return res

    def trade(self, trade_type, price, amount):
        res = self.api_trade(trade_type, price, amount)
        if res['code'] == 1000:
            return int(res['id'])
        else:
            return config.INVALID_ORDER_ID

    def api_cancel(self, order_id):
        param_dict = OrderedDict()
        param_dict['method'] = 'cancelOrder'
        param_dict['accesskey'] = self.key['api']
        param_dict['id'] = str(order_id)
        param_dict['currency'] = self.coin_type
        res = self._private_requests(param_dict)
        return res

    def cancel(self, order_id):
        res = self.api_cancel(order_id)
        if res['code'] == 1000:
            return True
        else:
            return False

    def api_order_info(self, order_id):
        param_dict = OrderedDict()
        param_dict['method'] = 'getOrder'
        param_dict['accesskey'] = self.key['api']
        param_dict['id'] = str(order_id)
        param_dict['currency'] = self.coin_type
        res = self._private_requests(param_dict)
        return res

    def order_info(self, order_id):
        res = self.api_order_info(order_id)
        remaining_amount = res['total_amount'] - res['trade_amount']
        catalog_type = res['type']
        if catalog_type == 1:
            catalog = 'buy'
        else:  # catalog_type == 0
            catalog = 'sell'
        order_info = OrderInfo(catalog, remaining_amount)
        return order_info


if __name__ == '__main__':
    common.init_logger()
    chbtc = CHBTC()
    ask1 = chbtc.ask1()
    print(type(ask1))
    # order_id = chbtc.trade('buy', 2000, 0.001)
    # print(order_id)
    # order_info = chbtc.order_info(order_id)
    # print(order_info)
    # cancel = chbtc.cancel(order_id)
    # print(cancel)
    # order_id = chbtc.trade('sell', 1000, 0.001)
    # print(order_id)
    # order_info = chbtc.order_info(order_id)
    # print(order_info)
    # cancel = chbtc.cancel(order_id)
    # print(cancel)
    # order_info = chbtc.order_info(order_id)
    # print(order_info)
    # res = chbtc.cancel(order_id)
    # print(res)
    # order_id = 1233456
    # res = chbtc.order_info(order_id)
    # print(res)
    # res = chbtc.cancel(123456)
    # print(res)
    # res = chbtc.assets()
    # print(res)
    # print(chbtc.api_depth())
    # print(chbtc.ask_bid_list(1))
    # print(chbtc.api_trades())
