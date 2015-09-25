#!/usr/bin/env python

# TODO: use singleton
import os
import yaml
import excepts
import logging_conf


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
        excepts.handle_exit(err_msg)


def parse_plt_conf():
    global _plt_ydata
    plt_yaml = os.path.join(os.path.dirname(__file__), 'plt.yaml')
    display_list = ['Enabled', 'Enable_Adjuster', 'CoinType']
    with open(plt_yaml) as yfile:
        _plt_ydata = yaml.load(yfile)
    print('=' * 80)
    for display in display_list:
        _display(display)
    print('=' * 80)


if __name__ == '__main__':
    logging_conf.init_logger()
    enabled = get_key_from_data('Enable_Adjuster')
    print(enabled)
