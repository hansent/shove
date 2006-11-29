# Copyright © 2001-2006 Python Software Foundation; All Rights Reserved
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
#    3. Neither the name of the Portable Site Information project nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
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

from shove import Base
from shove.store.simple import SimpleStore

__all__ = ['bsdb', 'db', 'durus', 'file', 'ftp', 'memory', 's3', 'simple',
    'svn', 'zodb']


class BaseStore(Base):

    '''Base Store class.'''
    
    def __init__(self):
        super(BaseStore, self).__init__()
        self._store = None

    def __cmp__(self, other):
        if other is None: return False
        if isinstance(other, BaseStore):  
            return cmp(dict(self.iteritems()), dict(other.iteritems()))

    def __del__(self):
        '''Handles object clean up if store is deleted and gced.'''
        # __init__ didn't succeed, so don't bother closing
        if not hasattr(self, '_store'): return
        self.close()
        
    def __iter__(self):
        for k in self.keys(): yield k

    def __len__(self):
        return len(self.keys())

    def __repr__(self):
        return repr(dict(self.iteritems()))

    def close(self):
        '''Closes internal store and clears object references.'''
        try:
            self._store.close()
        except AttributeError: pass
        self._store = None

    def clear(self):
        '''Removes all keys and values from a store.'''
        for key in self.keys(): del self[key]
     
    def items(self):
        '''Returns a list with all key/value pairs in the store.'''
        return list(self.iteritems())

    def iteritems(self):
        '''Lazily returns all key/value pairs in a store.'''        
        for k in self: yield (k, self[k])
            
    def iterkeys(self):
        '''Lazy returns all keys in a store.'''
        return self.__iter__()

    def itervalues(self):
        '''Lazily returns all values in a store.'''
        for _, v in self.iteritems(): yield v

    def keys(self):
        '''Returns a list with all keys in a store.'''
        raise NotImplementedError()        

    def pop(self, key, *args):
        '''Removes and returns a value from a store.

        @param args Default to return if key not present.'''
        if len(args) > 1:
            raise TypeError('pop expected at most 2 arguments, got '\
                + repr(1 + len(args)))
        try:
            value = self[key]            
        # Return default if key not in store
        except KeyError:
            if args: return args[0]
        del self[key]
        return value
        
    def popitem(self):
        '''Removes and returns a key, value pair from a store.'''
        try:
            k, v = self.iteritems().next()
        except StopIteration:
            raise KeyError('Container is empty')
        del self[k]
        return (k, v)
        
    def setdefault(self, key, default=None):
        '''Returns the value corresponding to an existing key or sets the
        to key to the default and returns the default.

        @param default Default value (default: None)        
        ''' 
        try:
            return self[key]
        except KeyError:
            self[key] = default
        return default

    def update(self, other=None, **kw):
        '''Adds to or overwrites the values in this store with values from
        another store.

        other Another store
        kw Additional keys and values to store
        '''        
        if other is None: pass
        elif hasattr(other, 'iteritems'):  
            for k, v in other.iteritems(): self[k] = v
        elif hasattr(other, 'keys'):
            for k in other.keys(): self[k] = other[k]
        else:
            for k, v in other: self[k] = v
        if kw: self.update(kw)

    def values(self):
        '''Returns a list with all values in a store.'''
        return list(v for _, v in self.iteritems())


class SyncStore(SimpleStore):

    '''Base class for stores where updates have to be committed.'''    

    def __init__(self, engine, **kw):
        super(SyncStore, self).__init__(engine, **kw)

    def __setitem__(self, key, value):        
        super(SyncStore, self).__setitem__(key, value)
        self.sync()

    def __delitem__(self, key):
        super(SyncStore, self).__delitem__(key)
        self.sync()