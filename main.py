import sys

from PyQt5 import QtGui
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication)

from ui.gui import OptimizationApp

if __name__ == "__main__":
    app = QApplication(sys.argv)

    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap("ui/icon_s.png"))
    app.setWindowIcon(icon)

    font = QFont()
    font.setPointSize(16)
    app.setFont(font)

    window = OptimizationApp()
    window.show()
    sys.exit(app.exec_())
