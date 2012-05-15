# -*- coding: utf-8 -*-
'''shove core.'''

import zlib

from stuf.utils import loads, dumps, items
from stuf.six import HIGHEST_PROTOCOL, keys


class Base(object):

    '''
    Base mapping.
    '''

    def __init__(self, engine, **kw):
        # keyword compress True, False, or an integer compression level (1-9)
        self._compress = kw.get('compress', False)
        # pickle protocol
        self._protocol = kw.get('protocol', HIGHEST_PROTOCOL)

    def __contains__(self, key):
        try:
            self[key]
            return True
        except KeyError:
            return False

    def dumps(self, value):
        '''
        Optionally serializes and compresses an object.
        '''
        # serialize anything but ASCII strings
        value = dumps(value, protocol=self._protocol)
        if self._compress:
            value = zlib.compress(
                value, 9 if self._compress is True else self._compress
            )
        return value

    def get(self, key, default=None):
        '''
        Fetch a given key from the mapping. If the key does not exist, return
        the default.

        :argument str key: keyword of item in mapping
        :keyword default: default value
        '''
        try:
            return self[key]
        except KeyError:
            return default

    def loads(self, value):
        '''
        Deserializes and optionally decompresses an object.
        '''
        if self._compress:
            try:
                value = zlib.decompress(value)
            except zlib.error:
                pass
        return loads(value)


class BaseStore(Base):

    '''Base Store (based on UserDict.DictMixin).'''

    def __cmp__(self, other):
        if other is None:
            return False
        if isinstance(other, BaseStore):
            return cmp(dict(self.items()), dict(other.items()))

    def __del__(self):
        # __init__ didn't succeed, so don't bother closing
        if not hasattr(self, '_store'):
            return
        self.close()

    def __iter__(self):
        for k in self.keys():
            yield k

    def __len__(self):
        return len(self.keys())

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

    def clear(self):
        '''
        Removes all keys and values from a store.
        '''
        for key in self.keys():
            del self[key]

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
        if other is None:
            pass
        elif hasattr(other, 'iteritems'):
            for k, v in items(other):
                self[k] = v
        elif hasattr(other, 'keys'):
            for k in keys(other):
                self[k] = other[k]
        else:
            for k, v in other:
                self[k] = v
        if kw:
            self.update(kw)

    def values(self):
        '''
        Lazily returns all values in a store.
        '''
        for _, v in self.items():
            yield v
