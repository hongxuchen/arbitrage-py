#!/usr/bin/env python

from __future__ import print_function
import decimal
import logging
import logging.config
import threading
import sys

from PySide.QtCore import QThread
import requests
import requests.exceptions as req_except
import yaml

import config


def get_usd_cny_rate():
    r = requests.get(
        "http://finance.yahoo.com/d/quotes.csv?e=.csv&f=sl1d1t1&s=USDCNY=X",
        timeout=5)
    return decimal.Decimal(r.text.split(",")[1])


def to_decimal(value_str, precision=config.precision):
    return round(float(value_str), precision)


def reverse_catelog(original_catelog):
    assert (original_catelog in ['buy', 'sell'])
    if original_catelog == 'buy':
        return 'sell'
    else:  # sell
        return 'buy'


def adjust_price(trade_catelog, price):
    assert (trade_catelog in ['buy', 'sell'])
    if trade_catelog == 'buy':
        return price * (1 + config.adjust_percentage)
    else:  # sell
        return price * (1 - config.adjust_percentage)


def is_retry_exception(exception):
    for except_type in retry_except_tuple:
        if isinstance(exception, except_type):
            return True
    return False


def handle_exit(exception):
    get_logger().critical('Error during request:"{}", will EXIT'.format(exception))
    sys.exit(1)


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
            QThread.msleep(config.RETRY_MILLISECONDS)
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
    QThread.sleep(config.REQUEST_EXCEPTION_WAIT_SECONDS)
    ### FIXME this makes "stop" button not work when network error
    res = handle_retry(exception, handler)  # recursive
    return res


def init_logger():
    # log_dir = os.path.join(os.path.dirname(__file__), 'logger').replace('\\', '/')
    # try:
    #     os.makedirs(log_dir)
    # except OSError as e:
    #     if e.errno != errno.EEXIST:
    #         raise
    # log_fname = os.path.join(log_dir, 'arbitrage.log').replace('\\', '/')
    # logging.config.fileConfig('logging.ini', defaults={
    #     'logfilename': log_fname
    # })
    with open('logging.yaml') as f:
        data = yaml.load(f)
    logging.config.dictConfig(data)


def get_logger():
    return logging.getLogger('sLogger')


class InvalidNonceError(Exception):
    def __init__(self, message):
        super(InvalidNonceError, self).__init__(message)


class NULLResponseError(Exception):
    def __init__(self, message):
        super(NULLResponseError, self).__init__(message)


def get_key(field, fname='Config.yaml'):
    with open(fname) as yfile:
        ydata = yaml.load(yfile)
    try:
        return ydata[field]
    except:
        print('no ydata', file=sys.stderr)
        return None


with open('Config.yaml') as yfile:
    ydata = yaml.load(yfile)


def get_key_from_data(field, dict_data=None):
    if dict_data is None:
        dict_data = ydata
    try:
        return dict_data[field]
    except:
        print('no ydata', file=sys.stderr)
        sys.exit(1)


MUTEX = threading.Lock()
retry_except_tuple = (
    req_except.ConnectionError, req_except.Timeout, req_except.HTTPError, InvalidNonceError, NULLResponseError)
exit_except_tuple = (req_except.URLRequired, req_except.TooManyRedirects)
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36'

if __name__ == '__main__':
    init_logger()
    logger = get_logger()
    logger.debug('debug')
    logger.info('info')
    logger.warning('warning')
    logger.error('error')
    logger.critical('critical')
