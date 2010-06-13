from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.Qt import Qt

class MListWidget(QListWidget):
    gainedFocus = pyqtSignal()
    lostFocus = pyqtSignal()
    def __init__(self, parent = None):
        QListWidget.__init__(self, parent)
    

    def focusInEvent(self, event):
        self.gainedFocus.emit()
        event.accept()
    
    def focusOutEvent(self, event):
        self.lostFocus.emit()
        event.accept()

    def addHtmlItem(self, html, data):
        '''Adds a new QTextEdit widget containing the given HTMl as an item in the list.
        '''
        item = QListWidgetItem(u'')
        item.setData(Qt.UserRole, data)
        self.addItem(item)
        label = QTextEdit(parent=self)
        #print self.font().pixelSize()
        label.setFont(self.font())
        #label.setMaximumSize(QSize(100, 20))
        label.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        label.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        #label.setPlainText('what huhhhh what')
        label.setText(html)

        f = QTextFrameFormat()
        f.setMargin(0)
        f.setPadding(0)
        f.setBorder(0)
        label.document().rootFrame().setFrameFormat(f)
        label.viewport().setAutoFillBackground(False)

        #label.setText('<b>hello</b>')
        #label.setText('yeah<img src=":/gaiji/confused.png"><img src=":/gaiji/confused.png"><img src=":/gaiji/confused.png">'+html) #setHtml to force html
        label.setReadOnly(True)
        label.setFrameShape(QFrame.NoFrame)
        label.setTextInteractionFlags(Qt.NoTextInteraction)

        font_metrics = QFontMetrics(label.currentFont())
        h = font_metrics.height() + label.frameWidth() * 2 + 1
        label.setFixedHeight(h)
        label.setFixedWidth(self.size().width() - 4)

        item.setSizeHint(label.frameSize())
        
        pm = QImage(label.size(), QImage.Format_ARGB32)
        pm.fill(Qt.transparent)
        #label.viewport().render(pm, flags=QWidget.DrawChildren)
        label.render(pm, flags=QWidget.DrawChildren)

        label2 = QLabel()
        label2.setPixmap(QPixmap.fromImage(pm))
        self.setItemWidget(item, label2)

        #self.setItemWidget(item, label)
        #self.
        #item = QtGui.QListWidgetItem(result.heading)
        #item.setData(Qt.UserRole, result)
        #sr.addItem(item)

