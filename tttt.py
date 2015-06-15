#!/usr/bin/env python
from PySide import QtCore
from PySide import QtGui


class MyWorkerThread(QtCore.QThread):
    def __init__(self):
        super(MyWorkerThread, self).__init__()

    def run(self):
        self.timer= QtCore.QTimer()
        print self.timer.thread()
        self.timer.setSingleShot(False)
        self.timer.timeout.connect(self.doWork)
        self.timer.start(1000)
        self.exec_()

    def doWork(self):
        print "Work!"

class TWin(QtGui.QMainWindow):
    def __init__(self):
        super(TWin, self).__init__()
        self.button = QtGui.QPushButton('test')




if __name__ == '__main__':
    worker = MyWorkerThread()
    worker.start()
    print('hello')
