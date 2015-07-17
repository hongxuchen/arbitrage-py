#!/usr/bin/env python

from __future__ import print_function
import threading
import time

from PySide.QtCore import *
from PySide.QtGui import *

NUM = 5

mutex = threading.Lock()


class Item(object):
    def __init__(self, seed):
        super(Item, self).__init__()
        self.val = seed % NUM

    def update(self, positive):
        if positive:
            self.val = (self.val + 1) % NUM
        else:
            self.val -= 1

    def __repr__(self):
        return str(self.val)


class Consumer(QThread):
    def __init__(self, trade_queue):
        super(Consumer, self).__init__()
        self.worklist = trade_queue
        self.running = True

    def do_work(self):
        for w in self.worklist:
            w[0].update(True)
            w[1].update(False)
            if w[0].val == 0 or w[1].val == 0:
                self.worklist.remove(w)
        print('consumer {}'.format(self.worklist))

    def run(self):
        while self.running or self.worklist:
            QThread.msleep(500)
            mutex.acquire(True)
            self.do_work()
            mutex.release()


class Producer(QThread):
    def __init__(self, trade_queue):
        super(Producer, self).__init__()
        self.running = True
        self.worklist = trade_queue

    def do_work(self):
        print('producer do work')
        now = int(time.time())
        trade_pair = (Item(now * 3), Item(now * 5))
        self.worklist.append(trade_pair)

    def run(self):
        while self.running:
            QThread.msleep(500)
            mutex.acquire(True)
            self.do_work()
            mutex.release()


class Widg(QWidget):
    def __init__(self):
        super(Widg, self).__init__()
        worklist = []
        self.consumer = Consumer(worklist)
        self.producer = Producer(worklist)
        self.startStopButton = QPushButton()
        self.startStopButton.setText('Go!')
        self.startStopButton.pressed.connect(self.startStopThread)
        hBoxLayout = QHBoxLayout()
        hBoxLayout.addWidget(self.startStopButton)

        self.setLayout(hBoxLayout)
        self.threadRunning = False

    def startThread(self):
        assert (self.threadRunning is False)
        self.threadRunning = True
        self.producer.running = True
        self.producer.start()
        self.consumer.running = True
        self.consumer.start()

    def stopThread(self):
        assert (self.threadRunning is True)
        self.threadRunning = False
        self.producer.running = False
        self.consumer.running = False

    def closeEvent(self, event):
        if self.threadRunning:
            self.stopThread()
            self.producer.wait()
            self.consumer.wait()

    def startStopThread(self):
        if self.threadRunning is False:
            self.startThread()
            self.startStopButton.setText('Stop!')
        else:
            self.stopThread()
            self.startStopButton.setText('Go!')


if __name__ == "__main__":
    from sys import argv

    qApp = QApplication(argv)
    widg = Widg()
    widg.show()
    qApp.exec_()
