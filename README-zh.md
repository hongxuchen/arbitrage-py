# 任务分工

1. Producer 发现差价(`ask_bid`), 并按照ask1/bid1进行交易(`trade`)
1. Consumer 超过一定时限后检查Producer所进行交易对是否完成(`order`), 有则调整
1. Monitor 负责监控全局资产状况，如果比特币数量超过一定限度波动则全局调整使得在一定范围内


# Producer

1. 发现bid1-ask1>D>0, 或考虑单词总收益(price, amount), 甚至历史因素  
1. 买价卖价需要适当调整(根据D或bid1-ask1), 以减少交易失败次数  
1. 数量由下面3个因素共同决定   
    1. 不超过aks/bid最小值   
    1. 不超过每个平台的资产购买(fiat)卖出(btc)能力   
    1. 不小于单个最小限额(Ma, Mb)的最大值M, 假定Ma<Mb   
1. 和Consumer共享一个队列, 当交易完成后将交易ID及price, amount信息(`TradeInfo`)结对给Consumer  

# Consumer
1. 只要发现剩余量A1（A2）, 立即取消(`cancel`); 取消后实际平台剩余量`[0, A1]`, `[0, A2]`。若`cancel`返回ID不存在错误, 剩余量更新为零; 但无法准确获知具体剩余量 // AAA  
1. 记A=A1-A2, 考虑资产能力和平台最小额度限制之后, 决定买入或卖出(catelog)  
    1. A>0, 需买入  
    1. A<0, 需卖出  
1. 价格选用远位价格, 极大减小交易失败可能  
1. 选用不同策略, 决定在哪个平台交易, 考虑如下因素  
    1. 两个交易平台的ask1/bid1信息; 缺陷: 通常多两次request  
        1. A>0, buy, 倾向于ask小的  
        1. A<0, sell, 倾向于bid大的  
    1. 交易数量: 当Ma<A<Mb时倾向于Ma对应平台; 否则在Mb所在平台需双向交易方可  
    1. 倾向于网络速度快的  
        1. 长期经验总结  
        1. 交易未完成原因分析  
    1. 倾向于波动差的(次要)  

## AdjustTrade算法

    // amount>=1
    // type 属于 {buy, sell}
    AdjustTrade(p, type, amount)
      M = p.M // 交易平台p的下限
      if amount == 0:
        no_trade_and_return
      wait_for_asset_times = 0  // 因为CNY或BTC不够的等待次数
      while amount < M: // 需要交易和反向交易
        // asset.amount 每次从交易平台读取,一直会改变
        if asset.amount > amount+M:
          Ta={p, type, amount+M}
          Tb={p, ~type, M}
        else:
          wait_for_asset_time += 1
          if wait_for_asset_times > ASSET_WAIT_TIMES: // 事先定义好的次数
            // 等待了一定次数后仍然不够交易, 返回状态, 可能的话另一个平台交易 // BBB
            no_trade_and_notify
      if amount >= M:
        t={p, type, amount}
        
# Monitor

1. 调整由下面原因引起的比特币数量差异  
    1. 浮点数受精确度影响不能够足够准确  
        1. 平台返回的json数据不够准确  
        1. 本地精度问题  
    1. Consumer取消之前有新交易，导致剩余数量没有及时更新(即AAA)  
    1. Consumer在尝试两个平台的调整交易之后均失败(即BBB)  
2. 适时更新UI资产显示  


# OKCoin错误码

```
10001	用户请求过于频繁
10002	系统错误
10009	订单不存在
10010	余额不足
10011	买卖的数量小于BTC/LTC最小买卖额度
10014	下单价格不得≤0或≥1000000
10015	下单价格与最新成交价偏差过大
10016	币数量不足
10023	获取最新成交价错误
10035	可用BTC/LTC不足
503	用户请求过于频繁(Http)
```
