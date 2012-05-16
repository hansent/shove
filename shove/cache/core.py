# -*- coding: utf-8 -*-
'''
shove cache core
'''

import random
from time import time
from copy import deepcopy
from threading import Condition

from shove._compat import synchronized
from shove.backends import SimpleBase, LRUBase, FileBase

__all__ = [
    'SimpleLRUCache', 'SimpleCache', 'MemoryCache', 'MemoryLRUCache',
    'FileCache', 'FileLRUCache',
]


class SimpleCache(SimpleBase):

    '''
    Single-process in-memory cache.

    The shove URI for a simple cache is:

    simple://
    '''

    def __init__(self, engine, **kw):
        super(SimpleCache, self).__init__(engine, **kw)
        # get random seed
        random.seed()
        # set maximum number of items to cull if over max
        self._maxcull = kw.get('maxcull', 10)
        # set max entries
        self._max_entries = kw.get('max_entries', 300)
        # set timeout
        self.timeout = kw.get('timeout', 300)

    def __getitem__(self, key):
        exp, value = super(SimpleCache, self).__getitem__(key)
        # delete if item timed out.
        if exp < time():
            super(SimpleCache, self).__delitem__(key)
            raise KeyError(key)
        return value

    def __setitem__(self, key, value):
        # cull values if over max number of entries
        if len(self) >= self._max_entries:
            self._cull()
        # set expiration time and value
        exp = time() + self.timeout
        super(SimpleCache, self).__setitem__(key, (exp, value))

    def _cull(self):
        # remove items in cache to make room
        num, maxcull = 0, self._maxcull
        # cull number of items allowed (set by self._maxcull)
        for key in self.keys():
            # remove only maximum # of items allowed by maxcull
            if num <= maxcull:
                # remove items if expired
                try:
                    self[key]
                except KeyError:
                    num += 1
            else:
                break
        choice = random.choice
        keys = list(self.keys())
        max_entries = self._max_entries
        # remove any additional items up to max # of items allowed by maxcull
        while len(self) >= max_entries and num <= maxcull:
            # cull remainder of allowed quota at random
            del self[choice(keys)]
            num += 1


class MemoryCache(SimpleCache):

    '''
    Thread-safe in-memory cache.

    The shove URI for a memory cache is:

    memory://
    '''

    def __init__(self, engine, **kw):
        super(MemoryCache, self).__init__(engine, **kw)
        self._lock = Condition()

    @synchronized
    def __getitem__(self, key):
        return deepcopy(super(MemoryCache, self).__getitem__(key))

    __setitem__ = synchronized(SimpleCache.__setitem__)
    __delitem__ = synchronized(SimpleCache.__delitem__)


class SimpleLRUCache(LRUBase):

    '''
    Single-process in-memory LRU cache that purges based on least recently
    used item.

    The shove URI for a simple cache is:

    simplelru://
    '''


class MemoryLRUCache(SimpleLRUCache):

    '''
    Thread-safe in-memory cache using LRU.

    The shove URI for a memory cache is:

    memlru://
    '''

    def __init__(self, engine, **kw):
        super(MemoryLRUCache, self).__init__(engine, **kw)
        self._lock = Condition()

    @synchronized
    def __getitem__(self, key):
        return deepcopy(super(MemoryLRUCache, self).__getitem__(key))

    __setitem__ = synchronized(SimpleLRUCache.__setitem__)
    __delitem__ = synchronized(SimpleLRUCache.__delitem__)


class FileCache(FileBase, SimpleCache):

    '''
    File-based cache

    shove's URI for file caches follows the form:

    file://<path>

    Where the path is a URI path to a directory on a local filesystem.
    Alternatively, a native pathname to the directory can be passed as the
    'engine' argument.
    '''

    def __init__(self, engine, **kw):
        super(FileCache, self).__init__(engine, **kw)

    def __getitem__(self, key):
        try:
            exp, value = super(FileCache, self).__getitem__(key)
            # remove item if time has expired.
            if exp < time():
                del self[key]
                raise KeyError(key)
            return value
        except:
            raise KeyError(key)

    def __setitem__(self, key, value):
        if len(self) >= self._max_entries:
            self._cull()
        super(FileCache, self).__setitem__(
            key, (time() + self.timeout, value)
        )


class FileLRUCache(FileBase, SimpleLRUCache):

    '''
    File-based LRU cache

    shove's URI for file caches follows the form:

    filelru://<path>

    Where the path is a URI path to a directory on a local filesystem.
    Alternatively, a native pathname to the directory can be passed as the
    'engine' argument.
    '''
