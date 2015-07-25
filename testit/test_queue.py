#!/usr/bin/env python

import sys

from queue import Queue, Empty
from PySide import QtCore, QtGui


class LogReceiver(QtCore.QObject):
    mysignal = QtCore.Signal(str)

    def __init__(self, queue, *args, **kwargs):
        QtCore.QObject.__init__(self, *args, **kwargs)
        self.queue = queue

    def run(self):
        self.active = True
        while self.active:
            try:
                text = self.queue.get(timeout=1.0)
                self.mysignal.emit('text')
            except Empty:
                continue
        print('finished')


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.queue = Queue()
        self.thread = QtCore.QThread(self)
        self.receiver = LogReceiver(self.queue)
        self.receiver.moveToThread(self.thread)
        self.thread.started.connect(self.receiver.run)
        self.thread.start()

    def closeEvent(self, event):
        print('close')
        self.receiver.active = False
        self.thread.quit()
        self.thread.wait()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
