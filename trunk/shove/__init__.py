# Copyright (c) 2005, the Lawrence Journal-World
# Copyright (c) 2005 Allan Saddi <allan@saddi.com>
# Copyright (c) 2006 L. C. Rees
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice, 
#       this list of conditions and the following disclaimer.
#    
#    2. Redistributions in binary form must reproduce the above copyright 
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
#    3. Neither the name of Django nor the names of its contributors may be used
#       to endorse or promote products derived from this software without
#       specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''Shove -- Universal Persistence and Caching.'''

import atexit
from shove.store import BaseStore

__all__ = ['Shove']

def _close(ref):
    '''Ensure store is closed at program termination.'''
    shove = ref()
    if shove is not None: store.close()

def synchronized(func):
    '''Decorator that locks and unlocks a method (by Phillip J. Eby).'''
    def wrapper(self, *__args, **__kw):
        self._lock.acquire()
        try:
            return func(self, *__args, **__kw)
        finally:
            self._lock.release()
    # Add same metainfo
    wrapper.__name__ = func.__name__
    wrapper.__dict__ = func.__dict__
    wrapper.__doc__ = func.__doc__
    return wrapper

def getshove(shove, uri, **kw):
    '''Loads a shove class.

    @param shove An instance or name string
    @param uri An init URI for a shove
    @param kw Keywords'''
    # Load module from storage
    if isinstance(shove, basestring): 
        dot = shove.rindex('.')
        # Load module
        mod = getattr(__import__(shove[:dot], '', '', ['']), shove[dot+1:])
        # Return instance
        return mod(uri, **kw)
    return shove

# Store registry
stores = dict(simple='shove.store.simple.SimpleStore',
    memory='shove.store.memory.MemoryStore',
    file='shove.store.file.FileStore',
    bsddb='shove.store.bsddb.BsddbStore',
    sqlite='shove.store.db.DbStore',
    postgres='shove.store.db.DbStore',
    mysql='shove.store.db.DbStore',
    oracle='shove.store.db.DbStore',
    svn='shove.store.svn.SvnStore',
    s3='shove.store.s3.S3Store',
    ftp='shove.store.ftp.FtpStore',
    zodb='shove.store.zodb.ZodbStore',
    durusdb='shove.store.durusdb.DurusStore')

# Cache registry
caches = dict(simple='shove.cache.simple.SimpleCache',
    memory='shove.cache.memory.MemoryCache',
    file='shove.cache.file.FileCache',
    sqlite='shove.cache.db.DbCache',
    postgres='shove.cache.db.DbCache',
    mysql='shove.cache.db.DbCache',
    oracle='shove.cache.db.DbCache',
    memcached='shove.cache.memcached.MemCached',
    bsddb='shove.cache.bsddb.BsddbCache')

    
class Base(object):

    '''Base Mapping class.'''
    
    def __init__(self):
        super(Base, self).__init__()
    
    def __getitem__(self, key):
        '''Fetch a given key from the mapping.'''
        raise NotImplementedError()

    def __setitem__(self, key, value):
        '''Set a value in the mapping. '''
        raise NotImplementedError()

    def __delitem__(self, key):
        '''Delete a key from the mapping.'''
        raise NotImplementedError()

    def __contains__(self, key):
        '''Tell if a given key is in the mapping.'''
        try:
            value = self[key]
        except KeyError:
            return False
        return True

    def get(self, key, default=None):
        '''Fetch a given key from the mapping. If the key does not exist,
        return default, which defaults to None.

        @param key Keyword of item in mapping.
        @param default Default value (default: None)
        '''
        try:
            return self[key]
        except KeyError:
            return default        

    def get_many(self, keys):
        '''Fetch a bunch of keys from the mapping. Returns a dict mapping each
        key in keys to its value. If the given key is missing, it will be
        missing from the response dict.

        @param keys Keywords of items in cache.
                '''
        response = dict()
        for k in keys:
            v = self.get(k)
            if v is not None: response[k] = v
        return response

    
class Shove(BaseStore):

    '''Shove class.'''
    
    def __init__(self, store='simple://', cache='simple://', **kw):
        super(Shove, self).__init__(**kw)
        # Load store
        sscheme = store.split(':', 1)[0]
        try:
            self._store = getshove(stores[sscheme], store, **kw)
        except (KeyError, ImportError):
            raise ImportError('Could not load store scheme "%s"' % sscheme)
        # Load cache
        cscheme = cache.split(':', 1)[0]
        try:
            self._cache = getshove(caches[cscheme], cache, **kw)
        except (KeyError, ImportError):
            raise ImportError('Invalid cache scheme "%s"' % cscheme)
        # Buffer for lazy writing and setting for frequency of syncing
        self._buffer, self._limit = dict(), kw.get('limit', 3)
        # Ensure close is called before program termination
        atexit.register(_close, self)

    def __getitem__(self, key):
        '''Gets a item from shove.'''
        try:
            return self._cache[key]
        except KeyError:
            # Synchronize cache and store
            self.sync()
            value = self._store[key]
            self._cache[key] = value
            return value

    def __setitem__(self, key, value):
        '''Sets an item in shove.'''
        self._cache[key] = value
        # When the buffer reaches self._limit, writes the buffer to the store
        if len(self._buffer) >= self._limit: self.sync()

    def __delitem__(self, key):
        '''Deletes an item from shove.'''
        try:
            del self._cache[key]
        except KeyError: pass
        self.sync()
        del self._store[key]

    def keys(self):
        '''Returns a list of keys in shove.'''
        self.sync()
        return self._store.keys()

    def sync(self):
        '''Writes buffer to store.'''
        for k, v in self._buffer.iteritems(): self._store[k] = v
        self._buffer.clear()
        
    def close(self):
        '''Finalizes and closes shove.'''
        self.sync()
        self._store.close()
        self._store = self._cache = self._buffer = None        