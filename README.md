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

## hosts
121.199.251.136 www.okcoin.cn
119.28.48.217   okcoin.cn
52.4.235.229    bitbays.com
106.38.234.116  api.huobi.com
103.10.87.2     huobi.com
112.74.124.237  trade.chbtc.com
112.74.124.237  api.chbtc.com
