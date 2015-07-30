#!/usr/bin/env python

from PySide import QtGui
import sys
from ui_common import centerized


class TradingViewer(QtGui.QTextBrowser):
    def __init__(self, parent=None):
        super(TradingViewer, self).__init__(parent)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    widget = TradingViewer()
    widget.move(centerized(widget))
    widget.show()
    sys.exit(app.exec_())
