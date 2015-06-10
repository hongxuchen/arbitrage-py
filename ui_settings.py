#!/usr/bin/env python

import sys

from PySide import QtGui

from ui_common import centerized


class SettingGB(QtGui.QGroupBox):
    def __init__(self, parent=None, step=1.0, min_amount=0.01):
        super(SettingGB, self).__init__(parent)
        diff_label = QtGui.QLabel('Differences')
        diff_button = QtGui.QDoubleSpinBox(self)
        diff_button.setSingleStep(step / 2)
        diff_button.setMinimum(step)
        diff_button.setValue(0)
        min_amount_label = QtGui.QLabel('Min Amount')
        min_amount_button = QtGui.QDoubleSpinBox(self)
        min_amount_button.setSingleStep(min_amount)
        min_amount_button.setMinimum(min_amount)
        min_amount_button.setValue(min_amount)
        layout = QtGui.QGridLayout()
        layout.addWidget(diff_label, 0, 0)
        layout.addWidget(diff_button, 0, 1)
        layout.addWidget(min_amount_label, 1, 0)
        layout.addWidget(min_amount_button, 1, 1)
        self.setLayout(layout)
        self.setTitle('settings')


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    widget = SettingGB()
    widget.move(centerized(widget))
    widget.show()
    sys.exit(app.exec_())
