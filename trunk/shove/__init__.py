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

import weakref
import atexit

__all__ = ['Base', 'BaseStore', 'Shove', 'synchronized']

stores = dict(simple='shove.store.simple.SimpleStore',
    memory='shove.store.memory.MemoryStore',
    file='shove.store.file.FileStore',
    bsddb='shove.store.bsddb.BsddbStore',
    sqlite='shove.store.db.DbStore',
    postgres='shove.store.db.DbStore',
    mysql='shove.store.db.DbStore',
    oracle='shove.store.db.DbStore',
    svn='shove.store.svn.SvnStore',
    s3='shove.store.s3.S3Store')

caches = dict(simple='shove.cache.simple.SimpleCache',
    memory='shove.cache.memory.MemoryCache',
    file='shove.cache.file.FileCache',
    sqlite='shove.cache.db.DbCache',
    postgres='shove.cache.db.DbCache',
    mysql='shove.cache.db.DbCache',
    oracle='shove.cache.db.DbCache',
    memcached='shove.cache.memcached.MemCached')

def _close(ref):
    store = ref()
    if store is not None: store.close()

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

def getmod(module):
    '''Loads a callable based on its name

    @param module A module name'''
    dot = module.rindex('.')
    return getattr(__import__(module[:dot], '', '', ['']), module[dot+1:])

    
class Base(object):

    '''Base class.'''    
    
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


class BaseStore(Base):

    '''Base Store.'''

    def keys(self):
        raise NotImplementedError()

    def __iter__(self):
        for k in self.keys(): yield k

    def iteritems(self):
        for k in self: yield (k, self[k])
            
    def iterkeys(self):
        return self.__iter__()

    def itervalues(self):
        for _, v in self.iteritems(): yield v
        
    def values(self):
        return [v for _, v in self.iteritems()]
    
    def items(self):
        return list(self.iteritems())
    
    def clear(self):
        for key in self.keys(): del self[key]
        
    def setdefault(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            self[key] = default
        return default

    def pop(self, key, *args):
        if len(args) > 1:
            raise TypeError('pop expected at most 2 arguments, got '\
                + repr(1 + len(args)))
        try:
            value = self[key]
        except KeyError:
            if args: return args[0]
            raise
        del self[key]
        return value

    def popitem(self):
        try:
            k, v = self.iteritems().next()
        except StopIteration:
            raise KeyError('container is empty')
        del self[k]
        return (k, v)

    def update(self, other=None, **kw):
        # Make progressively weaker assumptions about "other"
        if other is None:
            pass
        elif hasattr(other, 'iteritems'):  
            for k, v in other.iteritems():
                self[k] = v
        elif hasattr(other, 'keys'):
            for k in other.keys():
                self[k] = other[k]
        else:
            for k, v in other:
                self[k] = v
        if kw:
            self.update(kw)

    def __repr__(self):
        return repr(dict(self.iteritems()))

    def __cmp__(self, other):
        if other is None: return False
        if isinstance(other, BaseStore): other = dict(other.iteritems())
        return cmp(dict(self.iteritems()), other)

    def __len__(self):
        return len(self.keys())


class Shove(BaseStore):

    '''Shove class.'''    
    
    def __init__(self, store='simple://', cache='simple://', **kw):
        super(Shove, self).__init__(**kw)       
        sscheme = store.split(':', 1)[0] 
        #try:
        self._store = getmod(stores[sscheme])(store, **kw)
        #except (KeyError, ImportError):
        #    raise ImportError('Invalid store scheme "%s"' % sscheme)
        cscheme = cache.split(':', 1)[0]
        try:
            self._cache = getmod(caches[cscheme])(cache, **kw)
        except (KeyError, ImportError):
            raise ImportError('Invalid cache scheme "%s"' % cscheme)
        atexit.register(_close, weakref.ref(self))

    def __getitem__(self, key):
        try:
            return self._cache[key]
        except KeyError:
            return self._store[key]

    def __setitem__(self, key, value):        
        self._store[key] = value
        self._cache[key] = value

    def __delitem__(self, key):
        del self._store[key]
        try:
            del self._cache[key]
        except KeyError: pass

    def __del__(self):
        # __init__ didn't succeed, so don't bother closing
        if not hasattr(self, '_store'): return
        self.close()

    def keys(self):
        return self._store.keys()

    def close(self):
        try:
            self._store.close()
        except AttributeError: pass
        self._store = None