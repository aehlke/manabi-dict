from PyQt4 import QtGui, QtCore
from PyQt4.Qt import Qt

class MCornerSpacer(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.paint_top_line = True

    def paintEvent(self, e):
        painter = QtGui.QPainter(self)
        color = QtGui.QColor(0xe0, 0xe0, 0xe0, 255)
        painter.setPen(color)
        painter.drawLine(0, 0, 0, self.height())


