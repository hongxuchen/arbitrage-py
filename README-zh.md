# 监控未成交交易

## 前置条件

- 2个平台: P1, P2
- 平台最小交易下限: M1, M2; M = min{M1, M2}；假定 M1<M2, 即 M==M1
- 交易信息: t={P, type, amount}; type是"buy"或"sell", amount 是*剩下的*数量
- 当前未成交交易对: \<t1, t2>
- A1 = t1.amount, A2 = t2.amount, A\_max=max{A1, A2}, A\_max>0

## 策略
- 取消 t1, t2
- 对未成交交易进行*远位价格*交易，必须保证BTC的总量恒定；远位价格上下波动比例为pp:
    - A1<M2,A2<M2: A=A1-A2, AdjustTrade(P1, type, |A|)，这里:
      - A<0: type=~t1.type
      - A>0: type=t1.type
    - A1<M2, A2>=M2: t21={P2, t2.type, A2}, AdjustTrade(P1, t1.type, A1)
    - A1>=M2, A2>=M2: t11={P1, t2.type, A1}, t21={P2, t2.type, A2}
    - A1>=M2, A2<M2: A=A1-A2, t11=AdjustTrade(P1, t1.type, A)

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
            // 等待了一定次数后CNY/BTC仍然不够
            no_trade_and_return
      if amount >= M:
        t={p, type, amount}

## 后置条件
不再有未成交交易


# OKCoin error code

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
