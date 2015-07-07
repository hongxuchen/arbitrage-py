# known issues

## okcoin.py:49

* 'Connection aborted.', gaierror(-5, 'No address associated with hostname')
* 'Connection aborted.', gaierror(-2, 'Name or service not known')
* 'ConnectionError' ('Connection aborted.', BadStatusLine(""''''"))
* 'EOF occurred in violation of protocol (_ssl.c:581)'
* 'Connection aborted.', error(110, 'Connection timed out')
* 'Connection aborted.', error(104, 'Connection reset by peer')

## bitbays.py:132
* account too low <-- for arbitrage pair since the consumer may have used the asset

## other
* display asset issue
* when stop and exit, QThread may be unexpected terminated
* after lock, seems pending sometimes

## cases:
* OKCoin buys more than expected
* xxx
File "bitbays.py", line 206, in order_info
    create_time = BitBays._get_timestamp(info['created_at'], BitBays.fmt)
TypeError: 'NoneType' object has no attribute '__getitem__'
