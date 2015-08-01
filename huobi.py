#!/usr/bin/env python
import hashlib
import sys
import urllib
import time

import requests

import common
import config
from plt_api import Platform


class HuoBi(Platform):
    lower_bound = 0.001
    _logger = common.get_logger()
    data_domain = config.huobi_info['data_domain']
    common_headers = {
        'user-agent': common.USER_AGENT,
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    def __init__(self):
        super(HuoBi, self).__init__(config.huobi_info)
        self.key = common.get_key_from_data('HuoBi')
        self.coin_type = 'btc'
        self.api_private = ['cancel_order', 'get_account_info', 'buy', 'sell']

    def _real_uri(self, api_type):
        print('not used, exit')
        sys.exit(1)

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
    def setup_request(self, api_uri, params=None, data=None):
        def _request_impl():
            r = None
            if api_uri not in self.api_private:
                r = requests.get(api_uri, params=params, headers=HuoBi.common_headers, timeout=config.TIMEOUT,
                                 verify=True)
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
                print(param_dict)
                del param_dict['secret_key']
                r = requests.post(self.domain, params=param_dict)
                res_data = r.json()
                if 'code' in res_data and res_data['code'] != 0:
                    code = res_data['code']
                    HuoBi._logger.error(u'HuoBi Error: code={}, msg={}'.format(code, res_data['msg']))
                    if code in [5, 7]:
                        raise common.HuoBiExitError('HuoBiExitError: code={}'.format(code))
                    else:
                        raise common.HuoBiError('HuoBiError: code={}'.format(code))
            return r.json()

        try:
            result = _request_impl()
            return result
        except Exception as e:
            if common.is_retry_exception(e):
                return common.handle_retry(e, _request_impl)
            else:
                common.handle_exit(e)

    def api_ticker(self):
        api_uri = HuoBi.data_domain + '/' + 'ticker_' + self.coin_type + '_json.js'
        return self.setup_request(api_uri)

    def api_depth(self, length):
        api_uri = HuoBi.data_domain + '/' + 'depth_' + self.coin_type + '_' + str(length) + '.js'
        return self.setup_request(api_uri)

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
            'price': str(price),
            'amount': str(amount)
        }
        res = self.setup_request(trade_type, params)
        return res

    def cancel(self, order_id):
        params = {
            'id': order_id
        }
        res = self.setup_request('cancel_order', params)
        return res

    def assets(self):
        funds = self.setup_request('get_account_info')
        l = [
            [common.to_decimal(funds['frozen_cny_display']), common.to_decimal(funds['available_cny_display'])],
            [common.to_decimal(funds['frozen_btc_display']), common.to_decimal(funds['available_btc_display'])]
        ]
        return l


if __name__ == '__main__':
    common.init_logger()
    huobi = HuoBi()
    # res = huobi.trade('sell', 123456, 0.1)
    # print(res)
    # res = res = huobi.trade('sell', 12345, 0.1)
    # print(res)
    # res = huobi.cancel(123456)
    # print(res)
    print(huobi.assets())
    # print(huobi.ask1(), huobi.bid1())
    # print(huobi.ask_bid_list(1))
