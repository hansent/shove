import bsddb
try:
    import cPickle as pickle
except ImportError:
    import pickle
from shove import synchronized
from shove.store.memory import MemoryStore


class BsddbStore(MemoryStore):

    def __init__(engine, **kw):
        super(BsddbStore, self).__init__(engine, **kw)
        db = engine.split('/', 2)
        self._store = bsddb.htopen(db)

    @synchronized
    def __getitem__(self, key):
        return pickle.loads(self._store[key])

    @synchronized        
    def __setitem__(self, key, value):        
        self._store[key] = pickle.dumps(value)
        self._store.sync()

    @synchronized
    def __delitem__(self, key):
        del self._store[key]
        self._store.sync()