from PyQt4 import QtGui, QtCore
from PyQt4.Qt import Qt

class MScrollBar(QtGui.QScrollBar):
    def __init__(self, parent=None):
        QtGui.QScrollBar.__init__(self, parent)

    def paintEvent(self, e):
        super(MScrollBar, self).paintEvent(e)
        if self.minimum() == self.maximum():
            self._paintBottomLine()

    def _paintBottomLine(self):
        brush = self.palette().shadow()
        if self.orientation() == Qt.Vertical:
            painter = QtGui.QPainter(self)
            color = QtGui.QColor(0xe0, 0xe0, 0xe0, 255)
            painter.setPen(color)
            painter.drawLine(0, self.height() - 1, self.width(), self.height() - 1)
            #del painter
