
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.Qt import Qt

class MLineEdit(QLineEdit):
    def __init__(self, parent = None):
        QLineEdit.__init__(self, parent)

    keyUpPressed = pyqtSignal()
    keyDownPressed = pyqtSignal()
    keyEscapePressed = pyqtSignal()
    gotFocus = pyqtSignal()
    lostFocus = pyqtSignal()

    def focusInEvent(self, event):
        print 'edit got focus'
        self.gotFocus.emit()

    def focusOutEvent(self, event):
        print 'edit lost focus'
        self.lostFocus.emit()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            self.keyUpPressed.emit()
            event.accept()
        elif event.key() == Qt.Key_Down:
            self.keyDownPressed.emit()
            event.accept()
        elif event.key() == Qt.Key_Escape:
            self.keyEscapePressed.emit()
            event.accept()
        else:
            QLineEdit.keyPressEvent(self, event)
