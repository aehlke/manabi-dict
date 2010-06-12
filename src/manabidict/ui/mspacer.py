
from PyQt4 import uic
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.Qt import Qt

class MSpacer(QWidget):

    def __init__(self, parent=None):
        '''
        '''
        QWidget.__init__(self, parent)
        
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setSizePolicy(size_policy)
        
    def sizeHint(self):
        return QSize(1, 1)
