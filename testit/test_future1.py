#!/usr/bin/env python
from __future__ import print_function
import concurrent.futures
import requests

URLS = ('http://www.foxnews.com/',
        'http://www.cnn.com/',
        'http://europe.wsj.com/',
        'http://www.bbc.co.uk/',
        'http://some-made-up-domain.com/')

TIMEOUTS = [1, 2, 3, 52, 1]


def my_request(url, timeout):
    try:
        response = requests.get(url, timeout=timeout)
        return len(response.text)
    except Exception as e:
        print("Exception='{}' for {}".format(e, url))
        return 0


# We can use a with statement to ensure threads are cleaned up promptly
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    results = executor.map(my_request, URLS, TIMEOUTS)
    for url, r in zip(URLS, results):
        print("page {} is of {:d} bytes".format(url, r))
