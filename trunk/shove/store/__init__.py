from shove.store.simple import SimpleStore

__all__ = ['SyncStore', 'atom', 'bsddb', 'db', 'durus',
    'file', 'ftp', 'memory', 's3', 'simple', 'svn', 'zodb']


class SyncStore(SimpleStore):

    def __init__(self, engine, **kw):
        super(SyncStore, self).__init__(engine, **kw)

    def __setitem__(self, key, value):        
        super(SyncStore, self).__setitem__(key, value)
        self.sync()

    def __delitem__(self, key):
        super(SyncStore, self).__delitem__(key)
        self.sync()