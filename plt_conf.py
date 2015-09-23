#!/usr/bin/env python

# TODO: use singleton
import os
import yaml
import common
import excepts

plt_yaml = os.path.join(os.path.dirname(__file__), 'plt.yaml')

with open(plt_yaml) as yfile:
    ydata = yaml.load(yfile)


def get_key_from_data(field, dict_data=None):
    if dict_data is None:
        dict_data = ydata
    try:
        return dict_data[field]
    except KeyError:
        err_msg = 'msg: no ydata for field={}'.format(field)
        excepts.handle_exit(err_msg)


if __name__ == '__main__':
    enabled = get_key_from_data('Enable_Adjuster')
    print(type(enabled), enabled)
