#!/usr/bin/env python
from __future__ import print_function
import requests
from requests_futures.sessions import FuturesSession
s = FuturesSession()
s.request('get', 'https://www.okcoin.cn/api/v1/ticker.do?symbol=btc_cny')

from tornado.httpclient import  HTTPClient

http_client = HTTPClient()

