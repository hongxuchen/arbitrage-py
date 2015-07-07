# known issues

## okcoin.py:49

* 'Connection aborted.', gaierror(-5, 'No address associated with hostname')
* 'Connection aborted.', gaierror(-2, 'Name or service not known')  <-- DNS, ConnectionError
* 'Connection aborted.', error(110, 'Connection timed out')

* 'Connection aborted.', error(104, 'Connection reset by peer')
* 'ConnectionError' ('Connection aborted.', BadStatusLine(""''''"))
* 'EOF occurred in violation of protocol (_ssl.c:581)'

## bitbays.py:132
* account too low <-- for arbitrage pair since the consumer may have used the asset

## other
* display asset issue
* when stop and exit, QThread may be unexpected terminated
* after lock, seems pending sometimes


## hosts
121.199.251.136 www.okcoin.cn
119.28.48.217   okcoin.cn