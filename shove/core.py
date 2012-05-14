# -*- coding: utf-8 -*-
'''shove core.'''

from stuf.six import items

from shove.base import BaseStore
from shove.loadpoints import cache_backend, store_backend

__all__ = ('Shove', 'MultiShove')


class Shove(BaseStore):

    '''
    Common object frontend class.
    '''

    def __init__(self, store='simple://', cache='simple://', **kw):
        super(Shove, self).__init__(store, **kw)
        # load store backend
        self._store = store_backend(store, **kw)
        # load cache backend
        self._cache = cache_backend(cache, **kw)
        # buffer for lazy writing
        self._buffer = dict()
        # setting for syncing frequency
        self._sync = kw.get('sync', 2)

    def __getitem__(self, key):
        '''
        Gets a item from shove.
        '''
        try:
            return self._cache[key]
        except KeyError:
            # synchronize cache with store
            self.sync()
            self._cache[key] = value = self._store[key]
            return value

    def __setitem__(self, key, value):
        '''
        Sets an item in shove.
        '''
        self._cache[key] = self._buffer[key] = value
        # when buffer reaches self._limit, write buffer to store
        if len(self._buffer) >= self._sync:
            self.sync()

    def __delitem__(self, key):
        '''
        Deletes an item from shove.
        '''
        try:
            del self._cache[key]
        except KeyError:
            pass
        self.sync()
        del self._store[key]

    def keys(self):
        '''
        Returns a list of keys in shove.
        '''
        self.sync()
        return self._store.keys()

    def sync(self):
        '''
        Writes buffer to store.
        '''
        store = self._store
        for k, v in items(self._buffer):
            store[k] = v
        self._buffer.clear()

    def close(self):
        '''
        Finalizes and closes shove.
        '''
        # if close has been called, pass
        if self._store is not None:
            try:
                self.sync()
            except AttributeError:
                pass
            self._store.close()
            self._store = self._cache = self._buffer = None


class MultiShove(BaseStore):

    '''
    Common frontend to multiple object stores.
    '''

    def __init__(self, *stores, **kw):
        # init superclass with first store
        super(MultiShove, self).__init__('', **kw)
        if not stores:
            stores = ('simple://',)
        # load stores
        self._stores = list(store_backend(i, **kw) for i in stores)
        # load cache
        self._cache = cache_backend(kw.get('cache', 'simple://'), **kw)
        # buffer for lazy writing
        self._buffer = dict()
        # setting for syncing frequency
        self._sync = kw.get('sync', 2)

    def __getitem__(self, key):
        '''
        Get a item from shove.
        '''
        try:
            return self._cache[key]
        except KeyError:
            # synchronize cache and store
            self.sync()
            # get value from first store
            self._cache[key] = value = self._stores[0][key]
            return value

    def __setitem__(self, key, value):
        '''
        Sets an item in shove.
        '''
        self._cache[key] = self._buffer[key] = value
        # when the buffer reaches self._limit, writes the buffer to the store
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
        '''
        Returns a list of keys in shove.
        '''
        self.sync()
        return self._stores[0].keys()

    def sync(self):
        '''
        Writes buffer to store.
        '''
        stores = self._stores
        for k, v in items(self._buffer):
            # sync all stores
            for store in stores:
                store[k] = v
        self._buffer.clear()

    def close(self):
        '''
        Finalizes and closes shove stores.
        '''
        # if close has been called, pass
        stores = self._stores
        if self._stores is not None:
            self.sync()
            # close stores
            for idx, store in enumerate(stores):
                store.close()
                stores[idx] = None
            self._cache = self._buffer = self._stores = None
