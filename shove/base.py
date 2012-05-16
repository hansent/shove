# -*- coding: utf-8 -*-
'''shove core.'''

import os
import zlib
from os.path import exists, join

from stuf.utils import ld, optimize
from stuf.six import HIGHEST_PROTOCOL

from shove._compat import url2pathname, quote_plus, unquote_plus


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
        value = optimize(value)
        if self._compress:
            value = zlib.compress(
                value, 9 if self._compress else self._compress
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
        return ld(value)


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
