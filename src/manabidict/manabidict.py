
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
#import epywing.filters.linkifywords
#from epywing.bookfilter import load_filter_plugins

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
        book_paths = [path.toString() for path in self.settings.value('book_manager/book_paths', []).toList()]
        paths_to_remove = []
        for book_path in book_paths:
            book_path = unicode(book_path)
            new_books = self.book_manager.add_books(book_path)
            if not new_books:
                # it wasn't added successfully, so delete it from the prefs
                paths_to_remove.append(book_path)
        if paths_to_remove:
            book_paths = [_ for _ in book_paths if _ not in paths_to_remove]
            self.settings.setValue('book_manager/book_paths', book_paths)


    def setupUi(self):
        dictionary = Dictionary(self.book_manager)
        dictionary.show()
        dictionary.raise_()

        self.exec_()



if __name__=='__main__':
    #print book_manager.books
    app =  ManabiDictApplication(sys.argv)
    
