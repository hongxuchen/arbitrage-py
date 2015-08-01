#!/usr/bin/env python
import sys

import requests

import common
import config
from plt_api import Platform


class HuoBi(Platform):
    # TODO
    lower_bound = 0.001
    _logger = common.get_logger()
    data_domain = config.huobi_info['data_domain']
    common_headers = {
        'user-agent': common.USER_AGENT,
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    def __init__(self):
        super(HuoBi, self).__init__(config.huobi_info)
        self.coin_type = 'btc'

    def _real_uri(self, api_type):
        print('not used, exit')
        sys.exit(1)

    def setup_request(self, api_uri, params=None, data=None):
        def _request_impl():
            r = None
            r = requests.get(api_uri, params=params, timeout=config.TIMEOUT, verify=True)
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
        pass

    def cancel(self, order_id):
        pass

    def assets(self):
        pass


if __name__ == '__main__':
    common.init_logger()
    huobi = HuoBi()
    print(huobi.ask1(), huobi.bid1())
    print(huobi.ask_bid_list(2))
