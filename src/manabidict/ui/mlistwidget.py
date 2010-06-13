from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.Qt import Qt

class MListWidget(QListWidget):
    gainedFocus = pyqtSignal()
    lostFocus = pyqtSignal()

    def __init__(self, parent = None):
        QListWidget.__init__(self, parent)

        self._htmlItemLabel = None
        self._htmlItemWidget = None

        self._prepHtmlItemWidget()

    def focusInEvent(self, event):
        self.gainedFocus.emit()
        event.accept()
    
    def focusOutEvent(self, event):
        self.lostFocus.emit()
        event.accept()

    def _prepHtmlItemWidget(self):
        self._htmlItemWidget = QTextEdit(parent=self)
        hw = self._htmlItemWidget
        #hw.setText('test')

        hw.setFont(self.font())
        hw.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        hw.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        f = QTextFrameFormat()
        f.setMargin(0)
        f.setPadding(0)
        f.setBorder(0)
        hw.document().rootFrame().setFrameFormat(f)
        hw.viewport().setAutoFillBackground(False)

        #label.setText('<b>hello</b>')
        #label.setText('yeah<img src=":/gaiji/confused.png"><img src=":/gaiji/confused.png"><img src=":/gaiji/confused.png">'+html) #setHtml to force html
        hw.setReadOnly(True)
        hw.setFrameShape(QFrame.NoFrame)
        hw.setTextInteractionFlags(Qt.NoTextInteraction)

        font_metrics = QFontMetrics(hw.currentFont())
        h = font_metrics.height() + hw.frameWidth() * 2 + 1
        #hw.setFixedHeight(h)
        hw.setFixedHeight(18)
        hw.setFixedWidth(self.size().width() - 4)



    def addHtmlItem(self, html, data):
        '''Adds a new QTextEdit widget containing the given HTMl as an item in the list.
        '''
        item = QListWidgetItem(u'')
        item.setData(Qt.UserRole, data)
        self.addItem(item)

        self._htmlItemWidget.setHtml(html)

        pm = QImage(self._htmlItemWidget.size(), QImage.Format_ARGB32)
        #pm = QPixmap(self._htmlItemWidget.size())
        pm.fill(Qt.transparent)
        self._htmlItemWidget.viewport().render(pm, flags=QWidget.DrawChildren)

        item.setSizeHint(self._htmlItemWidget.frameSize())

        label = QLabel()
        label.setTextInteractionFlags(Qt.NoTextInteraction)

        label.setPixmap(QPixmap.fromImage(pm))
        
        self.setItemWidget(item, label)

        #self.setItemWidget(item, label)
        #self.
        #item = QtGui.QListWidgetItem(result.heading)
        #item.setData(Qt.UserRole, result)
        #sr.addItem(item)

