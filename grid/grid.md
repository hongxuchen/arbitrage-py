# property
* price in buy_grid decreases, prior pending => succ pending
* price in sell_grid increases, prior pending => succ pending
* min(sell_grid) > max(buy_grid)
* one grid slot contains >=1 order(s), linked to ...

* buy_grid: each time adding an order whose amount<AMOUNT, merge order if there is existing order; when this slot is empty, sell amount at corresponding sell_grid slot 
* sell_grid: when finding partial,
 
# Data Structure
buy_grid_list: element: (price, list(GridOrderInfo))
sell_grid_list: element: (price, list(GridOrderInfo))
monitor_list: list(GridOrderInfo)
partial_buy_list: (price, remaining_amount) (few elements)

# Algorithm

* init_buy:
```
bug_grid_list[i] buys AMOUNT at price PRICE(i); price decreases
```

* bought_handler
```
N: single batch orders_info number
SIZE = len(all_orders)
done_list, partial_list = get_orders_info()
sell(done_list)
update(partial_buy_list)
```

* sold_handler
```
```

* Different from arbitrage, this should always be server oriented