#!/usr/bin/env python

import logging

r = logging.getLogger()
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
r.addHandler(ch)

p = logging.getLogger('foo')
p.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(message)s')
ch.setFormatter(formatter)
p.addHandler(ch)

c = logging.getLogger('foo.bar')
c.debug('foo')
