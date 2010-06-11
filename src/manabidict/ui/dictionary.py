
from PyQt4 import QtGui, QtCore, uic
from PyQt4.Qt import Qt
#import Qt
import sys
import os

#from forms.dictionary import Ui_DictionaryWindow

#from epywing.manager 



class Dictionary(QtGui.QMainWindow): #, Ui_DictionaryWindow):

    ui_class, widget_class = uic.loadUiType('../../qtcreator/dictionary.ui')
    ui = ui_class()

    ZOOM_DELTA = 0.05

    def __init__(self, book_manager, parent=None):
        super(Dictionary, self).__init__(parent)

        self.book_manager = book_manager

        self.setupUi()
        self.setupMacUi()

        self.ui.searchField.setText('test')
        self.on_searchField_returnPressed()

    def setupUi(self):
        ui = self.ui
        ui.setupUi(self)

        ui.searchField.setFocus() #FIXME
        #ui.entryView.setSmoothScrolling(True)

        ui.entryView.setScrollBar(ui.entryVerticalScrollBar)


        # make the results list grayed out when unfocused
        #ui.searchResults.setStyleSheet('QListWidget:focus { selection-background-color: green; }; QListWidget { selection-background-color: red;};')
        #ui.searchResults.setStyleSheet('QListWidget:focus { selection-background-color: #DDDDDD; selection-color: black; }')


    def setupMacUi(self):
        ui = self.ui
        ui.searchResults.setAttribute(Qt.WA_MacShowFocusRect, False)
        #ui.searchResults.setStyleSheet('QListWidget { selection-background-color: #DDDDDD; selection-color: black; }')
        
        ui.dictionaryToolbar.insertWidget(None, ui.selectBook)
        #self.setWindowFlags(self.windowFlags() & ~ Qt.MacWindowToolBarButtonHint) # doesn't work, qt bug

        ui.splitter.setStretchFactor(0, 0)


    # Search field UI
    
    def on_searchField_returnPressed(self):
        sr, sf = self.ui.searchResults, self.ui.searchField

        if not sr.selectedItems():
            sr.setCurrentRow(0)

        if sr.currentItem():
            sf.setText(sr.currentItem().text())
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


    # toolbar actions

    def on_actionBack_triggered(self):
        print 'back'

    def on_actionDecreaseFontSize_triggered(self):
        ev = self.ui.entryView
        ev.setZoomFactor(ev.zoomFactor() - self.ZOOM_DELTA)

    def on_actionIncreaseFontSize_triggered(self):
        ev = self.ui.entryView
        ev.setZoomFactor(ev.zoomFactor() + self.ZOOM_DELTA)

    # general methods

    def do_search(self, query):
        results = self.book_manager.search_all(query, search_method='prefix')#, container=container)
        self.show_results(results)
    
    def show_results(self, results):
        '''Sets the list of search results, displaying them in the list box.
        '''
        sr = self.ui.searchResults
        sr.clear()
        for result in results:
            item = QtGui.QListWidgetItem(result.heading)
            item.setData(Qt.UserRole, result)
            sr.addItem(item)
        sr.scrollToItem(self.ui.searchResults.item(0))

    def show_entry(self, entry):
        html = '<div style="font-family:Baskerville">'+entry.text+'</div>'
        self.ui.entryView.setHtml(html)



