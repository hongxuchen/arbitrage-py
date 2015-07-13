#!/usr/bin/env python
import decimal
import logging
import logging.config
import os
import errno
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


def get_key_from_file(field, fname='Config.yaml'):
    with open(fname) as yfile:
        ydata = yaml.load(yfile)
    try:
        return ydata[field]
    except:
        print('no ydata')
        return None


def reverse_catelog(original_catelog):
    assert (original_catelog in ['buy', 'sell'])
    if original_catelog == 'buy':
        return 'sell'
    else:  # sell
        return 'buy'


def adjust_arbitrage_price(trade_catelog, price):
    assert (trade_catelog in ['buy', 'sell'])
    if trade_catelog == 'buy':
        return price + config.arbitrage_diff / 3.0
    else:  # sell
        return price - config.arbitrage_diff / 3.0


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


def handle_exit(exception, plt):
    plt._logger.critical('Error during request:"{}", will EXIT'.format(exception))
    # should exit
    sys.exit(1)


def handle_retry(exception, plt, handler):
    """
    # NOTE: this handling may be blocked OR not blocked
    :param exception: the relevant exception
    :param plt: the platform class, used for logging; must has class variable '_logger' (logging module)
    :param handler: real handler, no params, implemented as closure
    :return: if retry succeeds, should return request result; otherwise, exit abornormally
    """
    plt._logger.error('RETRY for Exception: "{}"'.format(exception))
    retry_counter = 0
    while retry_counter < config.RETRY_MAX:
        retry_counter += 1
        try:
            QThread.msleep(config.RETRY_MILLISECONDS)
            plt._logger.warning('retry_counter={:<2}'.format(retry_counter))
            config.verbose = True
            res = handler()  # real handle function
            config.verbose = False
            return res  # succeed
        # TODO check whether accessable to exception handling
        except Exception as e:  # all request exceptions
            if is_retry_exception(e):
                plt._logger.error('Exception during retrying:"{}", will RETRY'.format(e))
                continue
            else:
                return handle_exit(e, plt)  # fail
    plt._logger.critical(
        'Exception after retrying: "{}", will SLEEP {}s'.format(exception, config.REQUEST_EXCEPTION_WAIT_SECONDS))
    QThread.sleep(config.REQUEST_EXCEPTION_WAIT_SECONDS)
    res = handle_retry(exception, plt, handler)  # recursive
    return res


def setup_logger():
    log_dir = os.path.join(os.path.dirname(__file__), 'logger').replace('\\', '/')
    try:
        os.makedirs(log_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    log_fname = os.path.join(log_dir, 'arbitrage.log').replace('\\', '/')
    logging.config.fileConfig('logging_config.ini', defaults={
        'logfilename': log_fname
    })
    return logging.getLogger()


class InvalidNonceError(Exception):
    def __init__(self, message):
        super(InvalidNonceError, self).__init__(message)


class NULLResponseError(Exception):
    def __init__(self, message):
        super(NULLResponseError, self).__init__(message)


MUTEX = threading.Lock()
retry_except_tuple = (
    req_except.ConnectionError, req_except.Timeout, req_except.HTTPError, InvalidNonceError, NULLResponseError)
exit_except_tuple = (req_except.URLRequired, req_except.TooManyRedirects)
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36'
