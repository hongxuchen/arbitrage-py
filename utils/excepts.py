#!/usr/bin/env python

import os
import smtplib
import sys
import time
import traceback
import urllib3.exceptions as urllib3_except
from email.mime.text import MIMEText

import requests.exceptions as req_except

import utils.log_helper
import utils.plt_helper
from settings import config


# bitbays
class InvalidNonceError(Exception):
    def __init__(self, message):
        super(InvalidNonceError, self).__init__(message)


# bitbays
class RateExceedError(Exception):
    def __init__(self, message):
        super(RateExceedError, self).__init__(message)


# okcoin, bitbays
class NULLResponseError(Exception):
    def __init__(self, message):
        super(NULLResponseError, self).__init__(message)


# huobi
class HuoBiError(Exception):
    def __init__(self, msg):
        super(HuoBiError, self).__init__(msg)


# huobi
class HuoBiExitError(Exception):
    def __init__(self, msg):
        super(HuoBiExitError, self).__init__(msg)


# chbtc
class CHBTCExitError(Exception):
    def __init__(self, msg):
        super(CHBTCExitError, self).__init__(msg)


# chbtc
class CHBTCRetryError(Exception):
    def __init__(self, msg):
        super(CHBTCRetryError, self).__init__(msg)


retry_except_tuple = (
    req_except.ConnectionError, req_except.Timeout, req_except.HTTPError, InvalidNonceError, RateExceedError,
    NULLResponseError, HuoBiError, CHBTCRetryError, urllib3_except.TimeoutError, urllib3_except.HTTPError,
    urllib3_except.ConnectionError, ValueError)
exit_except_tuple = (req_except.URLRequired, req_except.TooManyRedirects, HuoBiExitError, CHBTCExitError)


def is_retry_exception(exception):
    for except_type in retry_except_tuple:
        if isinstance(exception, except_type):
            return True
    return False


def handle_exit(error):
    utils.log_helper.get_logger().critical('Error during request:"{}", will EXIT'.format(error))
    send_msg('{}'.format(error), 'plain')
    traceback.print_exc(file=sys.stdout)
    # noinspection PyProtectedMember
    os._exit(1)


def handle_retry(exception, handler):
    """
    # NOTE: this handling may be blocked OR not blocked
    :param exception: the relevant exception
    :param handler: real handler, no params, implemented as closure
    :return: if retry succeeds, should return request result; otherwise, exit abornormally
    """
    logger = utils.log_helper.get_logger()
    current_exception = exception
    logger.error('RETRY for Exception: "{}"'.format(current_exception))
    retry_counter = 0
    while retry_counter < config.RETRY_MAX:
        retry_counter += 1
        # sleep
        if isinstance(current_exception, RateExceedError):
            logger.error("RateExceedError, will sleep for {}s".format(config.RATE_EXCEED_SLEEP_SECONDS))
            time.sleep(config.RATE_EXCEED_SLEEP_SECONDS)
        else:
            if retry_counter % 10 == 0:
                time.sleep(config.RETRY_SLEEP_SECONDS)
            else:
                time.sleep(config.RETRY_SECONDS)
        # retry
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
    # notifying
    msg = 'Request Exception "{}" after retrying {} times'.format(current_exception, config.RETRY_MAX)
    logger.critical(msg)
    send_msg(msg, 'plain')
    time.sleep(config.RETRY_SLEEP_SECONDS)
    # retry
    return handle_retry(current_exception, handler)


def send_msg(report, msg_type):
    emailing_info = utils.plt_helper.get_key_from_data('Emailing')
    server = emailing_info['server']
    username = emailing_info['username']
    try:
        sender = emailing_info['sender']
    except KeyError:
        sender = username
    receivers = emailing_info['receivers']
    msg = MIMEText(report, msg_type, _charset='utf-8')
    client_id = utils.plt_helper.get_key_from_data('ClientID')
    subject = 'Arbitrage for {}'.format(client_id)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(receivers)
    # noinspection PyBroadException
    try:
        session = smtplib.SMTP(server)
        # session.set_debuglevel(1)
        if server != 'localhost':
            session.starttls()
            password = emailing_info['password']
            session.login(username, password)
        session.sendmail(sender, receivers, msg.as_string())
        utils.log_helper.get_logger().info("sending mail done")
        session.quit()
    except:
        traceback.print_exc(file=sys.stderr)


if __name__ == '__main__':
    utils.log_helper.init_logger()
    send_msg("HELLOWORLD", 'plain')
