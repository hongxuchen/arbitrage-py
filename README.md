# known issues

## okcoin.py

* ' Expecting value: line 1 column 1 (char 0)'               <-- when quite slow (ping failed)

## other
* exit error on Mac <-- due to QT bug?

## TODO
* statistical adjust
   sometimes, the price on Platform A is typically higher than B, so when there is "little" difference, we may choose to
* [FATAL] monitor adjust still may 'cannot afford' so that it causes long-term imbalance
reverse the fiat amount for futher trade. The net strategy is that we can change "diff".
- deal with logging issue
- add litecoin, if possible
- use websocket/fix to get faster connection
* calculate the probabilities
    - request time
    - failed frequency
    - ask/bid diff times w.r.t. certain amount
* add huobi

## cases

```
  File "/home/hongxu/Dropbox/Bitcoin/arbitrage/okcoin.py", line 230, in order_info
    info = self.api_order_info(order_id)['orders'][0]
IndexError: list index out of range
```

```
WARNING 2015-07-20 11:20:27      140251542492928             trade_info.py: 130 - OKCoinCN single adjust_trade
 WARNING 2015-07-20 11:20:28      140251542492928             trade_info.py:  42 - Trade in OKCoinCN  : sell     0.0470 btc at price  1518.9300 cny, order_id=904709729
   ERROR 2015-07-20 11:34:33      140251550885632                 common.py:  85 - RETRY for Exception: "HTTPSConnectionPool(host='www.okcoin.cn', port=443): Read timed out. (read timeout=3.0
)"                                                                                                                                                                                              WARNING 2015-07-20 11:34:33      140251550885632                 common.py:  91 - retry_counter=1
   ERROR 2015-07-20 11:58:06      140251550885632                 common.py:  85 - RETRY for Exception: "HTTPSConnectionPool(host='www.okcoin.cn', port=443): Read timed out. (read timeout=3.0
)"                                                                                                                                                                                              WARNING 2015-07-20 11:58:06      140251550885632                 common.py:  91 - retry_counter=1
Traceback (most recent call last):
  File "/home/hongxu/Dropbox/Bitcoin/arbitrage/arbitrage_producer.py", line 31, in run
    self.process_arbitrage()
  File "/home/hongxu/Dropbox/Bitcoin/arbitrage/arbitrage_producer.py", line 92, in process_arbitrage
    self._info_list = [plt.ask_bid_list(1) for plt in self.plt_list]
  File "/home/hongxu/Dropbox/Bitcoin/arbitrage/okcoin.py", line 115, in ask_bid_list
    asks = sorted(data['asks'], key=lambda ask: ask[0], reverse=True)
KeyError: 'asks'
```

```
 WARNING 2015-07-16 11:01:47      139708326995712             trade_info.py: 130 - BitBays single adjust_trade, waited 0 times
CRITICAL 2015-07-16 11:01:48      139708326995712                bitbays.py:  92 - ERROR: api_type=trade, error_message=Account balance is too low
```

```
 WARNING 2015-07-23 10:40:33      140613431838464         arbitrage_info.py:  31 - Arbitrage Start
 WARNING 2015-07-23 10:40:33      140613431838464             trade_info.py:  42 - Trade in OKCoinCN  : buy      0.3210 btc at price  1715.8400 cny, order_id=913079191
 WARNING 2015-07-23 10:40:34      140613431838464             trade_info.py:  42 - Trade in BitBays   : sell     0.3210 btc at price  1716.2600 cny, order_id=63491765
 WARNING 2015-07-23 10:40:39      140613431838464         arbitrage_info.py:  31 - Arbitrage Start
 WARNING 2015-07-23 10:40:39      140613289228032         arbitrage_info.py:  99 - A1=0.0000    , A2=0.0000    , A=0.0000
 WARNING 2015-07-23 10:40:39      140613431838464             trade_info.py:  42 - Trade in OKCoinCN  : buy      0.4441 btc at price  1715.3000 cny, order_id=913079637
 WARNING 2015-07-23 10:40:41      140613431838464             trade_info.py:  42 - Trade in BitBays   : sell     0.4441 btc at price  1716.2500 cny, order_id=63491772
 WARNING 2015-07-23 10:40:42      140613423445760          asset_monitor.py:  94 - [Monitor] exceed_counter=0, old_btc_changes=0.0003    , current=-0.4438
 WARNING 2015-07-23 10:40:44      140613289228032             trade_info.py: 139 - OKCoinCN   cancel order_id=913079637
 WARNING 2015-07-23 10:40:46      140613289228032         arbitrage_info.py:  99 - A1=0.4440    , A2=0.0000    , A=0.4440
 WARNING 2015-07-23 10:40:47      140613423445760          asset_monitor.py:  94 - [Monitor] exceed_counter=-1, old_btc_changes=-0.4438   , current=-0.4438
CRITICAL 2015-07-23 10:40:48      140613289228032             trade_info.py:  73 - OKCoinCN: not afford to "buy" after waiting > 1 times
 WARNING 2015-07-23 10:40:49      140613289228032             trade_info.py: 130 - BitBays single adjust_trade
 WARNING 2015-07-23 10:40:50      140613289228032             trade_info.py:  42 - Trade in BitBays   : buy      0.4440 btc at price  1887.8750 cny, order_id=63491785
```

