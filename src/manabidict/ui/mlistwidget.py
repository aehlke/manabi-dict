
from PyQt4 import QtGui, QtCore
from PyQt4.Qt import Qt

class MListWidget(QtGui.QListWidget):
    def __init__(self, parent = None):
        QtGui.QListWidget.__init__(self, parent)

    gainedFocus = QtCore.pyqtSignal()
    lostFocus = QtCore.pyqtSignal()

    def focusInEvent(self, event):
        self.gainedFocus.emit()
        event.accept()
    
    def focusOutEvent(self, event):
        self.lostFocus.emit()
        event.accept()


