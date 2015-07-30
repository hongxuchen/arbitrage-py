# known issues
* okcoin sometimes may return {} data, known issues for `ask_bid_list`, `order_info`
* not afford to buy on bitbays/okcoin
* exit error on Mac <-- due to QT bug?

# TODO
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
* order/cancel frequently for one platform; when completed, reverse trade on another platform
* different/dynamic diff for buy/sell
* okcoin can only preserve 3 decimal fractions for floating points

## hosts
- 121.199.251.136 www.okcoin.cn
- 119.28.48.217   okcoin.cn
