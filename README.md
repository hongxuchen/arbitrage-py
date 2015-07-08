# known issues

## okcoin.py:49

* 'Connection aborted.', gaierror(-5, 'No address associated with hostname')
* 'Connection aborted.', gaierror(-2, 'Name or service not known')  <-- DNS, ConnectionError
* 'Connection aborted.', error(110, 'Connection timed out')

* 'Connection aborted.', error(104, 'Connection reset by peer')
* 'ConnectionError' ('Connection aborted.', BadStatusLine(""''''"))
* 'EOF occurred in violation of protocol (\_ssl.c:581)'
* ' Expecting value: line 1 column 1 (char 0)'

## bitbays.py
* account too low <-- for arbitrage pair since the consumer may have used the asset

## other
* display asset issue
* exit error on Mac <-- maybe due to QT bug?
* producer should have higher priority

## cases
{u'status': 400, u'message': u'Invalid Nonce: Nonce should > 1436332312433', u'result': None} !!!


## hosts
121.199.251.136 www.okcoin.cn
119.28.48.217   okcoin.cn
