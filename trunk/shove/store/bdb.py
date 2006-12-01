import bsddb
try:
    import cPickle as pickle
except ImportError:
    import pickle
from shove.store.memory import MemoryStore


class BsdStore(MemoryStore):

    def __init__(self, engine, **kw):
        super(BsdStore, self).__init__(engine, **kw)
        if engine.startswith('bsd:'): engine = engine.split(':', 1)[1]
        self._store = bsddb.hashopen(engine)

    def __getitem__(self, key):
        return pickle.loads(super(BsdStore, self)[key])

    def __setitem__(self, key, value):
        super(BsdStore, self)[key] = pickle.dumps(value)
        self._store.sync()

    def __delitem__(self, key):
        del super(BsdStore, self)[key]
        self._store.sync()