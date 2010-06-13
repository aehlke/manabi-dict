
from PyQt4 import QtGui, QtCore, uic
from PyQt4.Qt import Qt
#import Qt
import sys
import os
from itertools import islice

from preferences import Preferences
from mspacer import MSpacer

#from forms.dictionary import Ui_DictionaryWindow

#from epywing.manager 



class Dictionary(QtGui.QMainWindow):

    ui_class, widget_class = uic.loadUiType('../../qtcreator/dictionary.ui')
    ui = ui_class()

    #ZOOM_DELTA = 0.05
    ZOOM_DELTA = 0.15

    def __init__(self, book_manager, parent=None):
        super(Dictionary, self).__init__(parent)

        self.book_manager = book_manager

        self.setupUi()
        self.setupMacUi()

        #self.ui.searchField.setText('test')
        #self.on_searchField_returnPressed()


    def setupUi(self):
        ui = self.ui
        ui.setupUi(self)

        ui.searchField.setFocus() #FIXME
        #ui.entryView.setSmoothScrolling(True)

        ui.entryView.setScrollBar(ui.entryVerticalScrollBar)
        self.reload_books_list()
        self.reload_search_methods_list()


    def setupMacUi(self):
        ui = self.ui
        ui.searchResults.setAttribute(Qt.WA_MacShowFocusRect, False)
        #ui.searchResults.setStyleSheet('QListWidget { selection-background-color: #DDDDDD; selection-color: black; }')
        
        #spacer = QtGui.QSpacer(10, 0, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        spacer = MSpacer()
        #spacer.setOrientation(Qt.Horizontal)
        ui.dictionaryToolbar.insertWidget(None, spacer)
        ui.dictionaryToolbar.insertWidget(None, ui.selectBook)
        #self.setWindowFlags(self.windowFlags() & ~ Qt.MacWindowToolBarButtonHint) # doesn't work, qt bug

        # make the results list grayed out when unfocused
        #ui.searchResults.setStyleSheet('QListWidget:focus { selection-background-color: green; }; QListWidget { selection-background-color: red;};')
        #ui.searchResults.setStyleSheet('QListWidget:focus { selection-background-color: #DDDDDD; selection-color: black; }')


    # Search field UI
    
    def on_searchField_returnPressed(self):
        sr, sf = self.ui.searchResults, self.ui.searchField

        if not sr.selectedItems():
            sr.setCurrentRow(0)

        if sr.currentItem():
            #TODO see todo file for notes on this: #sf.setText(sr.currentItem().text())
            self.ui.entryView.setFocus()
            #sf.selectAll()

    def on_searchField_keyUpPressed(self):
        sr = self.ui.searchResults

        if sr.currentRow() > 0:
            sr.setCurrentRow(sr.currentRow() - 1)

    def on_searchField_keyDownPressed(self):
        sr = self.ui.searchResults
        if sr.currentRow() < sr.count() - 1:
            sr.setCurrentRow(sr.currentRow() + 1)

    def on_searchField_textEdited(self, text):
        self.do_search(unicode(text))

    def on_clearSearch_clicked(self):
        sr, sf = self.ui.searchResults, self.ui.searchField
        sf.clear()
        sr.clear()
        sf.setFocus()
        

    # Search results UI

    def on_searchResults_currentItemChanged(self, current, previous):
        if current:
            item_data = current.data(Qt.UserRole).toPyObject()
            self.show_entry(item_data)

    def on_searchResults_lostFocus(self):
        pass

    def on_searchResults_gainedFocus(self):
        pass


    # Other UI

    @QtCore.pyqtSignature('int')
    def on_selectBook_currentIndexChanged(self, index):
        self.do_search()

    @QtCore.pyqtSignature('int')
    def on_searchMethod_currentIndexChanged(self, index):
        self.do_search()


    # toolbar actions

    def on_actionBack_triggered(self):
        print 'back'

    def on_actionDecreaseFontSize_triggered(self):
        ev = self.ui.entryView
        ev.setZoomFactor(ev.zoomFactor() - self.ZOOM_DELTA)

    def on_actionIncreaseFontSize_triggered(self):
        ev = self.ui.entryView
        ev.setZoomFactor(ev.zoomFactor() + self.ZOOM_DELTA)


    # menu actions

    @QtCore.pyqtSignature('')
    def on_actionPreferences_triggered(self):
        '''Display preferences dialog.
        '''
        prefs = Preferences(self.book_manager, parent=self)
        #prefs.setModal(True)
        #prefs.show()
        prefs.exec_()
        self.reload_books_list()


    # general methods

    def selected_search_method(self):
        '''Returns the string ID of the currently selected search method.
        '''
        return unicode(self.ui.searchMethod.itemData(self.ui.searchMethod.currentIndex()).toString())

    def selected_book(self):
        '''Returns the currently selected book's EpwingBook instance.
        '''
        sb = self.ui.selectBook
        if not sb.count(): return None
        book_id = unicode(sb.itemData(sb.currentIndex()).toString())
        return self.book_manager.books[book_id]

    def reload_books_list(self):
        '''Fills the book combobox with available books.
        Call this after updating installed book preferences, and on first launch.
        '''
        sb = self.ui.selectBook
        current_book_id = unicode(sb.itemData(sb.currentIndex()).toString())# if sb.currentIndex() else None
        sb.clear()
        for book_id, book in self.book_manager.books.items():
            if not book.subbooks: continue
            sb.addItem(book.subbooks[0]['name'], book_id)
        index = sb.findData(current_book_id)
        if index != -1:
            sb.setCurrentIndex(index)
        else:
            sb.setCurrentIndex(0)
            self.do_search()

    #def reload_search_methods(self):
    #TODO
    #    '''Fills the search methods combobox with available search methods for the selected book(s).
    #    Call this when the books list selection changes, and on first launch.
    #    '''
    #    sm = self.ui.searchMethod
    #    sm.clear()
    #    current_method = sm.itemData(sm.currentIndex())# if sb.currentIndex() else None
    #    for book_id, book in self.book_manager.books.items():
    #        if not book.subbooks: continue
    #        sb.addItem(book.subbooks[0]['name'], book_id)
    #    index = sb.findData(current_book_id)
    #    if index != -1:
    #        sb.setCurrentIndex(index)
    #    else:
    #        sb.setCurrentIndex(0)

    def reload_search_methods_list(self):
        '''Fills ui.searchMethod with the available methods for the current book.
        Currently a stub that just fills it with some defaults.
        '''
        methods = [('prefix', 'Begins with'), ('suffix', 'Ends with'), ('exact', 'Exactly')]
        sm = self.ui.searchMethod
        sm.clear()
        for id, name in methods:
            sm.addItem(name, id)
 

    def do_search(self, query=None, search_method=None, max_results_per_book=25):
        book = self.selected_book()
        if not book: return
        if not query:
            query = unicode(self.ui.searchField.text())
        if not search_method:
            search_method = self.selected_search_method()
        results = list(islice(book.search(query, search_method=search_method), 0, max_results_per_book))
        #results = self.book_manager.search_all(query, search_method='prefix')#, container=container)
        self.show_results(results)
    
    def show_results(self, results):
        '''Sets the list of search results, displaying them in the list box.
        '''
        sr = self.ui.searchResults
        sr.clear()
        #sr._prepHtmlItemWidget() #FIXME
        for result in results:
            sr.addHtmlItem(result.heading, result)
            #item = QtGui.QListWidgetItem(result.heading)
            #item.setData(Qt.UserRole, result)
            #sr.addItem(item)
        sr.scrollToItem(self.ui.searchResults.item(0))

    def show_entry(self, entry):
        html = '<div style="font-family:Baskerville">'+entry.text+'</div>'
        self.ui.entryView.setHtml(html)



