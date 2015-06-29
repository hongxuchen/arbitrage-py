# known issues

## okcoin.py:49

* 'Connection aborted.', gaierror(-5, 'No address associated with hostname'
* 'ConnectionError' ('Connection aborted.', BadStatusLine(""''''"))
* 'EOF occurred in violation of protocol (_ssl.c:581)'
* 'Connection aborted.', error(110, 'Connection timed out'


# monitor pending

## Pre-condition
- 2 platforms: P1, P2
- minimal trade amount: M1, M2; M = min{M1, M2}； suppose M1 < M2, M = M1
- trade information: t={P, type, amount}; type is "buy" or "sell", amount is *remaining* amount
- Current trade pair: <t1, t2>
- A1 = t1.amount, A2 = t2.amount, A_min={A1, A2}' A_min>0

## strategy
- Cancel t1, t2
- market-price trade with remaing amount:
    - A1<M2, A2<M2: A=A1-A2, AdjustTrade(P1, type, |A|) where:
      - A<0: type=~t1.type
      - A>0: type=t1.type
    - A1<M2, A2>=M2: t21={P2, t2.type, A2}, AdjustTrade(P1, t1.type, A1)
    - A1>=M2: A=A1-A2, AdjustTrade(P1, t1.type, A)

## AdjustTrade Algorithm
// amount>=0
// type in {buy, sell}
AdjustTrade(p, type, amount)
  M = p.M // minimal amount
  if amount == 0: no_trade_and_return
  wait_for_asset_times = 0
  while amount < M: // have to split
    // asset.amount can be changed each time 
    if asset.amount > amount+M:
      Ta={p, type, amount+M}
      Tb={p, ~type, M}
    else:
      wait_for_asset_time += 1
      if wait_for_asset_times > ASSET_WAIT_TIMES: // pre-defined
        // after waiting for several times because of short of asset
        no_trade_and_return
  if amount >= M:
    t={p, type, amount}
    
## post-condition
No pending trade
