# -*- coding: utf-8 -*-
'''shove store support.'''

import shutil
from copy import deepcopy
from threading import Condition

from stuf.six import items, keys

from shove.base import Base, SimpleBase, FileBase
from shove._compat import anydbm, synchronized, url2pathname

__all__ = ('DBMStore', 'FileStore', 'MemoryStore', 'SimpleStore')


class BaserStore(Base):

    '''Base Store (based on UserDict.DictMixin).'''

    def __eq__(self, other):
        if not isinstance(other, BaseStore):
            return NotImplemented
        return dict(self.items()) == dict(other.items())

    def __ne__(self, other):
        return not self == other

    def __iter__(self):
        for k in self.keys():
            yield k

    def __repr__(self):
        return repr(dict(self.items()))

    def close(self):
        '''
        Closes internal store and clears object references.
        '''
        try:
            self._store.close()
        except AttributeError:
            pass
        self._store = None

    def items(self):
        '''
        Lazily returns all key/value pairs in a store.
        '''
        for k in self:
            yield (k, self[k])

    def pop(self, key, *args):
        '''
        Removes and returns a value from a store.

        :argument str key: keyword in shove
        :param args: Default to return if key not present.
        '''
        if len(args) > 1:
            raise TypeError(
                'pop expected at most 2 arguments, got ' + repr(1 + len(args))
            )
        try:
            value = self[key]
        # Return default if key not in store
        except KeyError:
            if args:
                return args[0]
        del self[key]
        return value

    def popitem(self):
        '''
        Removes and returns a key, value pair from a store.
        '''
        try:
            k, v = next(self.items())
        except StopIteration:
            raise KeyError('store is empty')
        del self[k]
        return (k, v)


class BaseStore(BaserStore):

    '''Base Store (based on UserDict.DictMixin).'''

    def setdefault(self, key, default=None):
        '''
        Returns the value corresponding to an existing key or sets the to key
        to the default and returns the default.

        :argument str key: keyword in shove
        :keyword default: default value
        '''
        try:
            return self[key]
        except KeyError:
            self[key] = default
        return default

    def update(self, other=None, **kw):
        '''
        Adds to or overwrites the values in this store with values from
        another store.

        :keyword other: another store
        :param kw: additional keys and values to store
        '''
        if hasattr(other, 'items'):
            for k, v in items(other):
                self[k] = v
        elif hasattr(other, 'keys'):
            for k in keys(other):
                self[k] = other[k]
        elif other is not None:
            for k, v in other:
                self[k] = v
        if kw:
            self.update(kw)

    def values(self):
        '''
        Lazily returns all values in a store.
        '''
        for k in self:
            yield self[k]


class SimplerStore(SimpleBase, BaserStore):

    '''simpler'''


class SimpleStore(SimpleBase, BaseStore):

    '''
    Single-process in-memory store.

    The shove URI for a simple store is:

    simple://
    '''

    def __len__(self):
        return len(self.keys())

    def clear(self):
        '''
        Removes all keys and values from a store.
        '''
        for key in list(self.keys()):
            del self[key]


class ClientStore(SimpleStore):

    '''
    Base store where updates must be committed to disk.
    '''

    def __init__(self, engine, **kw):
        super(ClientStore, self).__init__(engine, **kw)
        if engine.startswith(self.init):
            self._engine = url2pathname(engine.split('://')[1])

    def __getitem__(self, key):
        return self.loads(super(ClientStore, self).__getitem__(key))

    def __setitem__(self, key, value):
        super(ClientStore, self).__setitem__(key, self.dumps(value))


class MemoryStore(SimpleStore):

    '''
    Thread-safe in-memory store.

    The shove URI for a memory store is:

    memory://
    '''

    def __init__(self, engine, **kw):
        super(MemoryStore, self).__init__(engine, **kw)
        self._lock = Condition()

    @synchronized
    def __getitem__(self, key):
        return deepcopy(super(MemoryStore, self).__getitem__(key))

    __setitem__ = synchronized(SimpleStore.__setitem__)
    __delitem__ = synchronized(SimpleStore.__delitem__)


class FileStore(FileBase, BaseStore):

    '''
    Filesystem-based object store.

    shove's URI for filesystem-based stores follows the form:

    file://<path>

    Where the path is a URI path to a directory on a local filesystem.
    Alternatively, a native pathname to the directory can be passed as the
    'engine' argument.
    '''

    def clear(self):
        shutil.rmtree(self._dir)
        self._createdir()


class SyncStore(ClientStore):

    '''
    Base store where updates have to be synced to disk.
    '''

    def __setitem__(self, key, value):
        super(SyncStore, self).__setitem__(key, value)
        try:
            self.sync()
        except AttributeError:
            pass

    def __delitem__(self, key):
        super(SyncStore, self).__delitem__(key)
        try:
            self.sync()
        except AttributeError:
            pass


class DBMStore(SyncStore):

    '''
    DBM Database Store.

    shove's URI for DBM stores follows the form:

    dbm://<path>

    Where <path> is a URL path to a DBM database. Alternatively, the native
    pathname to a DBM database can be passed as the 'engine' parameter.
    '''

    init = 'dbm://'

    def __init__(self, engine, **kw):
        super(DBMStore, self).__init__(engine, **kw)
        self._store = anydbm.open(self._engine, 'c')
        try:
            self.sync = self._store.sync
        except AttributeError:
            pass
