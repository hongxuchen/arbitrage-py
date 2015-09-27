#!/usr/bin/env python

import os

import yaml

from settings import config

import utils.excepts
import utils.log_helper


def _display(k):
    v = get_key_from_data(k)
    print('{}: {}'.format(k, v))


_plt_ydata = None


def get_key_from_data(field):
    global _plt_ydata
    if _plt_ydata is None:
        parse_plt_conf()
    try:
        return _plt_ydata[field]
    except KeyError:
        err_msg = 'msg: no ydata for field={}'.format(field)
        utils.excepts.handle_exit(err_msg)


def parse_plt_conf():
    global _plt_ydata
    plt_yaml = os.path.join(config.settings_dir, 'plt.yaml')
    display_list = ['Enabled', 'Enable_Adjuster', 'CoinType']
    with open(plt_yaml) as yfile:
        _plt_ydata = yaml.load(yfile)
    print('=' * 80)
    for display in display_list:
        _display(display)
    print('=' * 80)


if __name__ == '__main__':
    utils.log_helper.init_logger()
    enabled = get_key_from_data('Enable_Adjuster')
    print(enabled)
