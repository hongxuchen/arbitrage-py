#!/usr/bin/env python
from PySide import QtCore


class ArbitrageProducer(QtCore.QThread):
    def __init__(self, trade_queue):
        super(ArbitrageProducer, self).__init__(trade_queue)
        self.running = False
