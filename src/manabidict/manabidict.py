
#from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import uic
from PyQt4.Qt import Qt
import sys

from epywing import epwing
#from epywing import bookmanager.BookManager
#from bookmanager import BookManager
from epywing.bookmanager import BookManager

from eb import eb_initialize_library
from ui.dictionary import Dictionary

ORGANIZATION_NAME = 'Manabi'
ORGANIZATION_DOMAIN = 'manabi.org'
APPLICATION_NAME = 'Manabi Dictionary'
VERSION = '0.01'

class ManabiDictApplication(QApplication):
    def __init__(self, args):
        QApplication.__init__(self, args)

        eb_initialize_library()
        self.book_manager = BookManager()

        self.setupSettings()
        self.setupUi()

    def setupSettings(self):
        QCoreApplication.setOrganizationName(ORGANIZATION_NAME);
        QCoreApplication.setOrganizationDomain(ORGANIZATION_DOMAIN);
        QCoreApplication.setApplicationName(APPLICATION_NAME);
        QCoreApplication.setApplicationVersion(VERSION);

        self.settings = QSettings()

        # get installed dictionaries from stored settings and initialize them
        book_paths = [unicode(path.toString()) for path in self.settings.value('book_manager/book_paths', []).toList()]
        self.book_manager.add_books(*book_paths)


    def setupUi(self):
        dictionary = Dictionary(self.book_manager)
        dictionary.show()
        dictionary.raise_()

        self.exec_()



if __name__=='__main__':
    #print book_manager.books
    app =  ManabiDictApplication(sys.argv)
    
