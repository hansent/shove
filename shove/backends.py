# -*- coding: utf-8 -*-
'''shove backend support.'''

import os
from collections import deque
from os.path import exists, join

from shove.base import Base
from shove._compat import url2pathname, quote_plus, unquote_plus


class FileBase(Base):

    '''
    Base for file based storage.
    '''

    def __init__(self, engine, **kw):
        super(FileBase, self).__init__(engine, **kw)
        if engine.startswith('file://'):
            engine = url2pathname(engine.split('://')[1])
        self._dir = engine
        # Create directory
        if not exists(self._dir):
            self._createdir()

    def __getitem__(self, key):
        # (per Larry Meyn)
        try:
            with open(self._key_to_file(key), 'rb') as item:
                return self.loads(item.read())
        except:
            raise KeyError(key)

    def __setitem__(self, key, value):
        # (per Larry Meyn)
        try:
            with open(self._key_to_file(key), 'wb') as item:
                item.write(self.dumps(value))
        except (IOError, OSError):
            raise KeyError(key)

    def __delitem__(self, key):
        try:
            os.remove(self._key_to_file(key))
        except (IOError, OSError):
            raise KeyError(key)

    def __contains__(self, key):
        return exists(self._key_to_file(key))

    def __len__(self):
        return len(os.listdir(self._dir))

    def _createdir(self):
        # creates the store directory
        try:
            os.makedirs(self._dir)
        except OSError:
            raise EnvironmentError(
                'Cache directory "%s" does not exist and '
                'could not be created' % self._dir
            )

    def _key_to_file(self, key):
        # gives the filesystem path for a key
        return join(self._dir, quote_plus(key))

    def keys(self):
        '''
        Returns a list of keys in the store.
        '''
        return list(unquote_plus(name) for name in os.listdir(self._dir))


class SimpleBase(Base):

    '''
    Single-process in-memory store base.
    '''

    def __init__(self, engine, **kw):
        super(SimpleBase, self).__init__(engine, **kw)
        self._store = dict()

    def __getitem__(self, key):
        try:
            return self._store[key]
        except:
            raise KeyError(key)

    def __setitem__(self, key, value):
        self._store[key] = value

    def __delitem__(self, key):
        try:
            del self._store[key]
        except:
            raise KeyError(key)

    def __len__(self):
        return len(self._store)

    def keys(self):
        '''
        Returns a list of keys in the store.
        '''
        return self._store.keys()


class LRUBase(SimpleBase):

    def __init__(self, engine, **kw):
        super(LRUBase, self).__init__(engine, **kw)
        self._max_entries = kw.get('max_entries', 300)
        self._hits = 0
        self._misses = 0
        self._queue = deque()
        self._refcount = dict()

    def __getitem__(self, key):
        try:
            value = super(LRUBase, self).__getitem__(key)
            self._hits += 1
        except KeyError:
            self._misses += 1
            raise
        self._housekeep(key)
        return value

    def __setitem__(self, key, value):
        super(LRUBase, self).__setitem__(key, value)
        self._housekeep(key)
        if len(self._store) > self._max_entries:
            queue = self._queue
            store = self._store
            max_entries = self._max_entries
            refcount = self._refcount
            delitem = super(LRUBase, self).__delitem__
            while len(store) > max_entries:
                k = queue.popleft()
                refcount[k] -= 1
                if not refcount[k]:
                    delitem(k)
                    del refcount[k]

    def _housekeep(self, key):
        self._queue.append(key)
        self._refcount[key] = self._refcount.get(key, 0) + 1
        if len(self._queue) > self._max_entries * 4:
            queue = self._queue
            refcount = self._refcount
            for _ in [None] * len(queue):
                k = queue.popleft()
                if refcount[k] == 1:
                    queue.append(k)
                else:
                    refcount[k] -= 1


class DBBase(Base):

    '''Database common base.'''

    def __init__(self, engine, **kw):
        super(DBBase, self).__init__(engine, **kw)

    def __delitem__(self, key):
        self._store.delete(self._store.c.key == key).execute()

    def __len__(self):
        return self._store.count().execute().fetchone()[0]
