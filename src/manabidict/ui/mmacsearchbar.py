from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.Qt import Qt

from mlineedit import MLineEdit


class MMacSearchBar(QWidget):
    '''Segmented button (containing 2 parts), like the Cocoa one.
    '''
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.setMinimumSize(50, 22)
        self.setSizePolicy(self.sizePolicy().horizontalPolicy(), QSizePolicy.Fixed)

        self.resource_image_url_base = ':/'

        self.history_menu = None

        hb = self.history_button = QToolButton()
        hb.setFixedSize(23, 22)

        cb = self.clear_button = QToolButton()
        cb.setFixedSize(18, 22)
        cb.setEnabled(False)

        sf = self.search_field = MLineEdit()
        sf.setFocusPolicy(Qt.StrongFocus)
        sf.setObjectName('search_field')
        sf.setFrame(False)
        sf.setMaximumHeight(16)
        sf.setAttribute(Qt.WA_MacShowFocusRect, False)
        sf.setAutoFillBackground(False)
        pal = QPalette(sf.palette())
        pal.setColor(sf.backgroundRole(), Qt.transparent)
        sf.setPalette(pal)
        #sf.setAttribute(Qt.WA_NoSystemBackground, True)

        # center-piece which holds the search field
        ctr = self.center_container = QWidget()
        ctr.setObjectName('center_container')
        #ctr.setMinimumSize(30, 22)
        ctr.setLayout(QHBoxLayout())
        ctr.layout().setSpacing(0)
        ctr.setAutoFillBackground(True)
        ctr.layout().addWidget(sf)
        ctr.setAttribute(Qt.WA_OpaquePaintEvent, True)

        self._setStyleSheets()

        self.setLayout(QHBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)#4, 4, 4) #l, t, r, b

        self.layout().addWidget(hb)
        self.layout().addWidget(ctr)
        self.layout().addWidget(cb)

        self.setHistoryMenu(None)

        # events
        sf.textChanged.connect(self.on_textChanged)
        sf.keyEscapePressed.connect(self.on_clear_button_clicked)
        cb.clicked.connect(self.on_clear_button_clicked)


    def on_textChanged(self, text):
        self.clear_button.setEnabled(bool(text))

    def on_clear_button_clicked(self):
        self.search_field.clear()

    def _setStyleSheets(self):
        style_sheet = '''
            QToolButton {{ border-image: url({0}/history-button.png); }}
            QToolButton:disabled {{ border-image: url({0}/history-button-disabled.png); }}
        '''.format(self.resource_image_url_base)
        self.history_button.setStyleSheet(style_sheet)

        style_sheet = '''
            QToolButton {{ border-image: url({0}/clear-button.png); }}
            QToolButton:pressed {{ border-image: url({0}/clear-button-pressed.png); }}
            QToolButton:disabled {{ border-image: url({0}/clear-button-disabled.png); }}
        '''.format(self.resource_image_url_base)
        self.clear_button.setStyleSheet(style_sheet)

        self.center_container.setStyleSheet('''
            QLineEdit#search_field {{ background-color: rgba(255, 255, 255, 0%); }}
            QWidget#center_container {{ background-image: url({0}/background.png) }}
        '''.format(self.resource_image_url_base))


    def setResourceImageUrlBase(self, url):
        if url[-1] == '/':
            url = url[:-1]
        self.resource_image_url_base = url

        self._setStyleSheets()

    def setHistoryMenu(self, menu):
        '''`menu` should be a QMenu instance.
        '''
        self.history_menu = menu
        self.history_button.setEnabled(bool(menu))
        if menu:
            text_margin = 3
        else:
            text_margin = 0
        self.center_container.layout().setContentsMargins(text_margin, 0, 0, 0) #l, t, r, b



