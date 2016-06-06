#!/usr/bin/env python

import requests

url = 'http://localhost:9000/'


def signin(**params):
    signin_url = url + 'signin'
    print(params)
    res = requests.post(signin_url, data=params)
    print(res)


def fakeDB():
    fakeDB_url = url + 'fakeDB'
    res = requests.get(fakeDB_url)
    print(res)
    print(res.content)


signin(email='user1@mail.com', password='123456')
