#!/usr/bin/env python
from __future__ import print_function
import sys

from PySide import QtCore, QtGui


class Worker(QtCore.QObject):
    def __init__(self, msg):
        super(Worker, self).__init__()
        self.runnning = True
        self.msg = msg

    def trade(self):
        QtCore.QThread.msleep(100)
        print('{} TRADE in {:>20}'.format(self.msg, QtCore.QThread.currentThreadId()))

    def cancel(self):
        QtCore.QThread.msleep(100)
        print('{} cancel in {:>20}'.format(self.msg, QtCore.QThread.currentThreadId()))


class CancelThread(QtCore.QThread):
    def __init__(self, w):
        super(CancelThread, self).__init__()
        self.worker = w

    def run(self, *args, **kwargs):
        self.worker.cancel()


class TradeThread(QtCore.QThread):
    def __init__(self, worker):
        super(TradeThread, self).__init__()
        self.worker = worker

    def run(self, *args, **kwargs):
        self.worker.trade()


class InitThread(QtCore.QThread):
    def __init__(self, parent):
        super(InitThread, self).__init__(parent)
        self.w1 = Worker('worker1')
        ct1 = CancelThread(self.w1)
        tt1 = TradeThread(self.w1)
        self.w2 = Worker('worker2')
        ct2 = CancelThread(self.w2)
        tt2 = TradeThread(self.w2)
        tt1.start()
        tt2.start()
        ct1.start()
        ct2.start()
        tt1.wait()
        tt2.wait()
        ct1.wait()
        ct2.wait()


class MyWin(QtGui.QWidget):
    def __init__(self):
        super(MyWin, self).__init__()
        self.mythread = InitThread(self)
        self.mythread.start()

    def closeEvent(self, *args, **kwargs):
        self.mythread.quit()
        self.mythread.wait()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    win = MyWin()
    win.show()
    sys.exit(app.exec_())
