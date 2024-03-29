#!/usr/bin/env python
from __future__ import print_function

import hashlib
import hmac
import time
import urllib

import requests

from api.plt import Platform
from settings import config
from utils import excepts, common
from utils.log_helper import get_logger
from utils.order_info import PlatformOrderInfo


class BitBays(Platform):
    plt_info = {
        'prefix': 'https://bitbays.com/api/v1',
        'fiat': 'cny'
    }
    common_headers = {
        'user-agent': config.USER_AGENT
    }
    lower_bound_dict = {
        'btc': 0.001
    }
    trade_cancel_list = ['cancel', 'trade']

    # specific to bitbays
    catalog_dict = {
        0: 'buy',
        1: 'sell'
    }

    def __init__(self):
        super(BitBays, self).__init__(self.plt_info)
        self.lower_bound = BitBays.lower_bound_dict[self.coin_type]
        self.api_public = ['ticker', 'trades', 'depth']
        self.api_private = ['info', 'orders', 'transactions', 'trade', 'cancel', 'order']
        self._counter = int(time.time() * 1000)

    def _nonce(self):
        self._counter += 1
        return self._counter

    def _sign(self, params):
        return hmac.new(self.key['secret'], params, digestmod=hashlib.sha512).hexdigest()

    def _post_param(self, payload):
        params = {
            'Key': self.key['api'],
            'Sign': self._sign(urllib.urlencode(payload))
        }
        params.update(self.common_headers)
        return params

    def _real_uri(self, api_type):
        return self.prefix + '/' + api_type + '/'

    def _setup_request(self, api_type, params=None):

        def _request_impl():
            r = None
            if api_type in self.api_public:
                r = requests.get(self._real_uri(api_type), params=params, timeout=config.REQUEST_TIMEOUT, verify=True)
            elif api_type in self.api_private:
                params['nonce'] = self._nonce()
                headers = self._post_param(params)
                r = requests.post(self._real_uri(api_type), data=params, headers=headers,
                                  timeout=config.REQUEST_TIMEOUT)
            else:
                err_msg = 'msg: BitBays api_type={} not supported'.format(api_type)
                excepts.handle_exit(err_msg)
            try:
                res_data = r.json()
                if res_data is None or res_data is {}:
                    raise excepts.NULLResponseError('Response is empty for api_type={}'.format(api_type))
                result = res_data['result']
                if result is None:
                    msg = res_data['message']
                    if msg.startswith('Invalid Nonce'):
                        raise excepts.InvalidNonceError(
                            'InvalidNonceError: {}, current_nonce={}'.format(msg, params['nonce']))
                    if msg.startswith("Rate Limit Exceeded"):
                        raise excepts.RateExceedError("BitBays: Rate Exceeded for api_type={}".format(api_type))
                    else:
                        get_logger().critical(
                            'Error: api_type={}, error_message={}'.format(api_type, msg))
                        if api_type not in BitBays.trade_cancel_list:
                            err_msg = 'msg: BitBays Unknown Error during request when api_type={}'.format(api_type)
                            excepts.handle_exit(err_msg)
                return res_data
            except ValueError as ee:
                err_msg = 'msg: bitbays parse json error "{}" for api_type={}, response={}'.format(ee, api_type, r)
                get_logger().critical(err_msg)
                raise excepts.MayDisconnectedException(err_msg)

        try:
            result = _request_impl()
            return result
        except Exception as e:
            if excepts.is_retry_exception(e):
                return excepts.handle_retry(e, _request_impl)
            else:
                excepts.handle_exit(e)

    #############################################################################

    # public api
    def api_ticker(self):
        payload = {
            'market': self.coin_type + '_' + self.fiat_type
        }
        res = self._setup_request('ticker', params=payload)
        return res

    # uses public api
    def ask1(self):
        ticker = self.api_ticker()['result']
        sell = ticker['sell']
        sell = common.to_decimal(sell)
        return sell

    def bid1(self):
        ticker = self.api_ticker()['result']
        buy = ticker['buy']
        buy = common.to_decimal(buy)
        return buy

    # public api
    def ask_bid_list(self, length=2):
        assert (1 <= length <= 50)
        payload = {
            'market': self.coin_type + '_' + self.fiat_type
        }
        res = self._setup_request('depth', params=payload)['result']
        asks = sorted(res['asks'], key=lambda ask: ask[0], reverse=True)[-length:]
        bids = sorted(res['bids'], key=lambda bid: bid[0], reverse=True)[:length]
        # NOTE: bitbays keeps violating this assertion!!!
        # assert (asks[-1][0] + config.MINOR_DIFF >= bids[0][0])
        asks_bids = asks + bids
        return asks_bids

    def api_trades(self):
        """
        global trading response
        :return:
        """
        payload = {
            'market': self.coin_type + '_' + self.fiat_type
        }
        res = self._setup_request('trades', params=payload)
        return res

    #############################################################################

    def api_trade(self, order):
        payload = {
            'market': self.coin_type + '_' + self.fiat_type,
            'order_type': 0  # limit order
        }
        payload.update(order)
        # assert (payload['order_type'] in [0, 1])
        # assert (payload['op'] in ['buy', 'sell'])
        data = self._setup_request('trade', payload)
        return data

    def api_cancel(self, order_id):
        payload = {
            'id': order_id
        }
        data = self._setup_request('cancel', payload)
        return data

    def api_order_info(self, order_id):
        payload = {
            'id': order_id
        }
        data = self._setup_request('order', payload)
        return data

    def api_user_info(self):
        payload = {}
        data = self._setup_request('info', payload)
        return data

    def api_orders(self, catalog, status=0):
        payload = {
            'market': self.coin_type + '_' + self.fiat_type,
            'catalog': catalog,
            'status': status,
            'count': 20,
            'nonce': self._nonce()
        }
        # assert (catalog in [0, 1])
        if catalog == 0:
            payload['order'] = 'DESC'
        else:
            payload['order'] = 'ASC'
        data = self._setup_request('orders', payload)
        return data

    def api_transactions(self, catalog):
        payload = {
            'market': self.coin_type + '_' + self.fiat_type,
            'catalog': catalog,
            'count': 20,
            'nonce': self._nonce()
        }
        if catalog == 0:
            payload['order'] = 'DESC'
        else:
            payload['order'] = 'ASC'
        data = self._setup_request('transactions', payload)
        return data

    #############################################################################

    def trade(self, op_type, price, amount):
        """
        return: order_id if succeed, otherwise invalid id
        :param op_type:
        :param price:
        :param amount:
        """
        trade_dict = {
            'op': op_type,
            'price': str(price),
            'amount': str(amount)
        }
        res = self.api_trade(trade_dict)['result']
        if res is None:
            return config.INVALID_ORDER_ID
        else:
            return res['id']

    def _market_trade(self, op_type, mo_amount):
        trade_dict = {
            'order_type': 1,
            'op': op_type,
            'mo_amount': mo_amount
        }
        data = self.api_trade(trade_dict)['result']
        return data

    def buy_market(self, mo_amount):
        get_logger().debug('BitBays.buy_market with amount {}'.format(mo_amount))
        return self._market_trade('buy', mo_amount)

    def sell_market(self, mo_amount):
        get_logger().debug('BitBays.sell_market with amount {}'.format(mo_amount))
        return self._market_trade('sell', mo_amount)

    def cancel(self, order_id):
        data = self.api_cancel(order_id)['result']
        if data is None:
            return False
        else:
            return True

    def order_info(self, order_id):
        info = self.api_order_info(order_id)['result']
        amount = 0.0
        if 'amount_total' in info:
            amount = info['amount_total']
        elif 'mo_amount' in info:
            amount = info['mo_amount']
        remaining_amount = common.to_decimal(amount) - common.to_decimal(info['amount_done'])
        catalog = BitBays.catalog_dict[info['catalog']]
        order_info = PlatformOrderInfo(order_id, catalog, remaining_amount)
        return order_info

    def assets(self):
        user_info = self.api_user_info()['result']
        info = user_info['wallet']
        l = [
            [common.to_decimal(info[self.fiat_type]['lock']), common.to_decimal(info[self.fiat_type]['avail'])],
            [common.to_decimal(info[self.coin_type]['lock']), common.to_decimal(info[self.coin_type]['avail'])]
        ]
        return l


if __name__ == '__main__':
    bitbays = BitBays()
    # print(bitbays.lower_bound)
    print(bitbays.api_ticker())
    # print(bitbays.api_user_info())
    print(bitbays.assets())
