# known issues

## okcoin.py:49

* 'Connection aborted.', gaierror(-5, 'No address associated with hostname')
* 'Connection aborted.', gaierror(-2, 'Name or service not known')  <-- DNS, ConnectionError
* 'Connection aborted.', error(110, 'Connection timed out')

* 'Connection aborted.', error(104, 'Connection reset by peer')
* 'ConnectionError' ('Connection aborted.', BadStatusLine(""''''"))
* 'EOF occurred in violation of protocol (\_ssl.c:581)'
* ' Expecting value: line 1 column 1 (char 0)'               <-- when quite slow (ping failed)

## bitbays.py
* account too low <-- for arbitrage pair since the consumer may have used the asset

## other
* display asset issue
* exit error on Mac <-- maybe due to QT bug?
* producer should have higher priority

## cases
----------
bitbays.py:  93 - ERROR: api\_type=trade, error\_message=Account balance is too low

----------
ERROR 2015-07-09 09:55:00                140508430841600            common.py:  75 - Exception during request:"InvalidNonceError: Invalid Nonce: Nonce should > 1436406781893, current\_nonce=1436406781892", will retry
WARNING 2015-07-09 09:55:01                140508430841600            common.py:  81 - retry\_counter=1
INFO 2015-07-09 09:55:01                140508430841600           bitbays.py:  76 - PARAMS={'nonce': 1436406781894, 'order\_type': 0, 'price': '1508.499', 'amount': '0.012', 'market': 'btc\_cny', 'op': 'sell'}
 WARNING 2015-07-09 09:55:02                140508430841600        trade\_info.py:  41 - Trade in BitBays   : sell     0.0120 btc at price  1508.4990 cny, order\_id=56572553


## hosts
121.199.251.136 www.okcoin.cn
119.28.48.217   okcoin.cn
