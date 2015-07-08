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

   ERROR 2015-07-09 02:30:53 4677386240            common.py:  75 - Exception during request:"InvalidNonceError: Invalid Nonce: Nonce should > 1436380218744, current_nonce=1436380218743", will retry
    WARNING 2015-07-09 02:30:54 4677386240            common.py:  81 - retry_counter=1
        INFO 2015-07-09 02:30:54 4677386240           bitbays.py:  76 - PARAMS={'nonce': 1436380218745, 'order_type': 0, 'price': '1682.32', 'amount': '0.012', 'market': 'btc_cny', 'op': 'buy'}
         WARNING 2015-07-09 02:30:57 4677386240            common.py:  81 - retry_counter=2
             INFO 2015-07-09 02:30:57 4677386240           bitbays.py:  76 - PARAMS={'nonce': 1436380218746, 'order_type': 0, 'price': '1682.32', 'amount': '0.012', 'market': 'btc_cny', 'op': 'buy'}
             CRITICAL 2015-07-09 02:30:58 4677386240           bitbays.py:  93 - ERROR: api_type=trade, error_message=Account balance is too low
             QThread: Destroyed while thread is still running
                 INFO 2015-07-09 02:30:58 4678459392           bitbays.py:  76 - PARAMS={'nonce': 1436380218747}


## hosts
121.199.251.136 www.okcoin.cn
119.28.48.217   okcoin.cn
