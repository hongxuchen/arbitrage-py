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

itbit_info = {
    'domain': 'https://beta-api.itbit.com/v1/',
    'symbol': 'XBTUSD'
}

fiat = 'cny'

TRADE_PRECISION = 3
DISPLAY_PRECISION = 6
MINOR_DIFF = 10.0 ** (-DISPLAY_PRECISION)
INVALID_ORDER_ID = -1

# FIXME
ASJUST_PERCENTAGE = 0.095
ASSET_WAIT_MAX = 1
ASSET_FOR_TRAID_DIFF = 0.0005

CONSUMER_SLEEP_SECONS = 0.5

TIMEOUT = 3.0
RETRY_MAX = 8
RETRY_SECONDS = 0.012
REQUEST_EXCEPTION_WAIT_SECONDS = 10

MONITOR_FAIL_MAX = 2

COIN_EXCEED_TIMES = 3

HuoBi_Precision = 2
SLEEP_SECONDS = 0.34

# CONFIG
# upper_bound must > lower_bound for all platforms
PENDING_SECONDS = 5.0
MONITOR_INTERVAL_SECONDS = 3

EMAILING_INTERVAL_SECONDS = 3600

####################################################################

UPPER_BOUND = 0.6

exceed_max = {
    'btc': 0.001,
    'ltc': 0.01
}

upper_bound = {
    'btc': 0.6,
    'ltc': 30
}

# when Pa.ask1 + buy_diff <= Pb.bid1, buy at Pa, sell at Pb
btc_diff_dict = {
    'BitBays': {
        'OKCoinCN': 0.45, 'HuoBi': 0.45
    },
    'OKCoinCN': {
        'BitBays': 0.45, 'HuoBi': 0.75
    },
    'HuoBi': {
        'OKCoinCN': 0.00, 'BitBays': 0.45
    }
}

ltc_diff_dict = {
    'OKCoinCN': {
        'HuoBi': 0.006
    },
    'HuoBi': {
        'OKCoinCN': 0.002
    }
}

diff_dict = {
    'btc': btc_diff_dict,
    'ltc': ltc_diff_dict
}
