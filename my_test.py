#!/usr/bin/env python
from __future__ import print_function
from PySide import QtCore, QtGui
import sys


class Worker1(QtCore.QObject):
    def __init__(self, msg):
        super(Worker1, self).__init__()
        self.runnning = True
        self.msg = msg

    def my_run(self):
        print('hello')
        while self.runnning:
            QtCore.QThread.msleep(100)
            print('sleep')
            print(self.msg)

class MyThread(QtCore.QThread):
    def __init__(self, parent):
        super(MyThread, self).__init__(parent)
        self.worker = Worker1('w1')
        self.thread = QtCore.QThread()
        self.thread.started.connect(self.worker.my_run)
        self.worker.moveToThread(self.thread)
        print('before')
        self.thread.start()
        print('after')



class MyWin(QtGui.QWidget):
    def __init__(self):
        super(MyWin, self).__init__()
        self.mythread = MyThread(self)
        self.mythread.start()

    def closeEvent(self, *args, **kwargs):
        self.mythread.quit()
        self.mythread.wait()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    win = MyWin()
    win.show()
    sys.exit(app.exec_())

