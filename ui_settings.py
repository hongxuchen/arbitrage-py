#!/usr/bin/env python

import sys

from PySide import QtGui
import config

from ui_common import centerized


class SettingGB(QtGui.QGroupBox):
    def __init__(self, parent=None, step=1.0, min_amount=0.01):
        super(SettingGB, self).__init__(parent)
        diff_label = QtGui.QLabel('Differences')
        diff_box = QtGui.QDoubleSpinBox(self)
        diff_box.setSingleStep(step / 2)
        diff_box.setMinimum(0)
        diff_box.setValue(config.arbitrage_diff)
        diff_box.setDisabled(1)
        min_amount_label = QtGui.QLabel('Min Amount')
        min_amount_box = QtGui.QDoubleSpinBox(self)
        min_amount_box.setSingleStep(min_amount)
        min_amount_box.setMinimum(min_amount)
        min_amount_box.setValue(min_amount)
        min_amount_box.setDisabled(1)
        layout = QtGui.QGridLayout()
        layout.addWidget(diff_label, 0, 0)
        layout.addWidget(diff_box, 0, 1)
        layout.addWidget(min_amount_label, 1, 0)
        layout.addWidget(min_amount_box, 1, 1)
        self.setLayout(layout)
        self.setTitle('settings')


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    widget = SettingGB()
    widget.move(centerized(widget))
    widget.show()
    sys.exit(app.exec_())
