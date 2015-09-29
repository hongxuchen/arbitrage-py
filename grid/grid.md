# property
* price in buy_grid decreases, prior pending => succ pending
* price in sell_grid increases, prior pending => succ pending
* min(sell_grid) > max(buy_grid)
* one grid slot contains >=1 order(s), linked to ...
 
# Data Structure
buy_grid_list: element: (price, list(order_id)
sell_grid_list: element: (price, list(order_id))

# Algorithm

* init grid:
```
bug_grid_list[i] buys AMOUNT at price PRICE(i); price decreases
```

* Different from arbitrage, this should always be server oriented