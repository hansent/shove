import bsddb
try:
    import cPickle as pickle
except ImportError:
    import pickle
from shove.store.memory import MemoryStore


class BsdbStore(MemoryStore):

    def __init__(self, engine, **kw):
        super(BsdbStore, self).__init__(engine, **kw)
        self._store = bsddb.hashopen(engine.split('/', 2))

    def __getitem__(self, key):
        return pickle.loads(super(BsdbStore, self).__getitem__(key))

    def __setitem__(self, key, value):
        super(BsdbStore, self).__setitem__(key, pickle.dumps(value))
        self._store.sync()

    def __delitem__(self, key):
        super(BsdbStore, self).__delitem__(key)
        self._store.sync()