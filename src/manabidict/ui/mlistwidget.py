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

    def focusInEvent(self, event):
        self.gainedFocus.emit()
        event.accept()
    
    def focusOutEvent(self, event):
        self.lostFocus.emit()
        event.accept()

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
        h = font_size + 4
        hw.setFixedHeight(h)
        



    def addHtmlItem(self, html, data):
        '''Adds a new QTextEdit widget containing the given HTMl as an item in the list.
        '''
        item = QListWidgetItem()
        item.setData(Qt.UserRole, data)
        self.addItem(item)

        html = u'<html><body style="margin:0px 0px 0px 4px">{0}</body></html>'.format(html)
        self._htmlItemWidgetFinishedLoading = False
        self._htmlItemWidget.setHtml(html)

        pm = QImage(self._htmlItemWidget.size(), QImage.Format_ARGB32)
        pm.fill(Qt.transparent)

        # wait for it to finish loading, then render
        q_app = QApplication.instance()
        while not self._htmlItemWidgetFinishedLoading:
            q_app.processEvents(QEventLoop.WaitForMoreEvents | QEventLoop.ExcludeUserInputEvents)
        
        self._htmlItemWidget.render(pm, flags=QWidget.DrawChildren)

        item.setSizeHint(self._htmlItemWidget.frameSize())

        label = QLabel()
        label.setTextInteractionFlags(Qt.NoTextInteraction)

        label.setPixmap(QPixmap.fromImage(pm))
        
        self.setItemWidget(item, label)

