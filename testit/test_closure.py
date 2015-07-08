#!/usr/bin/env python

from __future__ import print_function

t = 0


def nonce():
    global t
    t += 1
    return t


def run(handler):
    for j in range(4):
        handler()


def outer(i):
    def inner():
        v = nonce()
        print(v, i)
    run(inner)

for i in range(-5, -1):
    outer(i)
