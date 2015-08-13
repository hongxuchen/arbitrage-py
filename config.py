okcoin_cn_info = {
    'domain': 'https://www.okcoin.cn/api/v1',
    'symbol': 'cny'
}

huobi_info = {
    'domain': 'https://api.huobi.com/apiv3',
    'symbol': 'cny',
    'data_domain': 'http://api.huobi.com/staticmarket'
}

okcoin_com_info = {
    'domain': 'https://www.okcoin.com/api/v1',
    'symbol': 'usd'
}

bitbays_info = {
    'domain': 'https://bitbays.com/api/v1',
    'symbol': 'cny'
}

chbtc_info = {
    'domain': 'https://trade.chbtc.com/api/',
    'data_domain': 'http://api.chbtc.com/data/',
    'symbol': 'cny'
}

itbit_info = {
    'domain': 'https://beta-api.itbit.com/v1/',
    'symbol': 'XBTUSD'
}

DISPLAY_PRECISION = 6
MINOR_DIFF = 10.0 ** (-DISPLAY_PRECISION)
INVALID_ORDER_ID = -1

# FIXME
ADJUST_PERCENTAGE = 0.0095
ASSET_WAIT_MAX = 1
ASSET_FOR_TRAID_DIFF = 0.0005

CONSUMER_TIMEOUTS = 1.0

TIMEOUT = 3.0
RETRY_MAX = 80
RETRY_SECONDS = 0.012
RETRY_SLEEP_SECONDS = 10

MONITOR_FAIL_MAX = 2

COIN_EXCEED_TIMES = 3

# CONFIG
# upper_bound must > lower_bound for all platforms
PENDING_SECONDS = 4.0
MONITOR_INTERVAL_SECONDS = 3

EMAILING_INTERVAL_SECONDS = 3600

PRICE_ROUND = 2.0

MUTEX_TIMEOUTS = 3.0

####################################################################

exceed_max = {
    'btc': 0.001,
    'ltc': 0.01
}

HuoBi_Price_Precision = 2
TRADE_PRECISION = 4
SLEEP_SECONDS = 0.4

upper_bound = {
    'btc': 0.6,
    'ltc': 30
}

# Semantics: when Pa.ask1 + diff_dict[Pa][Pb] <= Pb.bid1, (buy at Pa, sell at Pb)
# NOTE: if price(Pa) > price(Pb) for most of the time, it's more likely to (sell at Pa, buy at Pb);
# we should make btc_diff_dict[Pa][Pb] < diff_dict[Pb][Pa] so that (buy at Pa, sell at Pb) will be easier
btc_diff_dict = {
    'BitBays': {
        'CHBTC': 0.45, 'HuoBi': 0.45, 'OKCoinCN': 0.45
    },
    'CHBTC': {
        'BitBays': 0.45, 'HuoBi': 0.75, 'OKCoinCN': 0.75
    },
    'OKCoinCN': {
        'BitBays': 0.45, 'CHBTC': 0.75, 'HuoBi': 0.75
    },
    'HuoBi': {
        'BitBays': 0.45, 'CHBTC': 0.00, 'OKCoinCN': 0.00
    }
}

ltc_diff_dict = {
    'OKCoinCN': {
        'CHBTC': 0.05, 'HuoBi': 0.06
    },
    'HuoBi': {
        'CHBTC': 0.05, 'OKCoinCN': 0.02
    },
    'CHBTC': {
        'HuoBi': 0.05, 'OKCoinCN': 0.02
    }
}

diff_dict = {
    'btc': btc_diff_dict,
    'ltc': ltc_diff_dict
}
