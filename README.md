# known issues
* okcoin sometimes may return {} data, known for `ask_bid_list`, `order_info`
* not afford to buy
* HuoBi Error: code=37, msg=该委托已在队列中，不能取消或修

# TODO
* main thread works as a server
* [FATAL] monitor adjust still may 'cannot afford' so that it causes long-term imbalance
reverse the fiat amount for further trade. The net strategy is that we can change "diff".
* calculate the probabilities
    - request time
    - failed frequency
    - ask/bid diff times w.r.t. certain amount
    - profits per day
* profits against original
* order/cancel frequently for one platform; when completed, reverse trade on another platform
* Deal with common.py init issue
* force implementation
* Monitor gets starvation
* use market buy/sell to avoid connection issues

## hosts
121.199.251.136 www.okcoin.cn
119.28.48.217   okcoin.cn
52.4.235.229    bitbays.com
106.38.234.116  api.huobi.com
103.10.87.2     huobi.com
112.74.124.237  trade.chbtc.com
112.74.124.237  api.chbtc.com



# OKCoin错误码

```
10001   用户请求过于频繁
10002   系统错误
10009   订单不存在
10010   余额不足
10011   买卖的数量小于coin最小买卖额度
10014   下单价格不得≤0或≥1000000
10015   下单价格与最新成交价偏差过大
10016   币数量不足
10023   获取最新成交价错误
10035   可用coin不足
503 用户请求过于频繁(Http)
```
