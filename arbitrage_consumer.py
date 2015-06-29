#!/usr/bin/env python

from PySide import QtCore


class ArbitrageConsumer(QtCore.QThread):
    def __init__(self, trade_queue):
        super(ArbitrageConsumer, self).__init__(trade_queue)
        self.running = False
