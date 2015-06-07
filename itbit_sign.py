#!/usr/bin/env python
import base64
import time
import json
import urllib
import hashlib
import hmac

import requests

import config

import common

now = int(round(time.time() * 1000))
now_str = str(now)
print(now)

info = common.get_key_from_file('ItBit')

uid = info['uid']
key = info['api']
secret = info['secret']


def _nonce(timestamp):
    return int(7 * timestamp + 15 * timestamp / 2 + 31 * timestamp / 4)


nonce = _nonce(now)
nonce_str = str(nonce)

method = 'get'
base_url = config.itbit_info['domain'] + 'wallets'

params = {  # parameters for post
            'userId': uid
            }

full_url = base_url + '?' + urllib.urlencode(params)
print(full_url)

body = ''
arr = [method.upper(), full_url, body, nonce_str, now_str]
js_str = json.dumps(arr, separators=(',', ':'))
message = str(nonce_str) + js_str
print(message)

sha256_hash = hashlib.sha256()
sha256_hash.update(message)
hash_digest = sha256_hash.digest()
hmac_digest = hmac.new(secret, full_url.encode('utf8') + hash_digest, hashlib.sha512).digest()
signature = base64.b64encode(hmac_digest)
print(signature)

headers = {
    'Authorization': key + ':' + signature,
    'X-Auth-Timestamp': now_str,
    'X-Auth-Nonce': nonce_str,
    'Content-Type': 'application/json'
}
print(headers)

r = requests.request('get', base_url, params=params, data=None, headers=headers)
# print(r.text)
print(r.status_code)
