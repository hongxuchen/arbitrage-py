import threading
import requests.exceptions as req_except

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

precision = 4
TRADING_LOGGER = 'trading_logger'
DEBUG_LOGGER = 'debug_logger'
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36'
retry_max = 10

minor_diff = 10.0 ** (-precision)


upper_bound = 0.012
lower_bound = 0.010
lower_rate = 0.5
arbitrage_diff = 0.3
PENDING_SECONDS = 2
adjust_percentage = 0.1
ASSET_WAIT_MAX = 3
ASSET_FOR_TRAID_DIFF = 0.0005

MUTEX = threading.Lock()

retry_except_tuple = (req_except.ConnectionError, req_except.Timeout, req_except.HTTPError)
exit_except_tuple = (req_except.URLRequired, req_except.TooManyRedirects)