

class HistoryItem(object):

    def __init__(self, label):
        self.label = label
        self.entries = None
        self.entry = None


class UrlHistoryItem(HistoryItem):

    def __init__(self, label, url):
        super(UrlHistoryItem, self).__init__(label)
        self.url = url
        


#class EntryHistoryItem(HistoryItem):

    #def __init__(self, label, entries):
        #super(EntryHistoryItem, self).__init__(label)
        #self.entry = entry
    

#class CombinedEntriesHistoryItem(HistoryItem):

    #def __init__(self, label, entries):
        #super(CombinedEntryHistoryItem, self).__init__(label)
        #self.entries = entries
