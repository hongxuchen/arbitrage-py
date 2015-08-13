#!/usr/bin/env python
from __future__ import print_function
import hashlib
import hmac
import os
import urllib
import time

import requests

from plt_api import Platform
import common
import config
from order_info import OrderInfo


class BitBays(Platform):
    _logger = common.get_logger()
    catalog_dict = {
        0: 'buy',
        1: 'sell'
    }
    common_headers = {
        'user-agent': common.USER_AGENT
    }
    lower_bound_dict = {
        'btc': 0.001
    }
    trade_cancel_list = ['cancel', 'trade']

    def __init__(self):
        super(BitBays, self).__init__(config.bitbays_info)
        self.symbol = config.bitbays_info['symbol']
        self.lower_bound = BitBays.lower_bound_dict[self.coin_type]
        self.key = common.get_key_from_data('BitBays')
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
        return self.get_url('/' + api_type + '/')

    def _setup_request(self, api_type, params=None, data=None):
        """
        :param api_type:
        :param params:
        :param data:
        :return:
        """

        def _request_impl():
            r = None
            if api_type in self.api_public:
                r = requests.get(self._real_uri(api_type), params=params, timeout=config.TIMEOUT, verify=True)
            elif api_type in self.api_private:
                params['nonce'] = self._nonce()
                headers = self._post_param(params)
                r = requests.post(self._real_uri(api_type), data=params, headers=headers, timeout=config.TIMEOUT)
            else:
                err_msg = 'msg: BitBays api_type={} not supported'.format(api_type)
                common.handle_exit(err_msg)
            # TODO check error
            res_data = r.json()
            # BitBays._logger.warning('bitbays response={}'.format(res_data))
            if res_data is None or res_data is {}:
                raise common.NULLResponseError('NULLResponseError: Response is empty for api_type={}'.format(api_type))
            result = res_data['result']
            # TODO check other api_type fail
            if result is None:
                msg = res_data['message']
                if msg.startswith('Invalid Nonce'):
                    raise common.InvalidNonceError(
                        'InvalidNonceError: {}, current_nonce={}'.format(msg, params['nonce']))
                else:
                    BitBays._logger.critical(
                        'ERROR: api_type={}, error_message={}'.format(api_type, msg))
                    if api_type not in BitBays.trade_cancel_list:
                        err_msg = 'msg: BitBays Error during request when api_type={}'.format(api_type)
                        common.handle_exit(err_msg)
            return res_data

        try:
            result = _request_impl()
            return result
        except Exception as e:
            if common.is_retry_exception(e):
                return common.handle_retry(e, _request_impl)
            else:
                common.handle_exit(e)

    #############################################################################

    # public api
    def api_ticker(self):
        payload = {
            'market': self.coin_type + '_' + self.symbol
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
            'market': self.coin_type + '_' + self.symbol
        }
        res = self._setup_request('depth', params=payload)['result']
        asks = sorted(res['asks'], key=lambda ask: ask[0], reverse=True)[-length:]
        bids = sorted(res['bids'], key=lambda bid: bid[0], reverse=True)[:length]
        assert (asks[-1][0] + config.MINOR_DIFF >= bids[0][0])
        asks_bids = asks + bids
        return asks_bids

    def api_trades(self):
        """
        global trading response
        :return:
        """
        payload = {
            'market': self.coin_type + '_' + self.symbol
        }
        res = self._setup_request('trades', params=payload)
        return res

    #############################################################################

    def api_trade(self, order):
        payload = {
            'market': self.coin_type + '_' + self.symbol,
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
            'market': self.coin_type + '_' + self.symbol,
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
            'market': self.coin_type + '_' + self.symbol,
            'catalog': catalog,
            'count': 20,
            'nonce': self._nonce()
        }
        # assert (catalog in [0, 1])
        if catalog == 0:
            payload['order'] = 'DESC'
        else:
            payload['order'] = 'ASC'
        data = self._setup_request('transactions', payload)
        return data

    #############################################################################

    # uses private
    def trade(self, op_type, price, amount):
        """
        return: order_id if succeed, otherwise invalid id
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

    # uses private
    def _market_trade(self, op_type, mo_amount):
        trade_dict = {
            'order_type': 1,
            'op': op_type,
            'mo_amount': mo_amount
        }
        data = self.api_trade(trade_dict)['result']
        return data

    # uses private
    def buy_market(self, mo_amount):
        BitBays._logger.debug('BitBays.buy_market with amount {}'.format(mo_amount))
        return self._market_trade('buy', mo_amount)

    # uses private
    def sell_market(self, mo_amount):
        BitBays._logger.debug('BitBays.sell_market with amount {}'.format(mo_amount))
        return self._market_trade('sell', mo_amount)

    # uses private
    def cancel(self, order_id):
        data = self.api_cancel(order_id)['result']
        if data is None:
            return False
        else:
            return True

    # uses private
    def order_info(self, order_id):
        info = self.api_order_info(order_id)['result']
        amount = 0.0
        if 'amount_total' in info:
            amount = info['amount_total']
        elif 'mo_amount' in info:
            amount = info['mo_amount']
        remaining_amount = common.to_decimal(amount) - common.to_decimal(info['amount_done'])
        catalog = BitBays.catalog_dict[info['catalog']]
        order_info = OrderInfo(catalog, remaining_amount)
        return order_info

    # uses private
    def assets(self):
        user_info = self.api_user_info()['result']
        info = user_info['wallet']
        l = [
            [common.to_decimal(info[self.symbol]['lock']), common.to_decimal(info[self.symbol]['avail'])],
            [common.to_decimal(info[self.coin_type]['lock']), common.to_decimal(info[self.coin_type]['avail'])]
        ]
        return l


if __name__ == '__main__':
    bitbays = BitBays()
    print(bitbays.lower_bound)
    # while True:
    # print(bitbays.ask_bid_list(2))
    # print(bitbays.assets())
    # print(bitbays.api_transactions(0))
    # order_id = bitbays.trade('sell', 10000, 1000)
    # print(bitbays.ask1())
    # print(order_id)
    # print(bitbays.cancel(123456))
    # limit order id
    # res = bitbays.order_info(order_id)
    # print(res)
    # order_id = bitbays.trade('buy', 10, 0.001)
    # print(order_id)
    # order_info = bitbays.order_info(order_id)
    # print(order_info)
    # res = bitbays.buy_market(0.01)
    # print(res)
    # order_id = 44036603
    # res = bitbays.order_info(order_id)
    # res = bitbays.sell_market(0.001)
    # print(res)
