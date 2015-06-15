#!/usr/bin/env python

from PySide.QtCore import *
from PySide.QtGui import *


class DoStuffPeriodically(QThread):
    def __init__(self, parent):
        super(DoStuffPeriodically, self).__init__(parent)

    def doWork(self):
        # ... do work, post signal to consumer
        print "Start work"
        for i in range(0, 100):
            print "work %i" % i
            QThread.msleep(10)
        print "Done work"
        return

    def run(self):
        """ Setup "pullFiles" to be called once a second"""
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.doWork)
        self.timer.start(4000)
        self.exec_()


class Widg(QWidget):
    def __init__(self):
        super(Widg, self).__init__()
        self.thread = DoStuffPeriodically(self)
        self.startStopButton = QPushButton()
        hBoxLayout = QHBoxLayout()
        hBoxLayout.addWidget(self.startStopButton)
        self.startStopButton.pressed.connect(self.startStopThread)
        self.setLayout(hBoxLayout)
        self.threadRunning = False

    def startStopThread(self):
        if self.threadRunning:
            print "Stopping..."
            self.thread.exit(0)
            self.threadRunning = False
            print "Stopped"
        else:
            print "Starting..."
            self.thread.start()
            self.threadRunning = True
            print "Started"


if __name__ == "__main__":
    from sys import argv

    qApp = QApplication(argv)
    widg = Widg()
    widg.show()
    qApp.exec_()
