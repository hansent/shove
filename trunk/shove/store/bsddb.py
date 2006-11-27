import bsddb
try:
    import cPickle as pickle
except ImportError:
    import pickle
from shove.store.simple import SimpleStore


class BsddbStore(SimpleStore):

    def __init__(engine, **kw):
        super(BsddbStore, self).__init__(engine, **kw)

   def __getitem__(self, key):
       return pickle.loads(self._store[key])
        
    def __setitem__(self, key, value):        
        self._store[key] = pickle.dumps(value)