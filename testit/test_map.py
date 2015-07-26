#!/usr/bin/env python
from concurrent.futures import ThreadPoolExecutor


def fct(variable1, variable2):
    return variable1, variable2


variables1 = [1, 2, 3, 4]
variables2 = [7, 8, 9, 0]

with ThreadPoolExecutor(max_workers=8) as executor:
    future = executor.map(fct, variables1, variables2)
    print '[%s]' % ', '.join(map(str, future))
