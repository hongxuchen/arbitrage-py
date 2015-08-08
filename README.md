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

# cases

```
     INFO 2015-08-08 14:57:57      139871572018944     arbitrage_producer.py:  50 - [Producer] acquire lock
  WARNING 2015-08-08 20:22:52      139871624259392       arbitrage_driver.py:  64 - stop trade
  WARNING 2015-08-08 20:22:53      139871624259392       arbitrage_driver.py:  46 - stopping producer
```

## hosts
- 121.199.251.136 www.okcoin.cn
- 119.28.48.217   okcoin.cn
