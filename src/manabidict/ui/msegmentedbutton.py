from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.Qt import Qt

class MInnerToolButton(QToolButton):
    def __init__(self, parent=None):
        QToolButton.__init__(self, parent)

    def _set_button_urls(self, normal, pressed, disabled):
        stylesheet = '''
            QToolButton {{ border-image: url({0}); }}
            QToolButton:pressed {{ border-image: url({1}); }}
            QToolButton:disabled {{ border-image: url({2}); }}
            QToolButton::menu-indicator {{ image: none; }}
            '''.format(normal, pressed, disabled)
        self.setStyleSheet(stylesheet)

    def setImageUrls(self, normal, pressed, disabled):
        self._set_button_urls(normal, pressed, disabled)


class MSegmentedButton(QWidget):
    '''Segmented button (containing 2 parts), like the Cocoa one.
    '''
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.left_button = MInnerToolButton()
        self.right_button = MInnerToolButton()

        self.left_button.setFixedSize(27, 23)
        self.right_button.setFixedSize(26, 23)

        self.setLayout(QHBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 4, 4)

        self.layout().addWidget(self.left_button)
        self.layout().addWidget(self.right_button)

        self.setMinimumSize(53, 23)



