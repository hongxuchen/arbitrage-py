# known issues

## okcoin.py

* 'Connection aborted.', gaierror(-5, 'No address associated with hostname') <-- fixed by hosts
* 'Connection aborted.', gaierror(-2, 'Name or service not known')  <-- fixed by hosts

* 'Connection aborted.', error(110, 'Connection timed out')
* 'Connection aborted.', error(104, 'Connection reset by peer')
* 'ConnectionError' ('Connection aborted.', BadStatusLine(""''''"))
* 'EOF occurred in violation of protocol (\_ssl.c:581)'
* ' Expecting value: line 1 column 1 (char 0)'               <-- when quite slow (ping failed)

## other
* exit error on Mac <-- due to QT bug?
* cannot totally avoid btc changes since the pending amount may be changed during 'order' and 'cancel'
* when exception, should not exit, but wait for a longer time
* when btc changes exists for a long time(threshold), the monitor should adjust the trade according to catelog and platform ask/bid
* smarter strategy to determine which platform to adjust trade

## cases

```
  File "/home/hongxu/Dropbox/Bitcoin/arbitrage/okcoin.py", line 230, in order_info
    info = self.api_order_info(order_id)['orders'][0]
IndexError: list index out of range
```

## hosts
121.199.251.136 www.okcoin.cn
119.28.48.217   okcoin.cn
