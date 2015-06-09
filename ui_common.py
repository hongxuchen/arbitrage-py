#!/usr/bin/env python
from PySide import QtGui


def centerized(widget):
    return QtGui.QDesktopWidget().availableGeometry().center() - widget.frameGeometry().center()

def fill_table(tbl, row, col, text):
    item = QtGui.QTableWidgetItem(str(text))
    item.setTextAlignment(2)
    tbl.setItem(row, col, item)
