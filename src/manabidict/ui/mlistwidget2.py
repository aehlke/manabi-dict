from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.Qt import Qt
from PyQt4.QtWebKit import QWebView, QWebSettings
from mlistwidget import MListWidget


class ProxyLineEdit(QLineEdit):
    def __init__(self, parent=None):
        QLineEdit.__init__(self, parent)
        self.parent = parent


    def event(self, event):
        '''Redirects events to parent.
        '''
        #if event.type() == QEvent.InputMethod:
            #print 'ionout pmethod'
            #self.inputMethodEvent(event)
        if event.type() == QEvent.KeyPress:
            return self.parent.event(event)
        return QLineEdit.event(self, event)


class MListWidget2(MListWidget):
    '''Same as `MListWidget` but works with InputMethod events by way of using a hidden line edit.
    '''

    def __init__(self, parent = None):
        MListWidget.__init__(self, parent=parent)

        pw = self.proxy_widget = ProxyLineEdit(parent=self)
        pw.lower()
        pw.setAttribute(Qt.WA_MacShowFocusRect, False)

        self.setFocusPolicy(Qt.NoFocus)
        
    def focusInEvent(self, event):
        '''Shift the focus to the proxy line edit.
        '''
        print 'mlistwidget focus in'
        MListWidget.focusInEvent(self, event)
        self.proxy_widget.setFocus()
        event.accept()



