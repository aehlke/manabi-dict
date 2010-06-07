
from PyQt4 import QtGui, QtCore
from PyQt4.Qt import Qt

class MLineEdit(QtGui.QLineEdit):
    def __init__(self, parent = None):
        QtGui.QLineEdit.__init__(self, parent)

    keyUpPressed = QtCore.pyqtSignal()
    keyDownPressed = QtCore.pyqtSignal()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            self.keyUpPressed.emit()
            event.accept()
        elif event.key() == Qt.Key_Down:
            self.keyDownPressed.emit()
            event.accept()
        else:
            QtGui.QLineEdit.keyPressEvent(self, event)
