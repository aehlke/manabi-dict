from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QLinearGradient, QColor, QPainter, QBrush
from PyQt4.QtCore import QPoint, QPointF, QRect, QSize
from PyQt4.Qt import Qt

class MSplitterHandle(QtGui.QSplitterHandle):
    def __init__(self, orientation, parent):
        QtGui.QSplitterHandle.__init__(self, orientation, parent)
        self.setCursor(Qt.SplitHCursor) # Qt.SizeBDiagCursor

    #def resizeEvent(self, event):
       #if (self.orientation() == QtCore.Qt.Horizontal):
           #self.setContentsMargins(2, 0, 2, 0)
       #else:
           #self.setContentsMargins(0, 2, 0, 2)
       #QtGui.QSplitterHandle.resizeEvent(self, event)


    def paintEvent(self, e):
        '''
        Paint the horizontal handle as a gradient, paint
        the vertical handle as a line.
        '''
        painter = QPainter(self)

        topColor = QColor(145, 145, 145)
        bottomColor = QColor(142, 142, 142)
        gradientStart = QColor(252, 252, 252)
        gradientStop = QColor(223, 223, 223)

        if self.orientation() == Qt.Vertical:
            painter.setPen(topColor)
            painter.drawLine(0, 0, self.width(), 0)
            painter.setPen(bottomColor)
            painter.drawLine(0, self.height() - 1, self.width(), self.height() - 1)

            linearGrad = QLinearGradient(QPointF(0, 0), QPointF(0, height() - 3));
            linearGrad.setColorAt(0, gradientStart)
            linearGrad.setColorAt(1, gradientStop)
            painter.fillRect(QRect(QPoint(0,1), self.size() - QSize(0, 2)), QBrush(linearGrad))
        else:
            painter.setPen(topColor);
            painter.drawLine(0, 0, 0, self.height())


class MSplitter(QtGui.QSplitter):
    def __init__(self, parent=None):# orientation, parent):
        QtGui.QSplitter.__init__(self, parent)
        if self.orientation() == Qt.Vertical:
            self.setHandleWidth(1)
            self.setChildrenCollapsible(False)

    def createHandle(self):
        return MSplitterHandle(self.orientation(), self)

    def sizeHint(self):
        parent = super(MSplitter, self).sizeHint()
        if self.orientation() == Qt.Vertical:
            return parent + QSize(0, 3)
        else:
            return QSize(1, parent.height())

