# known issues

## okcoin.py

* ' Expecting value: line 1 column 1 (char 0)'               <-- when quite slow (ping failed)

## other
* exit error on Mac <-- due to QT bug?

## cases

```
  File "/home/hongxu/Dropbox/Bitcoin/arbitrage/okcoin.py", line 230, in order_info
    info = self.api_order_info(order_id)['orders'][0]
IndexError: list index out of range
```

## hosts
- 121.199.251.136 www.okcoin.cn
- 119.28.48.217   okcoin.cn
