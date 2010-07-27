# -*- coding: utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import uic
from PyQt4.Qt import Qt
from PyQt4.QtWebKit import QWebPage
#import Qt
import sys
import os
from itertools import islice, imap
import time
from functools import partial
import inspect

from preferences import Preferences
from mspacer import MSpacer
from msegmentedbutton import MSegmentedButton
from historyitems import UrlHistoryItem

from epwingprotocol import MNetworkAccessManager

from forms.dictionary import Ui_DictionaryWindow

#from epywing.manager 
from epywing.uris import route as route_dictionary_uri, collection_uri_prefix
from epywing.history import HistoryManager
from epywing.util import strip_tags
from epywing.categories import BookCategory


class JavaScriptBridge(QObject):
    '''Simple class for bridging JS to Python.
    '''
    def __init__(self, dictionary_window):
        QObject.__init__(self, dictionary_window)
        self.setObjectName('JavaScriptBridge')
        self.dictionary_window = dictionary_window

    @pyqtSignature('QString')
    def search(self, query):
        query = unicode(query)
        self.dictionary_window.select_book(all_books=True)
        self.dictionary_window.do_search(query)


class KeyPressFilter(QObject):
    '''Filters input so that when the search field isn't focused and 
    the user enters text, it will focus the field before inserting the text.
    Then the user can always just start typing when they want to start a new search.
    '''
    #TODO use QInputMethodEvent to handle japanese key input (must be installed on the app level)
    #FIXME this breaks for typing in the prefs

    # non-printing characters
    control_chars = u''.join(map(unichr, range(0,32) + range(127,160)))

    def __init__(self, parent=None):
        '''`parent` must be a window object.
        '''
        super(KeyPressFilter, self).__init__(parent)
        self.parent = parent

    def eventFilter(self, obj, event):
        '''Move focus to searchField if text is being entered.
        Only handle events for .
        '''
        if self.parent.isActiveWindow():
            #print event
            #print event.type() == QEvent.Gesture
            search_field = self.parent.ui.searchField.search_field
            if event.type() == QEvent.KeyPress:
                key_event = QKeyEvent(event)

                if obj is not search_field \
                        and key_event.text() \
                        and key_event.text() not in self.control_chars:
                    search_field.setFocus()
                    search_field.clear()
                    search_field.keyPressEvent(event)
                    return True
                elif key_event.key() in [Qt.Key_PageUp, Qt.Key_PageDown, Qt.Key_Home, Qt.Key_End]:
                    # scroll the entryView
                    return self.parent.ui.entryView.event(event)
                #else:
                    #print str(QApplication.instance().focusWidget())
            elif event.type() == QEvent.InputMethod:
                input_method_event = QInputMethodEvent(event)

                if obj is not search_field:
                    #search_field.setFocus()
                    #search_field.clear()
                    search_field.inputMethodEvent(input_method_event)
                    return True
            elif event.type() == QEvent.Gesture:
                swipe = event.gesture(Qt.SwipeGesture)

                if swipe and swipe.state() == Qt.GestureFinished:
                    # go back or forward in history
                    if swipe.horizontalDirection() == swipe.Left:
                        self.parent.go_back()
                    elif swipe.horizontalDirection() == swipe.Right:
                        self.parent.go_forward()
                    return True

        return QObject.eventFilter(self, obj, event)
            


