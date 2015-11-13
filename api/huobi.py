#!/usr/bin/env python

import hashlib
import time
import urllib
import requests
from api.plt import Platform
from settings import config
from utils import common, plt_helper
from utils import excepts
from utils import log_helper
from utils.order_info import PlatformOrderInfo


class HuoBi(Platform):
    plt_info = {
        'domain': 'https://api.huobi.com/apiv3',
        'data_domain': 'http://api.huobi.com/staticmarket',
        'fiat': 'cny'
    }
    data_domain = plt_info['data_domain']
    coin_type_map = {
        'btc': 1,
        'ltc': 2
    }
    catalog_map = {
        1: 'buy',
        2: 'sell',
        3: 'buy',
        4: 'sell'
    }
    lower_bound_dict = {
        'btc': 0.001,
        'ltc': 0.01
    }
    _logger = log_helper.get_logger()
    common_headers = {
        'user-agent': config.USER_AGENT,
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    def __init__(self):
        super(HuoBi, self).__init__(self.plt_info)
        self.lower_bound = HuoBi.lower_bound_dict[self.coin_type]
        self.key = plt_helper.get_key_from_data('HuoBi')
        self.api_private = ['cancel_order', 'get_account_info', 'buy', 'sell', 'order_info']

    @staticmethod
    def _sign(params):
        params = sorted(params.iteritems(), key=lambda d: d[0], reverse=False)
        message = urllib.urlencode(params)
        m = hashlib.md5()
        m.update(message)
        m.digest()
        sig = m.hexdigest()
        return sig

    # noinspection PyMethodMayBeStatic
    def _setup_request(self, api_uri, params=None):
        def _request_impl():
            if api_uri not in self.api_private:
                r = requests.get(api_uri, data=params, headers=HuoBi.common_headers, timeout=config.REQUEST_TIMEOUT)
            else:
                timestamp = long(time.time())
                param_dict = {
                    'access_key': self.key['api'],
                    'secret_key': self.key['secret'],
                    'created': timestamp,
                    'method': api_uri
                }
                if params is not None:
                    param_dict.update(params)
                param_dict['sign'] = self._sign(param_dict)
                del param_dict['secret_key']
                # print(param_dict)
                r = requests.post(self.domain, params=param_dict, headers=HuoBi.common_headers,
                                  timeout=config.REQUEST_TIMEOUT)
                res_data = r.json()
                # deal with exceptions
                if 'code' in res_data and res_data['code'] != 0:
                    code = res_data['code']
                    msg = res_data['msg']
                    HuoBi._logger.error(u'HuoBi Error: code={}, msg={}'.format(code, msg))
                    if code in [5, 7, 61, 63, 74]:
                        raise excepts.HuoBiExitError(u'HuoBi Fatal Error: code={}, msg={}'.format(code, msg))
                    elif code == 71:
                        raise excepts.RateExceedError(u'HuoBi Rate Exceed: code={}, msg={}'.format(code, msg))
                    elif code == 1:
                        raise excepts.HuoBiError(u'HuoBi Unknown Error: code={}, msg={}'.format(code, msg))
            try:
                res_data = r.json()
                return res_data
            except ValueError as ee:
                err_msg = u'msg: HuoBi parse json error "{}" for api_uri={}, response={}'.format(ee, api_uri, r)
                HuoBi._logger.critical(err_msg)
                raise excepts.MayDisconnectedException(err_msg)

        try:
            result = _request_impl()
            return result
        except Exception as e:
            if excepts.is_retry_exception(e):
                return excepts.handle_retry(e, _request_impl)
            else:
                HuoBi._logger.critical(u'HuoBi Error, Exception type: {}'.format(type(e)))
                excepts.handle_exit(e)

    def api_ticker(self):
        api_uri = HuoBi.data_domain + '/' + 'ticker_' + self.coin_type + '_json.js'
        return self._setup_request(api_uri)

    def api_depth(self, length):
        api_uri = HuoBi.data_domain + '/' + 'depth_' + self.coin_type + '_' + str(length) + '.js'
        return self._setup_request(api_uri)

    def ask1(self):
        ticker = self.api_ticker()
        return ticker['ticker']['sell']

    def bid1(self):
        ticker = self.api_ticker()
        return ticker['ticker']['buy']

    def ask_bid_list(self, length):
        res = self.api_depth(length)
        asks = sorted(res['asks'], key=lambda ask: ask[0], reverse=True)
        bids = sorted(res['bids'], key=lambda bid: bid[0], reverse=True)
        asks_bids = asks + bids
        return asks_bids

    def trade(self, trade_type, price, amount):
        params = {
            'coin_type': HuoBi.coin_type_map[self.coin_type],
            'price': str(price),
            'amount': str(amount)
        }
        res = self._setup_request(trade_type, params)
        if 'result' in res and res['result'] == 'success':
            return res['id']
        else:
            return config.INVALID_ORDER_ID

    def cancel(self, order_id):
        params = {
            'coin_type': HuoBi.coin_type_map[self.coin_type],
            'id': order_id
        }
        res = self._setup_request('cancel_order', params)
        if 'result' in res and res['result'] == 'success':
            return True
        else:
            return False

    def order_info(self, order_id):
        params = {
            'coin_type': HuoBi.coin_type_map[self.coin_type],
            'id': order_id
        }
        res = self._setup_request('order_info', params)
        order_amount = common.to_decimal(res['order_amount'])
        processed = common.to_decimal(res['processed_amount'])
        remaining_amount = order_amount - processed
        catalog = HuoBi.catalog_map[res['type']]
        order_info = PlatformOrderInfo(order_id, catalog, remaining_amount)
        return order_info

    def assets(self):
        funds = self._setup_request('get_account_info')
        l = [
            [common.to_decimal(funds['frozen_cny_display']), common.to_decimal(funds['available_cny_display'])],
            [common.to_decimal(funds['frozen_' + self.coin_type + '_display']),
             common.to_decimal(funds['available_' + self.coin_type + '_display'])]
        ]
        return l


if __name__ == '__main__':
    log_helper.init_logger()
    huobi = HuoBi()
    print(huobi.assets())
