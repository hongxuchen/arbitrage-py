okcoin_cn_info = {
    'domain': 'https://www.okcoin.cn/api/v1',
    'symbol': 'cny'
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

precision = 6
minor_diff = 10.0 ** (-precision)

## upper_bound must > lower_bound for all platforms
upper_bound = 0.02

arbitrage_diff = 0.9

PENDING_SECONDS = 5.0
adjust_percentage = 0.1
ASSET_WAIT_MAX = 1
ASSET_FOR_TRAID_DIFF = 0.0005

CONSUMER_SLEEP_MILLISECONS = 500

request_timeout = 3.0
RETRY_MAX = 8
RETRY_MILLISECONDS = 100

INVALID_ORDER_ID = -1

monitor_interval_seconds = 3

BTC_DIFF_MAX = 0.001
BTC_EXCEED_COUNTER = 3

verbose = False
