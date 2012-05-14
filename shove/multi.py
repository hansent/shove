# -*- coding: utf-8 -*-
'''
Common frontend for storing objects in multiple storage backends at once.
'''

from shove.core import BaseStore, getbackend, stores, caches

__all__ = ['MultiShove']


class MultiShove(BaseStore):

    '''
    Common frontend to multiple object stores.
    '''

    def __init__(self, *a, **kw):
        # Init superclass with first store
        super(MultiShove, self).__init__('', **kw)
        if not a:
            a = ('simple://',)
        # Load stores
        self._stores = list(getbackend(i, stores, **kw) for i in a)
        # Load cache
        self._cache = getbackend(kw.get('cache', 'simple://'), caches, **kw)
        # Buffer for lazy writing and setting for syncing frequency
        self._buffer, self._sync = dict(), kw.get('sync', 2)

    def __getitem__(self, key):
        '''Gets a item from shove.'''
        try:
            return self._cache[key]
        except KeyError:
            # Synchronize cache and store
            self.sync()
            # Get value from first store
            value = self._stores[0][key]
            self._cache[key] = value
            return value

    def __setitem__(self, key, value):
        '''Sets an item in shove.'''
        self._cache[key] = self._buffer[key] = value
        # When the buffer reaches self._limit, writes the buffer to the store
        if len(self._buffer) >= self._sync:
            self.sync()

    def __delitem__(self, key):
        '''
        Deletes an item from multiple stores.
        '''
        try:
            del self._cache[key]
        except KeyError:
            pass
        self.sync()
        for store in self._stores:
            del store[key]

    def keys(self):
        '''Returns a list of keys in shove.'''
        self.sync()
        return self._stores[0].keys()

    def sync(self):
        '''Writes buffer to store.'''
        for k, v in self._buffer.iteritems():
            # Sync all stores
            for store in self._stores:
                store[k] = v
        self._buffer.clear()

    def close(self):
        '''Finalizes and closes shove stores.'''
        # If close has been called, pass
        if self._stores is not None:
            self.sync()
            # Close stores
            for idx, store in enumerate(self._stores):
                store.close()
                self._stores[idx] = None
            self._cache = self._buffer = self._stores = None
