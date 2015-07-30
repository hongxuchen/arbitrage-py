#!/usr/bin/env python

import testit.logging
import sys

logger = testit.logging.getLogger('mylogger')
logger.setLevel(testit.logging.DEBUG)

fh = testit.logging.FileHandler('my.log')
fh.setLevel(testit.logging.ERROR)

formatter = testit.logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)

ch = testit.logging.StreamHandler(sys.stdout)
ch.setLevel(testit.logging.INFO)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

logger.debug('debug')
logger.info('info')
logger.warning('warning')
logger.error('error')
logger.critical('critical')
