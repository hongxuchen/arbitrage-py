# known issues

## okcoin.py

* 'Connection aborted.', gaierror(-5, 'No address associated with hostname') <-- fixed by hosts
* 'Connection aborted.', gaierror(-2, 'Name or service not known')  <-- fixed by hosts

* 'Connection aborted.', error(110, 'Connection timed out')
* 'Connection aborted.', error(104, 'Connection reset by peer')
* 'ConnectionError' ('Connection aborted.', BadStatusLine(""''''"))
* 'EOF occurred in violation of protocol (\_ssl.c:581)'
* ' Expecting value: line 1 column 1 (char 0)'               <-- when quite slow (ping failed)

## bitbays.py
* account too low <-- for arbitrage pair since the consumer may have used the asset

## other
* exit error on Mac <-- due to QT bug?

## hosts
121.199.251.136 www.okcoin.cn
119.28.48.217   okcoin.cn