```
WARNING 2015-07-26 18:04:04      139864961406720         arbitrage_info.py:  33 - Arbitrage Start
WARNING 2015-07-26 18:04:05      139864469141248             trade_info.py:  42 - Trade in OKCoinCN  : sell     0.4365 btc at price  1790.8300 cny, order_id=921421791
WARNING 2015-07-26 18:04:05      139864460748544             trade_info.py:  42 - Trade in BitBays   : buy      0.4365 btc at price  1790.3100 cny, order_id=65295446
WARNING 2015-07-26 18:04:07      139864737576704          asset_monitor.py:  80 - [Monitor] exceed_counter=1, old_btc_changes=-0.0001   , current=0.2654
WARNING 2015-07-26 18:04:11      139864460748544             trade_info.py: 139 - OKCoinCN   cancel order_id=921421791
CRITICAL 2015-07-26 18:04:11      139864460748544                 okcoin.py: 146 - ERROR: api_type=cancel_order, response_data={u'error_code': 10009, u'result': False}

```
```
 WARNING 2015-07-26 18:31:43      139864961406720         arbitrage_info.py:  33 - Arbitrage Start
 WARNING 2015-07-26 18:31:43      139864460748544             trade_info.py:  42 - Trade in OKCoinCN  : buy      0.9986 btc at price  1800.2000 cny, order_id=921479700
 WARNING 2015-07-26 18:31:44      139864720791296             trade_info.py:  42 - Trade in BitBays   : sell     0.9986 btc at price  1800.4200 cny, order_id=65307057
   ERROR 2015-07-26 18:31:48      139864961406720                 common.py:  85 - RETRY for Exception: "HTTPSConnectionPool(host='bitbays.com', port=443): Max retries exceeded with url: /api
/v1/depth/?market=btc_cny (Caused by ConnectTimeoutError(<requests.packages.urllib3.connection.VerifiedHTTPSConnection object at 0x7f34dc9738d0>, 'Connection to bitbays.com timed out. (connec
t timeout=3.0)'))"
   ERROR 2015-07-26 18:31:48      139864460748544                 common.py:  85 - RETRY for Exception: "HTTPSConnectionPool(host='bitbays.com', port=443): Max retries exceeded with url: /api
/v1/info/ (Caused by ConnectTimeoutError(<requests.packages.urllib3.connection.VerifiedHTTPSConnection object at 0x7f34dc996650>, 'Connection to bitbays.com timed out. (connect timeout=3.0)')
)"
 WARNING 2015-07-26 18:31:48      139864961406720                 common.py:  91 - retry_counter=1
 WARNING 2015-07-26 18:31:48      139864460748544                 common.py:  91 - retry_counter=1
 WARNING 2015-07-26 18:31:48      139864720791296             trade_info.py: 139 - OKCoinCN   cancel order_id=921479700
 WARNING 2015-07-26 18:31:49      139864737576704          asset_monitor.py:  92 - [Monitor] exceed_counter=0, old_btc_changes=0.0004    , current=-0.6196
 WARNING 2015-07-26 18:31:49      139864684955392             trade_info.py: 139 - BitBays    cancel order_id=65307057
CRITICAL 2015-07-26 18:31:50      139864684955392                bitbays.py:  91 - ERROR: api_type=cancel, error_message=Cancellation failed!
 WARNING 2015-07-26 18:31:50      139864953014016         arbitrage_info.py: 107 - A1=0.9980    , A2=0.0000    , A=0.9980
   ERROR 2015-07-26 18:31:55      139864953014016                 common.py:  85 - RETRY for Exception: "HTTPSConnectionPool(host='bitbays.com', port=443): Read timed out. (read timeout=3.0)"
 WARNING 2015-07-26 18:31:55      139864953014016                 common.py:  91 - retry_counter=1
   ERROR 2015-07-26 18:31:55      139864720791296                 common.py:  85 - RETRY for Exception: "HTTPSConnectionPool(host='bitbays.com', port=443): Max retries exceeded with url: /api
/v1/info/ (Caused by ConnectTimeoutError(<requests.packages.urllib3.connection.VerifiedHTTPSConnection object at 0x7f34dc98b510>, 'Connection to bitbays.com timed out. (connect timeout=3.0)')
)"
 WARNING 2015-07-26 18:31:55      139864720791296                 common.py:  91 - retry_counter=1
 WARNING 2015-07-26 18:31:56      139864737576704          asset_monitor.py:  92 - [Monitor] exceed_counter=-1, old_btc_changes=-0.6196   , current=-0.9982
CRITICAL 2015-07-26 18:31:59      139864953014016             trade_info.py:  73 - BitBays: not afford to "buy" after waiting > 1 times
CRITICAL 2015-07-26 18:31:59      139864953014016             trade_info.py:  73 - OKCoinCN: not afford to "buy" after waiting > 1 times
CRITICAL 2015-07-26 18:31:59      139864953014016         arbitrage_info.py: 140 - CRITAL: [BitBays, OKCoinCN] cannot adjust
 WARNING 2015-07-26 18:32:01      139864737576704          asset_monitor.py:  92 - [Monitor] exceed_counter=-2, old_btc_changes=-0.9982   , current=-0.9982
 WARNING 2015-07-26 18:32:05      139864737576704          asset_monitor.py:  92 - [Monitor] exceed_counter=-3, old_btc_changes=-0.9982   , current=-0.9982
 WARNING 2015-07-26 18:32:05      139864737576704          asset_monitor.py: 115 - [Monitor] exceed_counter=-4, amount=-0.9982
 WARNING 2015-07-26 18:32:07      139864737576704          asset_monitor.py: 121 - [Monitor] adjust at BitBays
CRITICAL 2015-07-26 18:32:08      139864737576704             trade_info.py:  73 - BitBays: not afford to "buy" after waiting > 1 times
 WARNING 2015-07-26 18:32:08      139864737576704          asset_monitor.py: 124 - [Monitor] FAILED adjust at BitBays
 WARNING 2015-07-26 18:32:08      139864737576704          asset_monitor.py: 128 - [Monitor] adjust at OKCoinCN
CRITICAL 2015-07-26 18:32:08      139864737576704             trade_info.py:  73 - OKCoinCN: not afford to "buy" after waiting > 1 times
CRITICAL 2015-07-26 18:32:08      139864737576704          asset_monitor.py: 132 - [Monitor] adjust fails for [BitBays, OKCoinCN]
 WARNING 2015-07-26 18:32:12      139864737576704          asset_monitor.py:  92 - [Monitor] exceed_counter=0, old_btc_changes=-0.9982   , current=-0.9982
 WARNING 2015-07-26 18:32:17      139864737576704          asset_monitor.py:  92 - [Monitor] exceed_counter=-1, old_btc_changes=-0.9982   , current=-0.9982
 WARNING 2015-07-26 18:32:21      139864737576704          asset_monitor.py:  92 - [Monitor] exceed_counter=-2, old_btc_changes=-0.9982   , current=-0.9982
 WARNING 2015-07-26 18:32:27      139864737576704          asset_monitor.py:  92 - [Monitor] exceed_counter=-3, old_btc_changes=-0.9982   , current=-0.9982
 WARNING 2015-07-26 18:32:27      139864737576704          asset_monitor.py: 115 - [Monitor] exceed_counter=-4, amount=-0.9982
 WARNING 2015-07-26 18:32:28      139864737576704          asset_monitor.py: 121 - [Monitor] adjust at BitBays
CRITICAL 2015-07-26 18:32:29      139864737576704             trade_info.py:  73 - BitBays: not afford to "buy" after waiting > 1 times
 WARNING 2015-07-26 18:32:29      139864737576704          asset_monitor.py: 124 - [Monitor] FAILED adjust at BitBays
 WARNING 2015-07-26 18:32:29      139864737576704          asset_monitor.py: 128 - [Monitor] adjust at OKCoinCN
CRITICAL 2015-07-26 18:32:30      139864737576704             trade_info.py:  73 - OKCoinCN: not afford to "buy" after waiting > 1 times
CRITICAL 2015-07-26 18:32:30      139864737576704          asset_monitor.py: 132 - [Monitor] adjust fails for [BitBays, OKCoinCN]
```

## hosts
- 121.199.251.136 www.okcoin.cn
- 119.28.48.217   okcoin.cn
