#!/usr/bin/env python

from __future__ import print_function
import decimal
from email.mime.text import MIMEText
import logging
import logging.config
import os
import smtplib
import threading
import sys
import time

import requests
import requests.exceptions as req_except
import yaml

import config


def get_usd_cny_rate():
    r = requests.get(
        "http://finance.yahoo.com/d/quotes.csv?e=.csv&f=sl1d1t1&s=USDCNY=X",
        timeout=5)
    return decimal.Decimal(r.text.split(",")[1])


def to_decimal(value_str, precision=config.DISPLAY_PRECISION):
    return round(float(value_str), precision)


def reverse_catelog(original_catelog):
    assert (original_catelog in ['buy', 'sell'])
    if original_catelog == 'buy':
        return 'sell'
    else:  # sell
        return 'buy'


def round_price(price, precision=config.HuoBi_Precision):
    return round(price, precision)


def adjust_price(trade_catelog, price):
    assert (trade_catelog in ['buy', 'sell'])
    if trade_catelog == 'buy':
        new_price = price * (1 + config.ASJUST_PERCENTAGE)
    else:  # sell
        new_price = price * (1 - config.ASJUST_PERCENTAGE)
    return round_price(new_price)


def is_retry_exception(exception):
    for except_type in retry_except_tuple:
        if isinstance(exception, except_type):
            return True
    return False


def handle_exit(exception):
    get_logger().critical('Error during request:"{}", will EXIT'.format(exception))
    send_msg('error during request')
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
        try:
            time.sleep(config.RETRY_SECONDS)
            logger.warning('retry_counter={:<2}'.format(retry_counter))
            res = handler()  # real handle function
            return res  # succeed
        except Exception as e:  # all request exceptions
            if is_retry_exception(e):
                # only log, do nothing
                current_exception = e
                logger.error('Exception during retrying:"{}", will RETRY'.format(current_exception))
                continue
            else:
                return handle_exit(e)  # fail, exit
    logger.critical(
        'SLEEP {}s for Exception: "{}"'.format(config.REQUEST_EXCEPTION_WAIT_SECONDS, current_exception))
    time.sleep(config.REQUEST_EXCEPTION_WAIT_SECONDS)
    ### FIXME this cannot exit until connection recovers
    res = handle_retry(exception, handler)  # recursive
    return res


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


plt_yaml = os.path.join(os.path.dirname(__file__), 'platforms.yaml')


def get_key(field, fname=plt_yaml):
    with open(fname) as yfile:
        ydata = yaml.load(yfile)
    try:
        return ydata[field]
    except:
        print('no ydata', file=sys.stderr)
        return None


with open(plt_yaml) as yfile:
    ydata = yaml.load(yfile)


def get_key_from_data(field, dict_data=None):
    if dict_data is None:
        dict_data = ydata
    try:
        return dict_data[field]
    except:
        print('no ydata', file=sys.stderr)
        os._exit(1)


def send_msg(report):
    # print('sending email')
    emailing_info = get_key_from_data('Emailing')
    sender = emailing_info['sender']
    receiver = emailing_info['receiver']
    server = emailing_info['server']
    msg = MIMEText(report)
    msg['Subject'] = 'Arbitrage Report'
    msg['From'] = sender
    msg['To'] = receiver
    session = smtplib.SMTP(server)
    session.sendmail(sender, [receiver], msg.as_string())
    session.quit()


MUTEX = threading.Lock()
retry_except_tuple = (
    req_except.ConnectionError, req_except.Timeout, req_except.HTTPError, InvalidNonceError, NULLResponseError,
    HuoBiError)
exit_except_tuple = (req_except.URLRequired, req_except.TooManyRedirects, HuoBiExitError)
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36'

if __name__ == '__main__':
    init_logger()
    logger = get_logger()
    logger.debug('debug')
    logger.info('info')
    logger.warning('warning')
    logger.error('error')
    logger.critical('critical')
