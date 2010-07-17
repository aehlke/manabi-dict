
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.Qt import Qt
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

from epywing.uris import route as route_dictionary_uri, collection_uri_prefix
import time


EPWING_URL_SCHEME = 'epwing'


class EpwingRenderer(QThread):

    readyRead = pyqtSignal()
    #finished = pyqtSignal()
    #beginning = pyqtSignal()

    def __init__(self, resource, parent=None):
        '''`resource` is an Entry or a list of entries to render.
        '''
        QThread.__init__(self, parent)
        self.resource = resource
        self.exiting = False

        stylesheet_file = QFile(':/css/entryview.css')
        stylesheet_file.open(QFile.ReadOnly)
        self.stylesheet = unicode(QString(stylesheet_file.readAll()))

        #self.beginning.connect(self._begin)

    def stop(self):
        self.exiting = True

    def __del__(self):
        self.exiting = True

    def render(self):
        self.start()

    def run(self):
        if isinstance(self.resource, (list, tuple)):
            self._render(self.render_entries(self.resource))
        else:
            self._render(self.render_entry(self.resource))

    def readAll(self):
        content = self.content
        self.content = ''
        return content

    def _render(self, renderer):
        '''`renderer` is an iterator that yields the data to be outputted.
        '''
        self.offset = 0
        self.content = ''
        for chunk in renderer:
            if self.exiting:
                break

            self.content = ''.join([self.content, chunk.encode('utf8')])

            # queue the signal rather than emit it directly since the browser
            # hasn't connected to it yet while initializing this object.
            QTimer.singleShot(0, self, SIGNAL('readyRead()'))
            #time.sleep(0.2)

        #QTimer.singleShot(0, self, SIGNAL('finished()'))

    def render_entry(self, entry):
        '''Renders a single entry.
        '''
        yield self._before_body()

        for chunk in entry.text_iterator():
            yield chunk

        yield self._after_body()

    def render_entries(self, entries):
        '''Render a list of entries, presumably from multiple dictionaries.
        They will be separated by a divider that can be clicked to hide its entry.
        '''
        def qrc_png_base64_data(path):
            import base64
            f = QFile(path)
            f.open(QFile.ReadOnly)
            data = QByteArray(f.readAll())
            b = str(QString(base64.b64encode(data)))
            return b

        stylesheet_file = QFile(':/css/entryview.css')
        stylesheet_file.open(QFile.ReadOnly)
        self.stylesheet = unicode(QString(stylesheet_file.readAll()))

        divider = u''.join([u'''
            <table width="98%" class="dict-divider" onclick="toggle_entry('entry-{0}', 'arrow-down-{0}', 'arrow-up-{0}');">
                <tr>
                    <td>
                        <img src="data:image/png;base64,''', qrc_png_base64_data(':/images/DisclosureDown.png'),
                        '''" class="dict-divider-arrow" id="arrow-down-{0}" style="display:block">
                        <img src="data:image/png;base64,''', qrc_png_base64_data(':/images/DisclosureUp.png'),
                        '''" class="dict-divider-arrow" id="arrow-up-{0}" style="display:none">
                    </td>
                    <td width="49%"><hr style="border-style:solid none none none; border-width:1px"></td>
                    <td style="white-space:nowrap" class="dict-name">{1}</td>
                    <td width="49%"><hr style="border-style:solid none none none; border-width:1px"></td>
                </tr>
            </table>
        '''])
        entry_counter = 0

        yield self._before_body()

        for entry in entries:
            # add the divider with the entry's book title
            yield divider.format(entry_counter, entry.parent.name)

            # add the entry's text
            yield u'<div class="dict-entry" id="entry-{0}">'.format(entry_counter)

            for chunk in entry.text_iterator():
                yield chunk

            yield u'</div>'

            entry_counter += 1
        yield self._after_body()


    def _before_body(self):
        '''Returns HTML before the body.
        '''
        return u''.join([u'''
            <html>
                <head>
                    <style type="text/css">''',
                        self.stylesheet,
                    '''
                    </style>
                    <script type="text/javascript">
                        function toggle_entry(entry_id, arrow_down_id, arrow_up_id) {
                            var entry = document.getElementById(entry_id);
                            var arrow_down = document.getElementById(arrow_down_id);
                            var arrow_up = document.getElementById(arrow_up_id);

                            if (entry.style.display == 'none') {
                                entry.style.display = 'block';
                                arrow_down.style.display = 'block';
                                arrow_up.style.display = 'none';
                            } else {
                                entry.style.display = 'none';
                                arrow_down.style.display = 'none';
                                arrow_up.style.display = 'block';
                            }
                        }

                        function get_text_of_children(node) {
                            // returns the text of all children of `node`
                            return 'textContent' in node ? node.textContent : node.innerText;
                        }

                        function search(node) {
                            // performs a search for the given node's text, using whatever search method is selected
                            var query = get_text_of_children(node);
                            manabi.search(query);
                        }
                    </script>
                </head>
                <body>'''])

    def _after_body(self):
        return u'</body></html>'



