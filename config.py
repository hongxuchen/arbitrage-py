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

ASJUST_PERCENTAGE = 0.1
ASSET_WAIT_MAX = 1
ASSET_FOR_TRAID_DIFF = 0.0005

CONSUMER_SLEEP_SECONS = 0.5

TIMEOUT = 3.0
RETRY_MAX = 8
RETRY_SECONDS = 0.012
REQUEST_EXCEPTION_WAIT_SECONDS = 10

MONITOR_FAIL_MAX = 2

BTC_EXCEED_COUNTER = 3
BTC_DIFF_MAX = 0.001

HuoBi_Precision = 2
SLEEP_SECONDS = 0.34

# CONFIG
## upper_bound must > lower_bound for all platforms
UPPER_BOUND = 0.6
PENDING_SECONDS = 5.0
MONITOR_INTERVAL_SECONDS = 3

EMAILING_INTERVAL_SECONDS = 3600

# when Pa.ask1 + buy_diff <= Pb.bid1, buy at Pa, sell at Pb
diff_dict = {
    'BitBays': {
        'OKCoinCN': 0.45, 'HuoBi': 0.45
    },
    'OKCoinCN': {
        'BitBays': 0.45, 'HuoBi': 0.75
    },
    'HuoBi': {
        'OKCoinCN': 0.15, 'BitBays': 0.45
    }
}
