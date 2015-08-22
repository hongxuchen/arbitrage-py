# known issues
* okcoin sometimes may return {} data, known for `ask_bid_list`, `order_info`
* not afford to buy
* HuoBi Error: code=37, msg=该委托已在队列中，不能取消或修

# TODO
* [FATAL] monitor adjust still may 'cannot afford' so that it causes long-term imbalance
reverse the fiat amount for futher trade. The net strategy is that we can change "diff".
* calculate the probabilities
    - request time
    - failed frequency
    - ask/bid diff times w.r.t. certain amount
    - profits per day
* order/cancel frequently for one platform; when completed, reverse trade on another platform
* Deal with common.py init issue
* force implementation
* Monitor gets starvation

# cases

```
CHBTC/OKCoinCN
Error during request:"('Connection broken: IncompleteRead(0 bytes read)', IncompleteRead(0 bytes read))", will EXIT
```

```
BitBays
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
121.199.251.136 www.okcoin.cn
119.28.48.217   okcoin.cn
52.4.235.229    bitbays.com
106.38.234.116  api.huobi.com
103.10.87.2     huobi.com
112.74.124.237  trade.chbtc.com
112.74.124.237  api.chbtc.com
