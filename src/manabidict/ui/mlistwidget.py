from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.Qt import Qt
from PyQt4.QtWebKit import QWebView, QWebSettings

class MListWidget(QListWidget):
    '''Allows setting HTML items instead of just text.
    This is a nasty hack, unfortunately - thanks to some unfortunate Qt API decicions (QLabel inconsistently hides certain internals :( )
    '''
    gainedFocus = pyqtSignal()
    lostFocus = pyqtSignal()

    def __init__(self, parent = None):
        QListWidget.__init__(self, parent)

        self._htmlItemLabel = None
        self._htmlItemWidget = None
        self._htmlItemWidgetFinishedLoading = False

        self._prepHtmlItemWidget()

    #def focusInEvent(self, event):
        #self.gainedFocus.emit()
        #event.accept()
        #QListWidget.focusInEvent(self, event)
    
    #def focusOutEvent(self, event):
        #self.lostFocus.emit()
        #event.accept()
        #QListWidget.focusOutEvent(self, event)

    #def event(self, event):
        #if event.type() == QEvent.InputMethod:
            #print 'ionout pmethod'
            #self.inputMethodEvent(event)
        #elif event.type() == QEvent.KeyPress:
            #print 'key pressed'
        #return QListWidget.event(self, event)

    #@pyqtSignature('QInputMethodEvent')
    #def inputMethodEvent(self, event):
        #print 'custom input event!'
        #print event

    def event(self, event):
        '''Intercept enter/return presses.
        '''
        if event.type() == QEvent.KeyPress:
            key_press = QKeyEvent(event)
            if key_press.key() in [Qt.Key_Enter, Qt.Key_Return]:
                self.returnPressed.emit()
                return True
        return QListWidget.event(self, event)

    def _htmlItemWidgetLoadedSignal(self, ok):
        self._htmlItemWidgetFinishedLoading = True

    def _prepHtmlItemWidget(self):
        self._htmlItemWidget = QWebView()
        hw = self._htmlItemWidget

        hw.loadFinished.connect(self._htmlItemWidgetLoadedSignal)

        #TODO hw.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        #hw.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # font
        ws = hw.settings()
        font_size = self.font().pointSize()
        ws.setFontSize(QWebSettings.DefaultFontSize, font_size)
        ws.setFontFamily(QWebSettings.StandardFont, self.font().family())

        # transparency
        palette = hw.palette()
        palette.setBrush(QPalette.Base, Qt.transparent)
        hw.page().setPalette(palette)
        hw.setAttribute(Qt.WA_OpaquePaintEvent, False)

        # better rendering
        hw.setRenderHint(QPainter.Antialiasing, True)
        hw.setRenderHint(QPainter.TextAntialiasing, True)
        hw.setRenderHint(QPainter.SmoothPixmapTransform, True)
        hw.setRenderHint(QPainter.HighQualityAntialiasing, True)

        hw.setHtml(u'')
        h = font_size + 6
        hw.setFixedHeight(h)
        


    def addHtmlItem(self, html, data):
        '''Adds a new QTextEdit widget containing the given HTMl as an item in the list.
        '''
        item = QListWidgetItem()
        item.setData(Qt.UserRole, data)
        self.addItem(item)
        item.setSizeHint(self._htmlItemWidget.frameSize())

        label = QLabel()
        label.setTextInteractionFlags(Qt.NoTextInteraction)

        html = u'<html><body style="margin:0px 0px 0px 4px">{0}</body></html>'.format(html)

        if '<img' in html:
            self._htmlItemWidgetFinishedLoading = False
            self._htmlItemWidget.setHtml(html)

            pm = QImage(self._htmlItemWidget.size(), QImage.Format_ARGB32)
            pm.fill(Qt.transparent)

            # wait for it to finish loading, then render
            q_app = QApplication.instance()
            while not self._htmlItemWidgetFinishedLoading:
                q_app.processEvents(QEventLoop.WaitForMoreEvents | QEventLoop.ExcludeUserInputEvents)
            
            self._htmlItemWidget.render(pm, flags=QWidget.DrawChildren)

            label.setPixmap(QPixmap.fromImage(pm))
        else:
            label.setText(html)
        
        self.setItemWidget(item, label)

