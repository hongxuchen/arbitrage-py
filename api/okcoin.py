#!/usr/bin/env python

from __future__ import print_function

import hashlib

import requests

from api.plt import Platform
from settings import config
from utils import common, excepts
from utils.log_helper import get_logger, init_logger
from utils.order_info import PlatformOrderInfo


class OKCoinBase(Platform):
    # plt_info is not specified here
    lower_bound_dict = {
        'btc': 0.01,
        'ltc': 0.1
    }
    common_headers = {
        'user-agent': config.USER_AGENT,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    trade_cancel_api_list = ['cancel_order', 'trade']

    def __init__(self, info):
        super(OKCoinBase, self).__init__(info)
        self.lower_bound = OKCoinBase.lower_bound_dict[self.coin_type]
        _api_future_public = ['future_ticker', 'future_depth', 'future_trades', 'future_index', 'exchange_rate',
                              'future_hold_amount']
        _api_future_private = ['future_userinfo', 'future_position', 'future_trade', 'future_batch_trade',
                               'future_cancel', 'future_order_info', 'future_orders_info', 'future_userinfo_4fix',
                               'future_position_4fix', 'future_explosive']
        self.api_public = ['ticker', 'depth', 'trades'] + _api_future_public
        self.api_private = ['userinfo', 'trade', 'batch_trade', 'cancel_order', 'orders', 'order_info', 'orders_info',
                            'order_history'] + _api_future_private

    def _real_uri(self, api_type):
        return self.prefix + '/' + api_type + '.do'

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
                r = requests.request('get', self._real_uri(api_type), params=params, headers=OKCoinBase.common_headers,
                                     timeout=config.REQUEST_TIMEOUT, verify=True)
            elif api_type in self.api_private:
                r = requests.request('post', self._real_uri(api_type), data=data, params=params,
                                     headers=OKCoinBase.common_headers, timeout=config.REQUEST_TIMEOUT, verify=True)
            else:
                err_msg = 'msg: OKCoin api_type [{}] not supported'.format(api_type)
                excepts.handle_exit(err_msg)
            try:
                res = r.json()
                # OKCoinAPI._logger.warning('response={}'.format(res))
                if res is None or res is {}:
                    raise excepts.NULLResponseError('Response is empty for api_type={}'.format(api_type))
                return res
            except ValueError as ee:
                err_msg = 'msg: OKCoin parse json error "{}" for api_type={}, response={}'.format(ee, api_type, r)
                get_logger().critical(err_msg)
                raise excepts.MayDisconnectedException(err_msg)

        try:
            response_data = _request_impl()
            return response_data
        except Exception as e:
            if excepts.is_retry_exception(e):
                return excepts.handle_retry(e, _request_impl)
            else:
                excepts.handle_exit(e)

    def _private_request(self, api_type, param_dict):
        params = {'api_key': self.key['api']}
        if param_dict is not None:
            params.update(param_dict)
        params['sign'] = self._sign(params)
        response_data = self._setup_request(api_type, None, params)
        result_status = response_data['result']
        if result_status is False:
            get_logger().critical(
                'Error: api_type={}, response_data={}'.format(api_type, response_data))
            if api_type not in OKCoinBase.trade_cancel_api_list:
                err_msg = 'msg: OKCoin Unknown Error during request api_type={}'.format(api_type)
                excepts.handle_exit(err_msg)
        return response_data


class OKCoinTrade(OKCoinBase):
    def __init__(self, info):
        super(OKCoinTrade, self).__init__(info)

    # public api

    def api_ticker(self):
        payload = {
            'symbol': self.coin_type + '_' + self.fiat_type
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
            'symbol': self.coin_type + '_' + self.fiat_type,
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
            'symbol': self.coin_type + '_' + self.fiat_type
        }
        if since is not None:
            payload['since'] = since
        res = self._setup_request('trades', payload)
        return res

    # private api

    def api_userinfo(self):
        res = self._private_request('userinfo', None)
        return res

    def api_trade(self, trade_dict):
        params = {
            'symbol': self.coin_type + '_' + self.fiat_type
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
        get_logger().debug('OKCoinAPI.buy_market with {}'.format(mo_amount))
        return self.trade('buy_market', mo_amount, None)

    def sell_market(self, mo_amount):
        assert (mo_amount >= self.lower_bound)
        get_logger().debug('OKCoinAPI.sell_market with amount {}'.format(mo_amount))
        return self.trade('sell_market', None, mo_amount)

    def api_cancel_order(self, order_id):
        params = {
            'symbol': self.coin_type + '_' + self.fiat_type,
            'order_id': order_id
        }
        res = self._private_request('cancel_order', params)
        return res

    def cancel(self, order_id):
        """
        return whether cancel succeeds or not
        :param order_id:
        """
        data = self.api_cancel_order(order_id)
        return data['result']

    def api_order_info(self, order_id):
        params = {
            'symbol': self.coin_type + '_' + self.fiat_type,
            'order_id': order_id
        }
        res = self._private_request('order_info', params)
        return res

    def order_info(self, order_id):
        response = self.api_order_info(order_id)
        info = response['orders'][0]
        catalog = info['type']
        remaining_amount = info['amount'] - info['deal_amount']
        order_info = PlatformOrderInfo(order_id, catalog, remaining_amount)
        return order_info

    def assets(self):
        funds = self.api_userinfo()['info']['funds']
        l = [
            [common.to_decimal(funds['freezed'][self.fiat_type]), common.to_decimal(funds['free'][self.fiat_type])],
            [common.to_decimal(funds['freezed'][self.coin_type]), common.to_decimal(funds['free'][self.coin_type])]
        ]
        return l

    def api_orders_info(self, order_id_list, status):
        assert (len(order_id_list) <= 50)
        params = {
            'symbol': self.coin_type + '_' + self.fiat_type,
            'order_id': ','.join(order_id_list),
            'type': status
        }
        res = self._private_request('orders_info', params)
        return res

    def orders_info(self, order_id_list, status):
        info = self.api_orders_info(order_id_list, status)
        return info

    def api_order_history(self, page, status):
        params = {
            'symbol': self.coin_type + '_' + self.fiat_type,
            'current_page': page,
            'page_length': 200,
            'status': status
        }
        res = self._private_request('order_history', params)
        return res

    # order_id cannot be used for sorting; but create_data can
    def order_history(self, page, status):
        histories = self.api_order_history(page, status)['orders']
        buy_list = []
        sell_list = []
        for order in histories:
            if status == 0:
                assert (order['status'] in [0, 1])
            else:  # status == 0
                assert (order['status'] in [-1, 2, 4])
            catalog = order['type']
            if order['symbol'] == self.coin_type + '_' + self.fiat_type:
                remaining = order['amount'] - order['deal_amount']
                plt_order_info = PlatformOrderInfo(order['order_id'], catalog, remaining)
                if catalog == 'buy':
                    buy_list.append(plt_order_info)
                else:
                    sell_list.append(plt_order_info)
        pending_dict = {
            'buy': buy_list,
            'sell': sell_list
        }
        return pending_dict

    def pending_orders(self):
        # 1st page, 0 for unfilled
        return self.order_history(1, 0)

    # avoid using this
    def filled_orders(self):
        return self.order_history(1, 1)


class OKCoinCN(OKCoinTrade):
    plt_info = {
        'prefix': 'https://www.okcoin.cn/api/v1',
        'fiat': 'cny'
    }

    def __init__(self):
        super(OKCoinCN, self).__init__(self.plt_info)


class OKCoinCOM(OKCoinTrade):
    plt_info = {
        'prefix': 'https://www.okcoin.com/api/v1',
        'fiat': 'usd'
    }

    def __init__(self):
        super(OKCoinCOM, self).__init__(self.plt_info)


if __name__ == '__main__':
    init_logger()
    okcoin_cn = OKCoinCN()
    okcoin_com = OKCoinCOM()
    print(okcoin_cn.assets())
    print(okcoin_com.assets())
