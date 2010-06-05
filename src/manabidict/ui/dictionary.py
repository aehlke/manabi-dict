
from PyQt4 import QtGui, QtCore, uic
from PyQt4.Qt import Qt
#import Qt
import sys
import os

#from forms.dictionary import Ui_DictionaryWindow

#from epywing.manager 

class Container(object):
    def __init__(self):
        pass

class Dictionary(QtGui.QMainWindow): #, Ui_DictionaryWindow):

    ui_class, widget_class = uic.loadUiType('../../qtcreator/dictionary.ui')
    ui = ui_class()

    def __init__(self, book_manager, parent=None):
        super(Dictionary, self).__init__(parent)

        self.book_manager = book_manager

        self.setupUi()
        self.setupMacUi()

        self.ui.searchField.setText('test')
        self.on_searchField_returnPressed()

    def setupUi(self):
        #ui = self.ui

        self.ui.setupUi(self)

        #self.connect(ui.searchField, QtCore.SIGNAL("returnPressed()"),
        #             self.actionGo, QtCore.SLOT("trigger()"))
    #@self.ui.searchField.returnPressed.connect
    #def doSearch():
        #self.book_manager.search_all_combined(self.ui.searchField.)

    def on_searchField_returnPressed(self):
        query = unicode(self.ui.searchField.text())
        print query
            #typedef struct _SContainer {
            #    id          clazz;
            #    id          string;
            #    NSMutableArray* styles;
            #    NSMutableArray* links;
            #    int         range;
            #    bool                gaiji;
            #    NSMutableData*  raw;
            #} SContainer;
            #buffer[sizeof(buffer) - 1] = '\0';
            #bufferString = [NSMutableString stringWithCapacity:64];
            #container.string = bufferString;
            #container.clazz = self;
            #container.styles = NULL;
            #container.gaiji = FALSE;
            #container.raw = NULL;
                
        container = Container()
        container.string = "1"*65#query
        container.styles = None
        container.gaiji = False
        container.raw = None
        #contaianer.clazz = 
        results = self.book_manager.search_all(query, search_method='prefix', container=container)
        self.setResults(results)
    
    def setResults(self, results):
        '''Sets the list of search results, displaying them in the list box.
        '''
        #print str(results)
        #for result in results:
        self.ui.searchResults.clear()
        self.ui.searchResults.addItems([result['heading'] for result in results])

    def setupMacUi(self):
        ui = self.ui
        ui.searchResults.setAttribute(Qt.WA_MacShowFocusRect, False)
        #ui.searchResults.setAutoFillBackground(True)
        #ui.searchToolbar.insertWidget(None, ui.searchMethod)
        #ui.searchToolbar.insertWidget(None, ui.searchField)
        ui.searchToolbar.insertWidget(None, ui.selectBook)
        #self.setWindowFlags(self.windowFlags() & ~ Qt.MacWindowToolBarButtonHint) # doesn't work, qt bug

    #def main(self)
    #    self.show()




