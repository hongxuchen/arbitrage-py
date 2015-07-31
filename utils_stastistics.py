#!/usr/bin/env python

from __future__ import print_function
cancel_counter = 0
with open('.arbitrage.log') as log:
    for line in log:
        if 'cancel order_id' in line:
            cancel_counter += 1
print('cancel_counter={:d}'.format(cancel_counter))