class Dictionary(QMainWindow):#, Ui_DictionaryWindow):

    #ui_class, widget_class = uic.loadUiType('../../qtcreator/dictionary.ui')
    #ui = ui_class()

    ZOOM_DELTA = 0.10
    ZOOM_RANGE = (0.4, 4.0,)

    EPWING_URL_PROTOCOL = 'epwing://'

    def __init__(self, book_manager, parent=None):
        super(Dictionary, self).__init__(parent)

        self.ui = Ui_DictionaryWindow()

        self.book_manager = book_manager
        self.history = HistoryManager()
        self.settings = QSettings()

        self._results_last_shown_at = 0
        self._push_history_on_next_stage = False
        self._last_query = None

        self._finishedUiSetup = False

        self.setupUi()
        self.setupMacUi()
        self.setupEpwingProtocol()
        self.setupJavaScriptBridge()
        self.setupActions()
        self.setupTabOrder()
        self.setupKeyboardEventFilter()
        self.setupGestures()
        self.restoreUiState()
        self.setupFinalUi()

        self._finishedUiSetup = True



    def setupUi(self):
        ui = self.ui
        ui.setupUi(self)

        ui.searchResults.setFocusPolicy(Qt.StrongFocus)
        #ui.searchResults.setAttribute(Qt.WA_InputMethodEnabled, True)
        #ui.searchResults.ret

        # QListWidget is broken and won't accept Japanese input,
        # so we have to focus the search field after every interaction with the list,
        # until we have a more elegant solution (i.e. a proxy hidden text field)
        #for signal in ['itemClicked', 'currentRowChanged']:
            #getattr(ui.searchResults, signal).connect(lambda e: self.ui.searchField.search_field.setFocus())

        # Entry view
        ui.entryView.setScrollBar(ui.entryVerticalScrollBar, scroll_bar_container=ui.entryVerticalScrollBarContainer)
        # all links should fire the linkClicked signal
        ui.entryView.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        #entry_css = QUrl('data:text/css, body{font-family:Baskerville;color:orange}')#:/css/entryview.css')
        #print entry_css
        #ui.entryView.settings().setUserStyleSheetUrl(entry_css)

        ui.searchField.search_field.setFocus() #FIXME
        #ui.entryView.setSmoothScrolling(True)

        self.reload_books_list()
        self.reload_search_menu()
        self.reload_search_methods_list()


    def setupMacUi(self):
        ui = self.ui
        ui.searchResults.setAttribute(Qt.WA_MacShowFocusRect, False)
        #ui.searchResults.setStyleSheet('QListWidget { selection-background-color: #DDDDDD; selection-color: black; }')
        
        spacer = MSpacer()
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
        ui.history_buttons.left_button.setImageUrls(url_base + 'left.png', 
                                                    url_base + 'left-pressed.png', url_base + 'left-disabled.png')
        ui.history_buttons.right_button.setImageUrls(url_base + 'right.png',
                                                    url_base + 'right-pressed.png', url_base + 'right-disabled.png')
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
        self.ui.text_size_buttons.setFocusPolicy(Qt.NoFocus)
        url_base = ':/images/icons/toolbar/text-'
        ui.text_size_buttons.left_button.setImageUrls(url_base + 'smaller.png', 
                                                      url_base + 'smaller-pressed.png', 
                                                      url_base + 'smaller-disabled.png')
        ui.text_size_buttons.right_button.setImageUrls(url_base + 'bigger.png', 
                                                       url_base + 'bigger-pressed.png', 
                                                       url_base + 'bigger-disabled.png')
        ui.text_size_buttons.left_button.clicked.connect(lambda: ui.actionDecreaseFontSize.trigger())
        ui.text_size_buttons.right_button.clicked.connect(lambda: ui.actionIncreaseFontSize.trigger())
        ui.navToolbar.addWidget(ui.text_size_buttons)

    def setupEpwingProtocol(self):
        '''Sets up the epwing:// protocol handler for entryView.
        '''
        old_manager = self.ui.entryView.page().networkAccessManager()
        self._new_network_manager = MNetworkAccessManager(old_manager, self.book_manager, parent=old_manager.parent())
        #self._new_network_manager.finished.connect(self.testing)
        self.ui.entryView.page().setNetworkAccessManager(self._new_network_manager)
        #self.ui.entryView.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        self.ui.entryView.page().setForwardUnsupportedContent(True)

    def _setupJavaScriptBridge(self):
        self.ui.entryView.page().mainFrame().addToJavaScriptWindowObject('manabi', self.javascript_bridge)

    def setupJavaScriptBridge(self):
        '''Sets up the JS bridge for entryView.
        '''
        self.javascript_bridge = JavaScriptBridge(self)
        self._setupJavaScriptBridge()
        self.ui.entryView.page().mainFrame().javaScriptWindowObjectCleared.connect(self._setupJavaScriptBridge)

    def setupActions(self):
        '''Connect text edit and webkit signals to menu action slots, particularly for enable/disable.
        '''
        sf = self.ui.searchField.search_field
        ev = self.ui.entryView

        # edit menu for search field text selection
        #for action in [self.ui.actionCut, self.ui.actionCopy, self.ui.actionDelete]:
            #sf.selectionChanged.connect(lambda: action.setEnabled(sf.hasSelectedText()))

        # set enabled based on focus events
        for action in [self.ui.actionUndo, self.ui.actionRedo, self.ui.actionPaste, self.ui.actionSelectAll]:
            action.setEnabled(False)
            sf.lostFocus.connect(partial(action.setEnabled, False))
            sf.gotFocus.connect(partial(action.setEnabled, True))

        def enable_search_field_action(action):
            action.setEnabled(bool(self.ui.searchField.search_field.selectedText()))

        for action in [self.ui.actionCut, self.ui.actionCopy, self.ui.actionDelete]:
            action.setEnabled(False)
            sf.selectionChanged.connect(partial(enable_search_field_action, action))
            sf.lostFocus.connect(partial(action.setEnabled, False))
            sf.gotFocus.connect(partial(enable_search_field_action, action))

        # Select All for entryView
        ev.lostFocus.connect(partial(self.ui.actionSelectAll.setEnabled, False))
        ev.gotFocus.connect(partial(self.ui.actionSelectAll.setEnabled, True))

        # enable Copy for webkit text selection
        ev.page().selectionChanged.connect(
                lambda: self.ui.actionCopy.setEnabled(bool(self.ui.entryView.selectedText())))

        # keyboard shortcuts for back/forward
        shortcut = [QKeySequence(Qt.Key_BracketLeft), QKeySequence(Qt.Key_Left)]
        self.ui.actionBack.setShortcuts(shortcut)
        shortcut = [QKeySequence(Qt.Key_BracketRight), QKeySequence(Qt.Key_Right)]
        self.ui.actionForward.setShortcuts(shortcut)

    def setupTabOrder(self):
        ui = self.ui
        widgets = [ui.selectBook, ui.searchMethod, ui.searchField.search_field,
                   ui.searchResults, ui.entryView, ui.selectBook]

        for i in xrange(1, len(widgets)):
            QWidget.setTabOrder(widgets[i - 1], widgets[i])


    # event filter for keyboard events
    # --------
    def setupKeyboardEventFilter(self):
        self.key_press_filter = KeyPressFilter(parent=self)
        q_app = QApplication.instance()
        q_app.installEventFilter(self.key_press_filter)

    def setupGestures(self):
        self.grabGesture(Qt.SwipeGesture)

    def restoreUiState(self):
        '''Restores UI state from the last time it was opened.
        '''
        index = int(self.settings.value('ui_state/selected_book_index', -1).toPyObject())

        if index != -1:
            self.ui.selectBook.setCurrentIndex(index)
    
    def setupFinalUi(self):
        '''The last UI setup method to be called.
        '''
        self.refresh_history_buttons()



    # Search field UI
    # ---------------
    
    def on_searchField_returnPressed(self):
        sr, sf = self.ui.searchResults, self.ui.searchField

        if not sr.selectedItems():
            sr.setCurrentRow(0)

        if sr.currentItem():
            #TODO see todo file for notes on this: #sf.setText(sr.currentItem().text())
            #self.ui.entryView.setFocus()
            sr.setFocus()
            #sf.selectAll()
            #self.stage_history()

    def on_searchField_keyUpPressed(self):
        sr = self.ui.searchResults

        if sr.currentRow() > 0:
            sr.setCurrentRow(sr.currentRow() - 1)
            #self.stage_history()

    def on_searchField_keyDownPressed(self):
        sr = self.ui.searchResults
        if sr.currentRow() < sr.count() - 1:
            sr.setCurrentRow(sr.currentRow() + 1)
            #self.stage_history()

    def on_searchField_textEdited(self, text):
        self.do_search(unicode(text))

    def on_clearSearch_clicked(self):
        sr, sf = self.ui.searchResults, self.ui.searchField
        #self.push_history()
        #self._push_history_on_next_stage = True
        sr.clear()
        sf.search_field.setFocus()
        

    # Search results UI
    # -----------------

    def on_searchResults_currentItemChanged(self, current, previous):
        if current:
            #self.stage_history()
            item_data = current.data(Qt.UserRole).toPyObject()
            # if this result is a multi-dictionary search result, 
            # it will be a list. Otherwise it will be an Entry.
            if isinstance(item_data, (list, tuple)):
                self.show_entries(item_data)
            else:
                self.show_entry(item_data)
            #self.stage_history()


    def on_searchResults_itemActivated(self, item):
        self.ui.entryView.setFocus()
    
    def on_searchResults_returnPressed(self):
        self.ui.entryView.setFocus()

    def on_searchResults_lostFocus(self):
        pass

    def on_searchResults_gainedFocus(self):
        pass


    # Entry view UI
    # -------------
    
    def on_entryView_linkClicked(self, url):
        url = unicode(url.toString())
        #print url

        #self.stage_history()
        #self.push_history()
        self._push_history_on_next_stage = True

        if '#' in url:
            # it contains a hash, which will scroll the view to the given named anchor
            self.load_url(url, show_loading_message=False)
            #self.ui.entryView.scrollToAnchor(hash_string)
        else:
            resource = route_dictionary_uri(url, self.book_manager.books.values())
            self.show_entry(resource)

    def on_entryView_loadFinished(self, ok):
        # rewrite links to point to anchors in the page
        self.ui.entryView.page().mainFrame().evaluateJavaScript('fix_anchor_links();')


    # Other UI
    # --------

    @pyqtSignature('int')
    def on_selectBook_currentIndexChanged(self, index):
        self.do_search()
        if self._finishedUiSetup:
            self.settings.setValue('ui_state/selected_book_index', int(index))

    @pyqtSignature('int')
    def on_searchMethod_currentIndexChanged(self, index):
        self.do_search()


    # toolbar actions
    # ---------------

    @pyqtSignature('')
    def on_actionBack_triggered(self):
        '''Action for toolbar button.
        '''
        self.go_back()

    @pyqtSignature('')
    def on_actionForward_triggered(self):
        '''Action for toolbar button.
        '''
        self.go_forward()

    @pyqtSignature('')
    def on_actionBack2_triggered(self):
        '''Action for menu item.
        '''
        self.go_back()

    @pyqtSignature('')
    def on_actionForward2_triggered(self):
        '''Action for menu item.
        '''
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
        self.reload_search_menu()

    # Edit Menu
    
    @pyqtSignature('')
    def on_actionUndo_triggered(self):
        self.ui.searchField.search_field.undo()

    @pyqtSignature('')
    def on_actionRedo_triggered(self):
        self.ui.searchField.search_field.redo()

    @pyqtSignature('')
    def on_actionCut_triggered(self):
        self.ui.searchField.search_field.cut()

    @pyqtSignature('')
    def on_actionCopy_triggered(self):
        if self.ui.searchField.search_field.hasFocus():
            self.ui.searchField.search_field.copy()
        elif self.ui.entryView.hasFocus():
            self.ui.entryView.page().triggerAction(QWebPage.Copy)

    @pyqtSignature('')
    def on_actionPaste_triggered(self):
        self.ui.searchField.search_field.paste()

    @pyqtSignature('')
    def on_actionDelete_triggered(self):
        self.ui.searchField.search_field.removeSelectedText()

    @pyqtSignature('')
    def on_actionSelectAll_triggered(self):
        if self.ui.searchField.search_field.hasFocus():
            self.ui.searchField.search_field.selectAll()
        elif self.ui.entryView.hasFocus():
            self.ui.entryView.page().triggerAction(QWebPage.SelectAll)

    @pyqtSignature('')
    def on_actionSearchForANewWord_triggered(self):
        '''Selects the search field, so the user can start searching for something new.
        '''
        self.ui.searchField.search_field.setFocus()
        self.ui.searchField.search_field.selectAll()





    # general methods
    # ---------------

    def _refresh_history_menu(self, menu, history_items, direction):
        '''`direction` is 1 or -1 and indicates if this is for forward or back.
        '''
        menu.clear()
        for index, item in enumerate(history_items, start=1):
            action = QAction(item.label, menu)
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
            history_item = self.history.go(index)
            #print 'going {0} to:'.format(index)#,
            #print back_item
            #print len(self.history)
            self.load_history_item(history_item)
            #if 'search_results' in back_item:
                #self.show_results(back_item['search_results'])
                #self.ui.searchResults.setCurrentRow(back_item['search_results_current_row'])
            #self.show_entry(back_item['entry'])
            #if 'entry_hash' in back_item:
                #self.ui.entryView.scrollToAnchor(back_item['entry_hash'])
            #if 'book' in back_item:
                #self.select_book(book=back_item['book'])
        except IndexError:
            # already at edge of history, ignore request
            pass
        self.refresh_history_buttons()

    def create_history_item(self, url=None):
        '''Creates a UrlHistoryItem based on the current entry's heading and 
        '''
        if not url:
            # get current entry URL
            url = unicode(self.ui.entryView.url().toString())

        #print url
        entries = route_dictionary_uri(url, self.book_manager.books.values())

        if not entries:
            # no matching entries for this URL
            return None

        if isinstance(entries, (list, tuple)):
            entry = entries[0]
        else:
            entry = entries

        label = entry.heading if entry.heading else entry.guess_heading_from_text()
        label = strip_tags(label)
        item = UrlHistoryItem(label, url)
        return item

    def load_history_item(self, item):
        url = item.url
        self.load_url(url, stage_history=False)

    def push_history(self):
        '''Pushes the currently staged back item to the history manager.
        '''
        #print self.history
        #if self._staged_back_item
        #FIXME
        if self.history.current_location:
            self.history.push()

        self.refresh_history_buttons()
        

    def stage_history(self, clear_forward_items=True, label=None, url=None):
        '''Set the staged back item to the current entry and search context.
        `label` is what the history item will show as in menus. Defaults to the entry heading.
        '''
        if self._push_history_on_next_stage:
            self.push_history()
            self._push_history_on_next_stage = False

        item = self.create_history_item(url=url)
        self.history.current_location = item

        if clear_forward_items:
            self.history.forward_items = []

                #lines = strip_tags(entry.text.replace('<br>', '\n')).split()
        #'search_results': self._current_results,
        #'search_results_current_row': self.ui.searchResults.currentRow(),
            #'':

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
        '''Returns the currently selected book's EpwingBook instance,
        or BookCategory instance if a category is selected instead.
        '''
        sb = self.ui.selectBook
        if not sb.count(): return None

        selected_data = sb.itemData(sb.currentIndex())
        if selected_data.type() == QVariant.String:
            selected_data = selected_data.toString()
            return self.book_manager.books[unicode(selected_data)]
        else:
            return selected_data.toPyObject()

    def select_next_book(self):
        sb = self.ui.selectBook
        index = sb.currentIndex()

        if index < sb.count() - 1:
            if sb.itemText(index + 1):
                sb.setCurrentIndex(index + 1)
            else:
                # would have been a eparator item
                sb.setCurrentIndex(index + 2)
        else:
            sb.setCurrentIndex(0)

    def select_previous_book(self):
        sb = self.ui.selectBook
        index = sb.currentIndex()

        if index > 0:
            if sb.itemText(index - 1):
                sb.setCurrentIndex(index - 1)
            else:
                # would have been a eparator item
                sb.setCurrentIndex(index - 2)
        else:
            sb.setCurrentIndex(sb.count() - 1)
    
    def select_book(self, book=None, all_books=False, category=None):
        '''Selects the book given an EpwingBook instance, or everything if `all_books` is True.
        Will select a category instead if `category` is not None.
        '''
        sb = self.ui.selectBook
        if all_books:
            index = 0
        elif category:
            index = sb.findText(category.label)
        else:
            index = sb.findData(book.id)
        if index != -1:
            sb.setCurrentIndex(index)

    def reload_search_menu(self):
        '''Same as `reload_books_list` except for the menu bar Search item.
        '''
        sm = self.ui.menuSearch

        sm.clear()

        number = 0
        def get_shortcut(number):
            if number <= 9:
                return [QKeySequence(Qt.CTRL + getattr(Qt, 'Key_' + str(number)))]

        # add 'All' options
        action_all = sm.addAction('All Dictionaries')
        action_all.triggered.connect(partial(self.select_book, all_books=True))
        shortcut = get_shortcut(number)
        if shortcut:
            action_all.setShortcuts(shortcut)
            number += 1
        sm.addSeparator()


        # add categories
        for category in self.book_manager.categories:
            action = sm.addAction(category.label)
            action.triggered.connect(partial(self.select_book, category=category))
            shortcut = get_shortcut(number)
            if shortcut:
                action.setShortcuts(shortcut)
                number += 1
        sm.addSeparator()

        # add books
        for book in self.book_manager.books.values():
            action = sm.addAction(book.name)
            action.triggered.connect(partial(self.select_book, book=book))
            shortcut = get_shortcut(number)
            if shortcut:
                action.setShortcuts(shortcut)
                number += 1
        sm.addSeparator()

        # prev / next
        action = sm.addAction('Select Next Dictionary')
        action.triggered.connect(self.select_next_book)
        action.setShortcuts([QKeySequence(Qt.CTRL + Qt.Key_BraceRight)])
        action = sm.addAction('Select Previous Dictionary')
        action.triggered.connect(self.select_previous_book)
        action.setShortcuts([QKeySequence(Qt.CTRL + Qt.Key_BraceLeft)])



    def reload_books_list(self):
        '''Fills the book combobox with available books.
        Call this after updating installed book preferences, and on first launch.

        Also adds the categories of available books, for searching across multiple books.

        This will duplicate the entries into the menu bar as well, under the Search item.
        '''
        sb = self.ui.selectBook

        selected_data = sb.itemData(sb.currentIndex())
        if selected_data.type() == QVariant.String:
            selected_data = selected_data.toString()
        else:
            selected_data = selected_data.toPyObject()
        #current_book_id = unicode(sb.itemData(sb.currentIndex()).toString())# if sb.currentIndex() else None

        sb.clear()

        # add 'all' option
        sb.addItem('All', None)
        sb.insertSeparator(sb.count())
        
        # add categories
        for category in self.book_manager.categories:
            sb.addItem(category.label, category)
        else:
            # add separator
            sb.insertSeparator(sb.count())

        # add books
        for book_id, book in self.book_manager.books.items():
            sb.addItem(book.name, book_id)

        index = sb.findData(selected_data)
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
        '''Performs search.
        '''
        selected_book = self.selected_book()
        #if not selected_book: return

        if not query:
            query = unicode(self.ui.searchField.search_field.text())

        if self._last_query is None:
            self._last_query = query
        elif query != self._last_query:
            self._push_history_on_next_stage = True
            self._last_query = query

        if not search_method:
            search_method = self.selected_search_method()

        if selected_book is None:
            # search all
            results = self.book_manager.search_all(
                    query, search_method=search_method, max_results_per_book=max_results_per_book)
        elif inspect.isclass(selected_book) and issubclass(selected_book, BookCategory):
            # category search
            results = self.book_manager.search_category(
                    selected_book, query, search_method=search_method, max_results_per_book=max_results_per_book)
        else:
            results = list(islice(selected_book.search(
                    query, search_method=search_method), 0, max_results_per_book))

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

        html_hints = ['<', '>', '&lt;', '&gt;']
        def add_result(heading, result):
            # add an HTML item if it contains HTML

            if any(imap(lambda x: x in heading, html_hints)):
                sr.addHtmlItem(heading, result)
            else:
                item = QListWidgetItem(heading)
                item.setData(Qt.UserRole, result)
                sr.addItem(item)

        if isinstance(results, dict):
            def sort_key(e):
                return e[1]
                #print e
                #key = e[0]
                #return key.lower().strip()

            for heading, entries in sorted(results.items(), key=sort_key):
                if ran_at < self._results_last_shown_at:
                    return
                add_result(heading, entries)
                if not i % 3:
                    q_app.processEvents()
                i += 1
        else:
            for result in results:
                if ran_at < self._results_last_shown_at:
                    return
                add_result(result.heading, result)
                if not i % 3:
                    q_app.processEvents()
                i += 1

        sr.scrollToItem(self.ui.searchResults.item(0))

    def _set_entryView_body(self, body_html):
        '''Sets the entryView's HTML to be `body_html` wrapped with the propery html and body tags.
        '''
        html = u''.join([u'''
            <html>
                <head><link rel="stylesheet" type="text/css" href="qrc:/css/entryview.css"></head>
                <body>''', body_html, u'</body></html>'])
        self.ui.entryView.setHtml(html)

    def _show_loading_message(self):
        self._set_entryView_body(u'Loading…')
        q_app = QApplication.instance()
        q_app.processEvents()

    def _generate_url(self, is_collection, *entries):
        '''`is_collection` denotes whether this URL will point to a collection of entries.
        It only matters when a single entry is passed yet should still be rendered as a collection of entries,
        since the dictionary title needs to be displayed in that case.
        '''
        entry_uris = [entry.uri for entry in entries]
        url = '&'.join(entry_uris)

        if is_collection:
            url = collection_uri_prefix + url

        url = self.EPWING_URL_PROTOCOL + url
        return url

    def show_entry(self, entry):
        url = self._generate_url(False, entry)
        self.load_url(url)

    def show_entries(self, entries):
        url = self._generate_url(True, *entries)
        self.load_url(url)


    def load_url(self, url, show_loading_message=True, stage_history=True):
        '''`url` is a string.
        '''
        if show_loading_message:
            self._show_loading_message()

        self.ui.entryView.load(QUrl(url))

        if stage_history:
            self.stage_history(url=url)





