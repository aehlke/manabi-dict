
from PyQt4 import QtGui, QtCore, QtWebKit
#from QtCore.QObject import connect, disconnect
#from PyQt4.QObject import connect, disconnect
from PyQt4.Qt import Qt

class MSearchToolbar(QtGui.QWidget):

    def __init__(self, parent=None):
        '''
        `user` is a QAbstractScrollArea
        '''
        QtGui.QWidget.__init__(self, parent)
        #self.setStyleSheet('background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 100, stop: 0 #dd0000, stop: 1 #D9D9D9) ')


    def paintEvent(self, e):
        super(MSearchToolbar, self).paintEvent(e)
        painter = QtGui.QPainter(self)

        # background
        gradient = QtGui.QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QtGui.QColor(0xed, 0xed, 0xed, 255))
        gradient.setColorAt(1, QtGui.QColor(0xd9, 0xd9, 0xd9, 255))
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRect(0, 0, self.width(), self.height())

        # bottom line
        line_color = QtGui.QColor(0x9f, 0x9f, 0x9f, 255)
        painter.setPen(line_color)
        painter.drawLine(0, self.height() - 1, self.width() - 1, self.height() - 1)





