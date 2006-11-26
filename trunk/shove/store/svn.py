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

'''Subversion store.'''

import pysvn
import urllib
try:
    import cPickle as pickle
except ImportError:
    import pickle
from shove import BaseStore, synchronized

__all__ = ['SvnStore']


class SvnStore(BaseStore):

    '''Subversion-accessed store.'''    
    
    def __init__(self, engine, **kw):
        super(SvnStore, self).__init__(*a, **kw)
        self._engine, self._client = engine, pysvn.Client()
        if not os.path.exists(self._dir): self._createdir()

    @synchronized
    def __getitem__(self, key):
        '''Fetch a given key from the cache.  If the key does not exist, return
        default, which itself defaults to None.

        @param key Keyword of item in cache.
        @param default Default value (default: None)
        '''
        try:
            return pickle.load(open(self._key_to_file(key), 'rb'))
        except: pass
        return default

    @synchronized
    def __setitem__(self, key, value):
        '''Set a value in the cache.

        @param key Keyword of item in cache.
        @param value Value to be inserted in cache.        
        '''
        try:
            f = open(self._key_to_file(key), 'wb')
            pickle.dump(value, f, 2)
        except (IOError, OSError): pass

    @synchronized
    def __delitem__(self, key):
        '''Delete a key from the cache, failing silently.

        @param key Keyword of item in cache.
        '''
        try:
            os.remove(self._key_to_file(key))
        except (IOError, OSError): pass        

    @synchronized
    def __contains__(self, key):
        '''Tell if a given key is in the cache.'''
        return os.path.exists(self._key_to_file(key))       

    @synchronized
    def keys(self):
        try:
            return os.listdir(self._dir)
        except (IOError, OSError): return list()            

    @synchronized    
    def _createdir(self):
        '''Creates the cache directory.'''
        try:
            self._client.mkdir(self._dir)
        except OSError:
            raise EnvironmentError('Cache directory "%s" does not exist and ' \
                'could not be created' % self._dir)

    def _key_to_file(self, key):
        '''Gives the filesystem path for a key.'''
        return os.path.join(self._dir, urllib.quote_plus(key))