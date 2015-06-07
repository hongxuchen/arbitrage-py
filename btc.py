#!/usr/bin/env python

class BTC(object):
    def __init__(self, info):
        self.info = info
        self.domain = info['domain']
        self.key = None
        self._btc_rate = None

    def _real_uri(self, method):
        pass

    def asset_list(self):
        pass

    def get_url(self, path):
        url = self.domain + path
        # print(url)
        return url
