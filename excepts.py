#!/usr/bin/env python

from email.mime.text import MIMEText
import os
import smtplib
import time
import traceback
import ipgetter
import sys
import config
import logging_conf
import plt_conf
import requests.exceptions as req_except
import urllib3.exceptions as urllib3_except


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


retry_except_tuple = (
    req_except.ConnectionError, req_except.Timeout, req_except.HTTPError, InvalidNonceError, NULLResponseError,
    HuoBiError, CHBTCRetryError, urllib3_except.TimeoutError, urllib3_except.HTTPError, urllib3_except.ConnectionError,
    ValueError)
exit_except_tuple = (req_except.URLRequired, req_except.TooManyRedirects, HuoBiExitError, CHBTCExitError)


def is_retry_exception(exception):
    for except_type in retry_except_tuple:
        if isinstance(exception, except_type):
            return True
    return False


def handle_exit(error):
    logging_conf.get_logger().critical('Error during request:"{}", will EXIT'.format(error))
    send_msg('error during request: {}'.format(error))
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
    logger = logging_conf.get_logger()
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
    msg = 'Request Exception "{}" after retrying {} times'.format(current_exception, config.RETRY_MAX)
    logger.critical(msg)
    send_msg(msg)
    time.sleep(config.RETRY_SLEEP_SECONDS)
    return handle_retry(current_exception, handler)


def send_msg(report):
    emailing_info = plt_conf.get_key_from_data('Emailing')
    server = emailing_info['server']
    username = emailing_info['username']
    try:
        sender = emailing_info['sender']
    except KeyError:
        sender = username
    receiver = emailing_info['receiver']
    ip_str = ipgetter.myip()
    report = str(ip_str) + '\n' + report
    msg = MIMEText(report)
    msg['Subject'] = 'Arbitrage Report'
    msg['From'] = sender
    msg['To'] = receiver
    try:
        session = smtplib.SMTP(server)
        # session.set_debuglevel(1)
        if server != 'localhost':
            session.starttls()
            password = emailing_info['password']
            session.login(username, password)
        session.sendmail(sender, [receiver], msg.as_string())
        logging_conf.get_logger().warning("sending mail done")
        session.quit()
    except:
        traceback.print_exc(file=sys.stderr)


if __name__ == '__main__':
    logging_conf.init_logger()
    send_msg("HELLOWORLD")
