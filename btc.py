#!/usr/bin/env python
import logging
import logging.handlers
import logging.config
import os
import errno


class BTC(object):
    def __init__(self, info):
        self.info = info
        self.domain = info['domain']
        self.key = None
        self._btc_rate = None
        self.setup_logger()

    def setup_logger(self):
        log_dir = os.path.join(os.path.dirname(__file__), 'logger')
        try:
            os.makedirs(log_dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        log_fname = os.path.join(log_dir, 'trading.log')
        logging.config.fileConfig('logging_config.ini', defaults={
            'logfilename': log_fname
        })
        self.logger = logging.getLogger()

    def _real_uri(self, method):
        pass

    def depth(self, length):
        pass

    def asset_list(self):
        pass

    def get_url(self, path):
        url = self.domain + path
        # print(url)
        return url