class EpwingReply(QNetworkReply):

    url_scheme = EPWING_URL_SCHEME

    def __init__(self, access_manager, request, url, operation, book_manager):
        QNetworkReply.__init__(self, access_manager)

        self.book_manager = book_manager

        uri = unicode(url.toEncoded()).split(self.url_scheme + '://')[1]
        self.resource = route_dictionary_uri(uri, self.book_manager.books.values())

        self.offset = 0
        self.content = ''
        self.aborted = False

        self.setHeader(QNetworkRequest.ContentTypeHeader, QVariant('text/html; charset=UTF-8'))
        self.setRequest(request)
        self.setUrl(url)

        self.open(self.ReadOnly | self.Unbuffered)

        self.renderer = EpwingRenderer(self.resource, parent=self)
        self.renderer.finished.connect(self._finished)
        self.renderer.terminated.connect(self._finished)
        self.renderer.readyRead.connect(self.get_rendered_data)
        self.renderer.render()
        #self.setHeader(QNetworkRequest.ContentLengthHeader, QVariant(len(self.content)))

    def __del__(self):
        #self.renderer.__del__()
        self.renderer.stop()
        self.renderer.wait()

    @pyqtSlot()
    def _finished(self):
        QTimer.singleShot(0, self, SIGNAL('finished()'))

    def abort(self):
        '''Public slot to abort the operation.
        '''
        self.renderer.stop()

    def bytesAvailable(self):
        if self.content:
            return len(self.content) - self.offset

    @pyqtSlot()
    def get_rendered_data(self):
        self.content = ''.join([self.content, self.renderer.readAll()])
        self.readyRead.emit()
        #QTimer.singleShot(0, self, SIGNAL('readyRead()'))

    def isSequential(self):
        return True
    
    def readData(self, maxSize):
        if self.offset < len(self.content):
            end = min(self.offset + maxSize, len(self.content))
            data = self.content[self.offset:end]
            self.offset = end

            return data



class MNetworkAccessManager(QNetworkAccessManager):

    url_scheme = EPWING_URL_SCHEME

    def __init__(self, old_manager, book_manager, parent=None):
        QNetworkAccessManager.__init__(self, parent)
        self.parent = parent
        self.old_manager = old_manager

        self.book_manager = book_manager
        self.setCache(old_manager.cache())
        #self.setCookieJar(old_manager.cookieJar())
        #self.setProxy(old_manager.proxy())
        #self.setProxyFactory(old_manager.proxyFactory())
    

    def createRequest(self, operation, request, data):
        if operation == self.GetOperation:
            if request.url().scheme() == self.url_scheme:
                # handle epwing:// urls separately by creating custom QNetworkReply objects.
                reply = EpwingReply(self, request, request.url(), self.GetOperation, self.book_manager)
                
                return reply
                

        #return self.old_manager.createRequest(operation, request, data)
        return QNetworkAccessManager.createRequest(self, operation, request, data)
