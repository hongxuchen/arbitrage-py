#!/usr/bin/env python

import base64
import hashlib
import hmac
import urllib
import json
import time
import requests

import config
import excepts
from api.plt import Platform
import plt_conf


class ItBitAPI(Platform):
    markets = ['XBTUSD', 'XBTSGD', 'XBTEUR']

    def __init__(self, info):
        super(ItBitAPI, self).__init__(info)
        self.domain = info['domain']
        self.symbol = info['symbol']
        self.key = plt_conf.get_key_from_data('ItBit')

    @staticmethod
    def _to_json(data):
        js_str = json.dumps(data, separators=(',', ':'))
        return js_str

    # noinspection PyMethodMayBeStatic
    def _setup_request(self, method, base_url, params=None, data=None, headers=None):
        r = requests.request(method, base_url, params=params, data=data, headers=headers)
        code = r.status_code
        print(r.url)
        if not str(code).startswith('2'):
            err_msg = 'msg: ItBit retcode ERROR: [{}], {}'.format(code, r.content)
            excepts.handle_exit(err_msg)

        try:
            jsdata = r.json()
            return jsdata
        except Exception as e:
            excepts.handle_exit(e)

    # public APIs

    def ticker(self):
        base_url = self.get_url('markets/' + self.symbol + '/ticker')
        r = self._setup_request('get', base_url)
        print(json.dumps(r, indent=2))

    def order_book(self):
        base_url = self.get_url('markets/' + self.symbol + '/order_book')
        print(base_url)
        r = self._setup_request('get', base_url)
        print(json.dumps(r, indent=2))

    # helper functions
    @staticmethod
    def _timestamp_nonce():
        timestamp = int(round(time.time()) * 1000)
        nonce = int(7 * timestamp + 15 * timestamp / 2 + 31 * timestamp / 4)
        return str(timestamp), str(nonce)

    def _sign(self, method, base_url, timestamp, nonce, params, data):
        assert (data is not None)
        if params is None:
            full_url = base_url
        else:
            full_url = base_url + '?' + urllib.urlencode(params)
        print(full_url)
        arr = [method.upper(), full_url, data, nonce, timestamp]
        msg = nonce + ItBitAPI._to_json(arr)
        print(msg)
        sha256_hash = hashlib.sha256()
        sha256_hash.update(msg)
        hash_digest = sha256_hash.digest()
        hmac_digest = hmac.new(self.key['secret'], full_url.encode('utf8') + hash_digest, hashlib.sha512).digest()
        return base64.b64encode(hmac_digest)

    def _private_request(self, method, base_url, params, data):
        timestamp, nonce = ItBitAPI._timestamp_nonce()
        signature = self._sign(method, base_url, timestamp, nonce, params, data)
        headers = {
            'Authorization': self.key['api'] + ':' + signature,
            'X-Auth-Timestamp': timestamp,
            'X-Auth-Nonce': nonce,
            'Content-Type': 'application/json'
        }
        res_data = self._setup_request(method, base_url, params, data, headers)
        return res_data

    def get_all_wallets(self):
        method = 'get'
        base_url = self.domain + 'wallets'
        params = {
            'userId': self.key['uid']
        }
        data = ''
        res_data = self._private_request(method, base_url, params, data)
        print(json.dumps(res_data, indent=2))

    def get_wallet(self, wallet_id):
        method = 'get'
        base_url = self.get_url('wallets/' + wallet_id)
        params = None
        data = ''
        res_data = self._private_request(method, base_url, params, data)
        print(res_data)

    def get_wallet_balance(self, wallet_id):
        method = 'get'
        base_url = self.get_url('wallets/' + wallet_id + '/balances/' + self.symbol[3:])
        params = None
        data = ''
        res_data = self._private_request(method, base_url, params, data)
        print(res_data)

    # TODO: need to ensure no existing wallet name
    def new_wallet(self, name):
        method = 'post'
        base_url = self.get_url('wallets')
        params = None
        data_dict = {
            'userId': self.key['uid'],
            'name': name
        }
        data = json.dumps(data_dict)
        res_data = self._private_request(method, base_url, params, data)
        print(res_data)

    def get_trades(self, wallet_id):
        method = 'get'
        base_url = self.get_url('wallets/' + wallet_id + '/trades')
        params = {
            'lastExecutionId': 10,  # exclude No. of executions before
            'page': 1,
            'perPage': 50,  # max
            'rangeStart': '2016-06-24T00:00:00',  # exclude after time
            'rangeEnd': '2012-01-01T00:00:00'  # exclude before time
        }
        data = ''
        res_data = self._private_request(method, base_url, params, data)
        print(res_data)

    def get_orders(self, wallet_id, status='open'):
        method = 'get'
        base_url = self.get_url('wallets/' + wallet_id + '/orders')
        params = {
            'instrument': self.symbol,
            'page': 1,  # default
            'perPage': 50,  # max
            'status': status  # submitted open filled cancelled rejected
        }
        data = ''
        res_data = self._private_request(method, base_url, params, data)
        print(res_data)
        return res_data

    def new_order(self, wallet_id, order_info):
        method = 'post'
        base_url = self.get_url('wallets/' + wallet_id + '/orders')
        data_dict = {
            'side': None,
            'type': 'limit',
            'currency': None,
            'amount': None,
            'display': None,
            'price': None,
            'instrument': self.symbol,
            'metadata': None,
            'clientOrderIdentifier': 'optional'
        }
        params = None
        data_dict.update(order_info)
        print(json.dumps(data_dict, indent=2))
        data = ItBitAPI._to_json(data_dict)
        res_data = self._private_request(method, base_url, params, data)
        print(res_data)

    def get_order(self, wallet_id, order_id):
        method = 'get'
        base_url = self.get_url('wallets/' + wallet_id + '/orders/' + order_id)
        params = None
        data = ''
        res_data = self._private_request(method, base_url, params, data)
        print(res_data)

    def cancel_order(self, wallet_id, order_id):
        method = 'delete'
        base_url = self.get_url('wallets/' + wallet_id + '/orders/' + order_id)
        params = None
        data = ''
        res_data = self._private_request(method, base_url, params, data)
        print(res_data)

    def new_cryptocurrency_withdraw(self, wallet_id, withdraw_info):
        method = 'post'
        base_url = self.get_url('wallets/' + wallet_id + '/cryptocurrency_withdrawals')
        params = None
        data_dict = {
            'currency': 'XBT',
            'amount': '',
            'address': None
        }
        data_dict.update(withdraw_info)
        data = ItBitAPI._to_json(data_dict)
        res_data = self._private_request(method, base_url, params, data)
        print(res_data)

    def new_cryptocurrency_deposit(self, wallet_id, deposit_info=None):
        method = 'post'
        base_url = self.get_url('wallets/' + wallet_id + '/cryptocurrency_deposits')
        params = None
        data_dict = {
            'currency': 'XBT',
            'metadata': {}
        }
        if deposit_info is not None:
            data_dict.update(deposit_info)
        data = ItBitAPI._to_json(data_dict)
        res_data = self._private_request(method, base_url, params, data)
        print(res_data)

    def new_wallet_transfer(self, wallet_transfer_info):
        method = 'post'
        base_url = self.get_url('wallet_transfers')
        params = None
        data_dict = {
            'sourceWalletId': None,
            'destinationWalletId': None,
            'amount': '',
            'currencyCode': 'XBT'
        }
        data_dict.update(wallet_transfer_info)
        data = ItBitAPI._to_json(data_dict)
        res_data = self._private_request(method, base_url, params, data)
        print(res_data)


