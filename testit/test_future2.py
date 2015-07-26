#!/usr/bin/env python

from __future__ import print_function
import time

import concurrent.futures


def my_fn(first, second, third):
    return first + second + third


class calculator(object):
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

    def __repr__(self):
        return "cal: a={}, b={}, c={}".format(self.a, self.b, self.c)


def sleep_run(cal, seconds):
    time.sleep(seconds)
    return my_fn(cal.a, cal.b, cal.c)


c_list = [calculator(1, 2, 3), calculator(-1, -2, -3)]
old = time.time()
SLEEP = [2, 1]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as e:
    rs = e.map(sleep_run, c_list, SLEEP)
print(time.time() - old)
for cal, r in zip(c_list, rs):
    print("{:30s} {:02d}".format(cal, r))
