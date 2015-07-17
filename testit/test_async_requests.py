#!/usr/bin/env python

import grequests

urls = [
    'http://www.heroku.com',
    'http://tablib.org',
    'http://httpbin.org',
    'http://python-requests.org',
    'http://kennethreitz.com'
]

rs = (grequests.get(u) for u in urls)
res = grequests.map(rs)
for r in res:
    print(r.url)
    print(r.text)
