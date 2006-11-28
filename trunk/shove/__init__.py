# Copyright (c) 2005, the Lawrence Journal-World
# Copyright (c) 2005 Allan Saddi <allan@saddi.com>
# Copyright (c) 2006 L. C. Rees
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
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
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''Shove Base'''

import atexit
from shove.store import BaseStore

__all__ = ['Shove']

def _close(ref):
    shove = ref()
    if shove is not None: store.close()

def synchronized(func):
    def wrapper(self, *__args, **__kw):
        try:
            rlock = self._lock
        except AttributeError:
            from threading import RLock
            rlock = self.__dict__.setdefault('_lock', RLock())
        rlock.acquire()
        try:
            return func(self, *__args, **__kw)
        finally:
            rlock.release()
    wrapper.__name__ = func.__name__
    wrapper.__dict__ = func.__dict__
    wrapper.__doc__ = func.__doc__
    return wrapper

def getshove(shove, uri, **kw):
    '''Loads a shove class.

    @param shove A shove instance or name string
    @param uri An init URI for a shove
    @param kw Keywords'''
    if isinstance(shove, basestring): 
        dot = shove.rindex('.')
        mod = getattr(__import__(shove[:dot], '', '', ['']), shove[dot+1:])
        module = mod(uri, **kw)
    return shove

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
    durusdb='shove.store.durusdb.DurusStore',
    atom='shove.store.atom.AtomStore')

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

    '''Base class.'''    
    
    def __init__(self):
        super(Base, self).__init__()
    
    def __getitem__(self, key):
        '''Fetch a given key from the cache.'''
        raise NotImplementedError()

    def __setitem__(self, key, value):
        '''Set a value in the cache. '''
        raise NotImplementedError()

    def __delitem__(self, key):
        '''Delete a key from the cache, failing silently.

        @param key Keyword of item in cache.
        '''
        raise NotImplementedError()

    def __contains__(self, key):
        '''Tell if a given key is in the cache.'''
        try:
            value = self[key]
        except KeyError:
            return False
        return True

    def get(self, key, default=None):
        '''Fetch a given key from the cache.  If the key does not exist, return
        default, which itself defaults to None.

        @param key Keyword of item in cache.
        @param default Default value (default: None)
        '''
        try:
            return self[key]
        except KeyError:
            return default        

    def get_many(self, keys):
        '''Fetch a bunch of keys from the cache.  For certain backends
        (memcached, pgsql) this can be *much* faster when fetching multiple values.

        Returns a dict mapping each key in keys to its value.  If the given
        key is missing, it will be missing from the response dict.

        @param keys Keywords of items in cache.        
        '''
        d = dict()
        for k in keys:
            val = self.get(k)
            if val is not None: d[k] = val
        return d

    
class Shove(BaseStore):

    '''Shove class.'''    
    
    def __init__(self, store='simple://', cache='simple://', **kw):
        super(Shove, self).__init__(**kw)    
        sscheme = store.split(':', 1)[0] 
        try:
            self._store = getshove(stores[sscheme], store, **kw)
        except (KeyError, ImportError):
            raise ImportError('Could not load store scheme "%s"' % sscheme)
        cscheme = cache.split(':', 1)[0]
        try:
            self._cache = getshove(caches[cscheme], cache, **kw)
        except (KeyError, ImportError):
            raise ImportError('Invalid cache scheme "%s"' % cscheme)
        self._buffer, self._flushnum = dict(), kw.get('flushnum', 3)
        atexit.register(_close, self)

    def __getitem__(self, key):
        try:
            return self._cache[key]
        except KeyError:
            return self._store[key]

    def __setitem__(self, key, value):
        self._cache[key] = value
        if len(self._buffer) >= self._flushnum: self.sync()

    def __delitem__(self, key):
        try:
            del self._cache[key]
        except KeyError: pass
        try:
            del self._buffer[key]
        except KeyError: pass
        del self._store[key]        

    def keys(self):
        return self._store.keys()

    def sync(self):
        for k, v in self._buffer.iteritems(): self._store[k] = v
        self._buffer.clear()
        
    def close(self):
        self.sync()
        self._store.close()
        self._store = self._cache = self._buffer = None        