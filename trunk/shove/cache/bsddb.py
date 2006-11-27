import bsddb
try:
    from cStringIO import StringIO
except ImportError:
    from cStringIO import StringIO
try:
    import cPickle as pickle
except ImportError:
    import pickle
from shove import synchronized
from shove.cache.memory import MemoryCache

__all__ = ['BsddbCache']


class BsddbCache(MemoryCache):

    def __init__(engine, **kw):
        super(BsddbCache, self).__init__(engine, **kw)
        db = engine.split('/', 2)
        self._cache = bsddb.htopen(db)
        
    @synchronized
    def __getitem__(self, key):
        '''Fetch a given key from the cache.  If the key does not exist, return
        default, which itself defaults to None.

        @param key Keyword of item in cache.
        @param default Default value (default: None)
        '''
        local = StringIO(self._cache[key])
        exp, now = pickle.load(local), time.time()
        # Remove item if time has expired.
        if exp < now: del self._cache[key]        
        return pickle.load(f)
                
    @synchronized
    def __setitem__(self, key, value):
        '''Set a value in the cache.

        @param key Keyword of item in cache.
        @param value Value to be inserted in cache.        
        '''
        if len(self._store) > self._max_entries: self._cull()
        local = StringIO()
        pickle.dump(time.time() + self.timeout, local, 2)
        pickle.dump(value, local, 2)
        self._cache[key] = local.getvalue()