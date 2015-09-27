#!/usr/bin/env python
import logging
import logging.config
import os
import yaml
from settings import config


def init_logger():
    logging_yaml = os.path.join(config.settings_dir, 'log.yaml')
    with open(logging_yaml) as f:
        data = yaml.load(f)
    logger_dir = 'log'
    if not os.path.isdir(logger_dir):
        os.mkdir(logger_dir)
    else:
        pass
        # for f in os.listdir(logger_dir):
        #     fpath = os.path.join(logger_dir, f)
        #     if f.endswith('.LOG') and os.path.isfile(fpath):
        #         os.remove(fpath)
    logging.config.dictConfig(data)


def get_logger():
    return logging.getLogger('logger')


def get_asset_logger():
    return logging.getLogger('asset_logger')
