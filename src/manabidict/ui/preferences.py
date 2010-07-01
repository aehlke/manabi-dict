from PyQt4 import uic
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.Qt import Qt
import sys
import os
from os import path

#from forms.dictionary import Ui_DictionaryWindow

#from epywing.manager 


class Preferences(QDialog):

    ui_class, widget_class = uic.loadUiType('../../qtcreator/preferences.ui')
    ui = ui_class()

    #booksChanged = pyqtSignal()

    def __init__(self, book_manager, parent=None):
        '''`parent` must be a dictionary window.
        '''
        super(Preferences, self).__init__(parent)

        self.settings = QSettings()

        self.book_manager = book_manager

        self.setupUi()
        self.setupMacUi()
        self.setupBooksTable()


    def setupUi(self):
        ui = self.ui
        ui.setupUi(self)

        # books table
        ui.booksTable.horizontalHeader().setResizeMode(QHeaderView.Stretch)


    def setupMacUi(self):
        ui = self.ui

    def setupBooksTable(self):
        '''Initialize the books table with installed books.
        '''
        self.add_books_to_table(self.book_manager.books)


    # UI signal handlers
    
    @pyqtSignature('')
    def on_moveUp_clicked(self):
        self.move_book_row('up')

    @pyqtSignature('')
    def on_moveDown_clicked(self):
        self.move_book_row('down')

    @pyqtSignature('')
    def on_addBook_clicked(self):
        path = unicode(QFileDialog.getExistingDirectory(self, 'Add EPWING Dictionary'))
        if not path: return

        book_paths = self.book_manager.find_books_in_path(path)
        if book_paths:
            new_books = self.book_manager.add_books(*book_paths)
            self.settings.setValue('book_manager/book_paths', self.book_manager.book_paths)
            self.add_books_to_table(new_books)
        else:
            QMessageBox.critical(self, 'Error', 
                    'The directory you selected is not an EPWING dictionary.\n\nChoose a directory that contains a CATALOG or CATALOGS file in order to add a valid EPWING dictionary.')


    @pyqtSignature('')
    def on_removeBook_clicked(self):
        tbl = self.ui.booksTable
        rows = tbl.selectionModel().selectedRows()
        for row in rows:
            self.remove_book(row)


    # general methods
    def move_book_row(self, index=None, direction='up'):
        '''`direction` is 'up' or 'down'
        `index` is the table row index
        '''
        pass
        #TODO
        #if not index:
        #    indexes = self.ui.booksTable.selectionModel().selectedRows()
        #    if not indexes:
        #        return
        #    index = indexes[0]

    def swap_book_rows(self, r1, r2):
        #TODO
        pass
        #tbl = self.ui.booksTable

        
    def remove_book(self, books_table_index):
        '''Removes the book in the given table index from both the book manager, and the books table.
        '''
        tbl = self.ui.booksTable
        row = books_table_index.row()
        item = tbl.item(row, 1) # 2nd column represents the dictionary, and has the book ID as its data
        book_id = unicode(item.data(Qt.UserRole).toString())
        tbl.removeRow(row)
        self.book_manager.remove_book(book_id)
        self.settings.setValue('book_manager/book_paths', self.book_manager.book_paths)


    def add_books_to_table(self, books):
        '''Adds the given dictionary of books (mapping ID to EpwingBook instance) to the table.
        '''
        tbl = self.ui.booksTable
        for book_id, book in books.items():
            # use the first subbook name as the label
            label = book.name
            #if book.subbooks:
                #label = book.subbooks[0]['name']
            #else:
                #continue
            label_item = QTableWidgetItem(label)
            label_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable)

            dictionary_item = QTableWidgetItem(path.basename(book.book_path))
            dictionary_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            dictionary_item.setData(Qt.UserRole, book_id) # keep the book ID in the item's data
            row = tbl.rowCount()
            tbl.insertRow(row)
            tbl.setItem(row, 0, label_item)
            tbl.setItem(row, 1, dictionary_item)

    #def reload_books_table(self, books):
    #    '''Refills the booksTable widget with the given list of books.
    #    `books` is a dictionary mapping book ID to EpwingDictionary instance.
    #    '''
    #    tbl = self.ui.booksTable
    #    tbl.clear()
    #    for book_id, book in books:
    #        item = QTableWidgetItem(tbl



