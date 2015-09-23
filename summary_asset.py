#!/usr/bin/env python
import concurrent
import concurrent.futures
import arbitrage_driver
from asset_info import AssetInfo
import excepts
import logging_conf
import plt_conf

logging_conf.init_logger()

enabled = plt_conf.get_key_from_data('Enabled')

enabled_plt = [arbitrage_driver.select_plt_dict[plt]() for plt in enabled]

with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    asset_info = executor.map(lambda plt: str(AssetInfo(plt)), enabled_plt)

report = '\n'.join(asset_info)
excepts.send_msg(report)
