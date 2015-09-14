#!/usr/bin/env python
import concurrent
import concurrent.futures
import arbitrage_driver
from asset_info import AssetInfo
import common

common.init_logger()

enabled = common.get_key_from_data('Enabled')

enabled_plt = [arbitrage_driver.select_plt_dict[plt]() for plt in enabled]

with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    asset_info = executor.map(lambda plt: str(AssetInfo(plt)), enabled_plt)

report = '\n'.join(asset_info)
common.send_msg(report)
