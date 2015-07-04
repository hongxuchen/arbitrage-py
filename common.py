#!/usr/bin/env python
import decimal
import logging
import logging.config
import os
import errno

import requests
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
