#!/usr/bin/env python
import decimal
import logging
import logging.config
import os
import errno
import sys
import threading

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
    plt._logger.critical('Error during request:"{}", will exit'.format(exception))
    # FIXME should terminate safely
    sys.exit(1)


def handle_retry(exception, plt, handler):
    """
    :param exception: the relevant exception
    :param plt: the platform class, used for logging; must has class variable '_logger' (logging module)
    :param handler: real handler, no params, implemented as closure
    :return: None
    """
    plt._logger.warn('Exception during request:"{}", will retry'.format(exception))
    retry_counter = 0
    while retry_counter < config.RETRY_MAX:
        retry_counter += 1
        try:
            QThread.msleep(config.RETRY_MILLISECONDS)
            plt._logger.debug('retry_counter={:<2}'.format(retry_counter))
            handler()  # real handle function
        except req_except.RequestException as e:  # all request exceptions
            if is_retry_exception(e):
                continue
            else:
                handle_exit(e, plt)
    handle_exit(exception, plt)


def setup_logger():
    log_dir = os.path.join(os.path.dirname(__file__), 'logger')
    try:
        os.makedirs(log_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    log_fname = os.path.join(log_dir, 'arbitrage.log')
    logging.config.fileConfig('logging_config.ini', defaults={
        'logfilename': log_fname
    })
    return logging.getLogger()


MUTEX = threading.Lock()
retry_except_tuple = (req_except.ConnectionError, req_except.Timeout, req_except.HTTPError)
exit_except_tuple = (req_except.URLRequired, req_except.TooManyRedirects)
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36'
