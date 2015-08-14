#!/usr/bin/env python

from __future__ import print_function
import decimal
from email.mime.text import MIMEText
import logging
import logging.config
import os
import smtplib
import threading
import time
import math
import requests
import requests.exceptions as req_except

import yaml
import ipgetter

import config


def synchronized(lock):
    """ Synchronization decorator. """

    def wrap(f):
        def new_func(*args, **kw):
            lock.acquire()
            try:
                return f(*args, **kw)
            finally:
                lock.release()

        return new_func

    return wrap


def get_usd_cny_rate():
    r = requests.get("http://finance.yahoo.com/d/quotes.csv?e=.csv&f=sl1d1t1&s=USDCNY=X", timeout=config.TIMEOUT)
    return decimal.Decimal(r.text.split(",")[1])


def to_decimal(value_str, precision=config.DISPLAY_PRECISION):
    return round(float(value_str), precision)


def reverse_catalog(original_catalog):
    assert (original_catalog in ['buy', 'sell'])
    if original_catalog == 'buy':
        return 'sell'
    else:  # sell
        return 'buy'


def round_price(price, precision=config.HuoBi_Price_Precision):
    return round(price, precision)


def adjust_price(trade_catalog, price):
    get_logger().info('trade_catalog={}, price={}'.format(trade_catalog, price))
    assert (trade_catalog in ['buy', 'sell'])
    if trade_catalog == 'buy':
        new_price = price * (1 + config.ADJUST_PERCENTAGE)
    else:  # sell
        new_price = price * (1 - config.ADJUST_PERCENTAGE)
    return round_price(new_price)


def adjust_amount(trade_amount, precision=config.TRADE_PRECISION):
    return math.floor(trade_amount * (10 ** precision)) / (10 ** precision)


def is_retry_exception(exception):
    for except_type in retry_except_tuple:
        if isinstance(exception, except_type):
            return True
    return False


def handle_exit(error):
    get_logger().critical('Error during request:"{}", will EXIT'.format(error))
    send_msg('error during request: {}'.format(error))
    # noinspection PyProtectedMember
    os._exit(1)


def handle_retry(exception, handler):
    """
    # NOTE: this handling may be blocked OR not blocked
    :param exception: the relevant exception
    :param handler: real handler, no params, implemented as closure
    :return: if retry succeeds, should return request result; otherwise, exit abornormally
    """
    logger = get_logger()
    current_exception = exception
    logger.error('RETRY for Exception: "{}"'.format(current_exception))
    retry_counter = 0
    while retry_counter < config.RETRY_MAX:
        retry_counter += 1
        if retry_counter % 10 == 0:
            time.sleep(config.RETRY_SLEEP_SECONDS)
        else:
            time.sleep(config.RETRY_SECONDS)
        try:
            logger.warning('retry_counter={:<2}'.format(retry_counter))
            res = handler()  # real handle function
            # logger.warning('res={}'.format(res))
            return res  # succeed
        except Exception as e:  # all request exceptions
            if is_retry_exception(e):
                # only log, do nothing
                current_exception = e
                logger.error('Exception during retrying:"{}", will RETRY'.format(current_exception))
                continue
            else:
                handle_exit(e)  # fail, exit
    logger.critical('Request Exception "{}" after retrying {} times'.format(current_exception, config.RETRY_MAX))
    handle_exit(current_exception)


logging_yaml = os.path.join(os.path.dirname(__file__), 'logging.yaml')


def init_logger():
    with open(logging_yaml) as f:
        data = yaml.load(f)
    logging.config.dictConfig(data)


def get_logger():
    return logging.getLogger('logger')


def get_asset_logger():
    return logging.getLogger('asset_logger')


class InvalidNonceError(Exception):
    def __init__(self, message):
        super(InvalidNonceError, self).__init__(message)


class NULLResponseError(Exception):
    def __init__(self, message):
        super(NULLResponseError, self).__init__(message)


class HuoBiError(Exception):
    def __init__(self, msg):
        super(HuoBiError, self).__init__(msg)


class HuoBiExitError(Exception):
    def __init__(self, msg):
        super(HuoBiExitError, self).__init__(msg)


class HuoBiIgnoreError(Exception):
    def __init__(self, msg):
        super(HuoBiIgnoreError, self).__init__(msg)


class CHBTCExitError(Exception):
    def __init__(self, msg):
        super(CHBTCExitError, self).__init__(msg)


class CHBTCRetryError(Exception):
    def __init__(self, msg):
        super(CHBTCRetryError, self).__init__(msg)


plt_yaml = os.path.join(os.path.dirname(__file__), 'platforms.yaml')

with open(plt_yaml) as yfile:
    ydata = yaml.load(yfile)


def get_key_from_data(field, dict_data=None):
    if dict_data is None:
        dict_data = ydata
    try:
        return dict_data[field]
    except:
        err_msg = 'msg: no ydata for field={}'.format(field)
        handle_exit(err_msg)


def send_msg(report):
    emailing_info = get_key_from_data('Emailing')
    sender = emailing_info['sender']
    receiver = emailing_info['receiver']
    server = emailing_info['server']
    ip_str = ipgetter.myip()
    report = str(ip_str) + '\n' + report
    msg = MIMEText(report)
    msg['Subject'] = 'Arbitrage Report'
    msg['From'] = sender
    msg['To'] = receiver
    try:
        session = smtplib.SMTP(server)
        session.sendmail(sender, [receiver], msg.as_string())
        session.quit()
    except:
        get_logger().warning('no mail server')


MUTEX = threading.Lock()
SIGNAL = None
retry_except_tuple = (
    req_except.ConnectionError, req_except.Timeout, req_except.HTTPError, InvalidNonceError, NULLResponseError,
    HuoBiError, CHBTCRetryError)
exit_except_tuple = (req_except.URLRequired, req_except.TooManyRedirects, HuoBiExitError, CHBTCExitError)
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36'

if __name__ == '__main__':
    init_logger()
    logger = get_logger()
    logger.debug('debug')
    logger.info('info')
    logger.warning('warning')
    logger.error('error')
    logger.critical('critical')
