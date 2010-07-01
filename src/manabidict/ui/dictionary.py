
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import uic
from PyQt4.Qt import Qt
from PyQt4.QtWebKit import QWebPage
#import Qt
import sys
import os
from itertools import islice
import time
from functools import partial

from preferences import Preferences
from mspacer import MSpacer
from msegmentedbutton import MSegmentedButton

#from forms.dictionary import Ui_DictionaryWindow

#from epywing.manager 
from epywing.uris import route as route_dictionary_uri
from epywing.history import HistoryManager
from epywing.util import strip_tags



class Dictionary(QMainWindow):

    ui_class, widget_class = uic.loadUiType('../../qtcreator/dictionary.ui')
    ui = ui_class()

    ZOOM_DELTA = 0.10
    ZOOM_RANGE = (0.4, 4.0,)

    def __init__(self, book_manager, parent=None):
        super(Dictionary, self).__init__(parent)

        self.book_manager = book_manager
        self.history = HistoryManager()
        self.settings = QSettings()

        self._current_entry = None
        self._current_entry_hash = None
        #self._staged_back_item = None
        self._results_last_shown_at = 0

        self._finishedUiSetup = False
        self.setupUi()
        self.setupMacUi()
        self.restoreUiState()
        self.setupFinalUi()
        self._finishedUiSetup = True


        #self.ui.searchField.setText('test')
        #self.on_searchField_returnPressed()


    def setupUi(self):
        ui = self.ui
        ui.setupUi(self)

        ui.searchResults.setFocusPolicy(Qt.StrongFocus)

        # Entry view
        ui.entryView.setScrollBar(ui.entryVerticalScrollBar, scroll_bar_container=ui.entryVerticalScrollBarContainer)
        # all links should fire the linkClicked signal
        ui.entryView.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)

        ui.searchField.search_field.setFocus() #FIXME
        #ui.entryView.setSmoothScrolling(True)

        self.reload_books_list()
        self.reload_search_methods_list()


    def setupMacUi(self):
        ui = self.ui
        ui.searchResults.setAttribute(Qt.WA_MacShowFocusRect, False)
        #ui.searchResults.setStyleSheet('QListWidget { selection-background-color: #DDDDDD; selection-color: black; }')
        
        #spacer = QtGui.QSpacer(10, 0, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        spacer = MSpacer()
        #spacer.setOrientation(Qt.Horizontal)
        ui.selectBook.setContentsMargins(0, 0, 0, 0) #l, t, r, b
        ui.selectBook.setMinimumHeight(26)
        ui.dictionaryToolbar.insertWidget(None, spacer)
        ui.dictionaryToolbar.insertWidget(None, ui.selectBook)
        #ui.dictionaryToolbar.insertWidget(None, ui.selectBookContainer)
        #self.setWindowFlags(self.windowFlags() & ~ Qt.MacWindowToolBarButtonHint) # doesn't work, qt bug

        # make the results list grayed out when unfocused
        #ui.searchResults.setStyleSheet('QListWidget:focus { selection-background-color: green; }; QListWidget { selection-background-color: red;};')
        #ui.searchResults.setStyleSheet('QListWidget:focus { selection-background-color: #DDDDDD; selection-color: black; }')

        # search bar
        ui.searchField.setResourceImageUrlBase(':/images/searchbar')
        isf = ui.searchField.search_field
        isf.returnPressed.connect(self.on_searchField_returnPressed)
        isf.keyUpPressed.connect(self.on_searchField_keyUpPressed)
        isf.keyDownPressed.connect(self.on_searchField_keyDownPressed)
        isf.textEdited.connect(self.on_searchField_textEdited)
        ui.searchField.clear_button.clicked.connect(self.on_clearSearch_clicked)

        # toolbar icons
        
        # history buttons
        self.ui.history_buttons = MSegmentedButton(parent=self)
        url_base = ':/images/icons/toolbar/button-'
        ui.history_buttons.left_button.setImageUrls(url_base + 'left.png', url_base + 'left-pressed.png', url_base + 'left-disabled.png')
        ui.history_buttons.right_button.setImageUrls(url_base + 'right.png', url_base + 'right-pressed.png', url_base + 'right-disabled.png')
        ui.history_buttons.left_button.clicked.connect(lambda: ui.actionBack.trigger())
        ui.history_buttons.right_button.clicked.connect(lambda: ui.actionForward.trigger())
        ui.navToolbar.addWidget(ui.history_buttons)

        # context menus for history buttons
        ui.back_history_menu = QMenu(parent=ui.history_buttons.left_button)
        ui.forward_history_menu = QMenu(parent=ui.history_buttons.right_button)

        ui.history_buttons.left_button.setPopupMode(QToolButton.DelayedPopup)
        ui.history_buttons.right_button.setPopupMode(QToolButton.DelayedPopup)

        ui.history_buttons.left_button.setMenu(ui.back_history_menu)
        ui.history_buttons.right_button.setMenu(ui.forward_history_menu)

        ui.back_history_menu.aboutToShow.connect(lambda: self.refresh_back_history_menu())
        ui.forward_history_menu.aboutToShow.connect(lambda: self.refresh_forward_history_menu())
        

        # hide the existing non-mac ones
        for action in [ui.actionBack, ui.actionForward, ui.actionDecreaseFontSize, ui.actionIncreaseFontSize]:
            action.setVisible(False)

        ui.text_size_buttons = MSegmentedButton(parent=self)
        url_base = ':/images/icons/toolbar/text-'
        ui.text_size_buttons.left_button.setImageUrls(url_base + 'smaller.png', url_base + 'smaller-pressed.png', url_base + 'smaller-disabled.png')
        ui.text_size_buttons.right_button.setImageUrls(url_base + 'bigger.png', url_base + 'bigger-pressed.png', url_base + 'bigger-disabled.png')
        ui.text_size_buttons.left_button.clicked.connect(lambda: ui.actionDecreaseFontSize.trigger())
        ui.text_size_buttons.right_button.clicked.connect(lambda: ui.actionIncreaseFontSize.trigger())
        ui.navToolbar.addWidget(ui.text_size_buttons)

    def setupFinalUi(self):
        '''The last UI setup method to be called.
        '''
        self.refresh_history_buttons()


    def restoreUiState(self):
        '''Restores UI state from the last time it was opened.
        '''
        book_id = unicode(self.settings.value('ui_state/selected_book_id').toString())
        index = self.ui.selectBook.findData(book_id)
        if index != -1:
            self.ui.selectBook.setCurrentIndex(index)


    # Search field UI
    # ---------------
    
    def on_searchField_returnPressed(self):
        sr, sf = self.ui.searchResults, self.ui.searchField

        if not sr.selectedItems():
            sr.setCurrentRow(0)

        if sr.currentItem():
            #TODO see todo file for notes on this: #sf.setText(sr.currentItem().text())
            self.ui.entryView.setFocus()
            #sf.selectAll()
            self.stage_history()

    def on_searchField_keyUpPressed(self):
        sr = self.ui.searchResults

        if sr.currentRow() > 0:
            sr.setCurrentRow(sr.currentRow() - 1)
            self.stage_history()

    def on_searchField_keyDownPressed(self):
        sr = self.ui.searchResults
        if sr.currentRow() < sr.count() - 1:
            sr.setCurrentRow(sr.currentRow() + 1)
            self.stage_history()

    def on_searchField_textEdited(self, text):
        self.do_search(unicode(text))

    def on_clearSearch_clicked(self):
        sr, sf = self.ui.searchResults, self.ui.searchField
        self.push_history()
        sr.clear()
        sf.search_field.setFocus()
        

    # Search results UI
    # -----------------

    def on_searchResults_currentItemChanged(self, current, previous):
        if current:
            item_data = current.data(Qt.UserRole).toPyObject()
            self.show_entry(item_data)

    #def on_searchResults_

    def on_searchResults_lostFocus(self):
        pass

    def on_searchResults_gainedFocus(self):
        pass


    # Entry view UI
    # -------------
    
    def on_entryView_linkClicked(self, url):
        url = unicode(url.toString())

        self.stage_history()
        self.push_history()

        if '#' in url:
            # it contains a hash, which will scroll the view to the given named anchor
            hash_string = url.split('#')[-1]
            self.ui.entryView.scrollToAnchor(hash_string)
            self._current_entry_hash = hash_string
        else:
            self._current_entry_hash = None
            resource = route_dictionary_uri(url, self.book_manager.books.values())
            self.show_entry(resource)
        self.stage_history()


    # Other UI
    # --------

    @pyqtSignature('int')
    def on_selectBook_currentIndexChanged(self, index):
        self.do_search()
        if index == -1:
            book_id = None
        else:
            book_id = self.selected_book().id
        if self._finishedUiSetup:
            self.settings.setValue('ui_state/selected_book_id', book_id)

    @pyqtSignature('int')
    def on_searchMethod_currentIndexChanged(self, index):
        self.do_search()


    # toolbar actions
    # ---------------

    @pyqtSignature('')
    def on_actionBack_triggered(self):
        self.go_back()

    @pyqtSignature('')
    def on_actionForward_triggered(self):
        self.go_forward()


    @pyqtSignature('')
    def on_actionDecreaseFontSize_triggered(self):
        self.zoom_entry_view(-self.ZOOM_DELTA)

    @pyqtSignature('')
    def on_actionIncreaseFontSize_triggered(self):
        self.zoom_entry_view(self.ZOOM_DELTA)


    # menu actions
    # ------------

    @pyqtSignature('')
    def on_actionPreferences_triggered(self):
        '''Display preferences dialog.
        '''
        prefs = Preferences(self.book_manager, parent=self)
        #prefs.setModal(True)
        #prefs.show()
        prefs.exec_()
        self.reload_books_list()


    # general methods
    # ---------------

    def _refresh_history_menu(self, menu, history_items, direction):
        '''`direction` is 1 or -1 and indicates if this is for forward or back.
        '''
        menu.clear()
        for index, item in enumerate(history_items, start=1):
            action = QAction(item['label'], menu)
            func = partial(self._go_history, index * direction)
            action.triggered.connect(func)
            menu.addAction(action)

    def refresh_back_history_menu(self):
        self._refresh_history_menu(self.ui.back_history_menu, self.history.back_items, -1)
        
    def refresh_forward_history_menu(self):
        self._refresh_history_menu(self.ui.forward_history_menu, self.history.forward_items, 1)

    def go_back(self):
        '''Go back one history item.
        '''
        self._go_history(-1)
    
    def go_forward(self):
        '''Go forward one history item.
        '''
        self._go_history(1)

    def _go_history(self, index):
        '''Go forward if positive, back if negative.
        '''
        #self.push_history()
        self.stage_history(clear_forward_items=False)
        try:
            back_item = self.history.go(index)
            print 'going {0} to:'.format(index)#,
            #print back_item
            print len(self.history)
            if 'search_results' in back_item:
                self.show_results(back_item['search_results'])
                self.ui.searchResults.setCurrentRow(back_item['search_results_current_row'])
            self.show_entry(back_item['entry'])
            if 'entry_hash' in back_item:
                self.ui.entryView.scrollToAnchor(back_item['entry_hash'])
            if 'book' in back_item:
                self.select_book(back_item['book'])
        except IndexError:
            # already at edge of history
            print 'indexerror!'
            pass
        self.refresh_history_buttons()
        

    def push_history(self):
        '''Pushes the currently staged back item to the history manager.
        We push a dictionary rather than just a URI because we want to load both search results and the entry when going back.
        '''
        #print self.history
        #if self._staged_back_item:
        if self.history.current_location:
            print 'pushing staged location',
            #print self.history.current_location
            #print self.staged_back_item
            #self.history.push(self._staged_back_item)
            self.history.push()
            #print self.history._back
            #self._staged_back_item = None
        #print len(self.history)
        self.refresh_history_buttons()
        #print self.history

    def stage_history(self, clear_forward_items=True, label=None):
        '''Set the staged back item to the current entry and search context.
        `label` is what the history item will show as in menus. Defaults to the entry heading.
        '''
        entry = self._current_entry

        if not label:
            if entry.heading:
                label = strip_tags(entry.heading)
            else:
                lines = strip_tags(entry.text.replace('<br>', '\n')).split()
                label = lines[0] if lines else ''

        staged_back_item = {
            'label': label,
            'book': self.selected_book(),
            'entry': entry,
            'search_results': self._current_results,
            'search_results_current_row': self.ui.searchResults.currentRow(),
            #'':
        }
        if self._current_entry_hash:
            staged_back_item['entry_hash'] = self._current_entry_hash
        self.history.current_location = staged_back_item
        if clear_forward_items:
            self.history.forward_items = []
        #print 'staging:',
        #print staged_back_item
        #print len(self.history)
        #print self.history
        #print 'staging:',
        #print self._staged_back_item

    def refresh_history_buttons(self):
        '''Enable or disable the history buttons depending on the history state.
        '''
        back_enabled = bool(self.history.back_items)
        self.ui.actionBack.setEnabled(back_enabled)
        self.ui.history_buttons.left_button.setEnabled(back_enabled)

        forward_enabled = bool(self.history.forward_items)
        self.ui.actionForward.setEnabled(forward_enabled)
        self.ui.history_buttons.right_button.setEnabled(forward_enabled)


    def zoom_entry_view(self, zoom_delta):
        ev = self.ui.entryView
        new_zoom = ev.zoomFactor() + (ev.zoomFactor() * zoom_delta)
        if new_zoom >= self.ZOOM_RANGE[0] and new_zoom <= self.ZOOM_RANGE[1]:
            ev.setZoomFactor(ev.zoomFactor() + zoom_delta)


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
    
    def select_book(self, book):
        '''Selects the book given an EpwingBook instance.
        '''
        sb = self.ui.selectBook
        index = sb.findData(book.id)
        if index != -1:
            sb.setCurrentIndex(index)

    def reload_books_list(self):
        '''Fills the book combobox with available books.
        Call this after updating installed book preferences, and on first launch.
        '''
        sb = self.ui.selectBook
        current_book_id = unicode(sb.itemData(sb.currentIndex()).toString())# if sb.currentIndex() else None
        sb.clear()
        for book_id, book in self.book_manager.books.items():
            sb.addItem(book.name, book_id)
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
 

    def do_search(self, query=None, search_method=None, max_results_per_book=30):
        book = self.selected_book()
        if not book: return
        if not query:
            query = unicode(self.ui.searchField.search_field.text())
        if not search_method:
            search_method = self.selected_search_method()
        results = list(islice(book.search(query, search_method=search_method), 0, max_results_per_book))
        #results = self.book_manager.search_all(query, search_method='prefix')#, container=container)
        self.show_results(results)
    
    def show_results(self, results):
        '''Sets the list of search results, displaying them in the list box.
        '''
        ran_at = time.time()
        self._results_last_shown_at = ran_at
        self._current_results = results
        #self._show_results_queue.append(queue_time)
        sr = self.ui.searchResults
        sr.clear()
        q_app = QApplication.instance()
        q_app.processEvents()
        i = 0
        for result in results:
            if ran_at < self._results_last_shown_at:
                return
            # add an HTML item if it contains HTML
            html_hints = ['<', '>', '&lt;', '&gt;']
            if any(map(lambda x: x in result.heading, html_hints)):
                sr.addHtmlItem(result.heading, result)
                if not i % 4:
                    q_app.processEvents()
                i += 1
            else:
                item = QListWidgetItem(result.heading)
                item.setData(Qt.UserRole, result)
                sr.addItem(item)
            #item = QtGui.QListWidgetItem(result.heading)
            #item.setData(Qt.UserRole, result)
            #sr.addItem(item)
        sr.scrollToItem(self.ui.searchResults.item(0))

    def show_entry(self, entry):
        self._current_entry = entry
        html = '<div style="font-family:Baskerville; line-height:1.5;">'+entry.text+'</div>'
        self.ui.entryView.setHtml(html)