if __name__ == '__main__':
    itbit = ItBitAPI(config.itbit_info)
    # itbit.ticker()
    # itbit.order_book()
    # itbit.get_all_wallets()
    # itbit.new_wallet('hw_chx5')
    # wallet_id = 'e112bd40-56fd-4ebd-a570-ba0b89009963'
    wallet_id = 'e112bd40-56fd-4ebd-a570-ba0b89009963'
    # itbit.get_trades(wallet_id)
    itbit.get_wallet_balance(wallet_id)
    # order_info = {
    #     'side': 'buy',
    #     'currency': 'XBT',
    #     'amount': '20.0',
    #     'display': '2.5',
    #     'price': '200',
    #     'instrument': 'XBTUSD',
    #     'metadata': {
    #         'key0': 'hello',
    #         'key1': 'world'
    #     }
    # }
    # itbit.new_order(wallet_id, order_info)
    # order_id = '2d2fc05f-3091-4dcb-aaf6-91b63cdb6b4d'
    # order_id = '72f6c19c-b3cd-4733-8d51-df1f82af521b'
    # itbit.get_order(wallet_id, order_id)
    # orders = itbit.get_orders(wallet_id)
    # if orders is not None:
    #     order_id = orders[0]['id']
    #     itbit.cancel_order(wallet_id, order_id)
    # else:
    #     print('no orders')
    # withdraw_info = {
    #     'address': '19eU8xnmE8qeVv9hNiacpWyL3qs757X3de',
    #     'amount': '0.33'
    # }
    # itbit.new_cryptocurrency_withdraw(wallet_id, withdraw_info)
    # # itbit.new_cryptocurrency_deposit(wallet_id)

    # wallet_id_1 = '1089527c-bbde-4e10-9b90-002ef40c1571'
    # wallet_transfer_info = {
    #     'sourceWalletId': wallet_id,
    #     'destinationWalletId': wallet_id_1,
    #     'amount': '3'
    # }
    # itbit.new_wallet_transfer(wallet_transfer_info)
