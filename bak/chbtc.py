#!/usr/bin/env python

from __future__ import print_function
import hashlib
from hashlib import sha1
import time
import struct
from collections import OrderedDict
import requests

from settings import config
from utils import common, plt_helper
from utils import excepts
from utils import log_helper
from utils.order_info import PlatformOrderInfo
from api.plt import Platform


class CHBTC(Platform):
    plt_info = {
        'domain': 'https://trade.chbtc.com/api/',
        'data_domain': 'http://api.chbtc.com/data/',
        'fiat': 'cny'
    }
    lower_bound_dict = {
        'btc': 0.001,
        'ltc': 0.001
    }
    trade_type_map = {
        'buy': 1,
        'sell': 0
    }
    _logger = log_helper.get_logger()
    trade_cancel_api_list = ['order', 'cancelOrder']
    data_domain = plt_info['data_domain']
    common_headers = {
        'user-agent': config.USER_AGENT
    }

    def __init__(self):
        super(CHBTC, self).__init__(self.plt_info)
        self.fiat_type = self.plt_info['fiat']
        self.lower_bound = CHBTC.lower_bound_dict[self.coin_type]
        self.key = plt_helper.get_key_from_data('CHBTC')
        self.api_public = ['ticker', 'depth', 'trades']
        self.api_private = ['order', 'cancelOrder', 'getOrder', 'getOrdersNew', 'getOrdersIgnoreTradeType',
                            'getUnfinishedOrdersIgnoreTradeType', 'getAccountInfo']

    def _setup_requests(self, api_type, params=None):
        def _request_impl():
            r = None
            if api_type in self.api_public:
                if self.coin_type == 'btc':
                    uri = CHBTC.data_domain + api_type
                else:
                    uri = CHBTC.data_domain + 'ltc/' + api_type
                r = requests.get(uri, headers=CHBTC.common_headers, timeout=config.REQUEST_TIMEOUT)
            elif api_type in self.api_private:
                base_uri = self.prefix + api_type + '?'
                param_str = self._signed_param(params)
                request_str = base_uri + param_str
                r = requests.get(request_str, timeout=config.REQUEST_TIMEOUT)
                if r.status_code != requests.codes.ok:
                    raise excepts.CHBTCRetryError('CHBTCRetryError: response status_code={}'.format(r.status_code))
            else:
                excepts.handle_exit('msg: CHBTC api_type={} not supported'.format(api_type))
            try:
                res_data = r.json()
                if 'code' in res_data:
                    code = res_data['code']
                    if code == 1000:
                        return res_data
                    CHBTC._logger.error(u'CHBTC Error: code={}, msg={}'.format(code, res_data['message']))
                    if code in [1001, 1002, 1003, 3002, 3003, 3004, 3005, 3006, 4001, 4002]:
                        raise excepts.CHBTCExitError(
                            'CHBTCExitError: code={}, msg={}'.format(code, res_data['message']))
                    elif code in [2001, 2002, 2003, 3001]:
                        CHBTC._logger.warning('ignore error, code={}'.format(code))
                    else:
                        raise excepts.CHBTCRetryError(
                            'CHBTCRetryError: code={}, msg={}'.format(code, res_data['message']))
                return res_data
            except ValueError as ee:
                err_msg = 'msg: CHBTC parse json error "{}" for api_type={}, response={}'.format(ee, api_type, r)
                excepts.handle_exit(err_msg)

        try:
            res = _request_impl()
            return res
        except Exception as e:
            if excepts.is_retry_exception(e):
                return excepts.handle_retry(e, _request_impl)
            else:
                excepts.handle_exit(e)

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

    @staticmethod
    def __fill(value, length, fill_byte):
        if len(value) >= length:
            return value
        else:
            fill_size = length - len(value)
            return value + chr(fill_byte) * fill_size

    @staticmethod
    def __do_xor(s, value):
        slist = list(s)
        for index in xrange(len(slist)):
            slist[index] = chr(ord(slist[index]) ^ value)
        return "".join(slist)

    @staticmethod
    def __digest(a_val):
        value = struct.pack("%ds" % len(a_val), a_val)
        h = sha1()
        h.update(value)
        dg = h.hexdigest()
        return dg

    def __hmac_sign(self, a_value, a_key):
        keyb = struct.pack("%ds" % len(a_key), a_key)
        value = struct.pack("%ds" % len(a_value), a_value)
        k_ipad = self.__do_xor(keyb, 0x36)
        k_opad = self.__do_xor(keyb, 0x5c)
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
        param_list = [l[0] + '=' + str(l[1]) for l in param_dict.items()]
        message_str = '&'.join(param_list)
        sha_secret = self.__digest(self.key['secret'])
        sig = self.__hmac_sign(message_str, sha_secret)
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
        frozen, avail = user_info['frozen'], user_info['balance']
        l = [
            [
                common.to_decimal(frozen[self.fiat_type.upper()]['amount']),
                common.to_decimal(avail[self.fiat_type.upper()]['amount'])],
            [
                common.to_decimal(frozen[self.coin_type.upper()]['amount']),
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
        order_info = PlatformOrderInfo(order_id, catalog, remaining_amount)
        return order_info


if __name__ == '__main__':
    log_helper.init_logger()
    chbtc = CHBTC()
    print(chbtc.assets())
