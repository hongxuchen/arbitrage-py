import os

root_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')
res_dir = os.path.join(root_dir, 'res')
settings_dir = os.path.join(root_dir, 'settings')
render_file = 'render.html'

# TODO add abnormal.html
abnormal_file = 'abnormal-zh.html'

####################################################################

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36'

DISPLAY_PRECISION = 6
MINOR_DIFF = 10.0 ** (-DISPLAY_PRECISION)
INVALID_ORDER_ID = -1

INVALID_INDEX = -1

# FIXME huobi requires that 0.1btc transaction cannot overrange 0.01
# both used for consumer/monitor
ADJUST_PERCENTAGE = 0.008

ASSET_WAIT_MAX = 3
ASSET_FOR_TRAID_DIFF = 0.0005

CONSUMER_TIMEOUTS = 1.0

REQUEST_TIMEOUT = 3.0
RETRY_MAX = 80
RETRY_SLEEP_SECONDS = 10
RATE_EXCEED_SLEEP_SECONDS = 1

COIN_EXCEED_TIMES = 2

# CONFIG
# upper_bound must > lower_bound for all platforms
PENDING_SECONDS = 3.0
MONITOR_INTERVAL_SECONDS = 3

PRICE_ROUND = 3.0

RETRY_SECONDS = 0.04

AMOUNT_PERCENT = 1.0
HUOBI_PRICE_PRECISION = 2

# TODO: OKCoin only supports 3; but bitbays and huobi supports 4
TRADE_PRECISION = 3

####################################################################

upper = 1544.4
grid_range = upper - 15, upper

grid_cancel_duration = 4800
grid_buy_sell_diff = 0.15
grid_price_diff = 3
grid_order_amount = 0.011

AVOID_TIMEOUT = True

####################################################################

# TODO should specify queue size

emailing_interval_seconds = 3600
ARBITRAGE_NUM = 10
ADJUST_RATIO = 0.4

monitor_fail_max = 2

exceed_max_dict = {
    'btc': 0.001,
    'ltc': 0.01
}
upper_bound = {
    'btc': 0.4,
    'ltc': 30
}

language = 'zh'

grid_cancel_all = True
grid_sleep_seconds = 1.0

# sleep seconds, to avoid API too frequently
sleep_seconds = 1.0

# Semantics: when Pa.ask1+diff_dict[Pa][Pb]<=Pb.bid1, { buy at Pa, sell at Pb }
# Tips: if price(a)<price(b) for most of the time, makes diff_dict[a][b]>diff_dict[b][a]
# Example: price(HuoBi)<price(OKCoinCN), makes btc_diff_dict['HuoBi']['OKCoinCN']>btc_diff_dict['OKCoinCN']['HuoBi']
btc_diff_dict = {
    'BitBays': {
        'CHBTC': 0.45, 'HuoBi': 2.0, 'OKCoinCN': 2.0
    },
    'CHBTC': {
        'BitBays': 0.45, 'HuoBi': 0.75, 'OKCoinCN': 0.75
    },
    'OKCoinCN': {
        'BitBays': 2.0, 'CHBTC': 0.75, 'HuoBi': -4.0
    },
    'HuoBi': {
        'BitBays': 2.0, 'CHBTC': 0.00, 'OKCoinCN': 10.0
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

######################
OKCOIN_LEVERAL_RATE = 20
