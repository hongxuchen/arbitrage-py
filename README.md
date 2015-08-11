# known issues
* okcoin sometimes may return {} data, known issues for `ask_bid_list`, `order_info`
* not afford to buy on bitbays/okcoin
* exit error on Mac <-- due to QT bug?

# TODO
* [FATAL] monitor adjust still may 'cannot afford' so that it causes long-term imbalance
reverse the fiat amount for futher trade. The net strategy is that we can change "diff".
- add litecoin, if possible
* calculate the probabilities
    - request time
    - failed frequency
    - ask/bid diff times w.r.t. certain amount
* order/cancel frequently for one platform; when completed, reverse trade on another platform
* Deal with common.py init issue
* deployed in lab, stopping fails
* force implementation
* "No JSON object could be decoded"
* Producer cannot release lock
* considering using RLock
* HuoBi error handling; HuoBi Retry
* should NOT always retry

# cases

```
CHBTC Error: code=2001, msg=人民币账户余额不足 # no ltc
```
```
  WARNING 2015-08-11 18:44:32     arbitrage_producer.py:  44 - [P] Arbitrage Start
  WARNING 2015-08-11 18:44:34       arbitrage_trader.py:  42 - Trade in BitBays   : sell     0.0900 btc at price  1679.5400 cny, order_id=73580581
    ERROR 2015-08-11 18:44:38                 common.py:  92 - RETRY for Exception: "HTTPSConnectionPool(host='api.huobi.com', port=443): Read timed out."
  WARNING 2015-08-11 18:44:38                 common.py:  98 - retry_counter=1
    ERROR 2015-08-11 18:44:40                  huobi.py:  77 - HuoBi Error: code=2, msg=没有足够的人民币
  WARNING 2015-08-11 18:44:40       arbitrage_trader.py:  42 - Trade in HuoBi     : buy      0.0900 btc at price  1679.5400 cny, order_id=-1
 CRITICAL 2015-08-11 18:44:40     arbitrage_producer.py:  49 - order_id not exists, EXIT
```

```
HuoBi Error: code=37, msg=该委托已在队列中，不能取消或修
```
```
ERROR 2015-08-10 21:29:44                 common.py:  79 - RETRY for Exception: "HTTPSConnectionPool(host='api.huobi.com', port=443): Max retries exceeded with url: /apiv3?access_key=09c77932-27624ec6-ac6e34e6-e7a34&created=1439213336&method=get_account_info&sign=5b521c80d6320eb6bcf073c819c3a87e (Caused by <class 'socket.error'>: [Errno 104] Connection reset by peer)"
```

```
ERROR 2015-08-10 21:09:15                 common.py:  79 - RETRY for Exception: "HTTPSConnectionPool(host='api.huobi.com', port=443): Max retries exceeded with url: /apiv3?access_key=09c7
    7932-27624ec6-ac6e34e6-e7a34&created=1439212090&method=get_account_info&sign=c4db4bbe2bb3c8a9b85f3fa1a1f4af26 (Caused by <class 'httplib.BadStatusLine'>: '')"
WARNING 2015-08-10 21:09:15                 common.py:  85 - retry_counter=1
```

```
CHBTC/OKCoinCN
Error during request:"('Connection broken: IncompleteRead(0 bytes read)', IncompleteRead(0 bytes read))", will EXIT
```
```
  File "/usr/lib/python2.7/threading.py", line 551, in __bootstrap_inner
    self.run()
  File "/home/ubuntu/arbitrage/arbitrage_monitor.py", line 185, in run
    adjust_status = self.asset_update_handler(False)  # TODO: return value not used here
  File "/home/ubuntu/arbitrage/arbitrage_monitor.py", line 162, in asset_update_handler
    status = self.coin_update_handler(coin, is_last)
  File "/home/ubuntu/arbitrage/arbitrage_monitor.py", line 126, in coin_update_handler
    adjust_status = self.adjust_trade(trade_catalog, coin_change_amount)
  File "/home/ubuntu/arbitrage/arbitrage_monitor.py", line 142, in adjust_trade
    t1_res = monitor_t1.adjust_trade()
  File "/home/ubuntu/arbitrage/arbitrage_trader.py", line 122, in adjust_trade
    trade_price = common.adjust_price(self.catalog, self.price)
  File "/home/ubuntu/arbitrage/common.py", line 52, in adjust_price
    new_price = price * (1 - config.ADJUST_PERCENTAGE)
TypeError: can't multiply sequence by non-int of type 'float'

```

```
Traceback (most recent call last):
  File "/usr/lib/python2.7/threading.py", line 810, in __bootstrap_inner
    self.run()
  File "/home/user1/Dropbox/FinTech/arbitrage/arbitrage_producer.py", line 34, in run
    self.process_arbitrage()
  File "/home/user1/Dropbox/FinTech/arbitrage/arbitrage_producer.py", line 136, in process_arbitrage
    info_list = list(executor.map(lambda plt: plt.ask_bid_list(1), self.plt_list))
  File "/usr/local/lib/python2.7/dist-packages/concurrent/futures/_base.py", line 579, in result_iterator
    yield future.result()
  File "/usr/local/lib/python2.7/dist-packages/concurrent/futures/_base.py", line 403, in result
    return self.__get_result()
  File "/usr/local/lib/python2.7/dist-packages/concurrent/futures/thread.py", line 55, in run
    result = self.fn(*self.args, **self.kwargs)
  File "/home/user1/Dropbox/FinTech/arbitrage/arbitrage_producer.py", line 136, in <lambda>
    info_list = list(executor.map(lambda plt: plt.ask_bid_list(1), self.plt_list))
  File "/home/user1/Dropbox/FinTech/arbitrage/bitbays.py", line 141, in ask_bid_list
    assert (asks[-1][0] + config.MINOR_DIFF >= bids[0][0])
AssertionError
```

## hosts
- 121.199.251.136 www.okcoin.cn
- 119.28.48.217   okcoin.cn
