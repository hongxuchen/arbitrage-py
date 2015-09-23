#!/usr/bin/env python
import logging
import logging.config
import os
import yaml


def init_logger():
    logging_yaml = os.path.join(os.path.dirname(__file__), 'logging.yaml')
    with open(logging_yaml) as f:
        data = yaml.load(f)
    logging.config.dictConfig(data)


def get_logger():
    return logging.getLogger('logger')


def get_asset_logger():
    return logging.getLogger('asset_logger')
