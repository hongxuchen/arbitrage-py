# known issues

## okcoin.py

* ' Expecting value: line 1 column 1 (char 0)'               <-- when quite slow (ping failed)

## other
* exit error on Mac <-- due to QT bug?

## TODO
* statistical adjust
   sometimes, the price on Platform A is typically higher than B, so when there is "little" difference, we may choose to
reverse the fiat amount for futher trade. The net strategy is that we can change "diff".
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

## TODO
- deal with logging issue
- add litecoin, if possible
- smartly choose which platform
- use websocket/fix to get faster connection

## hosts
- 121.199.251.136 www.okcoin.cn
- 119.28.48.217   okcoin.cn
