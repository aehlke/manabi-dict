
from PyQt4 import QtGui, QtCore, uic
from PyQt4.Qt import Qt
import sys

from epywing import epwing
#from epywing import bookmanager.BookManager
#from bookmanager import BookManager
from epywing.bookmanager import BookManager

from eb import eb_initialize_library
from ui.dictionary import Dictionary


def main():
    eb_initialize_library()
    book_manager = BookManager()
    book_manager.add_books(*book_manager.find_books_in_path('../../../epywing/src/epywing/tests'))
    print book_manager.books

    app = QtGui.QApplication(sys.argv)

    dictionary = Dictionary(book_manager)
    dictionary.show()
    dictionary.raise_()

    app.exec_()


if __name__=='__main__':
    main()
