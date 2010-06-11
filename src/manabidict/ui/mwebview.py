
from PyQt4 import QtGui, QtCore, QtWebKit
#from QtCore.QObject import connect, disconnect
#from PyQt4.QObject import connect, disconnect
from PyQt4.Qt import Qt
from msmoothscroller import MSmoothScroller

class MWebView(QtWebKit.QWebView):

    def __init__(self, parent=None):
        '''
        `user` is a QAbstractScrollArea
        '''
        QtWebKit.QWebView.__init__(self, parent)

        self._sb = None #scroll bar

        #self._smooth_scroller = MSmoothScroller()

    def setScrollBar(self, scroll_bar):
        '''Sets a scrollbar which will update and be updated by this webview.
        '''
        sb = self._sb = scroll_bar

        #frame = ui.entryView.page().mainFrame()
        frame = self.page().mainFrame()
        frame.setScrollBarPolicy(Qt.Vertical, Qt.ScrollBarAlwaysOff)

        #page = self.page()

        sb.setMinimum(0)
        sb.setSingleStep(20)
        self._updateScrollBarMax()

        self.page().scrollRequested.connect(self._scrollRequested)
        self.page().geometryChangeRequested.connect(lambda geom: self._updateScrollBarMax)
        #self.onResize.connect(self._geometryChangeRequested)
        self._ignore_value_changed = False
        #sb.valueChanged.connect(self._scrollValueChanged)
        sb.sliderMoved.connect(self._scrollValueChanged)
        sb.actionTriggered.connect(self._scrollActionTriggered)

    def paintEvent(self, e):
        super(MWebView, self).paintEvent(e)
        self._updateScrollBarMax()

    def resizeEvent(self, e):
        super(MWebView, self).resizeEvent(e)
        self._updateScrollBarMax()

    def _scrollActionTriggered(self, action):
        if action is not QtGui.QAbstractSlider.SliderMove:
            value = self._sb.sliderPosition()
            self._scrollToY(value)

    def _scrollToY(self, value):
        frame = self.page().mainFrame()
        pos = frame.scrollPosition()
        if pos.y() != value:
            pos.setY(value)
            frame.setScrollPosition(pos)

    def _scrollValueChanged(self, value):
        '''Vertical scrollbar's value changed.
        '''
        self._scrollToY(value)

    def _scrollRequested(self, dx, dy, rectToScroll):
        self._updateScrollBarMax()
        self._sb.setValue(self._sb.value() - dy)

    def _updateScrollBarMax(self):
        viewport_height = self.page().viewportSize().height()
        max_value = self.page().mainFrame().contentsSize().height() - viewport_height
        self._sb.setMaximum(max_value)
        self._sb.setPageStep(viewport_height)

        #page.


    #def setSmoothScrolling(self, value):
        #if value:
            #self._smooth_scroller.activateOn(self)
        #else:
            #self._smooth_scroller.deactivate()

