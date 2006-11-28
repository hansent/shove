# Copyright (c) 2005, the Lawrence Journal-World
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

'''File-based cache backend'''

import os
import time
import urllib
import random
try:
    import cPickle as pickle
except ImportError:
    import pickle
from cache.simple import SimpleCache

__all__ = ['FileCache']


class FileCache(SimpleCache):

    '''File-based cache backend'''    
    
    def __init__(self, engine, **kw):
        super(FileCache, self).__init__(engine, **kw)
        # Create directory
        try:
            self._dir = engine
        except IndexError:
            raise IOError('file.FileCache requires a valid directory path.')
        if not os.path.exists(self._dir): self._createdir()
        # Remove unneeded methods and attributes
        del self._cache
        del self._expire_info

    def __getitem__(self, key):
        '''Fetch a given key from the cache.  If the key does not exist, return
        default, which itself defaults to None.

        @param key Keyword of item in cache.
        @param default Default value (default: None)
        '''
        fname = self._key_to_file(key)
        try:
            f = open(fname, 'rb')
            exp, now = pickle.load(f), time.time()
            # Remove item if time has expired.
            if exp < now:
                f.close()
                os.remove(fname)
            return pickle.load(f)
        except (IOError, OSError, EOFError, pickle.PickleError): pass
                

    def __setitem__(self, key, value):
        '''Set a value in the cache.

        @param key Keyword of item in cache.
        @param value Value to be inserted in cache.        
        '''
        fname = self._key_to_file(key)
        try:
            filelist = os.listdir(self._dir)
        except (IOError, OSError):
            self._createdir()
            filelist = list()
        if len(filelist) > self._max_entries: self._cull()
        try:
            f = open(fname, 'wb')
            now = time.time()
            pickle.dump(now + self.timeout, f, 2)
            pickle.dump(value, f, 2)
        except (IOError, OSError): pass

    def __delitem__(self, key):
        '''Delete a key from the cache, failing silently.

        @param key Keyword of item in cache.
        '''
        try:
            os.remove(self._key_to_file(key))
        except (IOError, OSError): pass        

    def __contains__(self, key):
        '''Tell if a given key is in the cache.'''
        return os.path.exists(self._key_to_file(key))

    def get(self, key, default=None):
        '''Fetch a given key from the cache.  If the key does not exist, return
        default, which itself defaults to None.

        @param key Keyword of item in cache.
        @param default Default value (default: None)
        '''
        fname = self._key_to_file(key)
        try:
            f = open(fname, 'rb')
            exp, now = pickle.load(f), time.time()
            # Remove item if time has expired.
            if exp < now:
                f.close()
                os.remove(fname)
            else:
                return pickle.load(f)
        except (IOError, OSError, EOFError, pickle.PickleError): pass
        return default

    def _cull(self):
        '''Remove items in cache that have timed out.'''
        try:
            filelist = os.listdir(self._dir)
        except (IOError, OSError):
            self._createdir()
            filelist = list()
        num = 0
        for fname in filelist:
            if num < self._cullnum:
                # Remove expired items from cache.
                try:
                    f = open(fname, 'rb')
                    exp = pickle.load(f)
                    now = time.time()
                    if exp < now:
                        f.close()
                        del self[fname]
                        num += 1
                except (IOError, OSError, EOFError, pickle.PickleError): pass
            else: break            
        if len(self._cache) >= self._max_entries:
            for i in range(self._cullnum): del self[random.choice(filelist)]  

    def _createdir(self):
        '''Creates the cache directory.'''
        try:
            os.makedirs(self._dir)
        except OSError:
            raise EnvironmentError('Cache directory "%s" does not exist and ' \
                'could not be created' % self._dir)

    def _key_to_file(self, key):
        '''Gives the filesystem path for a key.'''
        return os.path.join(self._dir, urllib.quote_plus(key))