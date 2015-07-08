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

UI_TBL_COL_WIDTH = 100
UI_TBL_ROW_HEIGHT = 25

TRADING_LOGGER = 'trading_logger'
DEBUG_LOGGER = 'debug_logger'

fiat = 'cny'

precision = 4
minor_diff = 10.0 ** (-precision)

upper_bound = 0.012
lower_bound = 0.010
lower_rate = 0.5
arbitrage_diff = 0.3

PENDING_SECONDS = 3.0
adjust_percentage = 0.1
ASSET_WAIT_MAX = 3
ASSET_FOR_TRAID_DIFF = 0.0005

CONSUMER_SLEEP_MILLISECONS = 1800

RETRY_MAX = 10
RETRY_MILLISECONDS = 2000

monitor_interval_seconds = 3
