#!/usr/bin/env python

from PySide import QtGui
import sys
import common
from ui_common import centerized


class SelectGB(QtGui.QGroupBox):
    def __init__(self, available_plt, enabled_plt, parent=None, step=1.0, min_amount=0.01):
        super(SelectGB, self).__init__(parent)
        layout = QtGui.QVBoxLayout()
        for e in available_plt:
            plt = QtGui.QCheckBox(e)
            if e in enabled_plt:
                plt.setChecked(True)
            plt.setDisabled(1)
            layout.addWidget(plt)
        self.setLayout(layout)
        self.setTitle('platforms')


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    available_plt = common.get_key_from_file('Available')
    enabled_plt = common.get_key_from_file('Enabled')
    widget = SelectGB(available_plt, enabled_plt)
    widget.move(centerized(widget))
    widget.show()
    sys.exit(app.exec_())
