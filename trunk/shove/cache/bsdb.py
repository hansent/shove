import bsddb
import time
try:
    from cStringIO import StringIO
except ImportError:
    from cStringIO import StringIO
try:
    import cPickle as pickle
except ImportError:
    import pickle
from shove.cache.memory import MemoryCache

__all__ = ['BsddbCache']


class BsdbCache(MemoryCache):

    def __init__(self, engine, **kw):
        super(BsdbCache, self).__init__(engine, **kw)
        self._cache = bsddb.hashopen(engine.split('/', 2))
        
    def __getitem__(self, key):
        '''Fetch a given key from the cache.  If the key does not exist, return
        default, which itself defaults to None.

        @param key Keyword of item in cache.
        @param default Default value (default: None)
        '''
        local = StringIO(super(BsdbCache, self).__getitem__(key))
        exp, now = pickle.load(local), time.time()
        # Remove item if time has expired.
        if exp < now: del self._cache[key]        
        return pickle.load(local)
                
    def __setitem__(self, key, value):
        '''Set a value in the cache.

        @param key Keyword of item in cache.
        @param value Value to be inserted in cache.        
        '''
        if len(self._cache) > self._max_entries: self._cull()
        local = StringIO()
        pickle.dump(time.time() + self.timeout, local, 2)
        pickle.dump(value, local, 2)
        super(BsdbCache, self).__setitem__(key, local.getvalue())